import jarray

from fiji.process3d import EDT

from ij import IJ
from ij import ImagePlus
from ij import LookUpTable
from ij.gui import Overlay
from ij.gui import Plot
from ij.gui import Roi
from ij.util import ArrayUtil
from ij.measure import ResultsTable
from ij.measure import CurveFitter
from ij.measure import Measurements
from ij.plugin import ImageCalculator
from ij.plugin import LutLoader
from ij.plugin import ZProjector
from ij.process import AutoThresholder
from ij.process import ImageConverter
from ij.process import LUT
from ij.plugin.filter import GaussianBlur
from ij.plugin.filter import RankFilters
from ij.plugin.filter import ThresholdToSelection

from inra.ijpb.math import ImageCalculator as InraImageCalculator
from inra.ijpb.binary import BinaryImages
from inra.ijpb.label import LabelImages
from inra.ijpb.measure import IntensityMeasures
from inra.ijpb.morphology import Reconstruction
from inra.ijpb.morphology.strel import DiskStrel
from inra.ijpb.plugins  import AnalyzeRegions

from net.imglib2.img import VirtualStackAdapter
from net.imglib2.img.display.imagej import ImageJFunctions
from sc.fiji.labkit.ui.segmentation import SegmentationTool



class SkinAnalyzer(object):
    """ Segment 3 zones in the skin, the stratum corneum, the epidermis and the dermis and measure the intensity of
        the signal in the 3 zones.
    """
    
    
    def __init__(self, image, options=None):
        """ Create a new skin-segmenter for the given image.
            
            Parameters:
                    image (ImagePlus): A 3 channel image with one brightfield channel for the whole skin, one
                                       channel with a staining of the nuclei and one channel for the signal to
                                       be measured.
        """
        self.title = image.getTitle()
        self.image = image
        self.path = image.getFileInfo()
        if image.getOriginalFileInfo():
            self.path = image.getOriginalFileInfo().getFilePath()
        
        self.nucleiChannel = 1
        self.signalChannel = 2
        self.brightfieldChannel = 3
        self.strelRadius=50
        self.delta = 1
        self.normalize = True
        self.removeHoles = True
        self.skinMedianRadius = 50
        self.epidermisSigma = 32
        self.threshold = 1600
        self.function="Polynomial"
        self.epidermisFillHoles = True
        self.subtractBackground = True
        self.measureOnCentralSlice = True
        self.nrOfSubzonesCorneum = 4
        self.nrOfSubzonesEpidermis = 4
        self.nrOfSubzonesDermis = 4
        
        self.startDistDermis = 0
        self.startDistEpidermis = 0
        self.startDistCorneum = 0
        self.skin = None
        self.corneum = None
        self.epidermis = None
        self.dermis = None
        self.signal = None
        self.holes = None
        self.statsCorneum = {"Area": 0, "Mean": 0, "StdDev": 0, 
                            "Max": 0, "Min": 0, "Median": 0, 
                            "Mode": 0, "Skewness": 0, "Kurtosis": 0, 
                            "Depth": 0, "%Depth": 0, "Max. Depth": 0,
                            "Threshold": 0}
        self.statsEpidermis = {"Area": 0, "Mean": 0, "StdDev": 0, 
                            "Max": 0, "Min": 0, "Median": 0, 
                            "Mode": 0, "Skewness": 0, "Kurtosis": 0,
                            "Depth": 0, "%Depth": 0, "Max. Depth": 0,
                            "Threshold": 0}
        self.statsDermis = {"Area": 0, "Mean": 0, "StdDev": 0, 
                            "Max": 0, "Min": 0, "Median": 0, 
                            "Mode": 0, "Skewness": 0, "Kurtosis": 0,
                            "Depth": 0, "%Depth": 0, "Max. Depth": 0,
                            "Threshold": 0}          
        self.signalPerDepthCorneumTable = None
        self.signalPerDepthEpidermisTable = None
        self.signalPerDepthDermisTable = None
        self.plot = None
        if options:
            self.setOptions(options)
        
                                
    def analyzeImage(self):
        self.overlayZonesOnImage()
        if self.subtractBackground:
            self.doBackgroundSubtraction()
        self.measureSignalPerDepth()    
        self.measureSignal()        
        self.createCombinedPlot()
        
        
    def segmentZones(self):
        """ Create a label image for each of the zones (corneum, epidermis and dermis).
        """
        self._prepareImage()
        self._segmentSkin()
        self._segmentEpidermis()
        self._segmentNonHoles()
        self._computeZones()
        
            
    def measureSignal(self):
        self.measure(self.corneum, self.statsCorneum, self.signalPerDepthCorneumTable, self.nrOfSubzonesCorneum)
        self.measure(self.epidermis, self.statsEpidermis, self.signalPerDepthEpidermisTable, self.nrOfSubzonesEpidermis)
        self.measure(self.dermis, self.statsDermis, self.signalPerDepthDermisTable, self.nrOfSubzonesDermis)
                
            
    def measure(self, zone, stats, perDepthTable, nrOfSubzones):
        features = AnalyzeRegions.Features()
        features.setAll(False)
        features.area = True   
        table = AnalyzeRegions.process(zone, features)
        stats["Area"] = table.getColumn('Area')[0]
        measures = IntensityMeasures(self.signal, zone)
        stats["Mean"] = measures.getMean().getColumn('Mean')[0]
        stats["StdDev"] = measures.getStdDev().getColumn('StdDev')[0]
        stats["Max"] = measures.getMax().getColumn('Max')[0]
        stats["Min"] = measures.getMin().getColumn('Min')[0]
        stats["Median"] = measures.getMedian().getColumn('Median')[0]
        stats["Mode"] = measures.getMode().getColumn('Mode')[0]
        stats["Skewness"] = measures.getSkewness().getColumn('Skewness')[0]
        stats["Kurtosis"] = measures.getKurtosis().getColumn('Kurtosis')[0]
        self.measurePenetrationDepths(stats, perDepthTable)
        self.measureSubRegions(stats, perDepthTable, nrOfSubzones)
        

    def getFunctionForFit(self):
        function = CurveFitter.GAMMA_VARIATE
        if self.function == "Rodbard":
            function = CurveFitter.RODBARD
        if self.function == "Polynomial":
            function = CurveFitter.POLY6
        return function
        
        
    @classmethod        
    def getIndexOfFirstLocalMaximum(cls, arr):
        for i in range(1, len(arr) - 1):
            if arr[i] > arr[i - 1] and arr[i] > arr[i + 1]:
                return i
        return 0                
        
        
    def measurePenetrationDepths(self, stats, table):
        depths = table.getColumn("Depth")
        means = table.getColumn("Mean")
        fitter = CurveFitter(depths, means)        
        fitter.doFit(self.getFunctionForFit())        
        fittedValues = [fitter.f(depth) for depth in depths]
        startIndex = self.getIndexOfFirstLocalMaximum(fittedValues)
        first = True
        for depth in depths[startIndex:]:
            if fitter.f(depth) <= self.threshold:
                if first:
                    depth = 0
                break
            first = False
        stats["Depth"] = depth
        stats["%Depth"] = (depth * 100) / depths[-1]
        stats["Max. Depth"] = depths[-1]
        stats["Threshold"] = self.threshold
        
        
    def measureSubRegions(self, stats, table, nrOfZones):    
        depths = table.getColumn("Depth")       
        means = table.getColumn("Mean")
        fitter = CurveFitter(depths, means)        
        fitter.doFit(self.getFunctionForFit())        
        fittedValues = [fitter.f(depth) for depth in depths]
        chunkedDepths = self.chunkList(depths, nrOfZones)
        chunkedMeans = self.chunkList(fittedValues, nrOfZones)
        stats['Means'] = []
        stats['StdDevs'] = []
        stats['Starts'] = []
        stats['Ends'] = []
        for depthsChunk, meansChunk in zip(chunkedDepths, chunkedMeans):
            util = ArrayUtil(meansChunk)
            stats["Means"].append(util.getMean())
            stats["StdDevs"].append(util.getVariance() ** 0.5)
            stats["Starts"].append(depthsChunk[0])
            stats["Ends"].append(depthsChunk[-1])
            
        
    @classmethod
    def chunkList(cls, aList, nrOfChunks):
        lst = aList[:]
        chunked = []
        for i in reversed(range(1, nrOfChunks + 1)):
            split_point = len(lst) // i
            chunked.append(lst[:split_point])
            lst = lst[split_point:]
        return chunked
        
        
    def doBackgroundSubtraction(self):
        mask = self.skin.getProcessor().duplicate()
        mask.invert()
        strel = DiskStrel.fromRadius(self.strelRadius)
        mask = strel.erosion(mask)
        maskImage = ImagePlus("background", mask)
        measures = IntensityMeasures(self.signal, maskImage)
        table = measures.getMean()
        mean = table.getColumn('Mean')[0]
        self.signal.getProcessor().subtract(mean)
        
             
    def overlayZonesOnImage(self):
        if not self.dermis:
            self.segmentZones()
        overlay = Overlay()
        overlay.add(self.getDermisRoi())
        overlay.add(self.getEpidermisRoi())
        overlay.add(self.getCorneumRoi())
        self.image.setOverlay(overlay)
        
        
    def getDermisRoi(self, filled=False):
        roi = self.getRoiOfMask(self.dermis, filled)
        roi.setName("dermis")
        return roi
        
    
    def getEpidermisRoi(self, filled=False):
        roi = self.getRoiOfMask(self.epidermis, filled)
        roi.setName("epidermis")
        return roi 
        
    
    def getCorneumRoi(self, filled=False):
        roi = self.getRoiOfMask(self.corneum, filled)
        roi.setName("corneum")
        return roi
        
        
    def getRoiOfMask(self, mask, filled):
        layerMask = mask.duplicate()
        if filled:
            self.postProcess(layerMask, split=True)
        layerMask.getProcessor().setThreshold(125, 255)
        converter = ThresholdToSelection()
        roi = converter.convert(layerMask.getProcessor())
        return roi
        
        
    def doNormalize(self):
        converter = ImageConverter(self.image)
        converter.convertToGray32()
        channels = self.image.getNChannels()
        for c in range(1, channels+1):
            ip = self.image.getStack().getProcessor(c)
            stats = ip.getStats()
            ip.subtract(stats.mean)
            ip.multiply(1.0 / stats.stdDev)


    @classmethod
    def postProcessOneBackground(cls, mask):
        ip = mask.getProcessor()
        ip = Reconstruction.fillHoles(ip)
        ip.invert()
        ip = Reconstruction.fillHoles(ip)
        ip.invert()
        ip = BinaryImages.componentsLabeling(ip, 4, 16)
        ip = BinaryImages.keepLargestRegion(ip)
        ip.invert()
        ip = BinaryImages.componentsLabeling(ip, 4, 16)
        ip = BinaryImages.keepLargestRegion(ip)
        ip.invert()
        return ip


    @classmethod
    def postProcessSplitBackground(cls, mask):        
        ip = mask.getProcessor()
        ip = Reconstruction.fillHoles(ip)
        ip.invert()
        ip = Reconstruction.fillHoles(ip)
        ip.invert()
        ip = BinaryImages.componentsLabeling(ip, 4, 16)
        ip = BinaryImages.keepLargestRegion(ip)
        ip.invert()
        ip = BinaryImages.componentsLabeling(ip, 4, 16)
        ip1 = BinaryImages.keepLargestRegion(ip)
        LabelImages.removeLargestLabel(ip)
        ip2 = BinaryImages.keepLargestRegion(ip)
        op = InraImageCalculator.Operation.OR
        ip = InraImageCalculator.combineImages(ip1, ip2, op)
        ip.invert()
        return ip
        
        
    @classmethod        
    def disconnectLowerBorder(cls, mask):        
        width = mask.getWidth()
        height = mask.getHeight()
        roi = Roi(0, height-2, width, 4)
        mask.setRoi(roi)
        IJ.setBackgroundColor(0, 0, 0);
        IJ.run(mask, "Clear", "slice");
        mask.resetRoi()
    
    
    def postProcess(self, mask, split=False):
        self.disconnectLowerBorder(mask)
        if split:
            ip = self.postProcessSplitBackground(mask)
        else:
            ip = self.postProcessOneBackground(mask)
        mask.setProcessor(ip)
        
        
    def _prepareImage(self):
        if self.measureOnCentralSlice:
            nSlices = self.image.getDimensions()[3]
            middleIndex = nSlices // 2
            stack = self.image.getImageStack()
            index = self.image.getStackIndex(2, middleIndex, 1)
            self.signal = ImagePlus("signal", stack.getProcessor(index).duplicate())
        if self.image.getNSlices() > 1:
            self._doMIPProjection()
        if not self.measureOnCentralSlice:            
            self.signal = ImagePlus("signal", self.image.getStack().getProcessor(self.signalChannel))
        self.setCalibration(self.signal)
        if self.normalize:
            self.doNormalize()
        LUTTool.applyLutToChannel("blue", self.image, self.nucleiChannel)
        LUTTool.applyLutToChannel("red", self.image, self.signalChannel)
        LUTTool.applyLutToChannel("grays", self.image, self.brightfieldChannel)
        self.image.updateAndDraw()
            
            
    def _segmentSkin(self):
        self.image.resetRoi()
        ip = self.image.getStack().getProcessor(self.brightfieldChannel).duplicate()
        segmenter = SkinSegmenter(ip)
        segmenter.medianRadius = self.skinMedianRadius
        segmenter.run()    
        self.postProcess(segmenter.mask)
        self.skin = segmenter.mask
        self.setCalibration(self.skin)

 
    def setCalibration(self, image):
        cal = self.image.getCalibration()
        cal.pixelDepth = 0
        image.setCalibration(cal)
        
        
    def _segmentEpidermis(self):
        self.image.resetRoi()
        ip = self.image.getStack().getProcessor(self.nucleiChannel).duplicate()
        segmenter = EpidermisSegmenter(ip)
        segmenter.sigma = self.epidermisSigma
        segmenter.fillHoles = self.epidermisFillHoles
        segmenter.run()
        self.epidermis = ImagePlus("epidermis", segmenter.imageProcessor)
        self.setCalibration(self.epidermis)              
        
        
    def _computeZones(self):
         mask = ImageCalculator.run(self.skin, self.epidermis, "XOR create")
         ip = BinaryImages.componentsLabeling(mask.getProcessor(), 4, 16)
         labels = ImagePlus("labels of zones", ip)
         self.dermis = LabelImages.keepLargestLabel(labels)
         self.dermis.setProcessor(self.dermis.getProcessor())
         self.dermis.setTitle("dermis")
         self.setCalibration(self.dermis)
         LabelImages.removeLargestLabel(labels)
         self.corneum = LabelImages.keepLargestLabel(labels)
         self.corneum.setTitle("corneum")
         self.setCalibration(self.corneum)
         features = AnalyzeRegions.Features()
         features.setAll(False)
         features.centroid = True   
         dermisY = AnalyzeRegions.process(self.dermis, features).getColumn("Centroid.Y")[0]
         corneumY = AnalyzeRegions.process(self.corneum, features).getColumn("Centroid.Y")[0]
         if corneumY < dermisY:
            tmp = self.corneum
            self.corneum = self.dermis
            self.dermis = tmp
         if self.removeHoles:
            self.removeHolesInZones()
         
        
    def removeHolesInZones(self):
        self.corneum = self.removeHolesIn(self.corneum)
        self.epidermis = self.removeHolesIn(self.epidermis)
        
        
    def removeHolesIn(self, image):
        result = ImageCalculator.run(image, self.holes, "AND create")
        return result
        
        
    def _segmentNonHoles(self):
         self.image.resetRoi()
         ip = self.image.getStack().getProcessor(self.brightfieldChannel).duplicate()
         image = ImagePlus("holes", ip)
         path = self.getClassifierPath()
         segmenter = SegmentationTool(None)
         segmenter.setUseGpu(False)
         segmenter.openModel(path)
         self.holes = segmenter.segment(VirtualStackAdapter.wrap(image))
         self.holes = ImagePlus("holes", ImageJFunctions.wrap(self.holes, "").getProcessor().duplicate())
         self.holes.getProcessor().setThreshold (0,0)
         self.holes.setProcessor(self.holes.getProcessor().createMask())      
         
         
    @classmethod
    def getClassifierPath(cls):
        path = IJ.addSeparator(IJ.getDirectory("plugins")) +  "skin_drug_delivery"
        path = IJ.addSeparator(path) + "holes.classifier"
        return path
    
    
    def _doMIPProjection(self):
        self.image = ZProjector.run(self.image, "max")
        
        
    def getTable(self):
        table = ResultsTable()
        self.addToTable(table)
        return table
        
        
    def addToTable(self, aTable):
        self.addZoneToTable(self.statsCorneum, aTable, "corneum")
        self.addZoneToTable(self.statsEpidermis, aTable, "epidermis")
        self.addZoneToTable(self.statsDermis, aTable, "dermis")
        
    
    def replaceInTable(self, aTable):
        self.replaceZoneInTable(self.statsCorneum, aTable, "corneum")
        self.replaceZoneInTable(self.statsEpidermis, aTable, "epidermis")
        self.replaceZoneInTable(self.statsDermis, aTable, "dermis")
        
        
    def addZoneToTable(self, zone, aTable, nameOfZone):
        aTable.addRow()
        rowIndex = aTable.size()-1
        self.setRowInTable(rowIndex, zone, aTable, nameOfZone)
        
        
    def replaceZoneInTable(self, zone, aTable, nameOfZone):
        rowIndex = self.getIndexInTable(nameOfZone, aTable)
        if rowIndex == -1:
            return
        self.setRowInTable(rowIndex, zone, aTable, nameOfZone)
        
        
    def getIndexInTable(self, nameOfZone, table):
        images = table.getColumnAsStrings("Image")
        zones = table.getColumnAsStrings("Zone")
        for index, (image, zone) in enumerate(zip(images, zones)):
            if self.title == image and zone == nameOfZone:
                return index
        return -1                
        
        
    def setRowInTable(self, rowIndex, zone, aTable, nameOfZone):
        aTable.setValue("Image", rowIndex, self.title)
        aTable.setValue("Zone", rowIndex, nameOfZone)
        aTable.setValue("Area", rowIndex, zone["Area"])
        aTable.setValue("Mean", rowIndex, zone["Mean"])
        aTable.setValue("StdDev", rowIndex, zone["StdDev"])
        aTable.setValue("Max", rowIndex, zone["Max"])
        aTable.setValue("Min", rowIndex, zone["Min"])
        aTable.setValue("Median", rowIndex, zone["Median"])
        aTable.setValue("Mode", rowIndex, zone["Mode"])
        aTable.setValue("Skewness", rowIndex, zone["Skewness"])
        aTable.setValue("Kurtosis", rowIndex, zone["Kurtosis"])
        aTable.setValue("Depth", rowIndex, zone["Depth"])
        aTable.setValue("%Depth", rowIndex, zone["%Depth"])
        aTable.setValue("Max. Depth", rowIndex, zone["Max. Depth"])
        aTable.setValue("Threshold", rowIndex, zone["Threshold"])
        aTable.setValue("Path", rowIndex, self.path)
        index = 1
        for mean, stdDev, start, end in zip(zone["Means"],zone["StdDevs"], zone["Starts"], zone["Ends"]):
            aTable.setValue("Mean-" + str(index), rowIndex, mean)
            aTable.setValue("StdDev-" + str(index), rowIndex, stdDev)
            aTable.setValue("Start" + str(index), rowIndex, start)
            aTable.setValue("End" + str(index), rowIndex, end)
            index = index + 1
        
        
    def measureSignalPerDepth(self):
        skin = self.skin            
        edt = EDT()
        duplicatedSkinIP = skin.getProcessor().duplicate()
        duplicatedSkin = ImagePlus("duplicated skin", duplicatedSkinIP)
        edtImage = edt.compute(duplicatedSkin.getStack())
        edtImage.setRoi(self.getEpidermisRoi())
        stats = edtImage.getStatistics(Measurements.MIN_MAX)
        self.startDistEpidermis = stats.min
        edtImage.setRoi(self.getDermisRoi())
        stats = edtImage.getStatistics(Measurements.MIN_MAX)
        self.startDistDermis = stats.min
        edtImage.resetRoi()
        self.signalPerDepthCorneumTable = self.measureSignalPerDepthForZone(
                                                self.getCorneumRoi(), 
                                                ImagePlus("edt_corneum", edtImage.getProcessor().duplicate()))        
        duplicatedSkin.setRoi(self.getCorneumRoi(filled=True))
        IJ.run(duplicatedSkin, "Clear", "")
        duplicatedSkin.resetRoi()
        edtImage = edt.compute(duplicatedSkin.getStack())
        edtImage.resetRoi()
        self.signalPerDepthEpidermisTable = self.measureSignalPerDepthForZone(
                                                self.getEpidermisRoi(), 
                                                ImagePlus("edt_epidermis", edtImage.getProcessor().duplicate()))        
        duplicatedSkin.setRoi(self.getEpidermisRoi(filled=True))
        IJ.run(duplicatedSkin, "Clear", "")
        duplicatedSkin.resetRoi()      
        edtImage = edt.compute(duplicatedSkin.getStack())    
        self.signalPerDepthDermisTable = self.measureSignalPerDepthForZone(
                                                self.getDermisRoi(), 
                                                ImagePlus("edt_dermis", edtImage.getProcessor().duplicate()))                                                
        
        
        
    def measureSignalPerDepthForZone(self, zoneRoi, edt):
        IJ.setBackgroundColor(0, 0, 0)
        IJ.setForegroundColor(255, 255, 255)
        edt.setRoi(zoneRoi)
        IJ.run(edt, "Clear Outside", "")
        edt.resetRoi()
        edt.updateAndDraw()
        ip = edt.getProcessor()
        stats = ip.getStats()
        area = []
        mean = []
        stdDev = []
        depth = []
        for t in range(1, int(round(stats.max))):
            depth.append(self.signal.getCalibration().getX(t))
            if self.delta < 3:
                ip.setThreshold(t, t + 1)
            else:            
                leftOffset = self.delta // 2
                rightOffset = self.delta // 2
                if t - leftOffset < 0:
                    leftOffset = t
                if t + rightOffset > int(round(stats.max)):
                    rightOffset =  int(round(stats.max)) - t
                ip.setThreshold(t - leftOffset, t + rightOffset)                
            mask = ip.createMask()
            features = AnalyzeRegions.Features()
            features.setAll(False)
            features.area = True   
            table = AnalyzeRegions.process(ImagePlus("mask", mask), features)
            area.append(table.getColumn('Area')[0])
            measures = IntensityMeasures(self.signal, ImagePlus("mask", mask))
            mean.append(measures.getMean().getColumn('Mean')[0])
            stdDev.append(measures.getStdDev().getColumn('StdDev')[0])      
        table = ResultsTable()
        table.setValues("Depth", jarray.array(depth, "d"))
        table.updateResults()
        table.setValues("Mean", jarray.array(mean, "d"))
        table.updateResults()
        table.setValues("StdDev", jarray.array(stdDev, "d"))
        table.updateResults()
        table.setValues("Area", jarray.array(area, "d"))
        table.updateResults()
        return table

        
    def createCombinedPlot(self):
        depthCorneum = self.signalPerDepthCorneumTable.getColumn("Depth")
        meanCorneum = self.signalPerDepthCorneumTable.getColumn("Mean")
        corneumFitter = CurveFitter(depthCorneum, meanCorneum)
        corneumFitter.doFit(self.getFunctionForFit())
        corneumFittedValues = [corneumFitter.f(depth) for depth in depthCorneum] 
        depthEpidermis = self.signalPerDepthEpidermisTable.getColumn("Depth")
        meanEpidermis = self.signalPerDepthEpidermisTable.getColumn("Mean")
        epidermisFitter = CurveFitter(depthEpidermis, meanEpidermis)
        epidermisFitter.doFit(self.getFunctionForFit())
        epidermisFittedValues = [epidermisFitter.f(depth) for depth in depthEpidermis] 
        depthDermis = self.signalPerDepthDermisTable.getColumn("Depth")
        meanDermis = self.signalPerDepthDermisTable.getColumn("Mean")
        dermisFitter = CurveFitter(depthDermis, meanDermis)
        dermisFitter.doFit(self.getFunctionForFit())
        dermisFittedValues = [dermisFitter.f(depth) for depth in depthDermis] 
        deltaEpidermis = self.signal.getCalibration().getX(self.startDistEpidermis)
        deltaDermis = self.signal.getCalibration().getX(self.startDistDermis)
        depthEpidermis = [depth + deltaEpidermis for depth in depthEpidermis]
        depthDermis = [depth + deltaDermis for depth in depthDermis]    
        thresholdCorneum = [self.threshold] * len(meanCorneum)
        thresholdEpidermis = [self.threshold] * len(meanEpidermis)
        thresholdDermis = [self.threshold] * len(meanDermis)
        depthLabel = "depth[micron]"
        self.plot = Plot("Mean Nanoformulation per Depth", depthLabel, "Mean Intensity")
        self.plot.setLineWidth (1)
        self.plot.setColor("red")
        self.plot.add("circle", depthCorneum, meanCorneum)
        self.plot.setLineWidth (3)
        self.plot.add("line", depthCorneum, corneumFittedValues)
        self.plot.setLineWidth (1)
        self.plot.setColor("magenta")
        self.plot.setLineWidth (2)
        self.plot.add("line", depthCorneum, thresholdCorneum)
        self.plot.setLineWidth (1)
        self.plot.setColor("blue")
        self.plot.add("circle", depthEpidermis, meanEpidermis) 
        self.plot.setLineWidth (3)
        self.plot.add("line", depthEpidermis, epidermisFittedValues)
        self.plot.setLineWidth (1)
        self.plot.setColor("magenta")
        self.plot.setLineWidth (2)
        self.plot.add("line", depthEpidermis, thresholdEpidermis)
        self.plot.setLineWidth (1)
        self.plot.setColor("black")
        self.plot.add("circle", depthDermis, meanDermis)     
        self.plot.setLineWidth (3)
        self.plot.add("line", depthDermis, dermisFittedValues)
        self.plot.setLineWidth (1)
        self.plot.setColor("magenta")
        self.plot.setLineWidth (2)
        self.plot.add("line", depthDermis, thresholdDermis)
        self.plot.setLineWidth (1)
        self.plot.addLegend ("0_stratum corneum values\n1__stratum corneum\n2_threshold stratum\n3_epidermis values\n4__epidermis\n5_threshold_epidermis\n6_dermis values\n7__dermis\n8_threshold dermis")
        self.plot.setLimitsToFit(True)


    def setOptions(self, options):
        self.nucleiChannel = options.value("nuclei channel")
        self.signalChannel = options.value("signal channel")
        self.brightfieldChannel = options.value("brightfield channel")
        self.strelRadius = options.value("erosion radius")
        self.delta = options.value("delta")
        self.skinMedianRadius = options.value("median radius skin")
        self.epidermisSigma = options.value("sigma epidermis")
        self.normalize = options.value("normalize")
        self.epidermisFillHoles = options.value("fill holes epidermis")
        self.removeHoles = options.value("remove holes")
        self.threshold = options.value("threshold")
        self.function = options.value("function")
        self.subtractBackground = options.value("subtract background")
        self.measureOnCentralSlice = options.value("measure on central slice")
        self.nrOfSubzonesCorneum = options.value("corneum subregions")
        self.nrOfSubzonesEpidermis = options.value("epidermis subregions")
        self.nrOfSubzonesDermis = options.value("dermis subregions")
       
       
       
