from ij import ImagePlus
from ij import LookUpTable
from ij.gui import Overlay
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
from inra.ijpb.morphology import Reconstruction






class SkinAnalyzer(object):
    """ Segment 3 zones in the skin, the cornea, the epidermis and the dermis and measure the intensity of
        the signal in the 3 zones.
    """
    
    
    def __init__(self, image):
        """ Create a new skin-segmenter for the given image.
            
            Parameters:
                    image (ImagePlus): A 3 channel image with one brightfield channel for the whole skin, one
                                       channel with a staining of the nuclei and one channel for the signal to
                                       be measured.
        """
        self.image = image
        self.nucleiChannel = 1
        self.signalChannel = 2
        self.brightfieldChannel = 3
        self.normalize = True
        self.skin = None
        self.cornea = None
        self.epidermis = None
        self.dermis = None
        
        
    def segmentZones(self):
        """ Create a label image for each of the zones (cornea, epidermis and dermis).
        """
        self._prepareImage()
        self._segmentSkin()
        self._segmentEpidermis()
        self._computeZones()
        
    
    def overlayZonesOnImage(self):
        if not self.dermis:
            self.segmentZones()
        overlay = Overlay()
        overlay.add(self.getDermisRoi())
        overlay.add(self.getEpidermisRoi())
        overlay.add(self.getCorneaRoi())
        self.image.setOverlay(overlay)
        
        
    def getDermisRoi(self):
        roi = self.getRoiOfMask(self.dermis)
        roi.setName("dermis")
        return roi
        
    
    def getEpidermisRoi(self):
        roi = self.getRoiOfMask(self.epidermis)
        roi.setName("epidermis")
        return roi 
        
    
    def getCorneaRoi(self):
        roi = self.getRoiOfMask(self.cornea)
        roi.setName("cornea")
        return roi
        
        
    def getRoiOfMask(self, mask):
        mask.getProcessor().setThreshold(0,125)
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
        if self.normalize:
            self.doNormalize()
        LUTTool.applyLutToChannel("blue", self.image, self.nucleiChannel)
        LUTTool.applyLutToChannel("red", self.image, self.signalChannel)
        LUTTool.applyLutToChannel("grays", self.image, self.brightfieldChannel)
            
            
    def _segmentSkin(self):
        self.image.resetRoi()
        ip = self.image.getStack().getProcessor(self.brightfieldChannel).duplicate()
        segmenter = SkinSegmenter(ip)
        segmenter.run()
        self.skin = ImagePlus("skin", segmenter.imageProcessor)       
        self.postProcess(segmenter.mask)
        
 
    def _segmentEpidermis(self):
        self.image.resetRoi()
        ip = self.image.getStack().getProcessor(self.nucleiChannel).duplicate()
        segmenter = EpidermisSegmenter(ip)
        segmenter.run()
        self.epidermis = ImagePlus("epidermis", segmenter.imageProcessor)
              
        
    def _computeZones(self):
         mask = ImageCalculator.run(self.skin, self.epidermis, "XOR create")
         ip = BinaryImages.componentsLabeling(mask.getProcessor(), 4, 16)
         labels = ImagePlus("labels of zones", ip)
         largest = LabelImages.findLargestLabel(labels) 
         if not largest == 2:
            print("Could not segment 3 zones")
            return
         self.dermis = LabelImages.keepLabels(labels, [1])
         self.dermis.getProcessor().setThreshold (1,65535)
         self.dermis.setProcessor(self.dermis.getProcessor().createMask())
         self.dermis.setTitle("dermis")
         self.cornea = LabelImages.keepLabels(labels, [2])
         self.cornea.getProcessor().setThreshold (2,65535)
         self.cornea.setProcessor(self.cornea.getProcessor().createMask())
         self.cornea.setTitle("cornea")
        
        
    def _doMIPProjection(self):
        self.image = ZProjector.run(self.image, "max")
        self.image.getStack().getProcessor(self.nucleiChannel).set
        
        
        
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
        self.mask = None
        self.fillHoles = True
        
        
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
        image.getStack().getProcessor(channel).setLut(lut)
        image.updateAndDraw()