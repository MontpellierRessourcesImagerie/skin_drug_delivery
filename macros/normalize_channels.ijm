/**
 * Normalize each channel by mapping the range [min, max] of values in the image to [0,1]
 */

getDimensions(width, height, channels, slices, frames);

run("32-bit");

for (i=0; i<slices; i++) {
    Stack.setChannel(i+1);
    mean = getValue("Mean");
    stdDev = getValue("StdDev");
    run("Subtract...", "value=" + mean + " slice");
    run("Divide...", "value=" + stdDev + " slice");
}
