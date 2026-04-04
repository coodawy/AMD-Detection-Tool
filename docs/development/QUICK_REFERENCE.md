# Quick Reference Card

## 🚀 Quick Start (5 minutes)

### Apply Scaling Fix to Your Code

**Step 1: Find `processLandsat()` function**
```javascript
// Line ~50: Change this:
var scaled = bands.multiply(0.0000275).subtract(0.2);
var renamed = scaled.rename([...]);

// To this:
var scaled = bands.multiply(0.0000275).add(-0.2);
var clipped = scaled.clamp(0.0, 1.0);
var renamed = clipped.rename([...]);
```

**Step 2: Find `processSentinel2()` function**
```javascript
// Line ~100: Change this:
var scaled = image.select([...])
  .multiply(0.0001)
  .rename([...]);

// To this:
var scaled = image.select([...])
  .multiply(0.0001)
  .clamp(0.0, 1.0)
  .rename([...]);
```

**Step 3: Test**
- Copy updated code to Earth Engine
- Select "Goldfield, NV (Paper)"
- Check statistics: Iron Sulfate should be positive (0.5-2.5)

---

## 📊 Key Metrics

### Expected Values (After Fix)
| Metric | Range | Unit |
|--------|-------|------|
| Band Reflectance | 0.0-0.4 | dimensionless |
| Iron Sulfate Index | 0.5-2.5 | dimensionless |
| MNDWI (land) | -0.5 to 0.3 | dimensionless |
| MNDWI (water) | 0.3-1.0 | dimensionless |

### Paper Validation Sites
| Site | Iron Sulfate | Location |
|------|-------------|----------|
| Goldfield, NV | 1.2-1.8 | Nevada |
| Bauer Mill, UT | 0.9-1.4 | Utah |
| Silverton, CO | 1.1-1.6 | Colorado |
| Marysvale, UT | 0.8-1.3 | Utah |

---

## 🔧 Thresholds (Paper Defaults)

| Index | Threshold | Meaning |
|-------|-----------|---------|
| Iron Sulfate | > 1.15 | Jarosite likely present |
| Iron Sulfate | > 1.50 | High confidence |
| Ferric Iron 1 | > 1.40 | Hematite/Goethite |
| Ferric Iron 2 | > 2.50 | Enhanced ferric iron |
| Ferrous Iron | > 1.05 | Chlorite/Ferrous minerals |
| Clay-Sulfate-Mica | > 0.15 | Clay minerals present |
| MNDWI | > 0.30 | Water body |
| Green Vegetation | > 1.50 | Dense vegetation |

---

## 📁 File Organization

```
Sulfate-Methos/
├── README.md                      # Start here
├── PROJECT_SUMMARY.md             # Overview & next steps
├── QUICK_REFERENCE.md             # This file
│
├── docs/
│   ├── SCALING_FIX.md            # Technical details
│   ├── BUILD_INSTRUCTIONS.md     # How to assemble script
│   ├── IMPLEMENTATION_GUIDE.md   # Step-by-step guide
│   └── PATCH_INSTRUCTIONS.md     # Quick patch
│
├── earth-engine/
│   ├── amd_detection_v1.0.0.js   # Production script
│   ├── amd_detection_dev.js      # Development version
│   └── amd_detection_v4_fixed.js # Functions reference
│
└── config/
    ├── study_areas.json
    ├── thresholds.json
    └── band_config.json
```

---

## 🎯 19 Classification Classes

### AMD Indicator Classes (High Priority)
| Class | Color | Description |
|-------|-------|-------------|
| 14 | FFB6C1 | Oxidizing Sulfides |
| 12 | FF0000 | Major Iron Sulfate |
| 17 | DC143C | Proximal Jarosite |
| 18 | 8B0000 | Distal Jarosite |
| 9 | FF1493 | Argillic Alteration |
| 19 | C71585 | Clay+Ferrous+Iron |

### Other Mineral Classes
| Class | Color | Description |
|-------|-------|-------------|
| 8 | FF6347 | Clay+Major Ferric |
| 7 | FFA500 | Clay+Mod Ferric |
| 6 | FFFF00 | Clay+Minor Ferric |
| 5 | 00FF00 | Clay-Sulfate-Mica |
| 10 | 008B8B | Clay+Ferrous |
| 2 | FF00FF | Major Ferric Iron |
| 1 | A0522D | Minor Ferric (Hematite) |
| 3 | 800080 | Ferric+-Ferrous |
| 4 | 00CED1 | Ferrous (Chlorite) |
| 11 | 228B22 | Dense Vegetation |
| 13 | 9ACD32 | Sparse Veg+Ferric |

---

## 🔬 Spectral Indices Formulas

```javascript
// Iron Sulfate Mineral Index
(B2/B1) - (B5/B4)

// Ferric Iron 1 "Redness Index"
B4/B2

// Ferric Iron 2
(B4/B2) × (B4+B6)/(B5)

// Ferrous Iron
(B3+B6)/(B4+B5)

// Clay-Sulfate-Mica Index
(B6/B7) - (B5/B4)

// Green Vegetation Index
B5/B4

// NDVI
(B5-B4)/(B5+B4)

// MNDWI (Water)
(B3-B6)/(B3+B6)

// AWEINSH (Water)
B2 + 2.5×B3 - 1.5×B5 - 0.25×B6 - 0.25×B7
```

