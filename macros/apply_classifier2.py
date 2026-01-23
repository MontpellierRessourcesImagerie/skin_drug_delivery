from ij import IJ
from ij import ImagePlus
from  sc.fiji.labkit.ui.segmentation import SegmentationTool
from net.imglib2.img import VirtualStackAdapter
from net.imglib2.img.display.imagej import ImageJFunctions



use_gpu = False
path = IJ.addSeparator(IJ.getDirectory("plugins")) +  "skin_drug_delivery"
path = IJ.addSeparator(path) + "holes.classifier"

image = IJ.getImage()
segmenter = SegmentationTool(None)
segmenter.setUseGpu(use_gpu)
segmenter.openModel(path)
res = segmenter.segment(VirtualStackAdapter.wrap(image))
res = ImagePlus("holes", ImageJFunctions.wrap(res, "").getProcessor().duplicate())

res.show()