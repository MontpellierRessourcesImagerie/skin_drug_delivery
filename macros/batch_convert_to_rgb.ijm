/*
 * Process all images in the root folder and its direct subfolders.
 * 
 * For each image write a 2D rgb image with a scalebar.
 * 
 * 
 * written by Volker Baecker at mri.cnrs.fr
 * 

Copyright 2026 INSERM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal 
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is furnished 
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

EXT = "czi";
CONTRAST_SATURATION = 0.35;
OUTPUT_FILE_EXT = ".jpg";
OUTPUT_FOLDER = "rgb";
SCALEBAR_WIDTH = 50;
SCALEBAR_HEIGHT = 100;
SCALEBAR_THICKNESS = 8;
SCALEBAR_FONT = 18;
SCALEBAR_LOCATION = "[Lower Left]";
SCALEBAR_BOLD = true;


if (nImages>0 && !isKeyDown('alt')) {
    createRGBWithScaleBar();
} else {
    batchProcessImages();
}


function batchProcessImages() {
    rootFolder = getDir("Please select the input folder!");
    files = getFileList(rootFolder);
    setBatchMode(true);
    start = getTime();
    getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
    print("START PROCESSING at " + getTimestampNow());
    for (i = 0; i < files.length; i++) {
        file = files[i];
        if (isImage(file)) {
            processFile(rootFolder, file);
            continue;
        }
        if (File.isDirectory(rootFolder + File.separator + file)) {
            processFolder(rootFolder, file);
        }
    }
    stop = getTime();
    dt = (stop - start) / 1000;
    dMin = floor(dt / 60);
    dSec = round(dt % 60);
    getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
    print("STOP PROCESSING at " + getTimestampNow());
    print("PROCESSING took: " + dMin + "m and " + dSec + "s");
    setBatchMode("exit and display");
}


function processFolder(rootFolder, folder) {
    files = getFileList(rootFolder + File.separator + folder);
    images = filterImages(files);
    for (i = 0; i < images.length; i++) {
        image = images[i];
        processFile(rootFolder + File.separator + folder, image);
    }
}


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


function processFile(folder, file) {
    print("Processing:", folder, file);
    File.makeDirectory(folder + File.separator + "rgb");
    path = folder + File.separator + file;
    run("Bio-Formats", "open=[" + path + "] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
    createRGBWithScaleBar();
    basename = File.getNameWithoutExtension(file);
    save(folder + File.separator + OUTPUT_FOLDER + File.separator + basename + OUTPUT_FILE_EXT);
    close("*");
}


function createRGBWithScaleBar() {
    getDimensions(width, height, channels, slices, frames);
    if (slices>1) {
        run("Z Project...", "projection=[Max Intensity]");
    }
    if (channels>10) {
        close("*");
        continue;
    } 
    /*
    for (c = 1; c <= channels; c++) {
        Stack.setChannel(c);
        run("Enhance Contrast", "saturated=" + CONTRAST_SATURATION);
    }*/
    Property.set("CompositeProjection", "Sum");
    Stack.setDisplayMode("composite");
    run("RGB Color");
    options ="width="+SCALEBAR_WIDTH+" height="+SCALEBAR_HEIGHT+" thickness="+SCALEBAR_THICKNESS+" font="+SCALEBAR_FONT+" location="+SCALEBAR_LOCATION;
    if (SCALEBAR_BOLD) options = options + " bold";
    run("Scale Bar...", options);
}


function getTimestampNow() {
    getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
    now = "" + year + "-";
    now = now + IJ.pad(month+1, 2) + "-";
    now = now + IJ.pad(dayOfMonth, 2) + " ";
    now = now + IJ.pad(hour,2) + ":";
    now = now + IJ.pad(minute,2) + ":";
    now = now + IJ.pad(second,2);
    return now;
}
