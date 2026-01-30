import os
import traceback
from loci.plugins import BF
from ij import IJ
from ij import Prefs
from ij import WindowManager
from ij.measure import ResultsTable
from fr.cnrs.mri.cialib.skin import SkinAnalyzer
from autooptions import Options, OptionsDialog


tableTitle = "Nanoformulation Density"


def main():
    options = getOptions()
    dialog = OptionsDialog(options)
    
    optionsOnly = Prefs.get("mri.options.only", "false")
    optionsOnly = optionsOnly=='true'
    dialog.showDialog()
    if dialog.wasCanceled():
        return
    dialog.transferValues()
    if optionsOnly:
        options.save()
        return
    
    IJ.log("Running batch analyze skin drug delivery")
    IJ.log(options.asString())
    
    table = WindowManager.getWindow(tableTitle)
    if table:
        table = table.getResultsTable()
    else:    
        table = ResultsTable()
    folder = IJ.getDir("Please select the input folder!")
    batchAnalyzeImages(folder, options.value("image file extension"), table)


def batchAnalyzeImages(folder, ext, table):
    options = Options("skin drug delivery", "Analyze Image")
    options.load()
    images = getImages(folder, ext)
    if len(images) > 0:
        batchAnalyzeSubfolder(folder, ext, options, table)
    subfolders = getSubfolders(folder)
    for subfolder in subfolders:
        batchAnalyzeSubfolder(subfolder, ext, options, table)
    

def batchAnalyzeSubfolder(subfolder, ext, options, table):
    images = getImages(subfolder, ext)
    if len(images) < 1:
        return
    IJ.log("Entering folder: " + subfolder)
    for image in images:
        IJ.log("Processing image " + image)        
        imps = BF.openImagePlus(image)
        imp = imps[0]
        analyzer = SkinAnalyzer(imp, options)  
        try:
            analyzer.analyzeImage()
            analyzer.addToTable(table)
            table.show(tableTitle)
            table.save(os.path.join(subfolder, "results.xls"))
        except:
            outputTraceStack()
        finally: 
            IJ.log("Skipping image " + image)           
        imp.close()
        

def outputTraceStack():
    traceback.print_exc()
            
            
def getImages(path, ext):
    files = os.listdir(path)
    images = [os.path.join(path, aFile) for aFile in files if not os.path.isdir(os.path.join(path, aFile)) and aFile.endswith(ext)]
    return images
    
    
def getSubfolders(path):
    files = os.listdir(path)
    folders = [os.path.join(path, aFile) for aFile in files if os.path.isdir(os.path.join(path, aFile))]
    return folders
    
    
def getOptions():
    options = Options("skin drug delivery", "Batch Analyze Images")
    options.addStr("image file extension", value="czi")
    options.load()
    return options


main()