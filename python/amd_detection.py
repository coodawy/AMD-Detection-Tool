"""
AMD Detection Tool - Python Module for Google Earth Engine
===========================================================
Based on Rockwell et al. (2021) USGS methodology for detecting
Acid Mine Drainage (AMD) and iron sulfate minerals.

Version: 1.5.1-python
Author: AMD Detection Tool Team
License: MIT

This module provides functions for:
- Spectral index calculations (Iron Sulfate, Ferric Iron, etc.)
- Land AMD classification (19 classes)
- Water quality assessment
- Cloud masking for Landsat 8 and Sentinel-2

Usage:
    import amd_detection as amd
    amd.initialize_gee()
    results = amd.analyze_region(geometry, start_date, end_date)
"""

# =============================================================================
# IMPORTS
# =============================================================================

import ee
import geemap
from typing import List

# =============================================================================
# VERSION INFO
# =============================================================================

__version__ = "1.5.1"
__author__ = "AMD Detection Tool Team"

# =============================================================================
# GOOGLE EARTH ENGINE INITIALIZATION
# =============================================================================

def initialize_gee(project: str = "remote-sensing-class-fall-2025", auth_mode: str = "notebook") -> bool:
    """
    Initialize Google Earth Engine with authentication.
    
    Parameters
    ----------
    project : str, default "remote-sensing-class-fall-2025"
        GEE cloud project ID. Uses department default if not specified.
    auth_mode : str, default "notebook"
        Authentication mode: "notebook" for Colab/Jupyter, "service_account" for automation.
    
    Returns
    -------
    bool
        True if initialization successful, False otherwise.
    
    Examples
    --------
    >>> import amd_detection as amd
    >>> amd.initialize_gee()  # Uses default project
    True
    >>> amd.initialize_gee(project="your-custom-project")  # Custom project
    True
    """
    try:
        ee.Authenticate(auth_mode=auth_mode)
        if project:
            ee.Initialize(project=project)
            print(f"✅ Google Earth Engine initialized with project: {project}")
        else:
            ee.Initialize()
            print("✅ Google Earth Engine initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ GEE initialization failed: {e}")
        print("💡 Try running: ee.Authenticate() manually first")
        return False


# =============================================================================
# DEFAULT SETTINGS
# =============================================================================

DEFAULT_SETTINGS = {
    # Sensor selection
    "sensor": "Landsat 8",
    "cloud_masking_method": "Hybrid",
    
    # Compositing
    "compositing_method": "median",
    
    # Date filtering
    "use_specific_date": False,
    "specific_start_date": "2024-01-01",
    "specific_end_date": "2024-12-31",
    "season_filter": "Summer (Jul-Sep)",
    
    # Iron sulfate detection thresholds (from Rockwell et al. 2021)
    "iron_sulfate_threshold": 1.15,
    "ferric_iron1_threshold": 1.40,
    "ferric_iron2_threshold": 2.50,
    "ferrous_iron_threshold": 1.05,
    "clay_sulfate_mica_threshold": 0.12,
    
    # Vegetation thresholds - CRITICAL: JS uses 1.5 for greenVegThreshold!
    "green_veg_threshold": 1.5,
    "ndvi_max": 0.25,
    
    # Brightness thresholds
    "brightness_min": 0.02,
    "brightness_max": 0.35,
    
    # Dark pixel masking (from paper Section 3.5)
    "dark_mask_threshold": 0.2125,
    
    # Water detection thresholds
    "water_threshold": 0.30,  # MNDWI
    "aweinsh_threshold": 0.0,
    
    # Built-up area detection
    "buildup_brightness_min": 0.18,
    "buildup_ndvi_max": 0.15,
    "buildup_ndvi_min": -0.10,
    "buildup_mndwi_max": -0.20,
    
    # Cloud masking thresholds
    "cloud_probability_threshold": 20,
    "cs_threshold": 0.60,
    "cs_cdf_threshold": 0.60,
    
    # Adaptive thresholding (paper Section 3.3)
    "use_adaptive_thresholds": False,
    "iron_std_mult": 2.0,
    "ferric1_std_mult": 1.5,
    "ferric2_std_mult": 1.5,
    "ferrous_std_mult": 1.5,
    "clay_std_mult": 1.5,
    
    # Index clipping (paper Section 3.4)
    "use_index_clipping": False,
    
    # Water quality module
    "enable_water_quality_module": True,
    "contaminated_water_threshold": 1.80,
    "shallow_water_threshold": 1.30,
    "turbidity_threshold": 1.3,
    
    # NIR Anomaly thresholds
    "nir_anomaly_threshold_moderate": 0.03,
    "nir_anomaly_threshold_severe": 0.08,
    
    # Turbidity thresholds
    "turbidity_ratio_moderate": 1.3,
    "turbidity_ratio_severe": 2.0,
    
    # Iron Water Index thresholds
    "iron_water_index_moderate": 0.15,
    "iron_water_index_severe": 0.50,
    
    # Yellow Index thresholds
    "yellow_index_moderate": 1.10,
    "yellow_index_severe": 1.25,
    
    # NDWI threshold
    "ndwi_clean_threshold": 0.20,
    
    # Scoring thresholds
    "use_multi_criteria_score": True,
    "score_threshold_moderate": 3,
    "score_threshold_severe": 5,
    
    # Comparison options
    "use_ndwi_comparison": False,
    "ndwi_threshold": 0.0,
    
    # UI options
    "show_accuracy_tools": False,
}


# =============================================================================
# STUDY AREAS (Pre-defined AMD-known locations)
# =============================================================================

STUDY_AREAS = {
    # =========================================================================
    # COMPLETE STUDY AREAS LIST (Matching JavaScript GEE Tool)
    # =========================================================================
    
    # Iraq
    "Ganau Pond, Iraq": ee.Geometry.Point([44.940463, 36.214839]).buffer(1000),
    "Dukan Lake, Iraq": ee.Geometry.Point([44.921183, 36.125888]).buffer(20000),
    
    # California
    "Iron Mountain, CA": ee.Geometry.Point([-122.5278, 40.6722]).buffer(12000),
    "Penn Mine, CA": ee.Geometry.Point([-120.82, 38.23]).buffer(5000),
    
    # Colorado
    "Summitville, CO": ee.Geometry.Point([-106.5978, 37.4361]).buffer(8000),
    "Silverton, CO": ee.Geometry.Point([-107.665, 37.812]).buffer(15000),
    "Red Mountain Pass, CO": ee.Geometry.Point([-107.72, 37.89]).buffer(10000),
    "Leadville, CO": ee.Geometry.Point([-106.30, 39.25]).buffer(15000),
    
    # Nevada
    "Goldfield, NV": ee.Geometry.Point([-117.233, 37.708]).buffer(10000),
    
    # Utah
    "Bauer Mill, UT": ee.Geometry.Point([-112.388, 40.492]).buffer(3000),
    "Marysvale, UT": ee.Geometry.Point([-112.233, 38.450]).buffer(10000),
    
    # Ohio - CRITICAL: Fixed Atwood Lake coordinates and buffer!
    "Atwood Lake, OH": ee.Geometry.Point([-81.246189, 40.549551]).buffer(10000),
    "Piedmont Lake, OH": ee.Geometry.Point([-81.222, 40.154]).buffer(10000),
    "Clendening Lake, OH": ee.Geometry.Point([-81.25360, 40.27006]).buffer(10000),
    "Delaware, OH": ee.Geometry.Point([-83.168502, 40.264754]).buffer(50000),
    "Monday Creek, OH": ee.Geometry.Point([-82.20948, 39.48279]).buffer(15000),
    "Lake Superior, OH": ee.Geometry.Point([-87.060472, 47.548672]).buffer(5000),
    
    # Montana
    "Berkeley Pit, MT": ee.Geometry.Point([-112.5010, 46.0136]).buffer(5000),
    
    # Illinois
    "Tab-Simco, IL": ee.Geometry.Point([-89.1, 37.7]).buffer(3000),
    
    # Egypt
    "Lake Toshka, Egypt": ee.Geometry.Point([31.27994, 23.09845]).buffer(100000),
    "Lake Nasser, Egypt": ee.Geometry.Point([32.21471, 22.73580]).buffer(100000),
}


# =============================================================================
# SPECTRAL INDEX CALCULATIONS
# =============================================================================

