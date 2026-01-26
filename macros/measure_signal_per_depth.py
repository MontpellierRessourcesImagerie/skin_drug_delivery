from ij import IJ
from ij import ImagePlus
from ij import LookUpTable
from ij.gui import Overlay
from ij.measure import ResultsTable
from ij.plugin import ImageCalculator
from ij.plugin import LutLoader
from ij.plugin import ZProjector
from ij.process import AutoThresholder
from ij.process import ImageConverter
from ij.process import LUT
from ij.plugin.filter import GaussianBlur
from ij.plugin.filter import RankFilters
from ij.plugin.filter import ThresholdToSelection
from ij import WindowManager

from inra.ijpb.binary import BinaryImages
from inra.ijpb.label import LabelImages
from inra.ijpb.measure import IntensityMeasures
from inra.ijpb.morphology import Reconstruction
from inra.ijpb.morphology.strel import DiskStrel
from inra.ijpb.plugins  import AnalyzeRegions

from net.imglib2.img import VirtualStackAdapter
from net.imglib2.img.display.imagej import ImageJFunctions
from sc.fiji.labkit.ui.segmentation import SegmentationTool


DELTA = 1
EDT = WindowManager.getImage("EDT")
signal = WindowManager.getImage("signal")

ip = EDT.getProcessor()
stats = ip.getStats()

area = []
mean = []
stdDev = []
depth = []
for t in range(1, int(round(stats.max))):
    depth.append(signal.getCalibration().getX(t))
    ip.setThreshold(t,t+DELTA)
    mask = ip.createMask()
    features = AnalyzeRegions.Features()
    features.setAll(False)
    features.area = True   
    table = AnalyzeRegions.process(ImagePlus("mask", mask), features)
    area.append(table.getColumn('Area')[0])
    measures = IntensityMeasures(signal, ImagePlus("mask", mask))
    mean.append(measures.getMean().getColumn('Mean')[0])
    stdDev.append(measures.getStdDev().getColumn('StdDev')[0])


signalPerDepth = ResultsTable()
for a, m, s, d in zip(area, mean, stdDev, depth):
    signalPerDepth.addRow()
    rowIndex = signalPerDepth.size() - 1
    signalPerDepth.setValue("Depth", rowIndex, d)
    signalPerDepth.setValue("Mean", rowIndex, m)
    signalPerDepth.setValue("StdDev", rowIndex, s)
    signalPerDepth.setValue("Area", rowIndex, a)
    
signalPerDepth.show("Nanoformulation per Depth")

