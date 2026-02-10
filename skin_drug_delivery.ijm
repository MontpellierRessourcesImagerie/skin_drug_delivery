/**
  *  Skin Drug Delivery
  *  ------------------
  *  Tools to analyze the penetration of nanoformulations into the skin.
  *   
  *  (c) 2026, INSERM, distributed under the MIT license
  *  
  *  written  by Volker Baecker (INSERM) at Montpellier RIO Imaging (https://www.mri.cnrs.fr/en/data-analysis.html)
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


macro "Update Layer Rois (f8) Action Tool - C000T4b12u" {
    updateLayerRois();
}


macro "Update Layer Rois [f8]" {
    updateLayerRois();
}


macro "Open Original Image (f9) Action Tool - C000T4b12o" {
    openOriginalImage();
}


macro "Open Original Image (f9) Action Tool Options" {
    showOpenOriginalImageOptions();
}


macro "Open Original Image [f9]" {
    openOriginalImage();
}


macro "Reanalyze Layers (f10) Action Tool - C000T4b12r" {
    reanalyzeLayers();
}


macro "Reanalyze Layers [f10]" {
    reanalyzeLayers();
}

var dCmds = newMenu("Images Menu Tool", newArray("download dataset", 
                                                 "B2-DiI/B2-DiI-n1-c1 40X.czi", 
                                                 "B2-DiI/B2-DiI-n1-c2 40X.czi", 
                                                 "OEV/OEV_n3_c2_40X_1.czi", 
                                                 "OEV/OEV_n3_c2_40X_2.czi",
                                                 "PBS/PBS_n3_c1_40X_1.czi",
                                                 "options"));
    
macro "Images Menu Tool - CfffL00f0L0161CeeeD71CfffL81f1L0252CeeeD62C666D72CeeeD82CfffL92f2L0353CeeeD63C444D73CeeeD83CfffL93f3L0454CeeeD64C444D74CeeeD84CfffL94f4L0555CeeeD65C444D75CeeeD85CfffL95f5L0636CdddD46CfffD56CeeeD66C444D76CeeeD86CfffD96CdddDa6CfffLb6f6L0727CdddD37C444D47CbbbD57CeeeD67C444D77CeeeD87CbbbD97C444Da7CdddDb7CfffLc7f7L0838CbbbD48C444D58C999D68C444D78C999D88C444D98CbbbDa8CfffLb8f8L0949CbbbD59C333D69C111D79C333D89CbbbD99CfffLa9f9L0a5aCbbbD6aC444D7aCbbbD8aCfffL9afaL0b6bCeeeD7bCfffL8bfbL0c2cCeeeL3cbcCfffLccfcL0d1dCeeeD2dC666D3dC444L4dadC666DbdCeeeDcdCfffLddfdL0e2eCeeeL3ebeCfffLcefeL0fff" {
       cmd = getArgument();       
       if (cmd=="download dataset") {
           call("ij.Prefs.set", "mri.options.only", "false");   
           params = readOptionsDownloadDataset();
           print("Starting download of the dataset...");
           print(params);
           run("download sdd dataset", params); 
           print("...download of the dataset finished.");
           return;
       } 
       if (cmd=="options") {
            call("ij.Prefs.set", "mri.options.only", "true");
            run("download sdd dataset");
            call("ij.Prefs.set", "mri.options.only", "false"); 
            return;
       }
       params = readOptionsDownloadDataset();
       parts = split(params, " ");
       for (i = 0; i < parts.length; i++) {
            param = parts[i];
            iParts = split(param, "=");
            key = iParts[0];
            if (key=="data") {
                dataFolder = iParts[1];
            }
       }
       path = dataFolder + '/skin_drug_delivery_small_dataset/' + cmd;
       run("Bio-Formats", "open=[" + path + "] autoscale color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
}


macro "Install or Update Action Tool - N66C000D2dD2eD3cD58D59D5aD67D75Db3DbeDc3DcdDceDd3DddDdeDe3DeeC666D69Db4De4C222D2cD57D76D85D93DaeDc9DcaDcbDccDd9DdaDdbDdcCdddD0eD2aD47D4dD55D64D6bD8dDb9DbaDbbDc1Dd1De9DeaDebC111D3bD4aD94DadDbdDedC999D48D86D95Dc4Dd4C555D74Dc2Dd2CfffD0dD1bD46D87Da5Db1Db8De1De8C000D4bD66D84Da3C888D2bD3eD6aDa2C444D1eD3dD65D68D9dDa4CeeeD39D5cD73D79D9cDacCbbbD1cD78D92D9eDbcDc8Dd8DecC555D49D5bDb2De2C777D1dD3aD4cD56D77D83Bf0C000D35D47D58D59D5aD7cD8dD8eC666D49C222D0eD13D25D36D57D8cCdddD2dD44D4bD55D67D6dD8aDaeC111D0dD14D6aD7bC999D15D26D68C555D34CfffD05D27D66D9bDadC000D03D24D46D6bC888D02D4aD7eD8bC444D04D1dD45D48D7dD9eCeeeD0cD1cD33D39D5cD79CbbbD12D1eD38D9cC555D5bD69C777D23D37D56D6cD7aD9dB0fC000D65D74D80D81D82C666D35C222D55D64D90CdddD76D94Da0Da1C111D56D73C999D00D54D63D70D71D93C555D37D45D66D84CfffD10D67C000D06D16D26D36D46D83C888D05D15D25C444D07D17D27D75D91CeeeD01D44D62Da2CbbbD57D85C555D72D92C777D47Nf0C000D20D21D22D34D45Dc0Dd0C666D75Db1De1C222D44D55Db0De0CdddD00D01D14D36Dc3Dd3C111D23D33D56C999D13D30D31D43D54Da0C555D24D46D65D77CfffD47D90C000D66D76D86D96Da6Db6Dc1Dc6Dd1Dd6De6C888D85D95Da5Db5Dc5Dd5De5C444D10D11D35D87D97Da7Db7Dc7Dd7De7CeeeD02D42D64Da1Db2De2CbbbD25D57C555D12D32Dc2Dd2C777D67"{
    installOrUpdate();
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


function updateLayerRois() {
    call("ij.Prefs.set", "mri.options.only", "false");   
    run("update layer rois");
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


function getOptionsPathDownloadDataset() {
    pluginsPath = getDirectory("plugins");
    optionsPath = pluginsPath + "skin_drug_delivery/download_dataset_options.json";
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


function readOptionsDownloadDataset() {
    path = getOptionsPathDownloadDataset();
    options = readOptions(path);
    return options;    
}


function readOptions(path) {
    if (!File.exists(path)) {
        return "";
    }
    text = File.openAsString(path);
    text = replace(text, "https:", "httpsD");
    text = replace(text, '\\:\\\\', '\\*\\\\');
    parts = split(text, '}');
    options = "";
    booleanOptions = "";
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
    options = replace(options, "httpsD", "https:");
    options = replace(options, '\\*\\\\', '\\:\\\\');
    options = String.trim(options);
    return options;
}


function installOrUpdate() {        
    scriptsFolder = getDirectory("imagej") + "scripts/";
    if (File.exists(scriptsFolder + "rep_updater.py")) {
        print("Running the updater...");
        setToolInfo();
        run("rep updater");   
        unsetToolInfo();
    } else {
        print("Installing the updater...");
        updateUpdater();  
        print("Please restart FIJI and press the install/update button again!");
    }
       
}


function setToolInfo() {
    call("ij.Prefs.set", "mri.update.tool", "skin_drug_delivery");
    call("ij.Prefs.set", "mri.update.folder", "skin_drug_delivery"); 
    call("ij.Prefs.set", "mri.update.author", "volker"); 
}


function unsetToolInfo() {
    call("ij.Prefs.set", "mri.update.tool", "");
    call("ij.Prefs.set", "mri.update.folder", ""); 
    call("ij.Prefs.set", "mri.update.author", ""); 
}


function updateUpdater() {
    updaterContent = File.openUrlAsString("https://raw.githubusercontent.com/MontpellierRessourcesImagerie/skin_drug_delivery/master/scripts/rep_updater.py");
    scriptsFolder = getDirectory("imagej") + "scripts/";
    File.saveString(updaterContent, scriptsFolder + "rep_updater.py");
}
