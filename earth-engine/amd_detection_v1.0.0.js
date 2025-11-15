/**
 * USGS AMD/IRON SULFATE DETECTION TOOL - VERSION 1.0.0
 * 
 * Based on: Rockwell et al. (2021) - USGS SIM 3466
 * "Improved Automated Identification and Mapping of Iron Sulfate Minerals,
 *  Other Mineral Groups, and Vegetation using Landsat 8 Operational Land
 *  Imager Data, San Juan Mountains, Colorado, and Four Corners Region"
 * 
 * Multi-sensor support: Landsat 8, Landsat 9, Sentinel-2
 * 19-class Boolean classification with contaminated water detection
 * 
 * CRITICAL FIX (v1.0.0): Added .clamp(0.0, 1.0) to eliminate negative
 * reflectance values from Landsat Collection 2 scaling
 * 
 * Author: coodawy
 * Date: 2025-11-15
 * License: MIT
 */

// =============================================================================
// CONFIGURATION & STUDY AREAS
// =============================================================================

// Study areas with coordinates and buffer zones (in meters)
var studyAreas = {
  'Piedmont Lake, OH': ee.Geometry.Point([-81.222, 40.154]).buffer(10000),
  'Clendening Lake, OH': ee.Geometry.Point([-81.227, 40.195]).buffer(10000),
  'Genau Area, Iraq': ee.Geometry.Point([44.94305555555555, 36.21166666666667]).buffer(10000),
  'Delaware, OH': ee.Geometry.Point([-83.168502, 40.264754]).buffer(50000),
  'Goldfield, NV (Paper)': ee.Geometry.Point([-117.233, 37.708]).buffer(15000),
  'Bauer Mill, UT (Paper)': ee.Geometry.Point([-112.388, 40.492]).buffer(5000),
  'Silverton, CO (Paper)': ee.Geometry.Point([-107.665, 37.812]).buffer(20000),
  'Marysvale, UT (Paper)': ee.Geometry.Point([-112.233, 38.450]).buffer(15000),
};

// Current area selection
var areaNames = Object.keys(studyAreas);
var currentAreaName = areaNames[0];
var currentRegion = studyAreas[currentAreaName];

// Set map center to current region
Map.centerObject(currentRegion, 12);

// Date range for image collection
var START_DATE = '2020-01-01';
var END_DATE = '2025-12-01';

// =============================================================================
// IMAGE PROCESSING FUNCTIONS
// =============================================================================

/**
 * Process Landsat Collection 2 Level-2 Surface Reflectance data
 * Applies cloud masking, scaling, and valid range clipping
 */
function processLandsat(image) {
  // Cloud masking using QA_PIXEL band
  var qa = image.select('QA_PIXEL');
  var cloudMask = qa.bitwiseAnd(1<<3).eq(0)  // Bit 3: Cloud
    .and(qa.bitwiseAnd(1<<4).eq(0))          // Bit 4: Cloud confidence
    .and(qa.bitwiseAnd(1<<2).eq(0));         // Bit 2: Cloud shadow
  
  var masked = image.updateMask(cloudMask);
  
  // Select optical bands (B1-B7)
  var bands = masked.select('SR_B[1-7]');
  
  // Apply Landsat Collection 2 scaling formula with clipping to valid range
  // Formula: Reflectance = (DN * 0.0000275) - 0.2
  var scaled = bands.multiply(0.0000275).add(-0.2);
  
  // CRITICAL: Clip to valid reflectance range [0.0, 1.0]
  var clipped = scaled.clamp(0.0, 1.0);
  
  // Rename bands to standard naming
  var renamed = clipped.rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
  
  return masked.addBands(renamed, null, true);
}

/**
 * Process Sentinel-2 L2A data with multi-layer cloud masking
 * Uses QA60, Scene Classification (SCL), cloud probability, and AOT
 */
