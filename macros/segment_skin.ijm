RADIUS_VARIANCE =  4
THRESHOLDING_METHOD = "Yen"
OPEN_ITERATIONS = 4
BRIGHTFIELD_CHANNEL = 3

getDimensions(width, height, channels, slices, frames);

if (slices>1) {
    run("Z Project...", "projection=[Max Intensity]");
}
if (channels>1) {
    run("Duplicate...", "duplicate channels="+BRIGHTFIELD_CHANNEL+"-"+BRIGHTFIELD_CHANNEL);
}
run("Variance...", "radius=" + RADIUS_VARIANCE + " stack");
setAutoThreshold(THRESHOLDING_METHOD + " dark no-reset");
run("Convert to Mask", "method=" + THRESHOLDING_METHOD + " background=Dark black");
maskID = getImageID();
run("Morphological Filters", "operation=Closing element=Square radius="+OPEN_ITERATIONS);
run("Fill Holes", "stack");
run("Invert", "stack");
run("Fill Holes", "stack");
run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
labelsID = getImageID();
run("Remove Border Labels", "top");
labelsNoBordersID = getImageID();
run("Keep Largest Region");
labelsLargestID = getImageID();
run("Morphological Filters", "operation=Opening element=Square radius="+OPEN_ITERATIONS);
run("Keep Largest Region");

