/**
  *  Tools to analyze the penetration of nanoformulations into the skin.
  *   
  *  (c) 2026, INSERM
  *  written  by Volker Baecker (INSERM) at Montpellier RIO Imaging (www.mri.cnrs.fr)
  * 
  **
*/

var _URL = "https://github.com/MontpellierRessourcesImagerie/skin_drug_delivery?tab=readme-ov-file#skin_drug_delivery";


macro "Skin Drug Delivery Analysis Tools Help Action Tool - C212D0dD0eD0fD1eD1fD2fD3fD4fD5fD6fD7fD8fD9fDafDbfC83aD17D25D28D37D38D48D49D78D89D95D96D98Da6Db4Db5Db7De5C938D2aD35D4aD55D5aD6aD76D7aD86D8aD9aDaaDb8Db9DbaDbbDc4Dc7DcbDd8DdbDebDf5DfaC959D03D24D44D65D85D94C617D04D15D46D56D57D66D67D69D77D87D88Dc5Dd6Dd7De6De7C969D02D11D12D1cD32D34D51D52D54D61D62D64D75D80D81D83D90Da0Da1Da2Db0Db1Db2Dc0Dc1Dd0Dd1Dd3Dd4De3De4Df1Df2Ca47D6cD6dD8cD9cDbeDccDceDdcDfcCa4bD06D07D08D18D29D39D99Da4Da5Db6Dc8Dd9De9C634D1dD2eD3eD4eD5eD6eD7eD8eDcfDddDdfDedDefDffCa49D09D19D1aD3aD3bD4bD5bD6bD7bDc9DcaDdaDeaDf9C857D0cD2cD2dD3cD3dD9eDadDbdDcdDdeDeeDfdDfeCa6aD00D01D10D13D21D22D23D31D33D41D42D43D53D63D70D71D72D73D74D82D84D91D92D93Da3Db3Dc2Dc3Dd2De0De1De2Df0Df3Df4C828D05D14D16D26D27D36D45D47D58D59D68D79D97Da7Da8Da9Dc6Dd5De8Df6Df7Df8DfbCb59D0bD7dD8dD9bD9dCb48D0aD1bD2bD4cD4dD5cD5dD7cD8bDabDacDaeDbcDecCc6dD20D30D40D50D60" {
     run('URL...', 'url='+_URL);
}


macro "Analyze Image (f5) Action Tool - C000T4b12i" {
    analyzeImage();
}


macro "Analyze Image (f5) Action Tool Options" {
    showAnalyzeImageOptions();
}


macro "Analyze Image [f5]" {
    analyzeImage();
}


macro "Batch Analyze Images (f6) Action Tool - C000T4b12b" {
    batchAnalyzeImages();
}


macro "Batch Analyze Images (f6) Action Tool Options" {
    showBatchAnalyzeImagesOptions();
}


macro "Batch Analyze Images [f6]" {
    batchAnalyzeImages();
}


macro "Correct Layers (f7) Action Tool - C000T4b12c" {
    correctLayers();
}


macro "Correct Layers (f7) Action Tool Options" {
    showCorrectLayersOptions();
}


macro "Correct Layers [f7]" {
    correctLayers();
}


macro "Open Original Image (f8) Action Tool - C000T4b12o" {
    openOriginalImage();
}


macro "Open Original Image (f8) Action Tool Options" {
    showOpenOriginalImageOptions();
}


macro "Open Original Image [f8]" {
    openOriginalImage();
}


macro "Reanalyze Layers (f9) Action Tool - C000T4b12r" {
    reanalyzeLayers();
}


macro "Reanalyze Layers [f9]" {
    reanalyzeLayers();
}


function analyzeImage() {
    call("ij.Prefs.set", "mri.options.only", "false");   
    params = readOptionsAnalyzeImage();
    run("analyze skin drug delivery", params);   
}


function batchAnalyzeImages() {
    call("ij.Prefs.set", "mri.options.only", "false");   
    params = readOptionsBatchAnalyzeImages();
    run("batch analyze skin drug delivery", params); 
}