def calculate_spectral_indices(image: ee.Image, sensor: str = "Landsat 8") -> ee.Image:
    """
    Calculate all spectral indices for AMD detection.
    
    Based on Rockwell et al. (2021) USGS methodology.
    EXACTLY matches the JavaScript GEE version formulas.
    
    Parameters
    ----------
    image : ee.Image
        Input satellite image with surface reflectance bands.
    sensor : str, default "Landsat 8"
        Sensor type: "Landsat 8" or "Sentinel-2"
    
    Returns
    -------
    ee.Image
        Image with all spectral indices as bands.
    
    Notes
    -----
    Band mapping (both sensors normalized to Landsat naming):
    - SR_B1: Coastal/Aerosol (0.43-0.45 μm)
    - SR_B2: Blue (0.45-0.51 μm)
    - SR_B3: Green (0.53-0.59 μm)
    - SR_B4: Red (0.64-0.67 μm)
    - SR_B5: NIR (0.85-0.88 μm)
    - SR_B6: SWIR1 (1.57-1.65 μm)
    - SR_B7: SWIR2 (2.11-2.29 μm)
    """
    # Select bands (both sensors use same naming after preprocessing)
    b1 = image.select('SR_B1')  # Coastal/Aerosol
    b2 = image.select('SR_B2')  # Blue
    b3 = image.select('SR_B3')  # Green
    b4 = image.select('SR_B4')  # Red
    b5 = image.select('SR_B5')  # NIR
    b6 = image.select('SR_B6')  # SWIR1
    b7 = image.select('SR_B7')  # SWIR2
    
    # Add epsilon to avoid division by zero
    epsilon = 0.0001
    b1_safe = b1.add(epsilon)
    b2_safe = b2.add(epsilon)
    b4_safe = b4.add(epsilon)
    b5_safe = b5.add(epsilon)
    b7_safe = b7.add(epsilon)
    
    # =========================================================================
    # PRIMARY AMD INDICES (Rockwell et al. 2021, Table 3)
    # CRITICAL: These formulas MUST match the JavaScript version exactly!
    # =========================================================================
    
    # 1. IRON SULFATE MINERAL INDEX (Rockwell et al. 2021)
    # Formula: (B2 + B4) / B1
    # New L8 band addition index for robust jarosite detection
    # Clamp to reasonable range to avoid outliers from bad pixels
    iron_sulfate = (b2.add(b4).divide(b1_safe)
                    .clamp(0, 10)
                    .rename('IronSulfate'))
    
    # 2. FERRIC IRON 1 "REDNESS INDEX"
    # Formula: B4/B2
    # Detects hematite and goethite
    ferric_iron1 = b4.divide(b2_safe).rename('FerricIron1')
    
    # 3. FERRIC IRON 2 (Crystal Field Electronic Transition)
    # Formula: (B4/B2) × (B4+B6)/(B5)
    # Enhanced ferric iron detection
    ferric_iron2 = (b4.divide(b2_safe)
                    .multiply(b4.add(b6).divide(b5_safe))
                    .rename('FerricIron2'))
    
    # 4. FERROUS IRON
    # Formula: (B3+B6)/(B4+B5)
    # Detects chlorite and other ferrous minerals
    ferrous_iron = (b3.add(b6).divide(b4.add(b5).add(epsilon))
                    .rename('FerrousIron'))
    
    # 5. CLAY-SULFATE-MICA INDEX
    # Formula: (B6/B7) - (B5/B4)
    # Detects clay, sulfate, and mica minerals
    clay_sulfate = (b6.divide(b7_safe).subtract(b5.divide(b4_safe))
                    .rename('ClaySulfateMica'))
    
    # 6. GREEN VEGETATION INDEX
    # Formula: B5/B4 (NDVI-like)
    # Detects vegetation
    green_veg = b5.divide(b4_safe).rename('GreenVeg')
    
    # =========================================================================
    # STANDARD VEGETATION & WATER INDICES
    # =========================================================================
    
    # NDVI: Normalized Difference Vegetation Index
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    
    # NDWI: Normalized Difference Water Index (McFeeters)
    ndwi = image.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
    
    # MNDWI: Modified NDWI (Xu 2006)
    mndwi = image.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI')
    
    # Overall brightness (average of visible bands)
    brightness = b2.add(b3).add(b4).divide(3).rename('Brightness')
    
    # =========================================================================
    # WATER QUALITY INDICES
    # =========================================================================
    
    # AWEINSH: Automated Water Extraction Index (Feyisa et al. 2014)
    # Formula: B2 + 2.5×B3 - 1.5×B5 - 0.25×B7
    aweinsh = (b2.add(b3.multiply(2.5))
               .subtract(b5.multiply(1.5))
               .subtract(b7.multiply(0.25))
               .rename('AWEINSH'))
    
    # Turbidity Index (for contaminated water detection)
    # Formula: B4/B2 (red/blue ratio)
    # Higher values = more suspended sediments
    turbidity = b4.divide(b2_safe).rename('Turbidity')
    
    # NIR Anomaly - Critical for AMD water detection
    # Clean water: NIR < 1% (strong H₂O absorption)
    # Contaminated water: NIR = 3-10% (particle scattering)
    nir_anomaly = b5.rename('NIR_Anomaly')
    
    # Iron in Water Index
    # Formula: (Red/Blue) - (NIR/Red)
    # Combines: Red increase (Fe³⁺ color) + NIR increase (particle scattering)
    iron_water = (b4.divide(b2_safe)
                  .subtract(b5.divide(b4_safe))
                  .rename('IronWaterIndex'))
    
    # Yellow Substance Index (Green/Blue)
    # Detects dissolved/colloidal iron (Fe³⁺) shifting peak toward yellow-green
    yellow_index = b3.divide(b2_safe).rename('YellowIndex')
    
    # Water Depth Proxy
    # Formula: ln(Blue) / ln(Green)
    # Blue penetrates deeper than green; ratio decreases with depth
    b2_log = b2.log().add(epsilon)
    b3_log = b3.log().add(epsilon)
    depth_proxy = b2_log.divide(b3_log).rename('DepthProxy')
    
    # Red Anomaly - Additional contamination indicator
    red_anomaly = b4.rename('Red_Anomaly')
    
    # =========================================================================
    # ADDITIONAL INDICES FOR MASKING
    # =========================================================================
    
    # Coastal/Blue Ratio - Detects iron sulfate absorption <450nm
    coastal_blue_ratio = b1.divide(b2_safe).rename('CoastalBlueRatio')
    
    # NDBI - Normalized Difference Built-up Index
    # Formula: (SWIR1 - NIR) / (SWIR1 + NIR)
    # High values indicate urban/built-up areas
    ndbi = image.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI')
    
    # Combine all indices
    return image.addBands([
        iron_sulfate, ferric_iron1, ferric_iron2, ferrous_iron,
        clay_sulfate, green_veg, ndvi, ndwi, mndwi, brightness, aweinsh,
        turbidity, nir_anomaly, iron_water, yellow_index, depth_proxy,
        red_anomaly, coastal_blue_ratio, ndbi
    ])


# =============================================================================
# CLOUD MASKING FUNCTIONS
# =============================================================================

def mask_landsat8_clouds(image: ee.Image) -> ee.Image:
    """
    Apply cloud and shadow masking for Landsat 8 Collection 2.
    
    MATCHES JAVASCRIPT VERSION EXACTLY:
    - Bit 3: Cloud
    - Bit 4: Cloud confidence (NOT cloud shadow!)
    - Bit 2: Cloud shadow
    
    Parameters
    ----------
    image : ee.Image
        Landsat 8 Collection 2 Level-2 image.
    
    Returns
    -------
    ee.Image
        Cloud-masked image with scaled surface reflectance (0-1).
    """
    qa = image.select('QA_PIXEL')
    
    # Bit positions for cloud masking - MATCHING JAVASCRIPT EXACTLY
    # JavaScript uses: bitwiseAnd(1<<3).eq(0).and(bitwiseAnd(1<<4).eq(0)).and(bitwiseAnd(1<<2).eq(0))
    cloud_bit = 1 << 3       # Bit 3: Cloud
    cloud_conf_bit = 1 << 4  # Bit 4: Cloud confidence (JS uses this, NOT shadow!)
    shadow_bit = 1 << 2      # Bit 2: Cloud shadow (JS uses this position)
    
    # Create mask: 0 = cloudy, 1 = clear
    mask = (qa.bitwiseAnd(cloud_bit).eq(0)
            .And(qa.bitwiseAnd(cloud_conf_bit).eq(0))
            .And(qa.bitwiseAnd(shadow_bit).eq(0)))
    
    # Scale surface reflectance bands to 0-1
    optical = image.select('SR_B[1-7]').multiply(0.0000275).add(-0.2).clamp(0, 1)
    
    return image.addBands(optical, overwrite=True).updateMask(mask)


