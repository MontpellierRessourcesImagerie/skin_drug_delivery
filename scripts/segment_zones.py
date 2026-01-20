from ij import IJ
from fr.cnrs.mri.cialib.skin import SkinAnalyzer


image = IJ.getImage()
analyzer = SkinAnalyzer(image)
analyzer.segmentZones()
analyzer.image.show()