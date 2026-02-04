from ij import IJ
from ij.gui import Toolbar
from ij.plugin.frame import RoiManager
from autooptions import Options, OptionsDialog


def main():

    options = getOptions()
    dialog = OptionsDialog(options)
    if not dialog.showOptions():
        return
        
    image = IJ.getImage()
    
    if image.getBitDepth() == 24:
        path = image.getOriginalFileInfo().getFilePath()
        path = path.replace(".png", ".tif")
        image = IJ.openImage(path)
        image.show()    
    IJ.run("To ROI Manager", "")
    IJ.run("Remove Overlay", "")
    manager = RoiManager.getInstance()
    index = manager.getIndex("epidermis")
    if index > -1:
        manager.delete(index)
    IJ.setTool("brush")
    manager.runCommand(image,"Show None");
    manager.select(0)
    Toolbar.setBrushSize(options.value("brush width"))

    
def getOptions():
    options = Options("skin drug delivery", "Correct Layers")
    options.addInt("brush width", value=60)
    options.load()
    return options
    
    
main()