EXT = ".tif";
PERCENT = 10;

folder = getDir("Select the input folder!");

setBatchMode(true);
files = getFileList(folder);
images = filterImages(files);
totalNumberOfImage = images.length;
numberOfSelectedImages = floor((PERCENT* totalNumberOfImage) / 100);
for (i = 0; i < numberOfSelectedImages; i++) {
    index = round(random * (totalNumberOfImage-1));
    open(folder + File.separator + images[index]);
}
run("Images to Stack");
setBatchMode("exit and display");


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

