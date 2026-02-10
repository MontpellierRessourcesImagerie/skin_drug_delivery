import os
import shutil
from urllib import urlretrieve
from zipfile import ZipFile
from ij import IJ
from fr.cnrs.mri.cialib.options import Options
from fr.cnrs.mri.cialib.dialog import OptionsDialog


def main():    
    options = getOptions()
    dialog = OptionsDialog(options)
    dialog.columns = 48
    if not dialog.showOptions():
        return
    dataFolder = options.value("data folder")
    url = options.value("url")
    if os.path.exists(dataFolder):
        shutil.rmtree(dataFolder)
    os.makedirs(dataFolder)
    name = os.path.basename(url)
    IJ.log("Downloading Dataset...")
    outputFilePath = os.path.join(dataFolder, name)
    urlretrieve(url, outputFilePath)
    IJ.log("Download finished!")
    IJ.log("Extracting Dataset...")
    with ZipFile(outputFilePath, 'r') as zObject:
            zObject.extractall(path=dataFolder)
    os.remove(outputFilePath)          
    IJ.log("Extraction finished!")
            


def getOptions():
    appFolder = "skin_drug_delivery"
    dataFolder = os.path.join(IJ.getDirectory("imagej"), "mri-datasets", appFolder)    
    url = "https://zenodo.org/records/18594979/files/skin_drug_delivery_small_dataset.zip"
    options = Options("skin drug delivery", "Download Dataset")
    options.addStr("url", value=url)
    options.addStr("data folder", dataFolder)
    options.load()
    return options
    
    
main()
