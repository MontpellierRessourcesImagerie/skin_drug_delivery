SIGMA = 32;
FILL_HOLES = true;

segmentEpidermis();


function segmentEpidermis() {
    run("Select None");
    run("Duplicate...", " ");
    duplicateID = getImageID();
    run("Gaussian Blur...", "sigma="+SIGMA);
    setAutoThreshold("Default dark no-reset");
    setOption("BlackBackground", false);
    run("Convert to Mask");
    if (FILL_HOLES) run("Fill Holes");
    run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
    labelsID = getImageID();
    run("Keep Largest Region");
    largestID = getImageID();
    setAutoThreshold("Default dark no-reset");
    run("Create Selection");
    closeImage(largestID);
    closeImage(labelsID);
    closeImage(duplicateID);
    run("Restore Selection");
}


function closeImage(id) {
    selectImage(id);
    close();
}