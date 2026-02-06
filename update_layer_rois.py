# 
# Update skin layer rois

from ij import IJ
from ij import ImagePlus
from ij.plugin import ImageCalculator
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ThresholdToSelection


def main():
    image = IJ.getImage()
    roiManager = RoiManager.getInstance()
    roiManager.runCommand ("Update")
    
    index = roiManager.getSelectedIndex()
    rois = roiManager.getRoisAsArray()
    
    
    image.setRoi(rois[0])
    dermisMask = ImagePlus("dermis", image.createRoiMask())
    image.setRoi(rois[1])
    epidermisMask = ImagePlus("epidermis", image.createRoiMask())
    image.setRoi(rois[2])
    corneumMask = ImagePlus("corneum", image.createRoiMask())
    image.resetRoi()
    if index == 0:
        newEpidermisMask = subtract(epidermisMask, dermisMask)
        newEpidermisRoi = convertToRoi(newEpidermisMask, "epidermis")
        roiManager.setRoi(newEpidermisRoi, 1)
        roiManager.select(1)
    if index == 1:
        newDermisMask = subtract(dermisMask, epidermisMask)
        newDermisRoi = convertToRoi(newDermisMask, "dermis")
        roiManager.setRoi(newDermisRoi, 0)
        newCorneumMask = subtract(corneumMask, epidermisMask)
        newCorneumRoi = convertToRoi(newCorneumMask, "corneum")
        roiManager.setRoi(newCorneumRoi, 2)
        roiManager.select(2)
    if index == 2:
        newEpidermisMask = subtract(epidermisMask, corneumMask)
        newEpidermisRoi = convertToRoi(newEpidermisMask, "epidermis")
        roiManager.setRoi(newEpidermisRoi, 1)
        roiManager.select(1)


def convertToRoi(mask, name):
    t2s = ThresholdToSelection()
    ip = mask.getProcessor()
    ip.setThreshold(128,255)
    roi = t2s.convert(mask.getProcessor())
    roi.setName(name)
    return roi


def subtract(maskA, maskB):
    mask = ImageCalculator.run(maskA, maskB, "SUBTRACT create")
    return mask
    

main()