import java
from fr.cnrs.mri.cialib.skin import SkinAnalyzer
from ij.io import Opener
from ij import ImagePlus
from ij.process import FloatProcessor
from java.awt.image import ColorModel
import jarray
from ij.plugin import LutLoader
from fiji.plugin.volumeviewer import LookupTable
from fr.cnrs.mri.skin_drug_delivery.tests import channel1, channel2, channel3
from ij.plugin import RGBStackMerge


class Data:
    
    
    def __init__(self):
        self.image = self.getTestImage()


    def getTestImage(self):
        channel1Image = self.getTestImageFor(channel1, "test_c1", 'blue')
        channel2Image = self.getTestImageFor(channel2, "test_c2", 'red')
        channel3Image = self.getTestImageFor(channel3, "test_c3", 'grays')
        image = RGBStackMerge.mergeChannels([channel1Image, channel2Image, channel3Image], False)
        return image


    def getTestImageFor(self, data, name, color):
        rows = data.split("\n")
        height = len(rows)
        newRows = []
        for row in rows:
            newRow = row.split(',')
            width = len(newRow)
            newRows = newRows + map(float, newRow)
        bytes = jarray.array(newRows, 'f')
        cm = LutLoader.getLut(color)
        ip = FloatProcessor(width, height, bytes, cm)
        image = ImagePlus(name, ip)
        return image



data =Data()

