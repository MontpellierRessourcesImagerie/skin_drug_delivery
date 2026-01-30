EXT = ".czi"

folder = getDir("Please select the input folder!");

files = getFileList(folder);

for (i = 0; i < files.length; i++) {
    file = files[i];
    path = folder + file;
    if (File.isDirectory(path) || !endsWith(file, EXT)) continue;
    name_normalized = replace(file, "_", "-");
    index = indexOf(name_normalized, "-n");
    subfolder = substring(name_normalized, 0, index);
    destPath = folder + File.separator + subfolder;
    print(destPath);
    File.makeDirectory(destPath);
    File.copy(path, destPath + File.separator + file);
}
