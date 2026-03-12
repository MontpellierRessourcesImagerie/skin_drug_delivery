from ij import IJ
from ij import ImagePlus
from ij.gui import Roi
from inra.ijpb.binary import BinaryImages
from inra.ijpb.label import LabelImages
from inra.ijpb.measure import IntensityMeasures
from inra.ijpb.morphology import Reconstruction
from inra.ijpb.morphology.strel import DiskStrel
from inra.ijpb.plugins  import AnalyzeRegions
from inra.ijpb.math import ImageCalculator as InraImageCalculator

mask = IJ.getImage()
# remove the bottom line of the image 
width = mask.getWidth()
height = mask.getHeight()
roi = Roi(0, height-2, width, 2)
mask.getProcessor().fill(roi)
mask.setRoi(roi)
mask.getProcessor().invert()
mask.resetRoi()
ip = mask.getProcessor()
ip = Reconstruction.fillHoles(ip)
ip.invert()
ip = Reconstruction.fillHoles(ip)
ip.invert()
ip = BinaryImages.componentsLabeling(ip, 4, 16)
ip = BinaryImages.keepLargestRegion(ip)
ip.invert()
ip = BinaryImages.componentsLabeling(ip, 4, 16)
ip1 = BinaryImages.keepLargestRegion(ip)
LabelImages.removeLargestLabel(ip)
ip2 = BinaryImages.keepLargestRegion(ip)
op = InraImageCalculator.Operation.OR
ip = InraImageCalculator.combineImages(ip1, ip2, op)
ip.invert()
ImagePlus("result", ip).show()