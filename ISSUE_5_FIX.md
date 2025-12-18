# ISSUE #5 FIX - Water Classification Logic

## 🎯 Problem Statement

**Original Issue:** Contaminated water was being classified as AMD mineral classes (12, 14, 17, 18, 19) instead of as **Class 20: Contaminated Water (Sulfur)**.

**User Request:** "for problem 5 the water thing i need it to not be classified as AMD but as contaminated water (Sulfur)"

---

## 🔍 Root Cause Analysis

### What Was Wrong:

**Lines 410-412 (OLD CODE):**
```javascript
var amdLandMask = settings.useAdvancedWaterDetection ?
  standardLandMask.or(waterMasks.contaminated) :  // ❌ ALLOWED contaminated water in AMD classes!
  standardLandMask.or(extremeAMD.and(waterMasks.all));
```

**Problem:**
- When `useAdvancedWaterDetection = true`, contaminated water was **included** in `amdLandMask`
- This allowed contaminated water pixels to be classified as Classes 12-19 (AMD minerals)
- The water classification (Class 20) came **after** AMD classification, but AMD mask already included water!

**Result:** Contaminated water was classified as iron sulfate minerals (e.g., Class 14: Oxidizing Sulfides) instead of Class 20.

---

## ✅ Solution Implemented

### Fixed Code:

**Lines 409-411 (NEW CODE):**
```javascript
// AMD land mask: EXCLUDE ALL WATER (contaminated water will be Class 20, not AMD)
// This ensures contaminated water is classified as "Contaminated Water" not as iron sulfate
var amdLandMask = standardLandMask;
```

### What Changed:

1. **Removed contaminated water from AMD land mask**
   - `amdLandMask` now **only** includes land pixels (no water at all)
   - Contaminated water pixels are **excluded** from AMD classification

2. **Classification priority ensures correct assignment**
   - AMD classes (12-19) use `amdLandMask` → excludes all water
   - Water classes (20, 21) override everything at the end
   - Result: Contaminated water → Class 20 ✅

---

## 🧪 How It Works Now

### Classification Flow:

```
1. Detect water pixels (MNDWI + AWEInsh)
   ├─ Clean water: Iron < 1.8 OR turbidity < 1.3
   └─ Contaminated water: Iron > 1.8 AND turbidity > 1.3

2. Create land mask
   standardLandMask = NOT water AND NOT dark AND NOT bright

3. Create AMD land mask
   amdLandMask = standardLandMask  (NO WATER INCLUDED!)

4. Classify pixels:
   ├─ Classes 1-11: Non-iron sulfate (use standardLandMask)
   ├─ Classes 12-19: Iron sulfate AMD (use amdLandMask → LAND ONLY!)
   ├─ Class 20: Contaminated water (overrides everything)
   └─ Class 21: Clean water (overrides everything)
```

### Key Distinction:

| Type | Location | Classification | Description |
|------|----------|----------------|-------------|
| **Iron sulfate minerals** | Land | Classes 12-19 | Solid minerals (jarosite, etc.) |
| **Sulfur contamination** | Water | Class 20 | Dissolved/suspended in water |

---

## 📝 Additional Changes

### 1. Updated Comments:
```javascript
// NOTE: This will be classified as Class 20 (Contaminated Water), NOT as AMD classes
// This distinguishes sulfur-contaminated water from land-based iron sulfate minerals
```

### 2. Updated Legend:
```javascript
{color: '0000FF', label: '20: Contaminated Water (Sulfur)'}
```

### 3. Updated Click Handler:
```javascript
classification = 'CLASS 20: CONTAMINATED WATER (SULFUR)';
napLevel = 'EXTREME (Sulfur contamination in water)';
interpretation = 
  'SULFUR-CONTAMINATED WATER DETECTED!\n\n' +
  'Classification: Class 20 (NOT land-based AMD minerals)\n' +
  'This is dissolved/suspended sulfur compounds in water,\n' +
  'distinct from solid iron sulfate minerals on land.\n\n'
```

