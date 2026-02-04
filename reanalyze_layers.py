from ij import IJ
from ij import ImagePlus
from ij.plugin import ImageCalculator
from ij.plugin.frame import RoiManager
from ij.measure import Measurements
from inra.ijpb.plugins  import AnalyzeRegions
from inra.ijpb.binary import BinaryImages
from inra.ijpb.label import LabelImages


def main() :
    image = IJ.getImage()
    corneum, epidermis, dermis, skin = getLayerMasks(image)
        tableTitle = "Nanoformulation Density"
    table = WindowManager.getWindow(tableTitle)
    if table:
        table = table.getResultsTable()
    else:    
        table = ResultsTable()
        
    analyzer = SkinAnalyzer(image, options) 
    analyzer.corneum = corneum
    analyzer.epidermis = epidermis
    analyzer.dermis = dermis
    analyzer.skin = skin
    

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
    epidermisMask.setProcessor(epidermisLabel.createThresholdMask())
    skinMask = ImageCalculator.run(bothMask, epidermisMask, "OR create")
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


main()