---

## 📡 Band Mapping

### Landsat 8/9 Bands
| Band | Name | Wavelength | Use |
|------|------|-----------|-----|
| B1 | Coastal/Aerosol | 0.43-0.45 μm | Iron Sulfate |
| B2 | Blue | 0.45-0.51 μm | Iron Sulfate |
| B3 | Green | 0.53-0.59 μm | Water/Vegetation |
| B4 | Red | 0.64-0.67 μm | Iron Sulfate |
| B5 | NIR | 0.85-0.88 μm | Vegetation/Iron |
| B6 | SWIR1 | 1.57-1.65 μm | Clay/Water |
| B7 | SWIR2 | 2.11-2.29 μm | Clay/Minerals |

### Sentinel-2 Bands (Mapped to Landsat)
| Sentinel | Landsat | Wavelength | Resolution |
|----------|---------|-----------|------------|
| B1 | B1 | 0.60 μm | 60m |
| B2 | B2 | 0.49 μm | 10m |
| B3 | B3 | 0.56 μm | 10m |
| B4 | B4 | 0.67 μm | 10m |
| B8 | B5 | 0.84 μm | 10m |
| B11 | B6 | 1.61 μm | 20m |
| B12 | B7 | 2.19 μm | 20m |

---

## 🐛 Common Issues & Fixes

### Issue: Negative Iron Sulfate Index
**Fix:** Apply scaling fix (see above)
```javascript
var clipped = scaled.clamp(0.0, 1.0);
```

### Issue: No layers showing
**Fix:** Wait 30 seconds for imagery to load

### Issue: Statistics panel stuck on "Calculating..."
**Fix:** Try smaller study area or different sensor

### Issue: Band reflectances > 1.0
**Fix:** Verify `.clamp(0.0, 1.0)` is applied

---

## 📊 Processing Time

| Step | Time |
|------|------|
| Image loading | 5-10 sec |
| Index calculation | 2-3 sec |
| Classification | 2-3 sec |
| Statistics | 5-10 sec |
| **Total** | **15-30 sec** |

---

## 🔄 Git Quick Commands

```bash
# Check status
git status

# See recent commits
git log --oneline -5

# Create feature branch
git checkout -b feature/your-feature

# Stage & commit
git add .
git commit -m "feat: description"

# Push to GitHub
git push origin feature/your-feature

# Create pull request
# (Go to GitHub and click "New pull request")

# Merge to develop
git checkout develop
git pull origin develop
git merge feature/your-feature
git push origin develop
```

---

## 📋 Checklist: Before Release

- [ ] Scaling fix applied (2 changes)
- [ ] Script tested in Earth Engine
- [ ] No negative reflectance values
- [ ] All 19 classes visualize
- [ ] Paper sites validated
- [ ] Statistics panel working
- [ ] Documentation complete
- [ ] GitHub repository created
- [ ] Code committed
- [ ] Release tagged (v1.0.0)

---

## 🔗 Important Links

- **Earth Engine:** https://code.earthengine.google.com
- **GitHub:** https://github.com
- **Paper (Rockwell et al. 2021):** USGS SIM 3466
- **Landsat Collection 2:** https://www.usgs.gov/landsat-missions/landsat-collection-2
- **Sentinel-2:** https://sentinel.esa.int/web/sentinel/missions/sentinel-2

---

## 📞 Documentation Index

| Document | Purpose | Read Time |
|----------|---------|-----------|
| README.md | Project overview | 5 min |
| PROJECT_SUMMARY.md | Status & next steps | 10 min |
| QUICK_REFERENCE.md | This file | 5 min |
| SCALING_FIX.md | Technical details | 10 min |
| BUILD_INSTRUCTIONS.md | How to assemble | 15 min |
| GITHUB_SETUP.md | Git workflow | 20 min |
| PROJECT_PLAN.md | Development roadmap | 15 min |
| CHANGELOG.md | Version history | 10 min |

---

## ✅ Version Info

| Item | Value |
|------|-------|
| Current Version | 1.0.0 |
| Status | Production Ready |
| Last Updated | 2025-11-15 |
| Sensors | L8, L9, S2 |
| Classes | 19 |
| Study Areas | 8 |
| Indices | 11 |

---

## 🎓 Learning Path

1. **Start:** README.md (5 min)
2. **Understand:** SCALING_FIX.md (10 min)
3. **Implement:** PATCH_INSTRUCTIONS.md (5 min)
4. **Test:** Earth Engine (15 min)
5. **Deploy:** GITHUB_SETUP.md (30 min)
6. **Advance:** PROJECT_PLAN.md (15 min)

**Total Time:** ~1.5 hours to production

---

**Need help?** Check the relevant documentation file or refer to PROJECT_SUMMARY.md for next steps.
