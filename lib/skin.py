from ij import ImagePlus
from ij.plugin import ZProjector
from ij.process import ImageConverter
from ij.plugin.filter import RankFilters
from ij.process import AutoThresholder


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
        
        
    def _prepareImage(self):
        if self.image.getNSlices() > 1:
            self._doMIPProjection()
        if self.normalize:
            self.doNormalize()
        
        
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
        
        
        
    def _segmentSkin(self):
        self.image.resetRoi()
        ip = self.image.getStack().getProcessor(self.brightfieldChannel).duplicate()
        segmenter = SkinSegmenter(ip)
        segmenter.run()
        self.skin = ImagePlus("skin", segmenter.imageProcessor)       
        self.postProcess(mask)
        
 
    def _segmentEpidermis(self):
        pass
        
        
    def _computeZones(self):
        pass
        
        
    def _doMIPProjection(self):
        self.image = ZProjector.run(self.image, "max")
        
        
        
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
        self.mask = self.imageProcessor.createMask()
        
        
        