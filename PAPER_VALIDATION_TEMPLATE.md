# Paper Validation Template - Rockwell et al. (2021)

## Instructions
1. Load each site in GEE with Landsat 8, median compositing
2. Check console for statistics output
3. Fill in your results below
4. Compare with expected values

---

## Site 1: Goldfield, NV (Paper Figure 6, page 22)

### Expected Results:
- **AMD Classes:** 9, 12, 14, 17, 18
- **Total AMD Area:** 10-25%
- **Description:** High-sulfidation deposits, abundant jarosite
- **Dominant Minerals:** Jarosite, alunite, kaolinite

### Your Results:
```
Date Tested: ___________
Sensor: Landsat 8
Compositing: median

Class Distribution:
- Class 1 (Minor Ferric): _____%
- Class 4 (Ferrous): _____%
- Class 5 (Clay-Sulfate-Mica): _____%
- Class 6 (Clay+Minor Ferric): _____%
- Class 7 (Clay+Mod Ferric): _____%
- Class 8 (Clay+Major Ferric): _____%
- Class 9 (Argillic Alteration): _____%  ← Expected
- Class 10 (Clay+Ferrous): _____%
- Class 11 (Dense Vegetation): _____%
- Class 12 (Major Iron Sulfate): _____%  ← Expected
- Class 13 (Sparse Veg+Ferric): _____%
- Class 14 (Oxidizing Sulfides): _____%  ← Expected
- Class 17 (Proximal Jarosite): _____%  ← Expected
- Class 18 (Distal Jarosite): _____%  ← Expected
- Class 19 (Clay+Ferrous+Iron): _____%
- Class 20 (Contaminated Water): _____%
- Class 21 (Clean Water): _____%

Total AMD Area (9+12+14+17+18+19): _____%

Index Ranges:
- Iron Sulfate: _____ to _____
- Ferric Iron 1: _____ to _____
- Ferric Iron 2: _____ to _____
- Clay-Sulfate-Mica: _____ to _____

Images Used: _____
Date Range: _____ to _____
```

### Validation:
- [ ] Found 5/5 expected classes (9, 12, 14, 17, 18)
- [ ] Total AMD area 10-25%
- [ ] Iron Sulfate max > 2.0
- [ ] Spatial clustering reasonable

**Match Quality:** ☐ Excellent ☐ Good ☐ Poor

**Notes:**
_____________________________________________
_____________________________________________

---

## Site 2: Bauer Mill, UT (Paper Figure 9, page 27)

### Expected Results:
- **AMD Classes:** 14, 17
- **Total AMD Area:** 15-30%
- **Description:** Weathered pyrite near mill, proximal jarosite zones
- **Dominant Minerals:** Jarosite, goethite

### Your Results:
```
Date Tested: ___________
Sensor: Landsat 8
Compositing: median

Class Distribution:
- Class 1 (Minor Ferric): _____%
- Class 4 (Ferrous): _____%
- Class 5 (Clay-Sulfate-Mica): _____%
- Class 6 (Clay+Minor Ferric): _____%
- Class 7 (Clay+Mod Ferric): _____%
- Class 8 (Clay+Major Ferric): _____%
- Class 9 (Argillic Alteration): _____%
- Class 10 (Clay+Ferrous): _____%
- Class 11 (Dense Vegetation): _____%
- Class 12 (Major Iron Sulfate): _____%
- Class 13 (Sparse Veg+Ferric): _____%
- Class 14 (Oxidizing Sulfides): _____%  ← Expected
- Class 17 (Proximal Jarosite): _____%  ← Expected
- Class 18 (Distal Jarosite): _____%
- Class 19 (Clay+Ferrous+Iron): _____%
- Class 20 (Contaminated Water): _____%
- Class 21 (Clean Water): _____%

Total AMD Area (9+12+14+17+18+19): _____%

Index Ranges:
- Iron Sulfate: _____ to _____
- Ferric Iron 1: _____ to _____
- Ferric Iron 2: _____ to _____
- Clay-Sulfate-Mica: _____ to _____

Images Used: _____
Date Range: _____ to _____
```

### Validation:
- [ ] Found 2/2 expected classes (14, 17)
- [ ] Total AMD area 15-30%
- [ ] Iron Sulfate max > 1.8
- [ ] Spatial clustering reasonable

**Match Quality:** ☐ Excellent ☐ Good ☐ Poor

**Notes:**
_____________________________________________
_____________________________________________

---

## Site 3: Silverton, CO (Paper Map Sheet)

### Expected Results:
- **AMD Classes:** 8, 9, 17
- **Total AMD Area:** 5-15%
- **Description:** Phyllic alteration with jarosite zones
- **Dominant Minerals:** Jarosite, kaolinite, illite

### Your Results:
```
Date Tested: ___________
Sensor: Landsat 8
Compositing: median

Class Distribution:
- Class 1 (Minor Ferric): _____%
- Class 4 (Ferrous): _____%
- Class 5 (Clay-Sulfate-Mica): _____%
- Class 6 (Clay+Minor Ferric): _____%
- Class 7 (Clay+Mod Ferric): _____%
- Class 8 (Clay+Major Ferric): _____%  ← Expected
- Class 9 (Argillic Alteration): _____%  ← Expected
- Class 10 (Clay+Ferrous): _____%
- Class 11 (Dense Vegetation): _____%
- Class 12 (Major Iron Sulfate): _____%
- Class 13 (Sparse Veg+Ferric): _____%
- Class 14 (Oxidizing Sulfides): _____%
- Class 17 (Proximal Jarosite): _____%  ← Expected
- Class 18 (Distal Jarosite): _____%
- Class 19 (Clay+Ferrous+Iron): _____%
- Class 20 (Contaminated Water): _____%
- Class 21 (Clean Water): _____%

Total AMD Area (9+12+14+17+18+19): _____%

Index Ranges:
- Iron Sulfate: _____ to _____
- Ferric Iron 1: _____ to _____
- Ferric Iron 2: _____ to _____
- Clay-Sulfate-Mica: _____ to _____

Images Used: _____
Date Range: _____ to _____
```

