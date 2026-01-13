normalize();
// segment();

function normalize() {
    getDimensions(width, height, channels, slices, frames);
    
    run("32-bit");
    
    for (i=0; i<slices; i++) {
        Stack.setSlice(i+1);
        mean = getValue("Mean");
        stdDev = getValue("StdDev");
        run("Subtract...", "value=" + mean + " slice");
        run("Divide...", "value=" + stdDev + " slice");
    }
}


function segment() {
    run("Find Edges");
    setAutoThreshold("Percentile dark no-reset");
    run("Convert to Mask");
}
