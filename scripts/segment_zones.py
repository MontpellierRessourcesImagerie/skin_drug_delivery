from ij import IJ
from ij import WindowManager
from ij.measure import ResultsTable
from fr.cnrs.mri.cialib.skin import SkinAnalyzer


tableTitle = "Nanoformulation Density"
table = WindowManager.getWindow(tableTitle)
if table:
    table = table.getResultsTable()
else:    
    table = ResultsTable()
    
image = IJ.getImage()
analyzer = SkinAnalyzer(image)
analyzer.removeHoles = True
analyzer.analyzeImage()
analyzer.image.show()
analyzer.addToTable(table)
table.show(tableTitle)
analyzer.signalPerDepthCorneaTable.show("cornea - signal per depth")
analyzer.signalPerDepthEpidermisTable.show("epidermis - signal per depth")
analyzer.signalPerDepthDermisTable.show("dermis - signal per depth")
analyzer.plot.show()