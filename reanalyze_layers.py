import os
from ij import IJ
from ij import ImagePlus
from ij import WindowManager
from ij.plugin import ImageCalculator
from ij.plugin.frame import RoiManager
from ij.measure import Measurements
from ij.measure import ResultsTable
from inra.ijpb.plugins  import AnalyzeRegions
from inra.ijpb.binary import BinaryImages
from inra.ijpb.label import LabelImages
from fr.cnrs.mri.cialib.skin import SkinAnalyzer
from autooptions import Options, OptionsDialog


def main() :
    image = IJ.getImage()
    corneum, epidermis, dermis, skin = getLayerMasks(image)
    tableTitle = "Nanoformulation Density"
    table = WindowManager.getWindow(tableTitle)
    if table:
        table = table.getResultsTable()
    else:    
        table = ResultsTable()
    options = getOptions()        
    analyzer = SkinAnalyzer(image, options) 
    analyzer.corneum = corneum
    analyzer.setCalibration(analyzer.corneum)
    analyzer.epidermis = epidermis
    analyzer.setCalibration(analyzer.epidermis)
    analyzer.dermis = dermis
    analyzer.setCalibration(analyzer.dermis)
    analyzer.skin = skin
    analyzer.setCalibration(analyzer.skin)
    analyzer._prepareImage()
    analyzer.analyzeImage()
    analyzer.image.show()
    analyzer.addToTable(table)
    table.show(tableTitle)
    analyzer.signalPerDepthCorneumTable.show("corneum - signal per depth")
    analyzer.signalPerDepthEpidermisTable.show("epidermis - signal per depth")
    analyzer.signalPerDepthDermisTable.show("dermis - signal per depth")
    analyzer.plot.show()
    oPath = image.getOriginalFileInfo().getFilePath()
    conditionFolder = os.path.dirname(oPath)
    baseFolder = os.path.dirname(conditionFolder)
    imagesFolder = os.path.join(conditionFolder, "images")
    resultsPath = os.path.join(baseFolder, "results.xls")
    table = ResultsTable.open(resultsPath)
    analyzer.replaceInTable(table)
    table.show("results.xls")
    table.save(resultsPath)
    table.getResultsWindow().close()
    basename = os.path.splitext(os.path.basename(oPath))[0]
    analyzer.signalPerDepthCorneumTable.save(os.path.join(conditionFolder, basename + "_corneum.xls"))
    analyzer.signalPerDepthEpidermisTable.save(os.path.join(conditionFolder, basename + "_epidermis.xls"))
    analyzer.signalPerDepthDermisTable.save(os.path.join(conditionFolder, basename + "_dermis.xls"))
    pw = analyzer.plot.show()
    batchOptions = Options("skin drug delivery", "Batch Analyze Images")
    batchOptions.load()
    plotImage = analyzer.plot.makeHighResolution(basename, 
                                             batchOptions.value("plot scale"),
                                             True,
                                             False)                                             
    pw.close()   
    IJ.save(plotImage, os.path.join(imagesFolder, basename + "_plot.png"))
    IJ.save(analyzer.image, os.path.join(imagesFolder, basename + ".tif"))
    analyzer.image.getOverlay().setStrokeWidth(batchOptions.value("stroke width"))
    IJ.save(analyzer.image, os.path.join(imagesFolder, basename + ".png"))


def getLayerMasks(image):
    manager = RoiManager.getInstance()
    rois = manager.getRoisAsArray()
    dermisRoi = None
    corneumRoi = None
    epidermisRoi = None
    for roi in rois:
        if "corneum" in roi.getName():
            corneumRoi = roi
        if "dermis" in roi.getName() and not "epi" in roi.getName():
            dermisRoi = roi
        if "epidermis" in roi.getName():
            epidermisRoi = roi
    image.setRoi(corneumRoi)
    corneumMask = ImagePlus("corneum", image.createRoiMask())
    image.setRoi(dermisRoi)
    dermisMask = ImagePlus("dermis", image.createRoiMask())
    image.setRoi(epidermisRoi)
    epidermisMask = ImagePlus("epidermis", image.createRoiMask())
    bothMask = ImageCalculator.run(corneumMask, dermisMask, "OR create")
    skinMask = ImageCalculator.run(bothMask, epidermisMask, "OR create")
    image.resetRoi()
    return corneumMask, epidermisMask, dermisMask, skinMask
    
    
def getOptions():
    options = Options("skin drug delivery", "Analyze Image")
    options.load()
    return options


def getOriginalFileName(image):
    options = Options("skin drug delivery", "Open Original Image")
    options.load()
    path = image.getOriginalFileInfo().getFilePath()
    folder = os.path.dirname(os.path.dirname(path))
    name = os.path.basename(path)
    _, ext = os.path.splitext(name)
    name = name.replace(ext, "." + options.value("image file extension"))
    return name
    
    
main()