function processSentinel2(image) {
  var CLOUD_PROB_THRESHOLD = 50;  // 50% cloud probability threshold
  var AOT_THRESHOLD = 0.25;       // Aerosol optical thickness threshold
  
  // QA60 cloud masking
  var qa = image.select('QA60');
  var cloudBitMask = 1 << 10;     // Bit 10: Cloud
  var cirrusBitMask = 1 << 11;    // Bit 11: Cirrus
  var qa60Mask = qa.bitwiseAnd(cloudBitMask).eq(0)
                   .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  
  // Scene Classification Layer masking
  var scl = image.select('SCL');
  // Exclude: 3=Cloud shadow, 8=Cloud medium, 9=Cloud high, 10=Thin cirrus, 11=Snow/ice
  var sclMask = scl.neq(3).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  
  // Cloud probability masking
  var cloudProb = image.select('MSK_CLDPRB');
  var probMask = cloudProb.lt(CLOUD_PROB_THRESHOLD);
  
  // Aerosol optical thickness masking
  var aot = image.select('AOT');
  var aotMask = aot.lt(AOT_THRESHOLD * 1000);  // AOT is in 0.001 units
  
  // Combine all masks
  var combinedMask = qa60Mask.and(sclMask).and(probMask).and(aotMask);
  
  // Scale and rename Sentinel-2 bands to match Landsat naming
  // Sentinel-2 bands: B1(60m), B2(10m), B3(10m), B4(10m), B8(10m), B11(20m), B12(20m)
  // Mapping to Landsat: B1→B1, B2→B2, B3→B3, B4→B4, B8→B5, B11→B6, B12→B7
  var scaled = image.select(['B1', 'B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
    .multiply(0.0001)  // Sentinel-2 scale factor (0-10000 to 0-1)
    .clamp(0.0, 1.0)   // Ensure valid reflectance range
    .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
  
  return image.addBands(scaled, null, true).updateMask(combinedMask);
}

// =============================================================================
// SENSOR CONFIGURATION
// =============================================================================

var SENSOR_CONFIG = {
  'Landsat 8': {
    collection: 'LANDSAT/LC08/C02/T1_L2',
    processor: processLandsat,
    cloudProperty: 'CLOUD_COVER',
    dateRange: [START_DATE, END_DATE]
  },
  'Landsat 9': {
    collection: 'LANDSAT/LC09/C02/T1_L2',
    processor: processLandsat,
    cloudProperty: 'CLOUD_COVER',
    dateRange: [START_DATE, END_DATE]
  },
  'Sentinel-2': {
    collection: 'COPERNICUS/S2_SR_HARMONIZED',
    processor: processSentinel2,
    cloudProperty: 'CLOUDY_PIXEL_PERCENTAGE',
    dateRange: [START_DATE, END_DATE]
  }
};

// =============================================================================
// SPECTRAL INDICES CALCULATION
// =============================================================================

function calculateAllIndices(image) {
  // Select bands with safe division
  var b1 = image.select('SR_B1');  // Coastal/Aerosol 0.43-0.45 μm
  var b2 = image.select('SR_B2');  // Blue 0.45-0.51 μm
  var b3 = image.select('SR_B3');  // Green 0.53-0.59 μm
  var b4 = image.select('SR_B4');  // Red 0.64-0.67 μm
  var b5 = image.select('SR_B5');  // NIR 0.85-0.88 μm
  var b6 = image.select('SR_B6');  // SWIR1 1.57-1.65 μm
  var b7 = image.select('SR_B7');  // SWIR2 2.11-2.29 μm
  
  // Add epsilon to avoid division by zero
  var epsilon = 0.0001;
  var b1_safe = b1.add(epsilon);
  var b2_safe = b2.add(epsilon);
  var b4_safe = b4.add(epsilon);
  var b5_safe = b5.add(epsilon);
  var b7_safe = b7.add(epsilon);
  
  // 1. IRON SULFATE MINERAL INDEX (Rockwell et al. 2021, Table 3)
  // Formula: (B2/B1) - (B5/B4)
  // Detects jarosite and other iron sulfate minerals
  var ironSulfate = b2.divide(b1_safe).subtract(b5.divide(b4_safe))
    .rename('IronSulfate');
  
  // 2. FERRIC IRON 1 "REDNESS INDEX"
  // Formula: B4/B2
  // Detects hematite and goethite
  var ferricIron1 = b4.divide(b2_safe).rename('FerricIron1');
  
  // 3. FERRIC IRON 2 (Crystal Field Electronic Transition)
  // Formula: (B4/B2) × (B4+B6)/(B5)
  // Enhanced ferric iron detection
  var ferricIron2 = b4.divide(b2_safe).multiply(b4.add(b6).divide(b5_safe))
    .rename('FerricIron2');
  
  // 4. FERROUS IRON
  // Formula: (B3+B6)/(B4+B5)
  // Detects chlorite and other ferrous minerals
  var ferrousIron = b3.add(b6).divide(b4.add(b5).add(epsilon))
    .rename('FerrousIron');
  
  // 5. CLAY-SULFATE-MICA INDEX
  // Formula: (B6/B7) - (B5/B4)
  // Detects clay, sulfate, and mica minerals
  var claySulfateMica = b6.divide(b7_safe).subtract(b5.divide(b4_safe))
    .rename('ClaySulfateMica');
  
  // 6. GREEN VEGETATION INDEX
  // Formula: B5/B4 (NDVI-like)
  // Detects vegetation
  var greenVeg = b5.divide(b4_safe).rename('GreenVeg');
  
  // 7. STANDARD INDICES
  var ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
  var ndwi = image.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI');
  var mndwi = image.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI');
  var brightness = b2.add(b3).add(b4).divide(3).rename('Brightness');
  
  // 8. AWEInsh - Automated Water Extraction Index (Feyisa et al. 2014)
  // Formula: B2 + 2.5×B3 - 1.5×B5 - 0.25×B7
  // Detects water bodies
  var aweinsh = b2.add(b3.multiply(2.5))
    .subtract(b5.multiply(1.5))
    .subtract(b7.multiply(0.25))
    .rename('AWEINSH');
  
  // Return image with all indices added
  return image.addBands([
    ironSulfate, ferricIron1, ferricIron2, ferrousIron,
    claySulfateMica, greenVeg, ndvi, ndwi, mndwi, brightness, aweinsh
  ]);
}

// =============================================================================
// IMAGE COLLECTION LOADING
// =============================================================================

function loadImageCollection() {
  var sensorConfig = SENSOR_CONFIG[settings.currentSensor];
  
  return ee.ImageCollection(sensorConfig.collection)
    .filterDate(sensorConfig.dateRange[0], sensorConfig.dateRange[1])
    .filter(ee.Filter.lt(sensorConfig.cloudProperty, 30))  // Max 30% cloud cover
    .map(sensorConfig.processor)
    .map(calculateAllIndices);
}

// =============================================================================
// SETTINGS & THRESHOLDS
// =============================================================================

var settings = {
  // Sensor selection
  currentSensor: 'Landsat 8',
  
  // Iron sulfate threshold (Rockwell et al. 2021: >1.15 indicates presence)
  ironSulfateThreshold: 1.15,
  
  // Ferric iron thresholds
  ferricIron1Threshold: 1.4,
  ferricIron2Threshold: 2.5,
  
  // Ferrous iron threshold
  ferrousIronThreshold: 1.05,
  
  // Clay/mica/sulfate threshold
  claySulfateMicaThreshold: 0.15,
  
  // Vegetation thresholds
  greenVegThreshold: 1.5,
  ndviMax: 0.25,
  
  // Water masking
  useWaterMask: true,
  waterThreshold: 0.3,
  useAWEINSH: true,
  aweinshThreshold: 0.0,
  
  // Contaminated water detection
  useAdvancedWaterDetection: false,
  contaminatedWaterThreshold: 1.8,
  
  // Brightness filtering
  brightnessMax: 0.20,
  brightnessMin: 0.02,
  
  // Dark area masking
  darkMaskThreshold: 0.12,
  
  // Accuracy tools
  showAccuracyTools: false,
  
  // Current state
  currentComposite: null,
  currentRegion: currentRegion,
  currentAreaName: currentAreaName
};

// =============================================================================
// WATER MASK CREATION
// =============================================================================

function createContaminatedWaterMask() {
  if (!settings.currentComposite) {
    return {clean: ee.Image(0), contaminated: ee.Image(0), all: ee.Image(0)};
  }
  
  var iron = settings.currentComposite.select('IronSulfate');
  var mndwi = settings.currentComposite.select('MNDWI');
  var aweinsh = settings.currentComposite.select('AWEINSH');
  
  // Multi-index water detection
  var waterMask1 = mndwi.gt(settings.waterThreshold);
  var waterMask2 = settings.useAWEINSH ? aweinsh.gt(settings.aweinshThreshold) : ee.Image(0);
  var isWater = waterMask1.or(waterMask2);
  
  // Contaminated water: high iron IN water
  var isContaminatedWater = iron.gt(settings.contaminatedWaterThreshold).and(isWater);
  
  // Clean water
  var isCleanWater = isWater.and(isContaminatedWater.not());
  
  return {
    clean: isCleanWater,
    contaminated: isContaminatedWater,
    all: isWater
  };
}

// =============================================================================
// BOOLEAN CLASSIFICATION - 19 CLASSES
// =============================================================================

function createBooleanClassification() {
  if (!settings.currentComposite) return null;
  
  // Select indices
  var iron = settings.currentComposite.select('IronSulfate');
  var ferric1 = settings.currentComposite.select('FerricIron1');
  var ferric2 = settings.currentComposite.select('FerricIron2');
  var ferrous = settings.currentComposite.select('FerrousIron');
  var clay = settings.currentComposite.select('ClaySulfateMica');
  var greenVeg = settings.currentComposite.select('GreenVeg');
  var brightness = settings.currentComposite.select('Brightness');
  var b6 = settings.currentComposite.select('SR_B6');
  
  // Create binary masks
  var hasIron = iron.gt(settings.ironSulfateThreshold);
  var hasFerric1 = ferric1.gt(settings.ferricIron1Threshold);
  var hasFerric2 = ferric2.gt(settings.ferricIron2Threshold);
  var hasFerrous = ferrous.gt(settings.ferrousIronThreshold);
  var hasClay = clay.gt(settings.claySulfateMicaThreshold);
  var hasVeg = greenVeg.gt(settings.greenVegThreshold);
  
  // Water detection
  var waterMasks = createContaminatedWaterMask();
  
  // Quality masks
  var notBright = brightness.lt(settings.brightnessMax);
  var notDark = b6.gt(settings.darkMaskThreshold).and(brightness.gt(settings.brightnessMin));
  
  // Extreme AMD overrides water mask
  var extremeAMD = iron.gt(2.0);
  
  // Land mask logic
  var standardLandMask = waterMasks.clean.not().and(notDark).and(notBright);
  
  // Allow extreme AMD classification even in water
  var amdLandMask = settings.useAdvancedWaterDetection ?
    standardLandMask.or(waterMasks.contaminated) :
    standardLandMask.or(extremeAMD.and(waterMasks.all));
  
  // Classification with priority order
  var classification = ee.Image(0)
    .where(hasVeg, 11)
    .where(hasFerrous.and(hasClay.not()).and(hasFerric1.not()).and(standardLandMask), 4)
    .where(hasFerric1.and(hasFerric2.not()).and(hasClay.not()).and(hasIron.not()).and(standardLandMask), 1)
    .where(hasVeg.and(hasFerric1), 13)
    .where(hasFerric1.and(hasFerric2).and(hasClay.not()).and(standardLandMask), 2)
    .where(hasFerric1.and(hasClay.not()).and(standardLandMask), 3)
    .where(hasClay.and(hasFerric1.not()).and(hasIron.not()).and(standardLandMask), 5)
    .where(hasClay.and(hasFerric1).and(hasFerric2.not()).and(hasIron.not()).and(standardLandMask), 6)
    .where(hasClay.and(hasFerric1.or(hasFerric2)).and(hasIron.not()).and(standardLandMask), 7)
    .where(hasClay.and(hasFerric1).and(standardLandMask), 8)
    .where(hasClay.and(standardLandMask), 9)
    .where(hasFerrous.and(standardLandMask), 10)
    .where(hasFerric1.and(hasFerric2).and(standardLandMask), 12)
    .where(hasIron.and(standardLandMask), 14)
    .where(hasIron.and(hasFerric1).and(standardLandMask), 15)
    .where(hasIron.and(hasFerric1).and(hasFerric2).and(standardLandMask), 16)
    .where(hasIron.and(hasFerric1).and(hasFerric2).and(hasFerrous).and(standardLandMask), 17)
    .where(hasIron.and(hasFerric1).and(hasFerric2).and(hasFerrous).and(hasClay).and(standardLandMask), 18)
    .where(hasIron.and(hasFerric1).and(hasFerric2).and(hasFerrous).and(hasClay).and(hasVeg).and(standardLandMask), 19)
    .where(waterMasks.contaminated, 20)
    .where(waterMasks.clean, 21)
    .clip(settings.currentRegion);
    
  return classification.updateMask(amdLandMask.or(waterMasks.all));
}

// =============================================================================
// UPDATE COMPOSITE AND CLASSIFICATION
// =============================================================================

function updateComposite() {
  var collection = loadImageCollection();
  var composite = collection.median().clip(settings.currentRegion);
  settings.currentComposite = composite;
  return composite;
}

function updateDetection() {
  var classification = createBooleanClassification();
  if (!classification) return;
  
  // Classification visualization
  var classVis = {
    min: 1,
    max: 21,
    palette: [
      'A0522D', // 1: Minor Ferric (Hematite)
      'FF00FF', // 2: Major Ferric Iron
      'A0522D', // 3: Minor Ferric (Hematite)
      '00CED1', // 4: Ferrous (Chlorite)
      '00FF00', // 5: Clay-Sulfate-Mica
      'FFFF00', // 6: Clay+Minor Ferric
      'F5F5DC', // 7: Clay+Mod Ferric
      'FFA500', // 8: Clay+Major Ferric
      '008000', // 9: Clay minerals
      '00FF7F', // 10: Clay+Ferrous
      '228B22', // 11: Dense Vegetation
      'FF0000', // 12: Major Iron Sulfate
      '9ACD32', // 13: Sparse Veg+Ferric
      'FFB6C1', // 14: Oxidizing Sulfides
      'FF69B4', // 15: Iron Sulfate+Ferric
      'FF1493', // 16: Argillic Alteration
      'DC143C', // 17: Proximal Jarosite
      '8B0000', // 18: Distal Jarosite
      '4B0082', // 19: Clay+Ferrous+Iron
      '0000FF', // 20: Contaminated Water
      '1E90FF'  // 21: Clean Water
    ]
  };
  
  // Add to map
  Map.layers().reset();
  Map.addLayer(classification, classVis, 'AMD Classification');
  
  // Add water mask layer if enabled
  if (settings.useWaterMask) {
    var waterMasks = createContaminatedWaterMask();
    Map.addLayer(waterMasks.clean.selfMask(), {palette: ['blue']}, 'Clean Water', false);
    Map.addLayer(waterMasks.contaminated.selfMask(), {palette: ['red']}, 'Contaminated Water', false);
  }
  
  // Add raw bands for reference
  Map.addLayer(settings.currentComposite, {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 0, max: 0.3}, 'True Color (432)', false);
  Map.addLayer(settings.currentComposite, {bands: ['SR_B5', 'SR_B4', 'SR_B3'], min: 0, max: 0.3}, 'False Color (543)', false);
  
  // Add indices for analysis
  Map.addLayer(settings.currentComposite.select('IronSulfate'), {min: 0, max: 2.5, palette: ['blue', 'white', 'red']}, 'Iron Sulfate Index', false);
  Map.addLayer(settings.currentComposite.select('FerricIron1'), {min: 0, max: 3, palette: ['white', 'yellow', 'red']}, 'Ferric Iron 1', false);
  Map.addLayer(settings.currentComposite.select('MNDWI'), {min: -1, max: 1, palette: ['red', 'white', 'blue']}, 'MNDWI', false);
  
  return classification;
}

// =============================================================================
// STATISTICS AND CLICK HANDLER
// =============================================================================

function calculateStats() {
  if (!settings.currentComposite) return;
  
  // Get the region of interest
  var region = settings.currentRegion;
  
  // Calculate statistics for key indices
  var stats = settings.currentComposite.select([
    'SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7',
    'IronSulfate', 'FerricIron1', 'FerricIron2', 'FerrousIron',
    'ClaySulfateMica', 'GreenVeg', 'NDVI', 'MNDWI', 'AWEINSH'
  ]).reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: region,
    scale: 30,
    bestEffort: true
  });
  
  // Format statistics
  var statsText = [
    '=== STATISTICS ===',
    'Area: ' + settings.currentAreaName,
    'Sensor: ' + settings.currentSensor,
    'Date Range: ' + START_DATE + ' to ' + END_DATE,
    '',
    '=== BAND REFLECTANCES ===',
    'B1 (Coastal): ' + (stats.get('SR_B1') ? stats.get('SR_B1').format('%.4f').getInfo() : 'N/A'),
    'B2 (Blue):    ' + (stats.get('SR_B2') ? stats.get('SR_B2').format('%.4f').getInfo() : 'N/A'),
    'B3 (Green):   ' + (stats.get('SR_B3') ? stats.get('SR_B3').format('%.4f').getInfo() : 'N/A'),
    'B4 (Red):     ' + (stats.get('SR_B4') ? stats.get('SR_B4').format('%.4f').getInfo() : 'N/A'),
    'B5 (NIR):     ' + (stats.get('SR_B5') ? stats.get('SR_B5').format('%.4f').getInfo() : 'N/A'),
    'B6 (SWIR1):   ' + (stats.get('SR_B6') ? stats.get('SR_B6').format('%.4f').getInfo() : 'N/A'),
    'B7 (SWIR2):   ' + (stats.get('SR_B7') ? stats.get('SR_B7').format('%.4f').getInfo() : 'N/A'),
    '',
    '=== SPECTRAL INDICES ===',
    'Iron Sulfate:    ' + (stats.get('IronSulfate') ? stats.get('IronSulfate').format('%.4f').getInfo() : 'N/A') + ' (Threshold: >1.15)',
    'Ferric Iron 1:   ' + (stats.get('FerricIron1') ? stats.get('FerricIron1').format('%.4f').getInfo() : 'N/A') + ' (Threshold: >1.4)',
    'Ferric Iron 2:   ' + (stats.get('FerricIron2') ? stats.get('FerricIron2').format('%.4f').getInfo() : 'N/A') + ' (Threshold: >2.5)',
    'Ferrous Iron:    ' + (stats.get('FerrousIron') ? stats.get('FerrousIron').format('%.4f').getInfo() : 'N/A') + ' (Threshold: >1.05)',
    'Clay-Sulf-Mica:  ' + (stats.get('ClaySulfateMica') ? stats.get('ClaySulfateMica').format('%.4f').getInfo() : 'N/A') + ' (Threshold: >0.15)',
    'MNDWI:           ' + (stats.get('MNDWI') ? stats.get('MNDWI').format('%.4f').getInfo() : 'N/A') + ' (Water if >0.3)'
  ].join('\n');
  
  // Update statistics panel
  if (typeof statsPanel !== 'undefined') {
    statsPanel.setValue(statsText);
  } else {
    print(statsText);
  }
  
  return statsText;
}

