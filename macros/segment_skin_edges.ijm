MEDIAN_RADIUS = 50;


selectSkin();


function selectSkin() {
    run("Select None");
    imageID = getImageID();
    run("Duplicate...", " ");
    run("normalize slices");
    run("Enhance Contrast", "saturated=0.35");
    run("Find Edges");
    run("Median...", "radius=" + MEDIAN_RADIUS);
    setAutoThreshold("Minimum dark no-reset");
    setOption("BlackBackground", false);
    run("Convert to Mask");
    maskID = getImageID();
    postProcessImage();
    postProcessedID = getImageID();
    run("Create Selection");
    closeImage(maskID);
    closeImage(postProcessedID);
    selectImage(imageID);
    run("Restore Selection");
}


function postProcessImage() {
    run("Fill Holes", "stack");
    run("Invert", "stack");
    run("Fill Holes", "stack");
    run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
    labels1 = getImageID();
    run("Keep Largest Region");
    largest1 = getImageID();
    run("Invert");
    run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
    labels2 = getImageID();
    run("Keep Largest Region");
    run("Invert");
    closeImage(labels1);
    closeImage(largest1);
    closeImage(labels2);
}


function closeImage(id) {
    selectImage(id);
    close();
}