class SkinSegmenter(object):
    
    
    def __init__(self, imageProcessor):
        self.imageProcessor = imageProcessor
        self.medianRadius = 50
        self.mask = None
        
    
    def run(self):
        self.imageProcessor.findEdges()
        median = RankFilters()
        median.rank(self.imageProcessor, self.medianRadius, RankFilters.MEDIAN)
        self.imageProcessor.setAutoThreshold(AutoThresholder.Method.Minimum, True)
        self.mask = ImagePlus("mask of skin", self.imageProcessor.createMask())
        
        
        
class EpidermisSegmenter(object):
    
    
    def __init__(self, imageProcessor):
        self.imageProcessor = imageProcessor
        self.sigma = 32
        self.fillHoles = True
        self.mask = None
        
        
    def run(self):
        ip = self.imageProcessor
        gaussian = GaussianBlur()
        gaussian.blurGaussian(ip, self.sigma)
        ip.setAutoThreshold(AutoThresholder.Method.Default, True)
        ip = ip.createMask()
        if self.fillHoles:
            ip = Reconstruction.fillHoles(ip)
        ip = BinaryImages.componentsLabeling(ip, 4, 16)
        ip = BinaryImages.keepLargestRegion(ip)
        ip.setAutoThreshold(AutoThresholder.Method.Default, True)
        self.imageProcessor = ip.createMask()
        
        
        
class LUTTool(object):
    
    
    @classmethod
    def applyLutToChannel(cls, lut_name, image, channel):
        cm = LutLoader.getLut(lut_name)
        ltable = LookUpTable(cm)
        lut = LUT(ltable.getReds(), ltable.getGreens(), ltable.getBlues())
        image.setChannelLut(lut, channel)
        IJ.run(image, "Enhance Contrast", "saturated=0.35");
        image.setDisplayMode(IJ.COMPOSITE);
        image.updateAndDraw()