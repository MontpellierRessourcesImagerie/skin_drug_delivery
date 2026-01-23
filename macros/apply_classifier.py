from ij import IJ

path = IJ.addSeparator(IJ.getDirectory("plugins")) +  "skin_drug_delivery"
path = IJ.addSeparator(path) + "holes.classifier"
print(path)
image = IJ.getImage()
IJ.run(image, "Segment Image With Labkit (IJ1)", "segmenter_file="+path+" use_gpu=false");

