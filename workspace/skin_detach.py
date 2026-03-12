from ij import IJ
from ij.gui import Roi
from fr.cnrs.mri.cialib.skin import SkinAnalyzer
from fr.cnrs.mri.cialib.skin import SkinSegmenter

image = IJ.getImage()
image.resetRoi()
ip = image.getStack().getProcessor(3).duplicate()
segmenter = SkinSegmenter(ip)
segmenter.medianRadius = 50
segmenter.run()    
mask = segmenter.mask
width = mask.getWidth()
height = mask.getHeight()
roi = Roi(0, height-2, width, 4)
mask.setRoi(roi)
IJ.setBackgroundColor(0, 0, 0);
IJ.run(mask, "Clear", "slice");
mask.resetRoi()
mask.show()