def mask_sentinel2_clouds(image: ee.Image, 
                          cloud_prob_threshold: int = 20,
                          cs_threshold: float = 0.60) -> ee.Image:
    """
    Apply cloud masking for Sentinel-2 using multiple methods.
    
    Combines SCL, cloud probability, and Cloud Score+ for robust masking.
    
    Parameters
    ----------
    image : ee.Image
        Sentinel-2 Level-2A image.
    cloud_prob_threshold : int, default 20
        Maximum cloud probability percentage (0-100).
    cs_threshold : float, default 0.60
        Minimum Cloud Score+ clear probability (0-1).
    
    Returns
    -------
    ee.Image
        Cloud-masked image with scaled surface reflectance (0-1).
    """
    # SCL-based masking (Scene Classification Layer)
    # MATCHES JAVASCRIPT: Classes 3, 8, 9, 10 excluded
    # NOTE: Class 11 (snow/ice) is NOT excluded - matches JS behavior!
    scl = image.select('SCL')
    scl_mask = (scl.neq(3)   # Cloud shadow
                .And(scl.neq(8))   # Cloud medium probability
                .And(scl.neq(9))   # Cloud high probability
                .And(scl.neq(10))) # Thin cirrus
    # NOT excluding class 11 (snow/ice) - this matches JavaScript version
    
    # Cloud probability masking
    cloud_prob = image.select('MSK_CLDPRB')
    prob_mask = cloud_prob.lt(cloud_prob_threshold)
    
    # Combine masks
    combined_mask = scl_mask.And(prob_mask)
    
    # Scale surface reflectance bands to 0-1
    optical = (image.select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12'])
               .multiply(0.0001)
               .clamp(0, 1)
               .rename(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']))
    
    # Add coastal aerosol (B1) if available
    coastal = image.select('B1').multiply(0.0001).clamp(0, 1).rename('SR_B1')
    
    return image.addBands(optical, overwrite=True).addBands(coastal).updateMask(combined_mask)


# =============================================================================
# IMAGE COLLECTION FUNCTIONS
# =============================================================================

# Seasonal filtering months (matching JavaScript SEASON_MONTHS)
SEASON_MONTHS = {
    'All Year': None,
    'Summer (Jul-Sep)': [7, 8, 9],
    'Winter (Dec-Feb)': [12, 1, 2],
    'Spring (Mar-May)': [3, 4, 5],
    'Fall (Sep-Nov)': [9, 10, 11],
    'Snow-Free (May-Oct)': [5, 6, 7, 8, 9, 10]
}


def get_landsat8_collection(geometry: ee.Geometry,
                            start_date: str,
                            end_date: str,
                            cloud_cover_max: int = 30,
                            season: str = None) -> ee.ImageCollection:
    """
    Get Landsat 8 Collection 2 Level-2 imagery for a region.
    
    Parameters
    ----------
    geometry : ee.Geometry
        Area of interest.
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str
        End date in 'YYYY-MM-DD' format.
    cloud_cover_max : int, default 30
        Maximum cloud cover percentage for filtering.
    season : str, optional
        Season filter from SEASON_MONTHS. None for all year.
    
    Returns
    -------
    ee.ImageCollection
        Filtered and processed Landsat 8 collection.
    """
    collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                  .filterBounds(geometry)
                  .filterDate(start_date, end_date)
                  .filter(ee.Filter.lt('CLOUD_COVER', cloud_cover_max)))
    
    # Apply seasonal filter if specified
    if season and season in SEASON_MONTHS and SEASON_MONTHS[season]:
        months = SEASON_MONTHS[season]
        collection = collection.filter(
            ee.Filter.calendarRange(months[0], months[-1], 'month'))
    
    return collection.map(mask_landsat8_clouds)


def get_landsat9_collection(geometry: ee.Geometry,
                            start_date: str,
                            end_date: str,
                            cloud_cover_max: int = 30,
                            season: str = None) -> ee.ImageCollection:
    """
    Get Landsat 9 Collection 2 Level-2 imagery for a region.
    
    Uses same processing as Landsat 8 (compatible bands).
    
    Parameters
    ----------
    geometry : ee.Geometry
        Area of interest.
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str
        End date in 'YYYY-MM-DD' format.
    cloud_cover_max : int, default 30
        Maximum cloud cover percentage for filtering.
    season : str, optional
        Season filter from SEASON_MONTHS. None for all year.
    
    Returns
    -------
    ee.ImageCollection
        Filtered and processed Landsat 9 collection.
    """
    collection = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
                  .filterBounds(geometry)
                  .filterDate(start_date, end_date)
                  .filter(ee.Filter.lt('CLOUD_COVER', cloud_cover_max)))
    
    # Apply seasonal filter if specified
    if season and season in SEASON_MONTHS and SEASON_MONTHS[season]:
        months = SEASON_MONTHS[season]
        collection = collection.filter(
            ee.Filter.calendarRange(months[0], months[-1], 'month'))
    
    # Uses same cloud masking as Landsat 8
    return collection.map(mask_landsat8_clouds)


def get_sentinel2_collection(geometry: ee.Geometry,
                             start_date: str,
                             end_date: str,
                             cloud_cover_max: int = 30,
                             season: str = None) -> ee.ImageCollection:
    """
    Get Sentinel-2 Level-2A imagery for a region.
    
    Parameters
    ----------
    geometry : ee.Geometry
        Area of interest.
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str
        End date in 'YYYY-MM-DD' format.
    cloud_cover_max : int, default 30
        Maximum cloud cover percentage for filtering.
    season : str, optional
        Season filter from SEASON_MONTHS. None for all year.
    
    Returns
    -------
    ee.ImageCollection
        Filtered and processed Sentinel-2 collection.
    """
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterBounds(geometry)
                  .filterDate(start_date, end_date)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover_max)))
    
    # Apply seasonal filter if specified
    if season and season in SEASON_MONTHS and SEASON_MONTHS[season]:
        months = SEASON_MONTHS[season]
        collection = collection.filter(
            ee.Filter.calendarRange(months[0], months[-1], 'month'))
    
    return collection.map(mask_sentinel2_clouds)


def create_composite(collection: ee.ImageCollection,
                     method: str = "median",
                     sensor: str = "Landsat 8") -> ee.Image:
    """
    Create a composite image from a collection and calculate spectral indices.
    
    MATCHES JAVASCRIPT COMPOSITING METHODS:
    - median: Pixel-wise median (default, most robust)
    - mean: Pixel-wise mean
    - mosaic: Simple mosaic (most recent on top)
    - latest: Latest image mosaic (sorted by time)
    - quality: Quality mosaic using NIR (SR_B5) as quality band
    
    Parameters
    ----------
    collection : ee.ImageCollection
        Input image collection.
    method : str, default "median"
        Compositing method: "median", "mean", "mosaic", "latest", "quality".
    sensor : str, default "Landsat 8"
        Sensor type for index calculation.
    
    Returns
    -------
    ee.Image
        Composite image with all spectral indices.
    """
    # Create composite - MATCHING JAVASCRIPT METHODS
    if method == "median":
        composite = collection.median()
    elif method == "mean":
        composite = collection.mean()
    elif method == "mosaic":
        composite = collection.mosaic()
    elif method == "latest":
        # Sort by time (descending) and mosaic
        composite = collection.sort('system:time_start', False).mosaic()
    elif method == "quality":
        # Quality mosaic using NIR band as quality indicator
        composite = collection.qualityMosaic('SR_B5')
    else:
        composite = collection.median()
    
    # Calculate spectral indices
    composite = calculate_spectral_indices(composite, sensor)
    
    return composite


# =============================================================================
# MASKING FUNCTIONS
# =============================================================================

