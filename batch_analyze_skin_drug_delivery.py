import os
import traceback
import datetime
from loci.plugins import BF
from ij import IJ
from ij import Prefs
from ij import WindowManager
from ij.measure import ResultsTable
from fr.cnrs.mri.cialib.skin import SkinAnalyzer
from fr.cnrs.mri.cialib.autooptions import Options, OptionsDialog


tableTitle = "Nanoformulation Density"


def main():
    options = getOptions()
    dialog = OptionsDialog(options)
    if not dialog.showOptions():
        return
    folder = IJ.getDir("Please select the input folder!")
    IJ.log("Running batch analyze skin drug delivery")
    IJ.log(str(datetime.datetime.now()))
    IJ.log(options.asString())
    table = WindowManager.getWindow(tableTitle)
    if table:
        table = table.getResultsTable()
    else:    
        table = ResultsTable()
    batchAnalyzeImages(folder, options.value("image file extension"), table)
    

def batchAnalyzeImages(folder, ext, table):
    options = Options("skin drug delivery", "Analyze Image")
    options.load()
    batchOptions = getOptions()
    IJ.log(options.asString())
    images = getImages(folder, ext)
    if len(images) > 0:
        batchAnalyzeSubfolder(folder, ext, options, batchOptions, table)
    subfolders = getSubfolders(folder)
    for subfolder in subfolders:
        batchAnalyzeSubfolder(subfolder, ext, options, batchOptions, table)
    

def batchAnalyzeSubfolder(subfolder, ext, options, batchOptions, table):
    images = getImages(subfolder, ext)
    if len(images) < 1:
        return
    IJ.log("Entering folder: " + subfolder)
    IJ.log(str(datetime.datetime.now()))
    for image in images:
        IJ.log("Processing image " + image)        
        imps = BF.openImagePlus(image)
        imp = imps[0]
        analyzer = SkinAnalyzer(imp, options)  
        try:
            analyzer.analyzeImage()
            analyzer.addToTable(table)
            table.show(tableTitle)
            table.save(os.path.join(os.path.dirname(subfolder), "results.xls"))
            basename = os.path.splitext(os.path.basename(image))[0]
            analyzer.signalPerDepthCorneumTable.save(os.path.join(subfolder, basename + "_corneum.xls"))
            analyzer.signalPerDepthEpidermisTable.save(os.path.join(subfolder, basename + "_epidermis.xls"))
            analyzer.signalPerDepthDermisTable.save(os.path.join(subfolder, basename + "_dermis.xls"))
            path = os.path.join(subfolder, "images")
            if not os.path.exists(path):
                os.makedirs(path)   
            pw = analyzer.plot.show()
            plotImage = analyzer.plot.makeHighResolution(basename, 
                                             batchOptions.value("plot scale"),
                                             True,
                                             False)                                             
            pw.close()     
            IJ.save(plotImage, os.path.join(path, basename + "_plot.png"))
            IJ.save(analyzer.image, os.path.join(path, basename + ".tif"))
            analyzer.image.getOverlay().setStrokeWidth(batchOptions.value("stroke width"))
            IJ.save(analyzer.image, os.path.join(path, basename + ".png"))
            analyzer.plot.dispose()
        except:
            outputTraceStack()
            IJ.log("Skipping image " + image)           
        finally: 
            imp.close()
    IJ.log(str(datetime.datetime.now()))
    

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
    options.addFloat("plot scale", value=3.0)
    options.addInt("stroke width", value=8)
    options.load()
    return options


main()