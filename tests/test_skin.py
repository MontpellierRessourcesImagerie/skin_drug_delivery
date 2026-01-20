import sys
import unittest
from fr.cnrs.mri.skin_drug_delivery.tests.data import Data
from fr.cnrs.mri.cialib.skin import SkinAnalyzer



data = Data()



class SkinAnalyzerTest(unittest.TestCase):
    
    
    def testConstructor(self):
        analyzer = SkinAnalyzer(data.image)    
        self.assertTrue(analyzer.image is data.image)



def suite():
    suite = unittest.TestSuite()

    suite.addTest(SkinAnalyzerTest('testConstructor'))
    return suite
    
    
 
runner = unittest.TextTestRunner(sys.stdout, verbosity=1)
runner.run(suite())