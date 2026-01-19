from ij.plugin import ZProjector



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
        
        
    def _segmentSkin(self):
        pass
        
        
    def _segmentEpidermis(self):
        pass
        
        
    def _computeZones(self):
        pass
        
        
    def _doMIPProjection(self):
        self.image = ZProjector(self.image, ZProjector.MAX_METHOD)
        
        
        