// Click handler for point analysis
Map.onClick(function(coords) {
  if (!settings.currentComposite) return;
  
  var point = ee.Geometry.Point(coords.lon, coords.lat);
  
  // Get values at clicked point
  var values = settings.currentComposite.reduceRegion({
    reducer: ee.Reducer.first(),
    geometry: point,
    scale: 30
  });
  
  // Format output
  var coordsText = 'Coords: ' + coords.lon.toFixed(6) + ', ' + coords.lat.toFixed(6);
  var valuesText = [
    '=== PIXEL VALUES ===',
    coordsText,
    '',
    '=== RAW BAND REFLECTANCES ===',
    'B1 (Coastal): ' + (values.get('SR_B1') ? values.get('SR_B1').format('%.4f').getInfo() : 'N/A'),
    'B2 (Blue):    ' + (values.get('SR_B2') ? values.get('SR_B2').format('%.4f').getInfo() : 'N/A'),
    'B3 (Green):   ' + (values.get('SR_B3') ? values.get('SR_B3').format('%.4f').getInfo() : 'N/A'),
    'B4 (Red):     ' + (values.get('SR_B4') ? values.get('SR_B4').format('%.4f').getInfo() : 'N/A'),
    'B5 (NIR):     ' + (values.get('SR_B5') ? values.get('SR_B5').format('%.4f').getInfo() : 'N/A'),
    'B6 (SWIR1):   ' + (values.get('SR_B6') ? values.get('SR_B6').format('%.4f').getInfo() : 'N/A'),
    'B7 (SWIR2):   ' + (values.get('SR_B7') ? values.get('SR_B7').format('%.4f').getInfo() : 'N/A'),
    '',
    '=== SPECTRAL INDICES ===',
    'Iron Sulfate:    ' + (values.get('IronSulfate') ? values.get('IronSulfate').format('%.4f').getInfo() : 'N/A'),
    'Ferric Iron 1:   ' + (values.get('FerricIron1') ? values.get('FerricIron1').format('%.4f').getInfo() : 'N/A'),
    'Ferric Iron 2:   ' + (values.get('FerricIron2') ? values.get('FerricIron2').format('%.4f').getInfo() : 'N/A'),
    'Ferrous Iron:    ' + (values.get('FerrousIron') ? values.get('FerrousIron').format('%.4f').getInfo() : 'N/A'),
    'Clay-Sulf-Mica:  ' + (values.get('ClaySulfateMica') ? values.get('ClaySulfateMica').format('%.4f').getInfo() : 'N/A'),
    'MNDWI:           ' + (values.get('MNDWI') ? values.get('MNDWI').format('%.4f').getInfo() : 'N/A')
  ].join('\n');
  
  print(valuesText);
  
  // Add a marker at the clicked point
  Map.layers().set(0, ui.Map.Layer(point, {color: 'red'}, 'Selected Point'));
});

