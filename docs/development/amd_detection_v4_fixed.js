// =============================================================================
// LANDSAT 8 PROCESSING - CORRECTED SCALING WITH CLIPPING
// =============================================================================

function processLandsat(image) {
  // Cloud masking FIRST
  var qa = image.select('QA_PIXEL');
  var cloudMask = qa.bitwiseAnd(1<<3).eq(0)
    .and(qa.bitwiseAnd(1<<4).eq(0))
    .and(qa.bitwiseAnd(1<<2).eq(0));
  
  var masked = image.updateMask(cloudMask);
  
  // CRITICAL FIX: Landsat Collection 2 Level-2 Surface Reflectance scaling
  // Official USGS formula: Reflectance = (DN * 0.0000275) + (-0.2)
  // This is equivalent to: Reflectance = (DN * 0.0000275) - 0.2
  // 
  // The SR_B bands are ALREADY in DN format (0-10000 range typically)
  // We multiply by 0.0000275 to scale to 0-0.275 range, then subtract 0.2
  
  var bands = masked.select('SR_B[1-7]');
  
  // Apply official scaling: multiply by scale factor, then add offset
  var scaled = bands.multiply(0.0000275).add(-0.2);
  
  // CRITICAL: Clip to valid reflectance range [0.0, 1.0]
  // Negative values indicate low signal (shadows, water absorption)
  // Values >1.0 are physically impossible and indicate saturation
  var clipped = scaled.clamp(0.0, 1.0);
  
  // Rename to keep same band names
  var renamed = clipped.rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
  
  return masked.addBands(renamed, null, true);
}

// =============================================================================
// SENTINEL-2 V3 HYBRID CLOUD MASKING - WITH CLIPPING
// =============================================================================

function processSentinel2(image) {
  var CLOUD_PROB_THRESHOLD = 50;
  var AOT_THRESHOLD = 0.25;
  
  var qa = image.select('QA60');
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  var qa60Mask = qa.bitwiseAnd(cloudBitMask).eq(0)
                   .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  
  var scl = image.select('SCL');
  var sclMask = scl.neq(3).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  
  var cloudProb = image.select('MSK_CLDPRB');
  var probMask = cloudProb.lt(CLOUD_PROB_THRESHOLD);
  
  var aot = image.select('AOT');
  var aotMask = aot.lt(AOT_THRESHOLD * 1000);
  
  var combinedMask = qa60Mask.and(sclMask).and(probMask).and(aotMask);
  
  // Scale and rename Sentinel-2 bands to match Landsat naming
  // CRITICAL: Add clipping to ensure valid reflectance range
  var scaled = image.select(['B1', 'B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
    .multiply(0.0001)
    .clamp(0.0, 1.0)
    .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
  
  return image.addBands(scaled, null, true).updateMask(combinedMask);
}
