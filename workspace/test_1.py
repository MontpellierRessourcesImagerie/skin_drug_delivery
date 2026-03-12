from ij import IJ
from fr.cnrs.mri.cialib.skin import SkinAnalyzer

image = IJ.getImage()
analyzer = SkinAnalyzer(image)
analyzer._prepareImage()
analyzer._segmentSkin()
analyzer._segmentEpidermis()
analyzer._segmentNonHoles()
analyzer._computeZones()
analyzer.corneum.show()
roi = analyzer.getCorneumRoi(filled=True)
image.setRoi(roi)