def create_water_mask(composite: ee.Image, settings: dict = None) -> ee.Image:
    """
    Create a multi-criteria water mask to exclude water from land classification.
    
    Uses MNDWI, AWEINSH, brightness, NDVI, and NDWI for robust water detection.
    
    Parameters
    ----------
    composite : ee.Image
        Composite image with spectral indices.
    settings : dict, optional
        Settings dictionary. Uses DEFAULT_SETTINGS if None.
    
    Returns
    -------
    ee.Image
        Binary water mask (1 = water, 0 = land).
    """
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    mndwi = composite.select('MNDWI')
    aweinsh = composite.select('AWEINSH')
    brightness = composite.select('Brightness')
    ndvi = composite.select('NDVI')
    ndwi = composite.select('NDWI')
    
    # Multi-criteria water detection
    # Each criterion removes a different type of false positive
    water_mask = (mndwi.gt(settings["water_threshold"])
                  .And(aweinsh.gt(settings["aweinsh_threshold"]))
                  .And(brightness.lt(0.30))   # Excludes bright land
                  .And(ndvi.lt(0.2))          # Excludes vegetation
                  .And(ndwi.gt(-0.1)))        # Additional water confirmation
    
    return water_mask


def create_vegetation_road_mask(composite: ee.Image, settings: dict = None) -> ee.Image:
    """
    Create combined vegetation and road mask with iron signal bypass.
    
    MATCHES JAVASCRIPT VERSION EXACTLY:
    - Green/Red <= 1.0 (ALWAYS required - no vegetation green peak)
    - NOT a road (unless strong iron signal bypasses road check)
    - Either NDVI < threshold OR (hasHighIron AND lowSWIR1 AND notDenseVeg)
    
    Parameters
    ----------
    composite : ee.Image
        Composite image with spectral indices.
    settings : dict, optional
        Settings dictionary. Uses DEFAULT_SETTINGS if None.
    
    Returns
    -------
    ee.Image
        Binary mask where 1 = passes (valid for AMD detection), 0 = excluded.
    """
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    ndvi = composite.select('NDVI')
    green_veg = composite.select('GreenVeg')
    iron = composite.select('IronSulfate')
    b3 = composite.select('SR_B3')  # Green
    b4 = composite.select('SR_B4')  # Red
    b6 = composite.select('SR_B6')  # SWIR1
    
    # Green/Red ratio (chlorophyll detection)
    green_red_ratio = b3.divide(b4.add(0.0001))
    
    # Multi-criteria iron soil detection (matching JavaScript exactly)
    # KEY INSIGHTS:
    #   1. Green/Red > 1.0 = vegetation (chlorophyll green peak)
    #   2. High SWIR1 (>0.20) + low NDVI + weak iron = roads/buildings (asphalt)
    #   3. High SWIR1 + STRONG iron (>2.5) = REAL iron minerals (iron oxides have high SWIR1!)
    
    no_green_peak = green_red_ratio.lte(1.0)           # Red >= Green (no chlorophyll)
    low_swir1 = b6.lt(0.20)                            # SWIR1 < 0.20 (not road/impervious)
    not_dense_veg = green_veg.lt(3.5)                  # Not extremely high vegetation index
    strong_iron_signal = iron.gt(2.5)                  # Strong iron = likely real minerals
    has_high_iron = iron.gt(settings["iron_sulfate_threshold"])
    
    # Road detection: low NDVI + high SWIR1 + weak iron signal
    # BYPASS road detection if Iron Sulfate > 2.5 (strong detection = real minerals)
    is_road = ndvi.lt(0.25).And(b6.gte(0.20)).And(strong_iron_signal.Not())
    
    # A pixel passes if ALL of:
    #   1. Green/Red <= 1.0 (ALWAYS required - no green peak)
    #   2. NOT a road (unless strong iron signal bypasses road check)
    #   3. Either NDVI < ndvi_max OR (hasHighIron AND lowSWIR1 AND notDenseVeg)
    passes_veg_road_mask = (no_green_peak
        .And(is_road.Not())
        .And(
            ndvi.lt(settings["ndvi_max"])
            .Or(has_high_iron.And(low_swir1).And(not_dense_veg))
        ))
    
    return passes_veg_road_mask


def create_vegetation_mask(composite: ee.Image, settings: dict = None) -> ee.Image:
    """
    Create a simple vegetation mask (legacy function).
    
    For full JavaScript-matching behavior, use create_vegetation_road_mask() instead.
    
    Parameters
    ----------
    composite : ee.Image
        Composite image with spectral indices.
    settings : dict, optional
        Settings dictionary. Uses DEFAULT_SETTINGS if None.
    
    Returns
    -------
    ee.Image
        Binary mask where 1 = passes (not vegetation), 0 = vegetation.
    """
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    ndvi = composite.select('NDVI')
    green_veg = composite.select('GreenVeg')
    b3 = composite.select('SR_B3')  # Green
    b4 = composite.select('SR_B4')  # Red
    
    # Green/Red ratio (chlorophyll detection)
    green_red_ratio = b3.divide(b4.add(0.0001))
    
    no_green_peak = green_red_ratio.lte(1.0)
    low_ndvi = ndvi.lt(settings["ndvi_max"])
    not_dense_veg = green_veg.lt(settings["green_veg_threshold"])
    
    passes_veg_mask = no_green_peak.And(low_ndvi.Or(not_dense_veg))
    
    return passes_veg_mask


def create_buildup_mask(composite: ee.Image, 
                        sensor: str = "Landsat 8",
                        settings: dict = None) -> ee.Image:
    """
    Create a built-up area mask to exclude urban false positives.
    
    Uses brightness, NDVI, and MNDWI with sensor-specific thresholds.
    
    Parameters
    ----------
    composite : ee.Image
        Composite image with spectral indices.
    sensor : str, default "Landsat 8"
        Sensor type for threshold adjustment.
    settings : dict, optional
        Settings dictionary. Uses DEFAULT_SETTINGS if None.
    
    Returns
    -------
    ee.Image
        Binary built-up mask (1 = built-up, 0 = not built-up).
    """
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    brightness = composite.select('Brightness')
    ndvi = composite.select('NDVI')
    mndwi = composite.select('MNDWI')
    
    # Sensor-specific brightness threshold
    # Sentinel-2 (10m) needs lower threshold to catch individual roofs
    # Landsat 8 (30m) mixes buildings with surroundings
    brightness_threshold = 0.15 if sensor == "Sentinel-2" else settings["buildup_brightness_min"]
    
    # Built-up detection
    is_bright = brightness.gt(brightness_threshold)
    low_ndvi = ndvi.lt(settings["buildup_ndvi_max"]).And(ndvi.gt(settings["buildup_ndvi_min"]))
    
    # MNDWI logic: dry land OR water-edge buildings (marinas)
    is_dry_land = mndwi.lt(settings["buildup_mndwi_max"])
    is_water_edge = mndwi.gt(-0.10).And(mndwi.lt(0.10))
    
    buildup_mask = is_bright.And(low_ndvi).And(is_dry_land.Or(is_water_edge))
    
    return buildup_mask


def create_road_mask(composite: ee.Image, settings: dict = None) -> ee.Image:
    """
    Create a road/impervious surface mask.
    
    Roads have low NDVI and high SWIR1, but strong iron signals bypass this mask.
    
    Parameters
    ----------
    composite : ee.Image
        Composite image with spectral indices.
    settings : dict, optional
        Settings dictionary. Uses DEFAULT_SETTINGS if None.
    
    Returns
    -------
    ee.Image
        Binary road mask (1 = road, 0 = not road).
    """
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    ndvi = composite.select('NDVI')
    b6 = composite.select('SR_B6')  # SWIR1
    iron = composite.select('IronSulfate')
    
    # Strong iron signal bypasses road detection
    # Real iron minerals have high SWIR1 too!
    strong_iron = iron.gt(2.5)
    
    # Road detection: low NDVI + high SWIR1 + NOT strong iron
    is_road = ndvi.lt(0.25).And(b6.gte(0.20)).And(strong_iron.Not())
    
    return is_road


# =============================================================================
# ADAPTIVE THRESHOLDING FUNCTIONS (Matching JavaScript)
# =============================================================================

