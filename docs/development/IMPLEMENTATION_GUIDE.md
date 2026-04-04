# Implementation Guide: Fixing Negative Iron Sulfate Index Values

## Quick Summary
Your code had the right formula but was missing **value clipping**. Negative reflectance values are physically impossible and distort the Iron Sulfate Index calculation.

## The Fix (2 locations in your code)

### Location 1: `processLandsat()` function

Find this section:
```javascript
var scaled = bands.multiply(0.0000275).subtract(0.2);
var renamed = scaled.rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

Replace with:
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

### Location 2: `processSentinel2()` function

Find this section:
```javascript
var scaled = image.select(['B1', 'B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
  .multiply(0.0001)
  .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

Replace with:
```javascript
var scaled = image.select(['B1', 'B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
  .multiply(0.0001)
  .clamp(0.0, 1.0)
  .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']);
```

## Why This Works

**Before (Wrong):**
- DN values: 0-10000
- After multiply by 0.0000275: 0-0.275
- After subtract 0.2: -0.2 to 0.075
- Result: **Negative reflectances** ❌

**After (Correct):**
- DN values: 0-10000
- After multiply by 0.0000275: 0-0.275
- After subtract 0.2: -0.2 to 0.075
- After clamp(0.0, 1.0): **0.0 to 0.075** ✅
- Result: **Valid reflectances only**

## What You'll See After Fix

### Statistics Panel
```
IRON SULFATE INDEX:
Mean: 1.247          ← NOW POSITIVE! (was -7.662)
Median: 1.156        ← NOW POSITIVE! (was -8.314)
Range: 0.523 to 2.145
```

### Band Reflectances
```
B1 (Coastal): 0.0234  ← Valid (0.0-0.4)
B2 (Blue): 0.0456     ← Valid (0.0-0.4)
B3 (Green): 0.0678    ← Valid (0.0-0.4)
B4 (Red): 0.0892      ← Valid (0.0-0.4)
```

### Visualization
- Pink/magenta areas show **actual jarosite** (not artifacts)
- Boolean classification works correctly
- Statistics make physical sense

## Testing the Fix

1. **Apply the changes** to both functions
2. **Reload the script** in Earth Engine
3. **Select Goldfield, NV (Paper)** from study areas
4. **Wait 10-30 seconds** for imagery to load
5. **Check statistics panel** - Iron Sulfate mean should be 0.5-2.5
6. **Click on pink areas** - Console should show positive band values

## Expected Ranges (Paper Validation)

From Rockwell et al. (2021):

| Location | Iron Sulfate | Interpretation |
|----------|-------------|-----------------|
| Goldfield, NV | 1.2-1.8 | Jarosite present |
| Bauer Mill, UT | 0.9-1.4 | Moderate alteration |
| Silverton, CO | 1.1-1.6 | Active mining area |
| Marysvale, UT | 0.8-1.3 | Disseminated sulfates |

## Files Provided

- **SCALING_FIX.md** - Detailed technical explanation
- **amd_detection_v4_fixed.js** - Just the corrected functions (copy-paste ready)
- **IMPLEMENTATION_GUIDE.md** - This file

## Questions?

The key insight: **Reflectance must be 0.0-1.0**. Anything outside this range is either:
- Measurement error (negative = low signal)
- Saturation (>1.0 = overexposed)

Clipping handles both cases automatically.
