# Quick Patch Instructions for Main Code

## Location 1: Replace `processLandsat()` function

**Find this section in your code:**
```javascript
function processLandsat(image) {
  // Cloud masking FIRST
  var qa = image.select('QA_PIXEL');
  var cloudMask = qa.bitwiseAnd(1<<3).eq(0)
    .and(qa.bitwiseAnd(1<<4).eq(0))
    .and(qa.bitwiseAnd(1<<2).eq(0));
  
  var masked = image.updateMask(cloudMask);
  
  // CRITICAL FIX: Landsat Collection 2 Level-2 Surface Reflectance scaling
  // Official formula: Reflectance = (DN * 0.0000275) - 0.2
  // But we need to handle it differently to avoid negatives
  
  // Get the raw DN values
  var bands = masked.select('SR_B[1-7]');
  
  // Apply scaling: multiply first, then subtract offset
  var scaled = bands.multiply(0.0000275).subtract(0.2);
  
  // ALTERNATIVE: If still getting negatives, just multiply (no offset)
  // Uncomment this line if still having issues:
  // var scaled = bands.multiply(0.0000275);
  
  // Rename to keep same band names
  var renamed = scaled.rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
  
  return masked.addBands(renamed, null, true);
}
```

**Replace with:**
```javascript
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
  // This CAN produce negative values for low DN, which we clip to 0.0
  
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
```

## Location 2: Update `processSentinel2()` function

**Find this line:**
```javascript
  var scaled = image.select(['B1', 'B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
    .multiply(0.0001)
    .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

**Replace with:**
```javascript
  var scaled = image.select(['B1', 'B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
    .multiply(0.0001)
    .clamp(0.0, 1.0)
    .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

## That's it!

Just those two changes. The key addition is `.clamp(0.0, 1.0)` which ensures all reflectance values stay physically valid.

After patching, reload the script in Earth Engine and test with Goldfield, NV.
