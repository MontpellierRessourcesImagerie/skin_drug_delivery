from ij import IJ
from ij import ImagePlus
from ij import LookUpTable
from ij.gui import Overlay
from ij.plugin import ImageCalculator
from ij.plugin import LutLoader
from ij.plugin import ZProjector
from ij.process import AutoThresholder
from ij.process import ImageConverter
from ij.process import LUT
from ij.plugin.filter import GaussianBlur
from ij.plugin.filter import RankFilters
from ij.plugin.filter import ThresholdToSelection

from inra.ijpb.binary import BinaryImages
from inra.ijpb.label import LabelImages
from inra.ijpb.measure import IntensityMeasures
from inra.ijpb.morphology import Reconstruction
from inra.ijpb.morphology.strel import DiskStrel
from inra.ijpb.plugins  import AnalyzeRegions

from net.imglib2.img import VirtualStackAdapter
from net.imglib2.img.display.imagej import ImageJFunctions
from sc.fiji.labkit.ui.segmentation import SegmentationTool

image = IJ.getImage()

medianRadius = 50

        
ip = image.getStack().getProcessor(3)
ip.findEdges()
median = RankFilters()
median.rank(ip, medianRadius, RankFilters.MEDIAN)
ip.setAutoThreshold(AutoThresholder.Method.Minimum, True)
mask = ImagePlus("mask of skin", ip.createMask())
ip = mask.getProcessor()
ip = Reconstruction.fillHoles(ip)
ip.invert()
ip = Reconstruction.fillHoles(ip)
ip = BinaryImages.componentsLabeling(ip, 4, 16)
ip = BinaryImages.keepLargestRegion(ip)
ip.invert()
ip = BinaryImages.componentsLabeling(ip, 4, 16)
ip = BinaryImages.keepLargestRegion(ip)
mask.setProcessor(ip)
self.skin = mask
mask.show()