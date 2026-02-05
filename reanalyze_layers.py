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
    analyzer.epidermis = epidermis
    analyzer.dermis = dermis
    analyzer.skin = skin
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
    folder = os.path.dirname(os.path.dirname(oPath))
    resultsPath = os.path.join(folder, "results.xls")
    table = ResultsTable.open(resultsPath)
    analyzer.replaceInTable(table)
    table.save(resultsPath)
    basename = os.path.splitext(os.path.basename(oPath))[0]
    analyzer.signalPerDepthCorneumTable.save(os.path.join(folder, basename + "_corneum.xls"))
    analyzer.signalPerDepthEpidermisTable.save(os.path.join(folder, basename + "_epidermis.xls"))
    analyzer.signalPerDepthDermisTable.save(os.path.join(folder, basename + "_dermis.xls"))
    pw = analyzer.plot.show()
    batchOptions = Options("skin drug delivery", "Batch Analyze Images")
    batchOptions.load()
    plotImage = analyzer.plot.makeHighResolution(basename, 
                                             batchOptions.value("plot scale"),
                                             True,
                                             False)                                             
    pw.close()   
    path = os.path.join(folder, "images")
    IJ.save(plotImage, os.path.join(path, basename + "_plot.png"))
    IJ.save(analyzer.image, os.path.join(path, basename + ".tif"))
    analyzer.image.getOverlay().setStrokeWidth(batchOptions.value("stroke width"))
    IJ.save(analyzer.image, os.path.join(path, basename + ".png"))


def getLayerMasks(image):
    manager = RoiManager.getInstance()
    rois = manager.getRoisAsArray()
    dermisRoi = None
    corneumRoi = None
    for roi in rois:
        if "corneum" in roi.getName():
            corneumRoi = roi
        if "dermis" in roi.getName():
            dermisRoi = roi
    image.setRoi(corneumRoi)
    corneumMask = ImagePlus("corneum", image.createRoiMask())
    corneumX, corneumY = getCentroid(corneumMask)
    image.setRoi(dermisRoi)
    dermisMask = ImagePlus("dermis", image.createRoiMask())
    dermisX, dermisY = getCentroid(dermisMask)
    corneumMask.setRoi(dermisRoi)
    bothMask = ImageCalculator.run(corneumMask, dermisMask, "OR create")
    ip = bothMask.getProcessor().duplicate()
    ip.invert()
    ip = BinaryImages.componentsLabeling(ip, 4, 16)
    labels = ImagePlus("both labels", ip)
    _, centroidsY = getCentroids(labels)
    label = 1
    if centroidsY[1] < centroidsY[0]:
        label = 2
    epidermisMask = LabelImages.keepLabels(labels, [label])
    epidermisMask.getProcessor().setThreshold(label, 255)
    epidermisMask.setProcessor(epidermisMask.createThresholdMask())
    skinMask = ImageCalculator.run(bothMask, epidermisMask, "OR create")
    image.resetRoi()
    return corneumMask, epidermisMask, dermisMask, skinMask
    
    
def getCentroids(mask):
    features = AnalyzeRegions.Features()
    features.setAll(False)
    features.centroid = True   
    results = AnalyzeRegions.process(mask, features)
    y = results.getColumn("Centroid.Y")
    x = results.getColumn("Centroid.X")
    return x, y
    
    
def getCentroid(mask):
    x, y = getCentroids(mask)
    return x[0], y[0]


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