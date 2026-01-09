/**
 * Normalize each channel by mapping the range [min, max] of values in the image to [0,1]
 */

getDimensions(width, height, channels, slices, frames);

run("32-bit");

for (i=0; i<channels; i++) {
    Stack.setChannel(i+1);
    min = getValue("Min");
    max = getValue("Max");
    run("Subtract...", "value=" + min + " slice");
    run("Divide...", "value=" + (max - min) + " slice");
}
