from ij import IJ
from fr.cnrs.mri.cialib.skin import SkinAnalyzer


image = IJ.getImage()
analyzer = SkinAnalyzer(image)
analyzer.removeHoles = False
analyzer.analyzeImage()
analyzer.image.show()
analyzer.skin.show()
analyzer.epidermis.show()
print(analyzer.statsCornea)
print(analyzer.statsEpidermis)
print(analyzer.statsDermis)