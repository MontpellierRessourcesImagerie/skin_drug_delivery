EXT = ".tif";
RADIUS_VARIANCE = 4;
SCALE_FACTOR = 2;
CLOSING_RADIUS = 32;


processImage();


function batchProcessImages() {
    folder = getDir("Please select the input folder!");
    files = getFileList(folder);
    images = filterImages(files);
    
    File.makeDirectory(folder + File.separator + "out_variance");
    for (i = 0; i < images.length; i++) {
        path = folder + File.separator + images[i];
        open(path);
        processImage();
        
    }
}


function processImage() {
    image1 = getTitle();
    run("Duplicate...", "duplicate");
    image2 = getTitle();
    run("Gaussian Blur...", "sigma=32");
    imageCalculator("Subtract create", image1, image2);
    copyID = getImageID();
    run("normalize slices");
    run("Enhance Contrast", "saturated=0.35");  
    run("Subtract Background...", "rolling=50 stack");    
    run("Scale...", "x=" + (1/SCALE_FACTOR) + " y=" + (1/SCALE_FACTOR) + " z=1.0 interpolation=Bilinear average process create ");
    closeImage(copyID);
    run("Variance...", "radius=" + RADIUS_VARIANCE + " stack");
    setAutoThreshold("MinError dark no-reset");
    setOption("BlackBackground", false);
    run("Convert to Mask", "method=MinError background=Dark");
    run("Fill Holes", "stack");
    run("Invert", "stack");
    run("Fill Holes", "stack");
    run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
    run("Remove Border Labels", "top");
    run("Keep Largest Region");
    run("Invert");
    run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
    run("Keep Largest Region");
    run("Morphological Filters", "operation=Closing element=Square radius=" + CLOSING_RADIUS);
    run("Scale...", "x=2 y=2 interpolation=Bilinear average create");
    setAutoThreshold("MinError dark no-reset");
    run("Convert to Mask", "method=MinError background=Dark");
    
    
function filterImages(files) {
    images = newArray(0);
    for (i = 0; i < files.length; i++) {
        file = files[i];
        if (!isImage(file)) continue;
        images = Array.concat(images, file);
    }
    return images;
}


function isImage(file) {
    result = (!File.isDirectory(file) && endsWith(file, EXT));
    return result;
}


function closeImage(id) {
    selectImage(id);
    close();
}