// =============================================================================
// USER INTERFACE
// =============================================================================

// Create control panel
var panel = ui.Panel({
  style: {width: '440px', position: 'top-right', padding: '15px'}
});

// Title
var title = ui.Label('USGS AMD Detection Tool', {
  fontWeight: 'bold', fontSize: '18px', margin: '0 0 5px 0'
});

var subtitle = ui.Label('Rockwell et al. (2021) SIM 3466 - Multi-Sensor v1.0.0', {
  fontSize: '10px', color: '#666', margin: '0 0 15px 0'
});

// Sensor selector
var sensorLabel = ui.Label('Sensor:', {fontWeight: 'bold', fontSize: '11px', margin: '8px 0 3px 0'});
var sensorSelect = ui.Select({
  items: Object.keys(SENSOR_CONFIG),
  value: settings.currentSensor,
  style: {stretch: 'horizontal'},
  onChange: function(selected) {
    settings.currentSensor = selected;
    print('Sensor changed to: ' + selected);
    print('Reload study area to apply changes.');
  }
});

// Region selector
var regionLabel = ui.Label('Study Area:', {fontWeight: 'bold', fontSize: '11px'});
var regionSelect = ui.Select({
  items: areaNames,
  value: currentAreaName,
  style: {stretch: 'horizontal'},
  onChange: function(selected) {
    settings.currentAreaName = selected;
    settings.currentRegion = studyAreas[selected];
    Map.centerObject(settings.currentRegion, 12);
    updateEverything();
  }
});