def apply_std_dev_thresholding(index_image: ee.Image, 
                                band_name: str,
                                region: ee.Geometry,
                                multiplier: float = 2.0) -> ee.Image:
    """
    Apply standard deviation-based adaptive thresholding.
    
    Calculates threshold as: mean + (stdDev × multiplier)
    MATCHES JAVASCRIPT applyStdDevThresholding() function.
    
    Parameters
    ----------
    index_image : ee.Image
        Single-band index image.
    band_name : str
        Band name for statistics calculation.
    region : ee.Geometry
        Region to calculate statistics over.
    multiplier : float, default 2.0
        Standard deviation multiplier.
    
    Returns
    -------
    ee.Image
        Binary mask where index > adaptive threshold.
    """
    stats = index_image.reduceRegion(
        reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', True),
        geometry=region,
        scale=100,
        maxPixels=1e9,
        bestEffort=True
    )
    
    mean = ee.Number(stats.get(band_name + '_mean'))
    std_dev = ee.Number(stats.get(band_name + '_stdDev'))
    threshold = mean.add(std_dev.multiply(multiplier))
    
    return index_image.gt(threshold)


def apply_index_clipping(index_image: ee.Image,
                         band_name: str,
                         region: ee.Geometry,
                         percentile_clip: int = 30) -> ee.Image:
    """
    Apply percentile-based index clipping.
    
    Sets values below the specified percentile to 0.
    MATCHES JAVASCRIPT applyIndexClipping() function.
    
    Parameters
    ----------
    index_image : ee.Image
        Single-band index image.
    band_name : str
        Band name for statistics calculation.
    region : ee.Geometry
        Region to calculate statistics over.
    percentile_clip : int, default 30
        Percentile threshold (values below this are set to 0).
    
    Returns
    -------
    ee.Image
        Index image with values below percentile set to 0.
    """
    stats = index_image.reduceRegion(
        reducer=ee.Reducer.percentile([percentile_clip]),
        geometry=region,
        scale=100,
        maxPixels=1e9,
        bestEffort=True
    )
    
    clip_value = ee.Number(stats.get(band_name + '_p' + str(percentile_clip)))
    
    return index_image.where(index_image.lt(clip_value), 0)


# =============================================================================
# CLASSIFICATION FUNCTIONS
# =============================================================================

def create_land_classification(composite: ee.Image, 
                               sensor: str = "Landsat 8",
                               settings: dict = None) -> ee.Image:
    """
    Create 19-class land AMD classification based on Rockwell et al. (2021).
    
    Classification hierarchy (most restrictive first):
    - Classes 9, 17, 12, 18, 19, 14: Iron sulfate minerals (AMD indicators)
    - Classes 5, 6, 7, 8, 10: Clay and ferric combinations
    - Classes 1, 2, 3, 4: Ferric/ferrous iron minerals
    - Classes 11, 13: Vegetation classes
    
    Parameters
    ----------
    composite : ee.Image
        Composite image with spectral indices.
    sensor : str, default "Landsat 8"
        Sensor type for threshold adjustment.
    settings : dict, optional
        Settings dictionary. Uses DEFAULT_SETTINGS if None.
    
    Returns
    -------
    ee.Image
        Single-band classification image (0-19).
    """
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    # Extract indices
    iron = composite.select('IronSulfate')
    ferric1 = composite.select('FerricIron1')
    ferric2 = composite.select('FerricIron2')
    ferrous = composite.select('FerrousIron')
    clay = composite.select('ClaySulfateMica')
    green_veg = composite.select('GreenVeg')
    brightness = composite.select('Brightness')
    b6 = composite.select('SR_B6')
    
    # Create binary threshold masks
    has_iron = iron.gt(settings["iron_sulfate_threshold"])
    has_ferric1 = ferric1.gt(settings["ferric_iron1_threshold"])
    has_ferric2 = ferric2.gt(settings["ferric_iron2_threshold"])
    has_ferrous = ferrous.gt(settings["ferrous_iron_threshold"])
    has_clay = clay.gt(settings["clay_sulfate_mica_threshold"])
    has_veg = green_veg.gt(settings["green_veg_threshold"])
    
    # Quality masks
    not_bright = brightness.lt(settings["brightness_max"])
    not_dark = b6.gt(settings["dark_mask_threshold"]).And(brightness.gt(0.05))
    
    # Create exclusion masks
    water_mask = create_water_mask(composite, settings)
    veg_road_mask = create_vegetation_road_mask(composite, settings)  # Combined mask with iron bypass
    buildup_mask = create_buildup_mask(composite, sensor, settings)
    
    # Combined land mask for AMD classification - MATCHES JAVASCRIPT EXACTLY
    # Uses combined veg/road mask instead of separate masks
    amd_land_mask = (water_mask.Not()
                     .And(not_bright)
                     .And(not_dark)
                     .And(buildup_mask.Not())
                     .And(veg_road_mask))  # Combined veg+road mask with iron bypass!
    
    # Standard land mask for non-AMD minerals
    standard_land_mask = amd_land_mask
    
    # Initialize classification
    classification = ee.Image(0)
    
    # =========================================================================
    # STEP 1: Iron sulfate classes (AMD indicators) - most restrictive first
    # =========================================================================
    
    # Class 9: Argillic Alteration (Iron + Fe1 + Fe2 + Clay + not too bright)
    classification = classification.where(
        has_iron.And(has_ferric1).And(has_ferric2).And(has_clay).And(amd_land_mask).And(not_bright), 9)
    
    # Class 17: Proximal Jarosite (Iron + Fe1 + Fe2 + Clay)
    classification = classification.where(
        has_iron.And(has_ferric1).And(has_ferric2).And(has_clay).And(amd_land_mask), 17)
    
    # Class 12: Major Iron Sulfate (Iron + Fe1 + Clay, NO Fe2)
    classification = classification.where(
        has_iron.And(has_ferric1).And(has_ferric2.Not()).And(has_clay).And(amd_land_mask), 12)
    
    # Class 18: Distal Jarosite (Iron + Fe2 + Clay, NO Fe1)
    classification = classification.where(
        has_iron.And(has_ferric1.Not()).And(has_ferric2).And(has_clay).And(amd_land_mask), 18)
    
    # Class 19: Clay + Ferrous + Iron
    classification = classification.where(
        has_iron.And(has_ferrous).And(has_clay).And(amd_land_mask), 19)
    
    # Class 14: Oxidizing Sulfides (Iron + Clay, NO Fe1, NO Fe2)
    classification = classification.where(
        has_iron.And(has_clay).And(has_ferric1.Not()).And(has_ferric2.Not()).And(amd_land_mask), 14)
    
    # Fallback: Any strong iron gets Class 12
    classification = classification.where(has_iron.And(amd_land_mask), 12)
    
    # =========================================================================
    # STEP 2: Non-iron sulfate classes
    # =========================================================================
    
    # Class 8: Clay + Major Ferric (Clay + Fe1 + Fe2, no Iron)
    classification = classification.where(
        has_clay.And(has_ferric1).And(has_ferric2).And(has_iron.Not()).And(standard_land_mask), 8)
    
    # Class 7: Clay + Moderate Ferric (Clay + Fe1 OR Fe2, no Iron)
    classification = classification.where(
        has_clay.And(has_ferric1.Or(has_ferric2)).And(has_iron.Not()).And(standard_land_mask), 7)
    
    # Class 6: Clay + Minor Ferric (Clay + Fe1, no Fe2, no Iron)
    classification = classification.where(
        has_clay.And(has_ferric1).And(has_ferric2.Not()).And(has_iron.Not()).And(standard_land_mask), 6)
    
    # Class 5: Clay-Sulfate-Mica (Clay only, no Fe1, no Iron)
    classification = classification.where(
        has_clay.And(has_ferric1.Not()).And(has_iron.Not()).And(standard_land_mask), 5)
    
    # Class 10: Clay + Ferrous (Clay + Ferrous, no Iron)
    classification = classification.where(
        has_clay.And(has_ferrous).And(has_iron.Not()).And(standard_land_mask), 10)
    
    # Class 2: Major Ferric Iron (Fe1 + Fe2, no Clay)
    classification = classification.where(
        has_ferric1.And(has_ferric2).And(has_clay.Not()).And(standard_land_mask), 2)
    
    # Class 3: Ferric + Ferrous (Fe1 + Ferrous, no Clay)
    classification = classification.where(
        has_ferric1.And(has_ferrous).And(has_clay.Not()).And(standard_land_mask), 3)
    
    # Class 1: Minor Ferric/Hematite (Fe1 only, no Fe2, no Clay, no Iron)
    classification = classification.where(
        has_ferric1.And(has_ferric2.Not()).And(has_clay.Not()).And(has_iron.Not()).And(standard_land_mask), 1)
    
    # Class 4: Ferrous/Chlorite (Ferrous only, no Fe1, no Clay)
    classification = classification.where(
        has_ferrous.And(has_clay.Not()).And(has_ferric1.Not()).And(standard_land_mask), 4)
    
    # Class 13: Sparse Vegetation + Ferric (only if no iron)
    classification = classification.where(
        has_veg.And(has_ferric1).And(has_iron.Not()), 13)
    
    # Class 11: Dense Green Vegetation (only if no iron/ferric)
    classification = classification.where(
        has_veg.And(has_iron.Not()).And(has_ferric1.Not()), 11)
    
    return classification.rename('classification')


