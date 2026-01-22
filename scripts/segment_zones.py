from ij import IJ
from fr.cnrs.mri.cialib.skin import SkinAnalyzer


image = IJ.getImage()
analyzer = SkinAnalyzer(image)
analyzer.analyzeImage()
analyzer.image.show()
analyzer.signal.show()
analyzer.dermis.show()
print(analyzer.statsCornea)
print(analyzer.statsEpidermis)
print(analyzer.statsDermis)