// Iron Sulfate threshold
var ironLabel = ui.Label('Iron Sulfate Threshold: 1.15', {margin: '12px 0 3px 0', fontSize: '10px'});
var ironSlider = ui.Slider({
  min: 0.5, max: 2.5, value: 1.15, step: 0.05,
  style: {stretch: 'horizontal'},
  onChange: function(value) {
    settings.ironSulfateThreshold = value;
    ironLabel.setValue('Iron Sulfate Threshold: ' + value.toFixed(2));
    updateDetection();
  }
});

// Ferric Iron 1 threshold
var ferric1Label = ui.Label('Ferric Iron 1 Threshold: 1.40', {margin: '8px 0 3px 0', fontSize: '10px'});
var ferric1Slider = ui.Slider({
  min: 1.0, max: 2.5, value: 1.4, step: 0.05,
  style: {stretch: 'horizontal'},
  onChange: function(value) {
    settings.ferricIron1Threshold = value;
    ferric1Label.setValue('Ferric Iron 1 Threshold: ' + value.toFixed(2));
    updateDetection();
  }
});

// Clay-Sulfate-Mica threshold
var clayLabel = ui.Label('Clay-Sulfate-Mica Threshold: 0.15', {margin: '8px 0 3px 0', fontSize: '10px'});
var claySlider = ui.Slider({
  min: 0.0, max: 0.5, value: 0.15, step: 0.02,
  style: {stretch: 'horizontal'},
  onChange: function(value) {
    settings.claySulfateMicaThreshold = value;
    clayLabel.setValue('Clay-Sulfate-Mica Threshold: ' + value.toFixed(2));
    updateDetection();
  }
});

