# USGS AMD/Iron Sulfate Detection Tool

**Version:** 1.0.0  
**Status:** Active Development  
**Last Updated:** 2025-11-15

## Project Overview

Automated detection and mapping of iron sulfate minerals (jarosite) and acid mine drainage (AMD) indicators using Landsat 8/9 and Sentinel-2 satellite imagery. Based on Rockwell et al. (2021) USGS SIM 3466 methodology.

## Key Features

- ✅ Multi-sensor support (Landsat 8, Landsat 9, Sentinel-2)
- ✅ Spectral indices calculation (Iron Sulfate, Ferric Iron, Clay-Sulfate-Mica, etc.)
- ✅ Boolean classification (19 material classes)
- ✅ Contaminated water detection
- ✅ Real-time statistics and diagnostics
- ✅ Interactive map visualization with legend
- ✅ Paper validation sites included

## Project Structure

```
Sulfate-Methos/
├── README.md                          # This file
├── CHANGELOG.md                       # Version history & changes
├── PROJECT_PLAN.md                    # Development roadmap
├── GITHUB_SETUP.md                    # Git configuration guide
│
├── docs/
│   ├── ARCHITECTURE.md                # System design & data flow
│   ├── SCALING_FIX.md                 # Technical fixes documentation
│   ├── IMPLEMENTATION_GUIDE.md        # Step-by-step implementation
│   └── API_REFERENCE.md               # Function documentation
│
├── earth-engine/
│   ├── amd_detection_v1.0.0.js        # Main GEE script (production)
│   ├── amd_detection_dev.js           # Development version
│   └── test_cases.js                  # Unit tests for GEE
│
├── python/
│   ├── requirements.txt               # Python dependencies
│   ├── amd_detection.py               # Core Python module
│   ├── collab_notebook.ipynb          # Google Colab notebook
│   └── tests/
│       └── test_indices.py            # Python unit tests
│
├── web/
│   ├── index.html                     # Web interface (future)
│   ├── app.js                         # Frontend logic (future)
│   └── styles.css                     # Styling (future)
│
└── config/
    ├── study_areas.json               # Study area definitions
    ├── thresholds.json                # Default threshold values
    └── band_config.json               # Sensor band mappings
```

## Quick Start

### For Google Earth Engine
1. Copy `earth-engine/amd_detection_v1.0.0.js`
2. Paste into Earth Engine Code Editor
3. Select study area from dropdown
4. Wait for imagery to load (10-30 seconds)
5. Click on colored areas for spectral analysis

### For Python (Future)
```bash
pip install -r python/requirements.txt
jupyter notebook python/collab_notebook.ipynb
```

## Methodology

Based on **Rockwell et al. (2021) - USGS SIM 3466**:
- Iron Sulfate Index = (B2/B1) - (B5/B4)
- Ferric Iron 1 = B4/B2
- Ferric Iron 2 = (B4/B2) × (B4+B6)/(B5)
- Clay-Sulfate-Mica = (B6/B7) - (B5/B4)

**Thresholds:**
- Iron Sulfate > 1.15 = Jarosite likely present
- Iron Sulfate > 1.50 = High confidence

## Study Areas

- **Original Sites:** Piedmont Lake OH, Clendening Lake OH, Genau Iraq, Delaware OH
- **Paper Validation:** Goldfield NV, Bauer Mill UT, Silverton CO, Marysvale UT

## Recent Changes (v1.0.0)

- ✅ Fixed negative reflectance values with `.clamp(0.0, 1.0)`
- ✅ Added Sentinel-2 support with proper scaling
- ✅ Implemented contaminated water detection
- ✅ Enhanced water masking (MNDWI + AWEInsh)
- ✅ Complete 19-class Boolean classification

## Development Roadmap

### Phase 1: GEE Optimization (Current)
- [x] Core algorithm implementation
- [x] Multi-sensor support
- [x] Scaling fixes
- [ ] Performance optimization
- [ ] Additional validation sites

### Phase 2: Python Implementation
- [ ] Core module development
- [ ] Google Colab notebook
- [ ] Unit tests
- [ ] Batch processing capability

### Phase 3: Web Application
- [ ] Interactive web interface
- [ ] Real-time processing
- [ ] User authentication
- [ ] Result export/sharing

## Contributing

See `GITHUB_SETUP.md` for Git workflow and contribution guidelines.

## Citation

Rockwell, B. W., McDougal, R. R., & Gent, C. A. (2021). Improved automated identification and mapping of iron sulfate minerals, other mineral groups, and vegetation using Landsat 8 Operational Land Imager data, San Juan Mountains, Colorado, and Four Corners Region. U.S. Geological Survey Scientific Investigations Map 3466.

## License

[Specify License]

## Contact

[Your Contact Information]

## Acknowledgments

- USGS for Rockwell et al. (2021) methodology
- Google Earth Engine team
- Kent State University
