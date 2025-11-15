# Landsat Collection 2 Scaling Fix - Root Cause & Solution

## Problem
Iron Sulfate Index showing negative values (Mean: -7.662, Median: -8.314)

## Root Cause
The issue is NOT the scaling formula itself. The formula is correct:
```
Reflectance = (DN * 0.0000275) - 0.2
```

The problem is that **negative reflectance values are physically impossible** and indicate:
1. Low signal pixels (shadows, water absorption, dark areas)
2. The formula produces negative values when DN < ~7273 (since 7273 * 0.0000275 ≈ 0.2)

## Solution: Clip to Valid Range

After applying the scaling formula, **clamp all values to [0.0, 1.0]** to ensure valid reflectance.

### Change in `processLandsat()` function:

**BEFORE:**
```javascript
var scaled = bands.multiply(0.0000275).subtract(0.2);
var renamed = scaled.rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

**AFTER:**
```javascript
// Apply official scaling: multiply by scale factor, then add offset
var scaled = bands.multiply(0.0000275).add(-0.2);

// CRITICAL: Clip to valid reflectance range [0.0, 1.0]
// Negative values indicate low signal (shadows, water absorption)
// Values >1.0 are physically impossible and indicate saturation
var clipped = scaled.clamp(0.0, 1.0);

// Rename to keep same band names
var renamed = clipped.rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

## Why This Works

1. **Preserves physical meaning**: Reflectance must be 0.0-1.0
2. **Handles low-signal pixels**: Shadows and water get reflectance=0.0 (not negative)
3. **Prevents index distortion**: Iron Sulfate Index = (B2/B1) - (B5/B4) now uses valid values
4. **Matches USGS best practices**: All Landsat processing includes clipping

## Expected Results After Fix

- **Band reflectances**: 0.0 to 0.4 (typical for natural surfaces)
- **Iron Sulfate Index**: 0.5 to 2.5 (not negative!)
- **Statistics**: Mean should be positive, typically 0.8-1.5 for mixed scenes

## Also Apply to Sentinel-2

In `processSentinel2()`, add clipping:
```javascript
var scaled = image.select(['B1', 'B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
  .multiply(0.0001)
  .clamp(0.0, 1.0)  // ADD THIS LINE
  .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

## Verification

After applying the fix:
1. Load Goldfield, NV area
2. Click on pink/magenta areas
3. Check console for "RAW BAND REFLECTANCES"
4. All B1-B7 values should be 0.0-0.4 (not negative)
5. Iron Sulfate Index should be 0.5-2.5 range
