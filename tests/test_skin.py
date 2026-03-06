import sys
import unittest
from fr.cnrs.mri.skin_drug_delivery.tests.data import Data
from fr.cnrs.mri.cialib.skin import SkinAnalyzer



class SkinAnalyzerTest(unittest.TestCase):
    
    
    def setUp(self):
        data = Data()
        self.image = data.getTestImage()
        
        
    def testConstructor(self):
        analyzer = SkinAnalyzer(self.image)    
        self.assertTrue(analyzer.image is self.image)


    def testPrepareImage(self):
        originalValue = self.image.getStack().getProcessor(2).getPixelValue(1,1)
        analyzer = SkinAnalyzer(self.image)
        analyzer._prepareImage()
        signalValue = analyzer.signal.getProcessor().getPixelValue(1,1)
        normalizedValue = analyzer.image.getStack().getProcessor(2).getPixelValue(1,1)
        self.assertTrue(originalValue == signalValue)
        self.assertTrue(signalValue > normalizedValue)
        
        
    def testSubtract(self):
        originalValue = self.image.getStack().getProcessor(2).getPixelValue(1,1)
        analyzer = SkinAnalyzer(self.image)
        analyzer.skinMedianRadius=12
        analyzer.strelRadius = 5
        analyzer._prepareImage()
        analyzer._segmentSkin()
        analyzer.subtractBackground()
        signalValue = analyzer.signal.getProcessor().getPixelValue(1,1)
        self.assertTrue(originalValue > signalValue)
        analyzer.signal.show()
        


def suite():
    suite = unittest.TestSuite()

    suite.addTest(SkinAnalyzerTest('testConstructor'))
    suite.addTest(SkinAnalyzerTest('testPrepareImage'))
    suite.addTest(SkinAnalyzerTest('testSubtract'))
    return suite
    
    
 
runner = unittest.TextTestRunner(sys.stdout, verbosity=1)
runner.run(suite())