// Water mask controls
var waterCheckbox = ui.Checkbox({
  label: 'Exclude Water Bodies (MNDWI > threshold)',
  value: true,
  style: {fontSize: '10px'},
  onChange: function(checked) {
    settings.useWaterMask = checked;
    waterSlider.setDisabled(!checked);
    updateDetection();
  }
});

var waterLabel = ui.Label('Water MNDWI Threshold: 0.30', {margin: '3px 0 3px 0', fontSize: '10px'});
var waterSlider = ui.Slider({
  min: 0.0, max: 0.6, value: 0.3, step: 0.05,
  style: {stretch: 'horizontal'},
  onChange: function(value) {
    settings.waterThreshold = value;
    waterLabel.setValue('Water MNDWI Threshold: ' + value.toFixed(2));
    updateDetection();
  }
});

// Contaminated water detection
var contaminatedWaterCheckbox = ui.Checkbox({
  label: 'Detect Contaminated Water (Iron > threshold in water)',
  value: false,
  style: {fontSize: '10px', margin: '10px 0 3px 0'},
  onChange: function(checked) {
    settings.useAdvancedWaterDetection = checked;
    contaminatedWaterSlider.setDisabled(!checked);
    updateDetection();
  }
});

var contaminatedWaterLabel = ui.Label('Contaminated Water Iron Threshold: 1.80', {
  margin: '3px 0 3px 0', fontSize: '10px'
});
var contaminatedWaterSlider = ui.Slider({
  min: 1.5, max: 3.0, value: 1.8, step: 0.1,
  style: {stretch: 'horizontal'},
  disabled: true,
  onChange: function(value) {
    settings.contaminatedWaterThreshold = value;
    contaminatedWaterLabel.setValue('Contaminated Water Iron Threshold: ' + value.toFixed(2));
    updateDetection();
  }
});

// Reset button
var resetButton = ui.Button({
  label: 'Reset to Paper Defaults',
  style: {stretch: 'horizontal', margin: '12px 0 8px 0', fontSize: '11px'},
  onClick: function() {
    ironSlider.setValue(1.15);
    ferric1Slider.setValue(1.4);
    claySlider.setValue(0.15);
    waterCheckbox.setValue(true);
    waterSlider.setValue(0.3);
    contaminatedWaterCheckbox.setValue(false);
  }
});

// Accuracy tools button
var accuracyButton = ui.Button({
  label: 'Toggle Accuracy Verification Tools',
  style: {stretch: 'horizontal', margin: '0 0 8px 0', fontSize: '10px'},
  onClick: function() {
    settings.showAccuracyTools = !settings.showAccuracyTools;
    updateDetection();
  }
});