def create_water_quality_classification(composite: ee.Image,
                                        settings: dict = None) -> ee.Image:
    """
    Create water quality classification for AMD-contaminated water bodies.
    
    Uses multi-criteria scoring (0-8 points) based on:
    - Iron sulfate index
    - NIR anomaly
    - Turbidity ratio
    - Iron water index
    - Yellow index
    - NDWI degradation
    
    Parameters
    ----------
    composite : ee.Image
        Composite image with spectral indices.
    settings : dict, optional
        Settings dictionary. Uses DEFAULT_SETTINGS if None.
    
    Returns
    -------
    ee.Image
        Water quality classification with bands:
        - 'water_quality': 0=clean, 1=moderate, 2=severe, 3=extreme
        - 'score': Raw contamination score (0-8)
    """
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    # Get water mask (excluding land AMD pixels)
    water_mask = create_water_mask(composite, settings)
    land_class = create_land_classification(composite, settings=settings)
    is_land_amd = land_class.gte(1).And(land_class.lte(19))
    water_only_mask = water_mask.And(is_land_amd.Not())
    
    # Depth filtering (remove shallow water false positives)
    depth_proxy = composite.select('DepthProxy')
    deep_water_mask = water_only_mask.And(depth_proxy.lt(settings["shallow_water_threshold"]))
    
    # Extract water quality indices
    iron_sulfate = composite.select('IronSulfate')
    nir_anomaly = composite.select('NIR_Anomaly')
    turbidity = composite.select('Turbidity')
    iron_water = composite.select('IronWaterIndex')
    yellow_index = composite.select('YellowIndex')
    ndwi = composite.select('NDWI')
    brightness = composite.select('Brightness')
    
    # Multi-criteria scoring (0-7 points) - USING SETTINGS, NOT HARDCODED VALUES
    score = ee.Image(0)
    
    # Valid brightness for water
    valid_brightness = brightness.gt(0.05).And(brightness.lt(0.20))
    
    # Criterion 1: Iron Sulfate Index (2 points) - with brightness validation
    score = score.where(
        iron_sulfate.gt(settings["contaminated_water_threshold"]).And(valid_brightness), 
        score.add(2))
    
    # Criterion 2: NIR Anomaly (2 points total) - USING SETTINGS
    score = score.where(
        nir_anomaly.gt(settings["nir_anomaly_threshold_moderate"]), 
        score.add(1))
    score = score.where(
        nir_anomaly.gt(settings["nir_anomaly_threshold_severe"]), 
        score.add(1))
    
    # Criterion 3: Turbidity (2 points total) - USING SETTINGS
    score = score.where(
        turbidity.gt(settings["turbidity_ratio_moderate"]), 
        score.add(1))
    score = score.where(
        turbidity.gt(settings["turbidity_ratio_severe"]), 
        score.add(1))
    
    # Criterion 4: Iron Water Index (1 point) - USING SETTINGS
    score = score.where(
        iron_water.gt(settings["iron_water_index_moderate"]), 
        score.add(1))
    
    # Criterion 5: Yellow Index (1 point) - USING SETTINGS
    score = score.where(
        yellow_index.gt(settings["yellow_index_moderate"]), 
        score.add(1))
    
    # Criterion 6: NDWI Degradation (1 point) - USING SETTINGS
    score = score.where(
        ndwi.lt(settings["ndwi_clean_threshold"]), 
        score.add(1))
    
    # Apply water mask
    score = score.updateMask(deep_water_mask)
    
    # Classify into categories - MATCHING JAVASCRIPT (2 classes: moderate, severe)
    # JavaScript uses: score >= scoreThresholdModerate = 1 (Moderate)
    #                  score >= scoreThresholdSevere = 2 (Severe)
    water_quality = ee.Image(0)  # 0 = Clean water
    water_quality = water_quality.where(
        score.gte(settings["score_threshold_moderate"]), 1)  # Moderate
    water_quality = water_quality.where(
        score.gte(settings["score_threshold_severe"]), 2)    # Severe
    water_quality = water_quality.updateMask(deep_water_mask)
    
    return water_quality.addBands(score.rename('score')).rename(['water_quality', 'score'])


# =============================================================================
# VISUALIZATION PALETTES (MATCHING JAVASCRIPT VERSION EXACTLY)
# =============================================================================

# 19-class land classification palette (matches JS updateDetection classVis)
CLASSIFICATION_PALETTE = [
    '#000000',  # 0: Unclassified/Background
    '#8B7355',  # 1: Minor Ferric (light brown)
    '#FF00FF',  # 2: Major Ferric Iron (magenta)
    '#800080',  # 3: Ferric±Ferrous (purple)
    '#00CED1',  # 4: Ferrous/Chlorite (dark cyan)
    '#90EE90',  # 5: Clay-Sulfate-Mica (light green)
    '#FFFF00',  # 6: Clay+Minor Ferric (yellow)
    '#FFA500',  # 7: Clay+Mod Ferric (orange)
    '#FF6347',  # 8: Clay+Major Ferric (tomato)
    '#FF1493',  # 9: Argillic Alteration (deep pink) - EXTREME AMD
    '#008B8B',  # 10: Clay+Ferrous (dark cyan)
    '#228B22',  # 11: Dense Vegetation (forest green)
    '#FF0000',  # 12: Major Iron Sulfate (RED) - HIGH AMD
    '#9ACD32',  # 13: Sparse Veg+Ferric (yellow-green)
    '#FFB6C1',  # 14: Oxidizing Sulfides (light pink)
    '#000000',  # 15: Not used
    '#000000',  # 16: Not used
    '#DC143C',  # 17: Proximal Jarosite (crimson) - HIGH AMD
    '#8B0000',  # 18: Distal Jarosite (dark red)
    '#C71585',  # 19: Clay+Ferrous+Iron (medium violet red)
]

# Water quality classification palette (matches JS water quality module)
WATER_QUALITY_PALETTE = [
    '#1E90FF',  # 0: Clean water (dodger blue)
    '#FFA500',  # 1: Moderate contamination (orange)
    '#FF0000',  # 2: Severe contamination (red)
]

# Iron Sulfate Index visualization (matches JS Iron Sulfate layer)
IRON_SULFATE_PALETTE = ['#00FFFF', '#FFFF00', '#FFA500', '#FF0000']  # cyan->yellow->orange->red

# Water contamination score palette (0-7 scale)
WATER_SCORE_PALETTE = [
    '#0000FF', '#00FFFF', '#00FF00', '#FFFF00', 
    '#FFA500', '#FF4500', '#FF0000', '#8B0000'
]

# True color and false color visualization parameters
VIS_TRUE_COLOR = {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 0.3}
VIS_FALSE_COLOR = {'bands': ['SR_B5', 'SR_B4', 'SR_B3'], 'min': 0, 'max': 0.3}
VIS_IRON_SULFATE = {'min': 1.15, 'max': 4.0, 'palette': IRON_SULFATE_PALETTE}
VIS_FERRIC_IRON = {'min': 0, 'max': 3, 'palette': ['#FFFFFF', '#FFFF00', '#FF0000']}
VIS_MNDWI = {'min': -1, 'max': 1, 'palette': ['#FF0000', '#FFFFFF', '#0000FF']}
VIS_LAND_CLASS = {'min': 1, 'max': 19, 'palette': CLASSIFICATION_PALETTE[1:]}
VIS_WATER_QUALITY = {'min': 0, 'max': 2, 'palette': WATER_QUALITY_PALETTE}