### 4. Updated UI Checkbox:
```javascript
label: 'Detect Contaminated Water (Sulfur in water → Class 20)'
```

---

## 🎯 Expected Behavior

### Before Fix:
```
High iron in water → amdLandMask includes it → Class 14 (Oxidizing Sulfides) ❌
```

### After Fix:
```
High iron in water → excluded from amdLandMask → Class 20 (Contaminated Water) ✅
```

### Test Cases:

| Scenario | Iron Index | Water Mask | Turbidity | Expected Class |
|----------|-----------|------------|-----------|----------------|
| Clean lake | 0.5 | Yes | 1.0 | **21** (Clean Water) |
| Contaminated stream | 2.5 | Yes | 1.5 | **20** (Contaminated Water - Sulfur) |
| Land-based AMD | 2.5 | No | N/A | **12, 14, 17, 18, or 19** (AMD minerals) |
| Dry jarosite deposit | 3.0 | No | N/A | **17** (Proximal Jarosite) |

---

## 🔬 Scientific Rationale

### Why This Distinction Matters:

1. **Different environmental processes:**
   - **Land AMD:** Solid mineral deposits (jarosite, copiapite, etc.)
   - **Water contamination:** Dissolved iron sulfates + precipitates

2. **Different remediation strategies:**
   - **Land AMD:** Stabilization, capping, revegetation
   - **Water contamination:** pH adjustment, precipitation, filtration

3. **Different monitoring priorities:**
   - **Land AMD:** Source identification, extent mapping
   - **Water contamination:** Immediate aquatic toxicity concern

4. **Spectral signatures:**
   - **Land AMD:** Solid mineral reflectance
   - **Water contamination:** Water + suspended particles + dissolved ions

---

## ✅ Validation Checklist

- [x] `amdLandMask` excludes all water pixels
- [x] Contaminated water uses Class 20, not Classes 12-19
- [x] Clean water uses Class 21
- [x] Legend updated with "(Sulfur)" label
- [x] Click handler shows correct interpretation
- [x] UI checkbox clarifies Class 20 assignment
- [x] Comments explain the distinction

---

## 📊 Impact Summary

| Component | Change | Impact |
|-----------|--------|--------|
| **Classification logic** | Fixed | ✅ Contaminated water → Class 20 |
| **AMD land mask** | Simplified | ✅ No water included |
| **Legend** | Updated | ✅ Shows "(Sulfur)" label |
| **Click handler** | Enhanced | ✅ Clear interpretation |
| **UI** | Clarified | ✅ Shows "→ Class 20" |
| **Comments** | Added | ✅ Explains distinction |

---

## 🚀 Testing Instructions

1. **Enable contaminated water detection:**
   - Check "Detect Contaminated Water (Sulfur in water → Class 20)"
   - Set Iron threshold to 1.8

2. **Test with contaminated stream:**
   - Select study area with AMD drainage
   - Look for orange/red water
   - Click pixel → should show **Class 20**
   - Console should say "SULFUR-CONTAMINATED WATER DETECTED!"

3. **Test with land-based AMD:**
   - Click on dry jarosite deposit
   - Should show **Class 12, 14, 17, 18, or 19**
   - Should NOT be Class 20

4. **Test with clean water:**
   - Click on normal lake/river
   - Should show **Class 21** (Clean Water)

---

## 📚 Related Documentation

- **Paper:** Rockwell et al. (2021) - Classes 12-19 are land-based minerals
- **Enhancement:** Class 20 is your custom water contamination class
- **Distinction:** Land minerals vs. water contamination

---

**Fix Date:** 2025-11-18  
**Issue:** #5 - Water classification logic  
**Status:** ✅ RESOLVED  
**Commit Message:**
```
fix: Contaminated water now classified as Class 20, not AMD minerals

- Remove contaminated water from amdLandMask
- Ensure Class 20 is for sulfur in water, not land-based AMD
- Update legend to show "Contaminated Water (Sulfur)"
- Update click handler interpretation
- Clarify UI checkbox label

Fixes #5
```
