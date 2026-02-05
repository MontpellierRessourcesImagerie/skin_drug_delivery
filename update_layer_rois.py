# 
# Update skin layer rois

from ij import IJ
from ij import ImagePlus
from ij.plugin.frame import RoiManager


def main():
    image = IJ.getImage()
    roiManager = RoiManager.getInstance()
    
    index = roiManager.getSelectedIndex()
    rois = roiManager.getRoisAsArray()
    
    roiManager.runCommand ("Update")
    
    image.setRoi(rois[0])
    dermisMask = ImagePlus("dermis", image.createRoiMask())
    image.setRoi(rois[1])
    epidermisMask = ImagePlus("epidermis", image.createRoiMask())
    image.setRoi(rois[2])
    epidermisMask = ImagePlus("corneum", image.createRoiMask())
    image.resetRoi()


def subtract(maskA, maskB):
    pass
    

main()