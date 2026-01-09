EXT = "czi";

folder = getDir("Please select the input folder!");

files = getFileList(folder);
images = filterImages(files);
for (i = 0; i < images.length; i++) {
    image = images[i];
    path = folder + File.separator + image;
    run("Bio-Formats", "open=[" + path + "] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
    getDimensions(width, height, channels, slices, frames);
    for (c = 1; c <= channels; c++) {
        File.makeDirectory(folder + File.separator + "C" + c);
        run("Duplicate...", "duplicate channels=" + c);
        outName = File.getNameWithoutExtension(image);
        save(folder + File.separator + "C" + c + File.separator + outName + ".tif");
        close();
    }
    close();
}


function filterImages(files) {
    images = newArray(0);
    for (i = 0; i < files.length; i++) {
        file = files[i];
        if (File.isDirectory(file)) continue;
        if (!endsWith(file, EXT)) continue;     
        images = Array.concat(images, file);
    }
    return images;
}
