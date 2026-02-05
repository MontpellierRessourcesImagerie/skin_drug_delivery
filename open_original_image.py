import os
from ij import IJ
from loci.plugins import BF
from autooptions import Options, OptionsDialog


def main():
    options = getOptions()
    dialog = OptionsDialog(options)
    if not dialog.showOptions():
        return
    image = IJ.getImage()
    path = image.getOriginalFileInfo().getFilePath()
    folder = os.path.dirname(os.path.dirname(path))
    name = os.path.basename(path)
    _, ext = os.path.splitext(name)
    name = name.replace(ext, "." + options.value("image file extension"))
    originalPath = os.path.join(folder, name)
    image = BF.openImagePlus(originalPath)[0]
    image.show()



def getOptions():
    options = Options("skin drug delivery", "Open Original Image")
    options.addStr("image file extension", value="czi")
    options.load()
    return options
    
    
main()    