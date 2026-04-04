# 🚀 AMD Detection Tool v1.1.0 - QUICK START GUIDE

## 30-Second Overview

**Problem Solved:** Why do Landsat 8, Landsat 9, and Sentinel-2 look identical?  
**Answer:** Median compositing over 5 years averages out differences!

**New Features:**
- 📊 See image counts & dates
- 🔧 Choose compositing method (median/latest/quality)
- 📅 Filter by date range
- 🔬 3 validation tools (internal/cross-sensor/paper)

---

## 🎯 Quick Test (5 Minutes)

### See Why Sensors Look Identical:

1. **Load Goldfield, NV** (paper validation site)
2. **Sensor:** Landsat 8
3. **Compositing:** median (default)
4. **Look at Console:**
   ```
   📊 Images found: 247
   📅 First image: 2019-01-15
   📅 Last image: 2024-12-10
   ```
5. **Change Compositing to:** latest
6. **Reload** → See different patterns!
7. **Click:** 🛰️ Cross-Sensor Validation
8. **Result:** See quantitative L8 vs S2 comparison

**Expected:** Correlation ~0.85-0.95 (EXCELLENT agreement)

---

## 🔧 New UI Controls

### Compositing Method:
```
median  = Average all images (hides sensor differences)
latest  = Most recent image (shows current conditions)
quality = Best NIR pixels (best for vegetation)
mosaic  = First image on top (see individual scenes)
mean    = Mathematical average (smooth results)
```

**Recommendation:** Use "latest" to see sensor differences!

### Date Range:
```
Start: 2024-06-01
End:   2024-08-31
```
**Use Case:** Compare same summer period across sensors

### Validation Tools:
```
🔬 Internal Validation     → Statistical sanity checks
🛰️ Cross-Sensor Validation → L8 vs S2 agreement
📚 Paper Validation        → Compare to Rockwell et al.
```

---

## 📊 Validation Checklist

### ✅ Step 1: Internal Validation
**Click:** 🔬 Internal Validation

**Check:**
- [ ] AMD area 0.1-50% (not 0% or 100%)
- [ ] Index ranges reasonable (Iron: -2 to 5)
- [ ] Patch sizes >2 pixels (not noisy)

**If FAIL:** Adjust thresholds

---

### ✅ Step 2: Cross-Sensor Validation
**Click:** 🛰️ Cross-Sensor Validation

**Check:**
- [ ] Mean difference <0.5 (GOOD)
- [ ] Correlation >0.7 (GOOD)

**If FAIL:** Check preprocessing (Sentinel-2 resampling)

---

### ✅ Step 3: Paper Validation
**Click:** 📚 Paper Validation

**Check:**
- [ ] Goldfield: 5/5 classes found (EXCELLENT)
- [ ] Bauer Mill: 2/2 classes found (EXCELLENT)
- [ ] Silverton: 3/3 classes found (EXCELLENT)

**If FAIL:** Review methodology (thresholds, masking)

---

## 🎮 Common Workflows

### Workflow 1: Validate Methodology
```
1. Load Goldfield, NV
2. Sensor: Landsat 8, Compositing: median
3. Click: 🔬 Internal Validation → Check passes
4. Click: 📚 Paper Validation → Check EXCELLENT
5. ✅ Methodology validated!
```

### Workflow 2: Compare Sensors
```
1. Load Piedmont Lake, OH
2. Date: 2024-06-01 to 2024-08-31
3. Sensor: Landsat 8 → Note classification
4. Sensor: Sentinel-2 → Compare
5. Click: 🛰️ Cross-Sensor → Check R >0.85
```

### Workflow 3: Seasonal Analysis
```
1. Load Ganau Area, Iraq
2. Winter: 2024-12-01 to 2025-02-28 → Note AMD %
3. Summer: 2024-06-01 to 2024-08-31 → Note AMD %
4. Compare: Summer should show MORE AMD
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "NO IMAGES FOUND" | Clear date filter, use all dates |
| "POOR sensor agreement" | Check Sentinel-2 resampling |
| ">50% classified as AMD" | Increase Iron threshold (1.15→1.5) |
| "Very small patches" | Increase thresholds, use median |

---

## 📈 Expected Results

### Paper Sites:
- **Goldfield, NV:** 10-25% AMD (classes 9,12,14,17,18)
- **Bauer Mill, UT:** 15-30% AMD (classes 14,17)
- **Silverton, CO:** 5-15% AMD (classes 8,9,17)

### Your Sites:
- **Piedmont/Clendening/Atwood:** 1-5% AMD
- **Ganau/Dukan:** 5-15% AMD
- **Delaware:** <1% AMD (clean reference)

---

## 🎯 Key Insights

### Why Median Hides Differences:
- Landsat: 247 images → median = middle value
- Sentinel-2: 623 images → median = middle value
- **Result:** Both converge to same "average"

### Why Landsat 9 = Landsat 8:
- **By design!** Same sensor, same bands
- Only difference: 14-bit vs 12-bit (negligible)

### Why Sentinel-2 Should Match:
- After 30m resampling, spectral signatures align
- SWIR bands are key for AMD detection
- Your resampling is correct!

---

## ✅ Success Criteria

Your tool is working correctly if:
- ✅ Image counts display (not 0)
- ✅ Internal validation passes (no warnings)
- ✅ Cross-sensor R >0.7 (GOOD) or >0.85 (EXCELLENT)
- ✅ Paper validation: 5/5, 2/2, 3/3 classes found
- ✅ "Latest" compositing shows different patterns than "median"

---

## 🚀 Next Steps

1. **Test Now:** Load Goldfield, run all 3 validations
2. **Experiment:** Try different compositing methods
3. **Compare:** Test date filtering (summer only)
4. **Validate:** Run on all paper sites
5. **Research:** Apply to your Ohio/Iraq sites

---

**Version:** 1.1.0 Enhanced  
**Status:** ✅ Ready for Production  
**Documentation:** See V1.1.0_ENHANCEMENTS_SUMMARY.md for details
