# Acid Mine Drainage Detection System
### Advanced Remote Sensing for Environmental Monitoring

[![Version](https://img.shields.io/badge/version-1.5.4-blue.svg)](https://github.com/coodawy/AMD-Detection-Tool)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-Enabled-orange.svg)](https://earthengine.google.com/)
[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey.svg)](https://zenodo.org/)

> **Advancing environmental monitoring through satellite-based detection of acid mine drainage and water contamination worldwide**

---

## 🌍 Impact & Applications

This research tool addresses a **critical global environmental challenge**: acid mine drainage (AMD) contamination affects over **19,000 kilometers of waterways** in the United States alone, with millions more kilometers impacted worldwide. Traditional field surveys are costly, time-consuming, and limited in spatial coverage.

This automated detection system enables:
- **Large-scale monitoring** of mining-impacted watersheds across continents
- **Early warning detection** of emerging contamination in water bodies
- **Cost-effective assessment** reducing field survey needs by up to 80%
- **Temporal analysis** of contamination trends over decades using historical satellite data
- **Environmental justice** applications in underserved communities lacking monitoring infrastructure

**Real-world impact:**
- Successfully detected sulfate contamination (675 mg/L) in Ganau Lake, Iraq
- Validated against USGS reference sites in Colorado, Nevada, Utah, and Montana
- Applied to coal mining regions in Ohio, Mediterranean lakes, and global study areas
- Adaptable methodology extended to both terrestrial mineral mapping and aquatic contamination

---

## 🔬 Research Innovation

This tool represents significant methodological advancement over existing approaches:

### Novel Contributions
1. **Dual-Domain Detection**: First implementation extending USGS terrestrial mineral detection (Rockwell et al., 2021) to contaminated water bodies
2. **Multi-Criteria Water Quality Scoring**: 7-point contamination assessment combining spectral indices (NIR anomaly, turbidity, iron water index, yellow index)
3. **Adaptive Water Masking**: Unified water detection using AWEINSH threshold optimization to separate true water bodies from wet soil
4. **Multi-Sensor Integration**: Harmonized Landsat 8/9 and Sentinel-2 processing with automated sensor selection
5. **Open Science Implementation**: Fully reproducible Google Earth Engine workflow accessible to researchers worldwide

### Technical Achievements
- **19-class Boolean classification** for terrestrial minerals following USGS methodology
- **3-class water quality system** (clean, moderate, severe contamination)
- **Contamination score model** validated against ground truth measurements
- **Real-time interactive visualization** with diagnostic layers and pixel-level analysis

---

## 🚀 Quick Start

### Google Earth Engine (Recommended)
```javascript
// 1. Open Google Earth Engine Code Editor
// 2. Copy earth-engine/amd_detection_v1.0.0.js
// 3. Paste and run - interactive map loads automatically
// 4. Select study area from dropdown menu
// 5. Click any pixel for detailed spectral analysis
```

### Python Workflow (In Development)
```bash
pip install -r python/requirements.txt
python python/amd_detection.py --region "Ganau Pond, Iraq" --sensor landsat8
```

---

## 📊 Methodology

### Spectral Indices (Rockwell et al., 2021)
```
Iron Sulfate Index = (B2/B1) - (B5/B4)  [Threshold: >1.15]
Ferric Iron Index 1 = B4/B2  [Threshold: >1.40]
Ferric Iron Index 2 = (B4/B2) × (B4+B6)/B5  [Threshold: >2.50]
Clay-Sulfate-Mica = (B6/B7) - (B5/B4)  [Threshold: >0.12]
```

### Water Quality Scoring System
```
Score = ƒ(NIR Anomaly, Turbidity Ratio, Iron Water Index, 
          Yellow Index, NDWI, Iron Sulfate, Brightness)
          
Classification:
  Score 0-2:  Clean Water (Blue)
  Score 3-4:  Moderate Contamination (Orange)
  Score 5-7:  Severe Contamination (Red)
```

### Study Areas
- **United States**: Ohio coal mining lakes, Colorado mining districts, Nevada, Utah, Montana
- **Middle East**: Ganau Lake and Dukan Lake, Iraq
- **Africa**: Lake Toshka and Lake Naser, Egypt
- **Validation Sites**: USGS reference locations (Goldfield NV, Silverton CO, Iron Mountain CA)

---

## 📁 Project Structure

```
AMD-Detection-Tool/
├── earth-engine/
│   ├── amd_detection_v1.0.0.js       # Production GEE script (v1.5.4)
│   ├── USAGE_GUIDE.md                # Detailed user documentation
│   └── water_quality_module_guide.md # Water contamination methods
│
├── python/
│   ├── amd_detection.py              # Core processing module
│   ├── AMD_Detection_Tool.ipynb      # Jupyter notebook workflow
│   └── requirements.txt              # Dependencies
│
├── docs/
│   ├── METHODOLOGY.md                # Scientific methods
│   ├── VALIDATION.md                 # Accuracy assessment
│   └── API_REFERENCE.md              # Function documentation
│
├── CHANGELOG.md                      # Version history
├── CITATION.cff                      # Citation metadata
└── LICENSE                           # MIT License
```

---

## 🔗 Citation

If you use this tool in your research, please cite:

```bibtex
@software{hussein2025amd,
  author = {Hussein, Abdulrahman R. A.},
  title = {Acid Mine Drainage Detection System: Advanced Remote Sensing for Environmental Monitoring},
  year = {2025},
  version = {1.5.4},
  url = {https://github.com/coodawy/AMD-Detection-Tool},
  note = {Based on Rockwell et al. (2021) USGS SIM 3466}
}
```

**Reference methodology:**
Rockwell, B. W., McDougal, R. R., & Gent, C. A. (2021). Improved automated identification and mapping of iron sulfate minerals, other mineral groups, and vegetation using Landsat 8 Operational Land Imager data, San Juan Mountains, Colorado, and Four Corners Region. *U.S. Geological Survey Scientific Investigations Map 3466*.

---

## 📈 Development Status

**Current Version:** 1.5.4 (January 2025)

### Recent Updates
- ✅ Fixed wet bare soil misclassification using AWEINSH > 0.20 threshold
- ✅ Resolved water quality layer masking issues
- ✅ Validated against ground truth (Ganau Lake: 675 mg/L sulfate)
- ✅ Multi-sensor harmonization (Landsat 8/9, Sentinel-2)

### In Progress
- 🔄 Python workflow automation
- 🔄 Batch processing for large watersheds
- 🔄 Temporal trend analysis
- 🔄 Web application interface

### Roadmap
- ⏳ Machine learning classification enhancement
- ⏳ Real-time alert system for contamination events
- ⏳ Mobile app for field validation
- ⏳ Integration with hydrological models

---

## 🤝 Contributing

Contributions are welcome! This is an active research project with opportunities for collaboration in:
- Algorithm improvements and optimization
- New study area validation
- Python workflow development
- Documentation and tutorials

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📧 Contact & Collaboration

**Author:** Abdulrahman Rabie Ahmed Hussein  
**Affiliation:** Kent State University, Department of Earth Sciences  
**Website:** [www.climtawy.com](https://www.climtawy.com)  
**ORCID:** [0009-0003-0401-9219](https://orcid.org/0009-0003-0401-9219)  
**Email:** abdulrahman@climtawy.com  
**Research Focus:** Environmental remote sensing, hydrogeochemistry, agri-tech, climate adaptation

For collaboration inquiries, methodological questions, or data sharing:
- Open an [Issue](https://github.com/coodawy/AMD-Detection-Tool/issues)
- Visit [www.climtawy.com](https://www.climtawy.com)
- Email: abdulrahman@climtawy.com

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

Open science principles: This tool is freely available to support environmental monitoring and research worldwide.

---

## 🙏 Acknowledgments

- **U.S. Geological Survey** for the foundational Rockwell et al. (2021) methodology
- **Google Earth Engine** team for cloud-based geospatial processing infrastructure
- **Kent State University** for research support
- **Global remote sensing community** for validation and feedback

---

**⭐ If this tool supports your research or environmental monitoring work, please star this repository and cite our work!**