// Statistics panel
var statsPanel = ui.Label('Loading...', {
  fontSize: '9px',
  whiteSpace: 'pre-wrap',
  padding: '8px',
  margin: '10px 0',
  border: '1px solid #ddd',
  backgroundColor: '#f9f9f9',
  maxHeight: '300px'
});

// Instructions
var instructions = ui.Label(
  'ROCKWELL ET AL. (2021) METHOD:\n\n' +
  'Iron Sulfate = (Blue/Coastal) - (NIR/Red)\n' +
  '  >1.15 = jarosite likely present\n' +
  '  >1.50 = high confidence\n\n' +
  'NEW: Contaminated water detection\n' +
  '  Allows Iron>threshold even in water\n' +
  '  Fixes Delaware Iron=2.25 issue\n\n' +
  'Paper validation sites included',
  {fontSize: '8px', whiteSpace: 'pre', color: '#555', margin: '8px 0'}
);

// Add all controls to panel
panel.add(title);
panel.add(subtitle);
panel.add(sensorLabel);
panel.add(sensorSelect);
panel.add(regionLabel);
panel.add(regionSelect);
panel.add(ironLabel);
panel.add(ironSlider);
panel.add(ferric1Label);
panel.add(ferric1Slider);
panel.add(clayLabel);
panel.add(claySlider);
panel.add(waterCheckbox);
panel.add(waterLabel);
panel.add(waterSlider);
panel.add(contaminatedWaterCheckbox);
panel.add(contaminatedWaterLabel);
panel.add(contaminatedWaterSlider);
panel.add(resetButton);
panel.add(accuracyButton);
panel.add(statsPanel);
panel.add(instructions);

// Add panel to map
Map.add(panel);

// =============================================================================
// LEGEND
// =============================================================================

// Create the legend panel
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px',
    backgroundColor: 'white',
    border: '1px solid #ddd'
  }
});

// Add legend title
var legendTitle = ui.Label({
  value: 'AMD Classification (19 Classes)',
  style: {
    fontWeight: 'bold',
    fontSize: '12px',
    margin: '0 0 4px 0',
    padding: '0'
  }
});

// Add the title to the panel
legend.add(legendTitle);

// Create and add the legend content
var legendContent = ui.Panel({
  style: {
    padding: '0',
    margin: '0',
    maxHeight: '300px',
    overflowY: 'auto',
    fontSize: '10px'
  }
});

// AMD Indicator Classes (High Priority)
var amdClasses = [
  {color: 'FFB6C1', label: '14: Oxidizing Sulfides'},
  {color: 'FF0000', label: '12: Major Iron Sulfate'},
  {color: 'DC143C', label: '17: Proximal Jarosite'},
  {color: '8B0000', label: '18: Distal Jarosite'},
  {color: 'FF1493', label: '9: Argillic Alteration'},
  {color: 'C71585', label: '19: Clay+Ferrous+Iron'}
];

// Other Mineral Classes
var otherClasses = [
  {color: 'FF6347', label: '8: Clay+Major Ferric'},
  {color: 'FFA500', label: '7: Clay+Mod Ferric'},
  {color: 'FFFF00', label: '6: Clay+Minor Ferric'},
  {color: '00FF00', label: '5: Clay-Sulfate-Mica'},
  {color: '008B8B', label: '10: Clay+Ferrous'},
  {color: 'FF00FF', label: '2: Major Ferric Iron'},
  {color: 'A0522D', label: '1: Minor Ferric (Hematite)'},
  {color: '800080', label: '3: Ferric+-Ferrous'},
  {color: '00CED1', label: '4: Ferrous (Chlorite)'},
  {color: '228B22', label: '11: Dense Vegetation'},
  {color: '9ACD32', label: '13: Sparse Veg+Ferric'}
];

// Water Classes
var waterClasses = [
  {color: '0000FF', label: '20: Contaminated Water'},
  {color: '1E90FF', label: '21: Clean Water'}
];

// Function to create a single legend item
function createLegendItem(color, label) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: '#' + color,
      padding: '8px',
      margin: '0 0 4px 0'
    }
  });
  
  var description = ui.Label({
    value: label,
    style: {margin: '0 0 4px 8px'}
  });
  
  return ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
}

// Add AMD classes to legend
var amdHeader = ui.Label({
  value: 'AMD Indicator Classes:',
  style: {fontWeight: 'bold', margin: '8px 0 4px 0'}
});
legendContent.add(amdHeader);

// Add AMD classes in a grid
var amdGrid = ui.Panel({
  layout: ui.Panel.Layout.Flow('horizontal'),
  style: {stretch: 'horizontal'}
});

// Split into two columns
var col1 = ui.Panel({
  layout: ui.Panel.Layout.Flow('vertical'),
  style: {width: '50%'}
});

var col2 = ui.Panel({
  layout: ui.Panel.Layout.Flow('vertical'),
  style: {width: '50%'}
});

// Add first half to col1, second half to col2
for (var i = 0; i < amdClasses.length; i++) {
  var item = createLegendItem(amdClasses[i].color, amdClasses[i].label);
  if (i < Math.ceil(amdClasses.length / 2)) {
    col1.add(item);
  } else {
    col2.add(item);
  }
}

amdGrid.add(col1);
amdGrid.add(col2);
legendContent.add(amdGrid);