### Validation:
- [ ] Found 3/3 expected classes (8, 9, 17)
- [ ] Total AMD area 5-15%
- [ ] Iron Sulfate max > 1.5
- [ ] Spatial clustering reasonable

**Match Quality:** ☐ Excellent ☐ Good ☐ Poor

**Notes:**
_____________________________________________
_____________________________________________

---

## Site 4: Marysvale, UT (Paper Reference Site)

### Expected Results:
- **AMD Classes:** 12, 14, 17
- **Total AMD Area:** 8-20%
- **Description:** Alunite-jarosite alteration
- **Dominant Minerals:** Jarosite, alunite, kaolinite

### Your Results:
```
Date Tested: ___________
Sensor: Landsat 8
Compositing: median

Class Distribution:
- Class 1 (Minor Ferric): _____%
- Class 4 (Ferrous): _____%
- Class 5 (Clay-Sulfate-Mica): _____%
- Class 6 (Clay+Minor Ferric): _____%
- Class 7 (Clay+Mod Ferric): _____%
- Class 8 (Clay+Major Ferric): _____%
- Class 9 (Argillic Alteration): _____%
- Class 10 (Clay+Ferrous): _____%
- Class 11 (Dense Vegetation): _____%
- Class 12 (Major Iron Sulfate): _____%  ← Expected
- Class 13 (Sparse Veg+Ferric): _____%
- Class 14 (Oxidizing Sulfides): _____%  ← Expected
- Class 17 (Proximal Jarosite): _____%  ← Expected
- Class 18 (Distal Jarosite): _____%
- Class 19 (Clay+Ferrous+Iron): _____%
- Class 20 (Contaminated Water): _____%
- Class 21 (Clean Water): _____%

Total AMD Area (9+12+14+17+18+19): _____%

Index Ranges:
- Iron Sulfate: _____ to _____
- Ferric Iron 1: _____ to _____
- Ferric Iron 2: _____ to _____
- Clay-Sulfate-Mica: _____ to _____

Images Used: _____
Date Range: _____ to _____
```

### Validation:
- [ ] Found 3/3 expected classes (12, 14, 17)
- [ ] Total AMD area 8-20%
- [ ] Iron Sulfate max > 1.8
- [ ] Spatial clustering reasonable

**Match Quality:** ☐ Excellent ☐ Good ☐ Poor

**Notes:**
_____________________________________________
_____________________________________________

---

## Overall Validation Summary

### Methodology Validation:
- [ ] All 4 sites show expected AMD classes
- [ ] AMD percentages within expected ranges
- [ ] Index ranges reasonable (Iron: -2 to 5)
- [ ] No major warnings in console

### Match Quality:
- Goldfield: ☐ Excellent ☐ Good ☐ Poor
- Bauer Mill: ☐ Excellent ☐ Good ☐ Poor
- Silverton: ☐ Excellent ☐ Poor
- Marysvale: ☐ Excellent ☐ Good ☐ Poor

### Issues Found:
_____________________________________________
_____________________________________________
_____________________________________________

### Threshold Adjustments Made:
_____________________________________________
_____________________________________________
_____________________________________________

---

## Interpretation Guide

### Match Quality Criteria:

**Excellent:**
- All expected classes found with >5% coverage
- Total AMD area within expected range
- Index ranges reasonable
- No major warnings

**Good:**
- 70%+ of expected classes found
- AMD area within ±5% of expected range
- Minor warnings only

**Poor:**
- <70% of expected classes found
- AMD area significantly different
- Major warnings or errors

### Common Issues:

**Issue: AMD area too high (>50%)**
- **Cause:** Thresholds too lenient
- **Fix:** Increase Iron threshold (1.15 → 1.5)

**Issue: AMD area too low (<0.1%)**
- **Cause:** Thresholds too strict
- **Fix:** Decrease Iron threshold (1.15 → 1.0)

**Issue: Missing expected classes**
- **Cause:** Threshold mismatch or preprocessing error
- **Fix:** Check index ranges, adjust Ferric/Clay thresholds

**Issue: Index values out of range**
- **Cause:** Preprocessing error (scaling, cloud masking)
- **Fix:** Check Landsat scaling formula, cloud mask

---

## Next Steps After Validation

### If All Sites Match (Excellent/Good):
✅ **Your methodology is validated!**
- Proceed to your Ohio/Iraq study sites
- Use same thresholds
- Document any site-specific adjustments

### If Some Sites Don't Match:
⚠️ **Troubleshooting needed:**
1. Check console for warnings
2. Review index value ranges
3. Adjust thresholds incrementally
4. Re-test on paper sites
5. Document changes

### For Your Study Sites:
After validation, test on:
- Piedmont Lake, OH
- Clendening Lake, OH
- Atwood Lake, OH
- Ganau Area, Iraq
- Dukan Lake, Iraq
- Delaware, OH (clean reference)

Expected AMD ranges:
- Ohio lakes: 1-5%
- Iraq sites: 5-15%
- Delaware: <1% (should be clean)

---

**Template Version:** 1.0  
**Date Created:** 2025-01-22  
**For Use With:** AMD Detection Tool v1.1.0
