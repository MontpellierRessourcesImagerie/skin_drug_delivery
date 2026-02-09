from ij import IJ
from ij import Prefs
from ij import WindowManager
from ij.measure import ResultsTable
from fr.cnrs.mri.cialib.skin import SkinAnalyzer
from fr.cnrs.mri.cialib.options import Options
from fr.cnrs.mri.cialib.dialog import OptionsDialog


def main():
    options = getOptions()
    dialog = OptionsDialog(options)
    if not dialog.showOptions():
        return
    
    image = IJ.getImage()
    IJ.log("Running analyze skin drug delivery on " + image.getTitle())
    IJ.log(options.asString())
    
    tableTitle = "Nanoformulation Density"
    table = WindowManager.getWindow(tableTitle)
    if table:
        table = table.getResultsTable()
    else:    
        table = ResultsTable()
        
    analyzer = SkinAnalyzer(image, options)    
    analyzer.analyzeImage()
    analyzer.image.show()
    analyzer.addToTable(table)
    table.show(tableTitle)
    analyzer.signalPerDepthCorneumTable.show("corneum - signal per depth")
    analyzer.signalPerDepthEpidermisTable.show("epidermis - signal per depth")
    analyzer.signalPerDepthDermisTable.show("dermis - signal per depth")
    analyzer.plot.show()
   
   
def getOptions():
    options = Options("skin drug delivery", "Analyze Image")
    options.addInt("nuclei channel", value=1)
    options.addInt("signal channel", value=2)
    options.addInt("brightfield channel", value=3)
    options.addInt("erosion radius", value=50)
    options.addInt("delta", value=1)
    options.addInt("median radius skin", value=50)
    options.addFloat("sigma epidermis", value=32.0)
    options.addInt("threshold", value=650)
    options.addChoice("function", choices=["Gamma Variate", "Rodbard"], value="Gamma Variate")
    options.addBool("normalize", value=True)
    options.addBool("fill holes epidermis", True)
    options.addBool("remove holes", True)
    options.load()
    return options


main()