function correctLayers() {
    call("ij.Prefs.set", "mri.options.only", "false");   
    params = readOptionsCorrectLayers();
    run("correct layers", params);
}


function openOriginalImage() {
    call("ij.Prefs.set", "mri.options.only", "false");   
    params = readOptionsOpenOriginalImage();
    run("open original image", params);
}


function reanalyzeLayers() {
    call("ij.Prefs.set", "mri.options.only", "false");   
    run("reanalyze layers");
}


function showAnalyzeImageOptions() {
    call("ij.Prefs.set", "mri.options.only", "true");
    run("analyze skin drug delivery");
    call("ij.Prefs.set", "mri.options.only", "false");   
}


function showBatchAnalyzeImagesOptions() {
    call("ij.Prefs.set", "mri.options.only", "true");
    run("batch analyze skin drug delivery");
    call("ij.Prefs.set", "mri.options.only", "false");   
}


function showCorrectLayersOptions() {
    call("ij.Prefs.set", "mri.options.only", "true");
    run("correct layers");
    call("ij.Prefs.set", "mri.options.only", "false");  
}


function showOpenOriginalImageOptions() {
    call("ij.Prefs.set", "mri.options.only", "true");
    run("open original image");
    call("ij.Prefs.set", "mri.options.only", "false");      
}


function getOptionsPathCorrectLayers() {
    pluginsPath = getDirectory("plugins");
    optionsPath = pluginsPath + "skin_drug_delivery/correct_layers_options.json";
    return optionsPath;
}


function getOptionsPathAnalyzeImage() {
    pluginsPath = getDirectory("plugins");
    optionsPath = pluginsPath + "skin_drug_delivery/analyze_image_options.json";
    return optionsPath;
}


function getOptionsPathBatchAnalyzeImages() {
    pluginsPath = getDirectory("plugins");
    optionsPath = pluginsPath + "skin_drug_delivery/batch_analyze_images_options.json";
    return optionsPath;
}


function getOptionsPathOpenOriginalImage() {
    pluginsPath = getDirectory("plugins");
    optionsPath = pluginsPath + "skin_drug_delivery/open_original_image_options.json";
    return optionsPath;        
}


function getOptionsPathReanalyzeLayers() {
    pluginsPath = getDirectory("plugins");
    optionsPath = pluginsPath + "skin_drug_delivery/reanalyze_layers_options.json";
    return optionsPath;        
}


function readOptionsCorrectLayers() {
    path = getOptionsPathCorrectLayers();
    options = readOptions(path);
    return options;
}


function readOptionsAnalyzeImage() {
    path = getOptionsPathAnalyzeImage();
    options = readOptions(path);
    return options;
}


function readOptionsBatchAnalyzeImages() {
    path = getOptionsPathBatchAnalyzeImages();
    options = readOptions(path);
    return options;
}


function readOptionsOpenOriginalImage() {
    path = getOptionsPathOpenOriginalImage();
    options = readOptions(path);
    return options;
}


function readOptions(path) {
    text = File.openAsString(path);
    parts = split(text, '}');
    options = ""
    booleanOptions = ""
    for (i = 0; i < parts.length; i++) {    
        line = parts[i];
        if (line.length==0) continue;
        line = replace(line, '{', "");
        line = replace(line, '"', '');
        name = split(line, ":");
        name = replace(name[0], ", ", "");
        name = String.trim(name);
        if (name == "") continue;
        nameParts = split(name, " ");
        option = nameParts[0]; 
        params = substring(line, indexOf(line, ":"));
        params = split(params, ",");
        type = split(params[1], ':');
        type = String.trim(type[1]);
        transient = split(params[2], ':');
        transient = String.trim(transient[1]);
        if (transient=='true') continue;
        value = split(params[5], ':');
        value = String.trim(value[1]);
        if (type=='bool' && value=='true') {
            booleanOptions = booleanOptions + " " + option;
        }
        if (type=='int' || type=='float' || type=='str') {
            options = options + " " + option + "=" + value;
        }
    }
    options = options + booleanOptions;
    options = String.trim(options);
    return options;
}