# =============================================================================
# HIGH-LEVEL ANALYSIS FUNCTIONS
# =============================================================================

def analyze_region(geometry: ee.Geometry,
                   start_date: str,
                   end_date: str,
                   sensor: str = "Landsat 8",
                   settings: dict = None,
                   cloud_cover_max: int = 30) -> dict:
    """
    Complete AMD analysis for a region of interest.
    
    This is the main entry point for analyzing a region. It:
    1. Loads and processes satellite imagery
    2. Creates composite with spectral indices
    3. Runs land AMD classification
    4. Runs water quality classification
    
    Parameters
    ----------
    geometry : ee.Geometry
        Area of interest.
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str
        End date in 'YYYY-MM-DD' format.
    sensor : str, default "Landsat 8"
        Sensor: "Landsat 8" or "Sentinel-2"
    settings : dict, optional
        Custom settings. Uses DEFAULT_SETTINGS if None.
    cloud_cover_max : int, default 30
        Maximum cloud cover percentage.
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'composite': ee.Image with spectral indices
        - 'land_classification': ee.Image with 19-class land classification
        - 'water_quality': ee.Image with water quality classification
        - 'iron_sulfate': ee.Image with iron sulfate index
        - 'metadata': dict with analysis parameters
    
    Examples
    --------
    >>> import amd_detection as amd
    >>> amd.initialize_gee()
    >>> geometry = ee.Geometry.Point([-122.5278, 40.6722]).buffer(12000)
    >>> results = amd.analyze_region(geometry, '2023-06-01', '2023-09-30')
    >>> print(results['metadata'])
    """
    if settings is None:
        settings = DEFAULT_SETTINGS.copy()
    
    # Get image collection based on sensor
    if sensor == "Sentinel-2":
        collection = get_sentinel2_collection(geometry, start_date, end_date, cloud_cover_max)
    elif sensor == "Landsat 9":
        collection = get_landsat9_collection(geometry, start_date, end_date, cloud_cover_max)
    else:  # Default to Landsat 8
        collection = get_landsat8_collection(geometry, start_date, end_date, cloud_cover_max)
    
    # Create composite
    composite = create_composite(collection, method="median", sensor=sensor)
    
    # Run classifications
    land_class = create_land_classification(composite, sensor, settings)
    water_quality = create_water_quality_classification(composite, settings)
    
    # Extract iron sulfate layer
    iron_sulfate = composite.select('IronSulfate')
    
    # Prepare metadata
    metadata = {
        'sensor': sensor,
        'start_date': start_date,
        'end_date': end_date,
        'cloud_cover_max': cloud_cover_max,
        'settings': settings,
        'version': __version__,
    }
    
    return {
        'composite': composite,
        'land_classification': land_class,
        'water_quality': water_quality,
        'iron_sulfate': iron_sulfate,
        'metadata': metadata,
    }


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_map(center: List[float] = None,
               zoom: int = 10,
               basemap: str = "SATELLITE") -> geemap.Map:
    """
    Create an interactive map for visualization.
    
    Parameters
    ----------
    center : list, optional
        Map center [lat, lon]. Defaults to Iron Mountain, CA.
    zoom : int, default 10
        Initial zoom level.
    basemap : str, default "SATELLITE"
        Basemap type: "SATELLITE", "TERRAIN", "ROADMAP", "HYBRID"
    
    Returns
    -------
    geemap.Map
        Interactive map object.
    """
    if center is None:
        center = [40.6722, -122.5278]  # Iron Mountain, CA
    
    m = geemap.Map(center=center, zoom=zoom)
    m.add_basemap(basemap)
    
    return m


