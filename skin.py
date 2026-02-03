import jarray

from fiji.process3d import EDT

from ij import IJ
from ij import ImagePlus
from ij import LookUpTable
from ij.gui import Overlay
from ij.gui import Plot
from ij.measure import ResultsTable
from ij.measure import CurveFitter
from ij.plugin import ImageCalculator
from ij.plugin import LutLoader
from ij.plugin import ZProjector
from ij.process import AutoThresholder
from ij.process import ImageConverter
from ij.process import LUT
from ij.plugin.filter import GaussianBlur
from ij.plugin.filter import RankFilters
from ij.plugin.filter import ThresholdToSelection


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
        self.image = image
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
        self.threshold = 650
        self.function="Gamma Variate"
        self.epidermisFillHoles = True
        
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
        self.subtractBackground()
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
        self.measure(self.corneum, self.statsCorneum, self.signalPerDepthCorneumTable)
        self.measure(self.epidermis, self.statsEpidermis, self.signalPerDepthEpidermisTable)
        self.measure(self.dermis, self.statsDermis, self.signalPerDepthDermisTable)
                
            
    def measure(self, zone, stats, perDepthtable):
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
        self.measurePenetrationDepths(stats, perDepthtable)
        
        
    def measurePenetrationDepths(self, stats, table):
        depths = table.getColumn("Depth")
        means = table.getColumn("Mean")
        fitter = CurveFitter(depths, means)
        function = CurveFitter.GAMMA_VARIATE
        if self.function == "Rodbard":
            function = CurveFitter.RODBARD
        fitter.doFit(function)
        noLimit = True
        noEntry = False
        first = True
        for depth in depths:
            if fitter.f(depth) <= self.threshold:
                noLimit = False
                if first:
                    depth = 0
                    noEntry = True
                break
            first = False
        stats["Depth"] = depth
        stats["%Depth"] = (depth * 100) / depths[-1]
        stats["Max. Depth"] = depths[-1]
        stats["Threshold"] = self.threshold
        
        
    def subtractBackground(self):
        mask = self.skin.getProcessor()
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
        
        
    def getDermisRoi(self):
        roi = self.getRoiOfMask(self.dermis)
        roi.setName("dermis")
        return roi
        
    
    def getEpidermisRoi(self):
        roi = self.getRoiOfMask(self.epidermis)
        roi.setName("epidermis")
        return roi 
        
    
    def getCorneumRoi(self):
        roi = self.getRoiOfMask(self.corneum)
        roi.setName("corneum")
        return roi
        
        
    def getRoiOfMask(self, mask):
        mask.getProcessor().setThreshold(125, 255)
        converter = ThresholdToSelection()
        roi = converter.convert(mask.getProcessor())
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
        
        
    def postProcess(self, mask):
        ip = mask.getProcessor()
        ip = Reconstruction.fillHoles(ip)
        ip.invert()
        ip = Reconstruction.fillHoles(ip)
        ip = BinaryImages.componentsLabeling(ip, 4, 16)
        ip = BinaryImages.keepLargestRegion(ip)
        ip.invert()
        ip = BinaryImages.componentsLabeling(ip, 4, 16)
        ip = BinaryImages.keepLargestRegion(ip)
        mask.setProcessor(ip)
        self.skin = mask
        
        
    def _prepareImage(self):
        if self.image.getNSlices() > 1:
            self._doMIPProjection()
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
        self.skin = ImagePlus("skin", segmenter.imageProcessor)  
        self.setCalibration(self.skin)
        self.postProcess(segmenter.mask)
        
 
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
        
        
    def addZoneToTable(self, zone, aTable, nameOfZone):
        aTable.addRow()
        rowIndex = aTable.size()-1
        aTable.setValue("Image", rowIndex, self.image.getTitle())
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
        
        
    def measureSignalPerDepth(self):
        skin = self.skin            
        edt = EDT()
        invertedSkinIP = skin.getProcessor().duplicate()
        invertedSkinIP.invert()
        invertedSkin = ImagePlus("inverted skin", invertedSkinIP)
        edtImage = edt.compute(invertedSkin.getStack())
        self.signalPerDepthCorneumTable = self.measureSignalPerDepthForZone(
                                                self.getCorneumRoi(), 
                                                ImagePlus("edt_corneum", edtImage.getProcessor().duplicate()))
        invertedSkin.setRoi(self.getCorneumRoi())
        IJ.run(invertedSkin, "Clear", "")
        invertedSkin.resetRoi()
        edtImage = edt.compute(invertedSkin.getStack())
        self.signalPerDepthEpidermisTable = self.measureSignalPerDepthForZone(
                                                self.getEpidermisRoi(), 
                                                ImagePlus("edt_epidermis", edtImage.getProcessor().duplicate()))
        invertedSkin.setRoi(self.getEpidermisRoi())
        IJ.run(invertedSkin, "Clear", "")
        invertedSkin.resetRoi()
        edtImage = edt.compute(invertedSkin.getStack())                                                        
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
        for t in range(1, int(round(stats.max))-self.delta):
            depth.append(self.signal.getCalibration().getX(t))
            ip.setThreshold(t,t+self.delta)
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
        depthEpidermis = self.signalPerDepthEpidermisTable.getColumn("Depth")
        meanEpidermis = self.signalPerDepthEpidermisTable.getColumn("Mean")
        depthDermis = self.signalPerDepthDermisTable.getColumn("Depth")
        meanDermis = self.signalPerDepthDermisTable.getColumn("Mean")
        depthEpidermis = [depth+depthCorneum[-1] for depth in depthEpidermis]
        depthDermis = [depth+depthEpidermis[-1] for depth in depthDermis]
        depthLabel = "depth[micron]"
        self.plot = Plot("Mean Nanoformulation per Depth", depthLabel, "Mean Intensity")
        self.plot.setLineWidth (2)
        self.plot.setColor("red")
        self.plot.add("line", depthCorneum, meanCorneum)
        self.plot.setColor("blue")
        self.plot.add("line", depthEpidermis, meanEpidermis) 
        self.plot.setColor("black")
        self.plot.add("line", depthDermis, meanDermis)     
        self.plot.addLegend ("stratum corneum\nepidermis\ndermis")
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