// Add other classes header
var otherHeader = ui.Label({
  value: 'Other Mineral Classes:',
  style: {fontWeight: 'bold', margin: '8px 0 4px 0'}
});
legendContent.add(otherHeader);

// Add other classes in a grid
var otherGrid = ui.Panel({
  layout: ui.Panel.Layout.Flow('horizontal'),
  style: {stretch: 'horizontal'}
});

// Split into two columns
var col3 = ui.Panel({
  layout: ui.Panel.Layout.Flow('vertical'),
  style: {width: '50%'}
});

var col4 = ui.Panel({
  layout: ui.Panel.Layout.Flow('vertical'),
  style: {width: '50%'}
});

// Add first half to col3, second half to col4
for (var j = 0; j < otherClasses.length; j++) {
  var item = createLegendItem(otherClasses[j].color, otherClasses[j].label);
  if (j < Math.ceil(otherClasses.length / 2)) {
    col3.add(item);
  } else {
    col4.add(item);
  }
}

otherGrid.add(col3);
otherGrid.add(col4);
legendContent.add(otherGrid);

// Add water classes header
var waterHeader = ui.Label({
  value: 'Water Classes:',
  style: {fontWeight: 'bold', margin: '8px 0 4px 0'}
});
legendContent.add(waterHeader);

// Add water classes in a row
var waterGrid = ui.Panel({
  layout: ui.Panel.Layout.Flow('horizontal'),
  style: {stretch: 'horizontal'}
});

for (var k = 0; k < waterClasses.length; k++) {
  waterGrid.add(createLegendItem(waterClasses[k].color, waterClasses[k].label));
}

legendContent.add(waterGrid);

// Add legend content to legend panel
legend.add(legendContent);

// Add legend to map
Map.add(legend);

// =============================================================================
// INITIALIZATION
// =============================================================================

// Main update function
function updateEverything() {
  // Show loading message
  print('Loading ' + settings.currentSensor + ' data for ' + settings.currentAreaName + '...');
  
  // Update composite and detection
  var composite = updateComposite();
  var classification = updateDetection();
  
  // Calculate and display statistics
  var stats = calculateStats();
  
  // Add a marker for paper validation sites
  if (settings.currentAreaName.includes('(Paper)')) {
    Map.layers().set(0, ui.Map.Layer(settings.currentRegion, {color: 'yellow'}, 'Validation Site'));
  }
  
  print('Done! Use the controls to adjust thresholds and click on the map for pixel values.');
  
  // Print paper reference
  print('\nREFERENCE: Rockwell, B. W., McDougal, R. R., & Gent, C. A. (2021). ' +
        'Improved automated identification and mapping of iron sulfate minerals, ' +
        'other mineral groups, and vegetation using Landsat 8 Operational Land ' +
        'Imager data, San Juan Mountains, Colorado, and Four Corners Region. ' +
        'U.S. Geological Survey Scientific Investigations Map 3466.');
}

// Print welcome message
print('USGS AMD/Iron Sulfate Detection Tool v1.0.0');
print('Initializing...');

// Run initial update
updateEverything();

// =============================================================================
// EXPORT FUNCTIONS (For reference, not used in UI by default)
// =============================================================================

function exportClassification() {
  if (!settings.currentComposite) return;
  
  var classification = createBooleanClassification();
  var region = settings.currentRegion;
  var name = 'AMD_Classification_' + settings.currentSensor.replace(/\s+/g, '') + 
             '_' + settings.currentAreaName.replace(/[^a-zA-Z0-9]/g, '_') + 
             '_' + ee.Date(Date.now()).format('yyyyMMdd').getInfo();
  
  Export.image.toDrive({
    image: classification,
    description: name,
    scale: 30,
    region: region,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
    formatOptions: {
      cloudOptimized: true
    },
    folder: 'GEE_Exports',
    fileNamePrefix: name
  });
  
  print('Export started: ' + name);
}

function exportIndices() {
  if (!settings.currentComposite) return;
  
  var region = settings.currentRegion;
  var name = 'AMD_Indices_' + settings.currentSensor.replace(/\s+/g, '') + 
             '_' + settings.currentAreaName.replace(/[^a-zA-Z0-9]/g, '_') + 
             '_' + ee.Date(Date.now()).format('yyyyMMdd').getInfo();
  
  // Select only the index bands for export
  var indices = settings.currentComposite.select([
    'IronSulfate', 'FerricIron1', 'FerricIron2', 'FerrousIron',
    'ClaySulfateMica', 'NDVI', 'MNDWI', 'AWEINSH'
  ]);
  
  Export.image.toDrive({
    image: indices,
    description: name,
    scale: 30,
    region: region,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
    formatOptions: {
      cloudOptimized: true
    },
    folder: 'GEE_Exports',
    fileNamePrefix: name
  });
  
  print('Export started: ' + name);
}

// Add export buttons to the UI (hidden by default)
var exportPanel = ui.Panel({
  widgets: [
    ui.Button('Export Classification', exportClassification, false, {stretch: 'horizontal'}),
    ui.Button('Export Indices', exportIndices, false, {stretch: 'horizontal'})
  ],
  layout: ui.Panel.Layout.Flow('vertical'),
  style: {position: 'top-right', margin: '10px 10px 0 0', width: '200px'}
});

// Uncomment to enable export buttons
// Map.add(exportPanel);

// =============================================================================
// END OF SCRIPT
// =============================================================================