def add_results_to_map(m: geemap.Map, 
                       results: dict,
                       geometry: ee.Geometry = None,
                       show_diagnostics: bool = False) -> geemap.Map:
    """
    Add AMD analysis results to a map (matches JavaScript layer structure).
    
    Adds layers in the same order as the JavaScript GEE version:
    1. Land AMD Classification (19 classes)
    2. Water Quality Classification (3 classes)
    3. True Color reference
    4. Iron Sulfate Index (diagnostic)
    5. Ferric Iron Index (diagnostic)
    6. MNDWI (diagnostic)
    
    Parameters
    ----------
    m : geemap.Map
        Map object to add layers to.
    results : dict
        Results dictionary from analyze_region().
    geometry : ee.Geometry, optional
        Region to clip visualization to.
    show_diagnostics : bool, default False
        If True, show diagnostic layers visible by default.
    
    Returns
    -------
    geemap.Map
        Map with added layers.
    """
    composite = results['composite']
    
    # ═══════════════════════════════════════════════════════════════════════
    # PRIMARY LAYERS (Visible by default - matches JS)
    # ═══════════════════════════════════════════════════════════════════════
    
    # 1. LAND AMD CLASSIFICATION (19 classes)
    m.addLayer(
        results['land_classification'],
        VIS_LAND_CLASS,
        '🏔️ Land AMD Classification',
        True  # Visible
    )
    
    # 2. WATER QUALITY CLASSIFICATION (3 classes)
    m.addLayer(
        results['water_quality'].select('water_quality'),
        VIS_WATER_QUALITY,
        '🌊 Water Quality Classification',
        True  # Visible
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # REFERENCE LAYERS (Hidden by default - matches JS)
    # ═══════════════════════════════════════════════════════════════════════
    
    # True Color (RGB)
    m.addLayer(
        composite,
        VIS_TRUE_COLOR,
        '📷 True Color (RGB)',
        False  # Hidden
    )
    
    # False Color (NIR-R-G)
    m.addLayer(
        composite,
        VIS_FALSE_COLOR,
        '📷 False Color (NIR-R-G)',
        False  # Hidden
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIAGNOSTIC LAYERS (Hidden by default - matches JS)
    # ═══════════════════════════════════════════════════════════════════════
    
    # Iron Sulfate Index
    m.addLayer(
        results['iron_sulfate'],
        VIS_IRON_SULFATE,
        '🔬 Iron Sulfate Index',
        show_diagnostics
    )
    
    # Ferric Iron 1 Index
    m.addLayer(
        composite.select('FerricIron1'),
        VIS_FERRIC_IRON,
        '🔬 Ferric Iron 1',
        False
    )
    
    # Ferric Iron 2 Index
    m.addLayer(
        composite.select('FerricIron2'),
        {'min': 0, 'max': 5, 'palette': ['#FFFFFF', '#FFFF00', '#FF0000']},
        '🔬 Ferric Iron 2',
        False
    )
    
    # Ferrous Iron Index
    m.addLayer(
        composite.select('FerrousIron'),
        {'min': 0.8, 'max': 1.5, 'palette': ['#FFFFFF', '#00CED1', '#008B8B']},
        '🔬 Ferrous Iron',
        False
    )
    
    # Clay-Sulfate-Mica Index
    m.addLayer(
        composite.select('ClaySulfateMica'),
        {'min': -0.2, 'max': 0.5, 'palette': ['#0000FF', '#FFFFFF', '#90EE90']},
        '🔬 Clay-Sulfate-Mica',
        False
    )
    
    # NDVI (Vegetation)
    m.addLayer(
        composite.select('NDVI'),
        {'min': -0.2, 'max': 0.8, 'palette': ['#8B4513', '#FFFF00', '#228B22']},
        '🔬 NDVI (Vegetation)',
        False
    )
    
    # MNDWI (Water)
    m.addLayer(
        composite.select('MNDWI'),
        VIS_MNDWI,
        '🔬 MNDWI (Water)',
        False
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # WATER QUALITY DIAGNOSTIC LAYERS (Hidden by default - matches JS)
    # ═══════════════════════════════════════════════════════════════════════
    
    # Water Contamination Score (0-7)
    m.addLayer(
        results['water_quality'].select('score'),
        {'min': 0, 'max': 7, 'palette': WATER_SCORE_PALETTE},
        '📊 Water Score (0-7)',
        False
    )
    
    # NIR Anomaly (Water) - MATCHING JS
    m.addLayer(
        composite.select('NIR_Anomaly'),
        {'min': -0.05, 'max': 0.15, 'palette': ['#0000FF', '#FFFFFF', '#FF0000']},
        '🔬 NIR Anomaly (Water)',
        False
    )
    
    # Turbidity Ratio - MATCHING JS
    m.addLayer(
        composite.select('Turbidity'),
        {'min': 0.5, 'max': 3.0, 'palette': ['#0000FF', '#FFFFFF', '#8B4513']},
        '🔬 Turbidity Ratio',
        False
    )
    
    # Iron Water Index
    m.addLayer(
        composite.select('IronWaterIndex'),
        {'min': -0.3, 'max': 0.8, 'palette': ['#0000FF', '#FFFFFF', '#FF0000']},
        '🔬 Iron Water Index',
        False
    )
    
    # Yellow Index
    m.addLayer(
        composite.select('YellowIndex'),
        {'min': 0.8, 'max': 1.5, 'palette': ['#FFFFFF', '#FFFF00', '#FFA500']},
        '🔬 Yellow Index',
        False
    )
    
    # Brightness
    m.addLayer(
        composite.select('Brightness'),
        {'min': 0, 'max': 0.4, 'palette': ['#000000', '#FFFFFF']},
        '🔬 Brightness',
        False
    )
    
    # Add region boundary if provided
    if geometry:
        m.addLayer(geometry, {'color': 'white'}, '📍 Study Area Boundary', False)
    
    return m


def add_legend_to_map(m: geemap.Map) -> geemap.Map:
    """
    Add AMD classification legend to the map.
    
    Parameters
    ----------
    m : geemap.Map
        Map object to add legend to.
    
    Returns
    -------
    geemap.Map
        Map with legend added.
    """
    # Land classification legend
    land_legend_dict = {
        '1: Minor Ferric': '#8B7355',
        '2: Major Ferric Iron': '#FF00FF',
        '3: Ferric±Ferrous': '#800080',
        '4: Ferrous/Chlorite': '#00CED1',
        '5: Clay-Sulfate-Mica': '#90EE90',
        '6: Clay+Minor Ferric': '#FFFF00',
        '7: Clay+Mod Ferric': '#FFA500',
        '8: Clay+Major Ferric': '#FF6347',
        '9: Argillic Alteration (EXTREME)': '#FF1493',
        '10: Clay+Ferrous': '#008B8B',
        '11: Dense Vegetation': '#228B22',
        '12: Major Iron Sulfate (HIGH)': '#FF0000',
        '13: Sparse Veg+Ferric': '#9ACD32',
        '14: Oxidizing Sulfides': '#FFB6C1',
        '17: Proximal Jarosite (HIGH)': '#DC143C',
        '18: Distal Jarosite': '#8B0000',
        '19: Clay+Ferrous+Iron': '#C71585',
    }
    
    m.add_legend(
        title='🏔️ Land AMD Classification',
        legend_dict=land_legend_dict,
        position='bottomright'
    )
    
    return m


def add_water_legend_to_map(m: geemap.Map) -> geemap.Map:
    """
    Add water quality legend to the map.
    
    Parameters
    ----------
    m : geemap.Map
        Map object to add legend to.
    
    Returns
    -------
    geemap.Map
        Map with legend added.
    """
    water_legend_dict = {
        '0: Clean Water': '#1E90FF',
        '1: Moderate Contamination': '#FFA500',
        '2: Severe Contamination': '#FF0000',
    }
    
    m.add_legend(
        title='🌊 Water Quality',
        legend_dict=water_legend_dict,
        position='bottomleft'
    )
    
    return m


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_to_drive(image: ee.Image,
                    description: str,
                    folder: str = "GEE_Exports",
                    region: ee.Geometry = None,
                    scale: int = 30,
                    crs: str = "EPSG:4326",
                    file_format: str = "GeoTIFF",
                    cloud_optimized: bool = True) -> ee.batch.Task:
    """
    Export an image to Google Drive (matching JavaScript export options).
    
    Parameters
    ----------
    image : ee.Image
        Image to export.
    description : str
        Export task description (also used as filename).
    folder : str, default "GEE_Exports"
        Google Drive folder name (matches JavaScript default).
    region : ee.Geometry, optional
        Region to export. Required if image is not bounded.
    scale : int, default 30
        Export resolution in meters.
    crs : str, default "EPSG:4326"
        Coordinate reference system.
    file_format : str, default "GeoTIFF"
        Output file format.
    cloud_optimized : bool, default True
        Whether to create cloud-optimized GeoTIFF (COG).
    
    Returns
    -------
    ee.batch.Task
        Export task (call .start() to begin export).
    """
    # Build format options (matching JavaScript)
    format_options = {}
    if file_format == "GeoTIFF" and cloud_optimized:
        format_options = {'cloudOptimized': True}
    
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description,
        folder=folder,
        fileNamePrefix=description,  # Match JavaScript behavior
        region=region,
        scale=scale,
        crs=crs,
        fileFormat=file_format,
        formatOptions=format_options,
        maxPixels=1e13
    )
    
    return task


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_study_area(name: str) -> ee.Geometry:
    """
    Get a pre-defined study area by name.
    
    Parameters
    ----------
    name : str
        Study area name (see STUDY_AREAS for options).
    
    Returns
    -------
    ee.Geometry
        Study area geometry.
    
    Raises
    ------
    ValueError
        If study area name not found.
    """
    if name not in STUDY_AREAS:
        available = ", ".join(STUDY_AREAS.keys())
        raise ValueError(f"Study area '{name}' not found. Available: {available}")
    
    return STUDY_AREAS[name]


def print_class_legend():
    """Print the AMD classification legend to console."""
    legend = """
    ═══════════════════════════════════════════════════════════════
    AMD DETECTION TOOL - CLASSIFICATION LEGEND
    ═══════════════════════════════════════════════════════════════
    
    IRON SULFATE MINERALS (AMD Indicators):
    ───────────────────────────────────────
    Class  9: Argillic Alteration (Iron+Fe1+Fe2+Clay)     [EXTREME]
    Class 17: Proximal Jarosite (Iron+Fe1+Fe2+Clay)       [HIGH]
    Class 12: Major Iron Sulfate (Iron+Fe1+Clay)          [HIGH]
    Class 18: Distal Jarosite (Iron+Fe2+Clay)             [MODERATE]
    Class 19: Clay + Ferrous + Iron                       [MODERATE]
    Class 14: Oxidizing Sulfides (Iron+Clay)              [HIGH]
    
    CLAY & FERRIC MINERALS:
    ───────────────────────────────────────
    Class  5: Clay-Sulfate-Mica                           [LOW]
    Class  6: Clay + Minor Ferric                         [LOW]
    Class  7: Clay + Moderate Ferric                      [LOW]
    Class  8: Clay + Major Ferric                         [MODERATE]
    Class 10: Clay + Ferrous                              [LOW]
    
    FERRIC/FERROUS IRON:
    ───────────────────────────────────────
    Class  1: Minor Ferric (Hematite)                     [MINIMAL]
    Class  2: Major Ferric Iron                           [LOW]
    Class  3: Ferric + Ferrous                            [LOW]
    Class  4: Ferrous/Chlorite                            [MINIMAL]
    
    VEGETATION:
    ───────────────────────────────────────
    Class 11: Dense Green Vegetation                      [NONE]
    Class 13: Sparse Vegetation + Ferric                  [MINIMAL]
    
    WATER QUALITY SCORES:
    ───────────────────────────────────────
    Score 0   : Clean Water                               [NONE]
    Score 1-2 : Moderate Contamination                    [LOW]
    Score 3-4 : Severe Contamination                      [HIGH]
    Score 5+  : Extreme Contamination                     [EXTREME]
    
    ═══════════════════════════════════════════════════════════════
    """
    print(legend)


def print_version():
    """Print version and credits."""
    print(f"""
    ═══════════════════════════════════════════════════════════════
    AMD Detection Tool v{__version__} (Python/Google Colab Edition)
    ═══════════════════════════════════════════════════════════════
    
    Based on: Rockwell et al. (2021) USGS methodology
    
    Reference:
    Rockwell, B.W., 2021, Mapping acid-generating minerals, 
    acidic drainage, iron sulfate minerals, and other mineral 
    groups using Landsat 8 OLI data, San Juan Mountains, Colorado.
    U.S. Geological Survey Scientific Investigations Map 3466.
    
    ═══════════════════════════════════════════════════════════════
    """)
