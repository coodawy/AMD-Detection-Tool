# Project Overview: Acid Mine Drainage Detection System

## Executive Summary

This repository contains an advanced remote sensing tool for detecting and mapping acid mine drainage (AMD) contamination and iron sulfate minerals using satellite imagery. The system addresses a critical global environmental challenge affecting millions of kilometers of waterways worldwide.

### Key Innovation
First open-source implementation extending USGS terrestrial mineral detection methodology (Rockwell et al., 2021) to aquatic contamination assessment, enabling large-scale water quality monitoring through freely available satellite data.

## Repository Structure

### Core Implementation
- **`earth-engine/amd_detection_v1.0.0.js`** (v1.5.4): Production Google Earth Engine script
  - 19-class land mineral classification
  - 3-class water quality assessment
  - Multi-sensor support (Landsat 8/9, Sentinel-2)
  - Interactive visualization and analysis

### Python Development
- **`python/amd_detection.py`**: Core Python module (in development)
- **`python/AMD_Detection_Tool.ipynb`**: Jupyter notebook workflow
- **`python/requirements.txt`**: Package dependencies

### Documentation
- **`README.md`**: Project overview and quick start
- **`METHODOLOGY.md`**: Scientific methods and algorithms (docs/)
- **`CHANGELOG.md`**: Version history with detailed changes
- **`CONTRIBUTING.md`**: Contribution guidelines for collaborators
- **`CITATION.cff`**: Academic citation metadata
- **`LICENSE`**: MIT open-source license

### User Guides
- **`earth-engine/USAGE_GUIDE.md`**: Detailed user instructions
- **`earth-engine/water_quality_module_guide.md`**: Water contamination methods
- **`earth-engine/validation_results.md`**: Accuracy assessment results

## Technical Capabilities

### Land AMD Classification (19 Classes)
Based on Rockwell et al. (2021) USGS SIM 3466 methodology:
1. Extreme AMD (Iron Sulfate > 2.0)
2. Very Strong AMD (1.8-2.0)
3. Strong AMD (1.6-1.8)
4. Moderate-Strong AMD (1.5-1.6)
5. Moderate AMD (1.4-1.5)
6. Weak AMD (1.15-1.4)
7-19. Additional mineral classes (ferric iron, clay-sulfate, vegetation, etc.)

### Water Quality Classification (3 Classes)
Novel multi-criteria contamination scoring system:
- **Clean Water** (Score 0-2): Blue visualization
- **Moderate Contamination** (Score 3-4): Orange visualization
- **Severe Contamination** (Score 5-7): Red visualization

**Scoring Components:**
- NIR Anomaly (dissolved iron detection)
- Turbidity Ratio (suspended particles)
- Iron Water Index
- Yellow Index (ferric iron in water)
- Iron Sulfate Index
- NDWI (water content)
- Brightness validation

### Multi-Sensor Processing
- **Landsat 8/9 OLI**: Collection 2 Level-2 Surface Reflectance
- **Sentinel-2 MSI**: Level-2A harmonized products
- Automated cloud masking and quality assessment
- Temporal compositing (median, mean, mosaic, quality-based)

## Study Areas

### Global Coverage (20+ Sites)
- **United States**: Ohio coal mining lakes, Colorado AMD districts, Nevada, Utah, Montana, California, Illinois
- **Middle East**: Iraq (Ganau Lake, Dukan Lake) - sulfate contamination validation
- **Africa**: Egypt (Lake Toshka, Lake Naser) - large reservoir assessment

### Validation
- Ground truth: Ganau Lake (675 mg/L sulfate) - correctly classified as severe
- USGS reference sites: Colorado, Nevada, Utah - methodology validation

## Scientific Impact

### Addresses Critical Gap
Traditional field monitoring:
- Limited spatial coverage
- High cost ($500-2000 per site visit)
- Infrequent sampling (quarterly to annual)
- Inaccessible remote areas

This automated system:
- **Continental-scale monitoring** using free satellite data
- **Cost reduction** of 70-90% compared to field surveys
- **Temporal resolution** from 1984-present with Landsat archive
- **Objective, reproducible** methodology

### Research Applications
1. **Environmental Monitoring**: Large watershed AMD assessment
2. **Regulatory Compliance**: Mining permit monitoring and enforcement
3. **Climate Change**: Long-term contamination trend analysis
4. **Environmental Justice**: Underserved community water quality
5. **Disaster Response**: Post-mining accident contamination tracking

## Technical Architecture

### Processing Workflow
```
Satellite Data Acquisition
    ↓
Cloud Masking & Quality Control
    ↓
Surface Reflectance Processing
    ↓
Spectral Index Calculation
    ↓
Unified Water Mask Generation
    ↓
    ├── Land AMD Classification (19 classes)
    └── Water Quality Classification (3 classes)
        ↓
Interactive Visualization & Analysis
```

### Key Algorithms
1. **Unified Water Mask**: Multi-criteria (MNDWI, AWEINSH, brightness, NDVI, NDWI)
2. **Land/Water Separation**: Mutual exclusivity prevents classification overlap
3. **Contamination Scoring**: 7-point system combining spectral indicators
4. **Depth Filtering**: Excludes shallow water for accuracy improvement

## Version History

- **v1.5.4** (2025-01-09): AWEINSH threshold optimization for wet soil exclusion
- **v1.5.2** (2025-01-08): Fixed water quality layer masking issue
- **v1.5.0** (2025-01-03): Water quality module implementation
- **v1.0.0** (2024-11-15): Initial release with land AMD classification

## Future Development

### Near-Term (v1.6-2.0)
- Python workflow automation
- Batch processing for large watersheds
- Temporal trend analysis algorithms
- Enhanced validation dataset

### Long-Term (v2.0+)
- Machine learning classification enhancement
- Web application interface
- Real-time contamination alerts
- Mobile field validation app
- Hydrological model integration

## Getting Started

### For Researchers
1. Open Google Earth Engine Code Editor
2. Copy `earth-engine/amd_detection_v1.0.0.js`
3. Select study area and run
4. Explore results with interactive tools

### For Developers
1. Review `CONTRIBUTING.md` for guidelines
2. Fork repository and create feature branch
3. Test changes with multiple study areas
4. Submit pull request with documentation

### For Collaborators
Visit [www.climtawy.com](https://www.climtawy.com) or open GitHub issue for research partnerships.

## License & Citation

**License**: MIT (open science principles)

**Citation**:
```
Hussein, A. R. A. (2025). Acid Mine Drainage Detection System: Advanced Remote 
Sensing for Environmental Monitoring. GitHub. 
https://github.com/coodawy/AMD-Detection-Tool
```

## Author

**Abdulrahman Rabie Ahmed Hussein**  
PhD Student, Kent State University, Department of Earth Sciences  
Environmental Remote Sensing, Hydrogeochemistry, & AgriTech  
Website: [www.climtawy.com](https://www.climtawy.com)  
ORCID: [0009-0003-0401-9219](https://orcid.org/0009-0003-0401-9219)  
Email: abdulrahman@climtawy.com

---

**This research tool supports global environmental protection through open science and accessible technology.**
