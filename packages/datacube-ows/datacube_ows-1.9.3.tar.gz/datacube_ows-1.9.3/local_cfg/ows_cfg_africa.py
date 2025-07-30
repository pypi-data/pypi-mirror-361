# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0



import os
if os.environ.get("DATACUBE_OWS_CFG", "").startswith("local"):
    cfgbase = "local_cfg"
else:
    cfgbase = "config"


reslim_srtm = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 10.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
    },
}

reslim_sentinel2 = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 300.0,  # defaults to 300!
        "max_datasets": 64,  # Defaults to no dataset limit
    },
    "wcs": {
        "max_datasets": 64,  # Defaults to no dataset limit
    },
}

reslim_landsat = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 300.0,  # defaults to 300!
        "max_datasets": 64,  # Defaults to no dataset limit
    },
    "wcs": {
        "max_datasets": 64,  # Defaults to no dataset limit
    },
}
bands_ls8c = {
    "red": [],
    "green": [],
    "blue": [],
    "nir": [],
    "swir_1": [],
    "swir_2": [],
}

legend_idx_0_1_5ticks = {
    "begin": "0.0",
    "end": "1.0",
    "ticks_every": "0.2",
    "units": "unitless",
}

bands_ls = {
    "red": [],
    "green": [],
    "blue": [],
    "nir": ["near_infrared"],
    "swir1": ["shortwave_infrared_1", "near_shortwave_infrared"],
    "swir2": ["shortwave_infrared_2", "far_shortwave_infrared"],
}

bands_sentinel = {
    "B01": ["band_01", "coastal_aerosol"],
    "B02": ["band_02", "blue"],
    "B03": ["band_03", "green"],
    "B04": ["band_04", "red"],
    "B05": ["band_05", "red_edge_1"],
    "B06": ["band_06", "red_edge_2"],
    "B07": ["band_07", "red_edge_3"],
    "B08": ["band_08", "nir", "nir_1"],
    "B8A": ["band_8a", "nir_narrow", "nir_2"],
    "B09": ["band_09", "water_vapour"],
    "B11": ["band_11", "swir_1", "swir_16"],
    "B12": ["band_12", "swir_2", "swir_22"],
    "AOT": ["aerosol_optical_thickness"],
    "WVP": ["scene_average_water_vapour"],
    "SCL": ["mask", "qa"],
}

bands_s2_gm = {
    "B02": ["band_02", "blue"],
    "B03": ["band_03", "green"],
    "B04": ["band_04", "red"],
    "B05": ["band_05", "red_edge_1"],
    "B06": ["band_06", "red_edge_2"],
    "B07": ["band_07", "red_edge_3"],
    "B08": ["band_08", "nir", "nir_1"],
    "B8A": ["band_8a", "nir_narrow", "nir_2"],
    "B11": ["band_11", "swir_1", "swir_16"],
    "B12": ["band_12", "swir_2", "swir_22"],
    "SMAD": ["smad", "sdev"],
    "EMAD": ["emad", "edev"],
    "BCMAD": ["bcmad", "bcdev", "BCDEV"],
    "COUNT": ["count"],
}



bands_fc = {
    "bs": ["BS", "bare_soil"],
    "pv": ["PV", "green_vegetation"],
    "npv": ["NPV", "brown_vegetation"],
    "ue": ["UE", "unmixing_error"],
}



style_fc_simple_rgb = {
    "name": "simple_rgb",
    "title": "Simple RGB",
    "abstract": "Simple true-colour image, using the red, green and blue bands",
    "components": {
        "red": {"BS_PC_50": 1.0},
        "green": {"PV_PC_50": 1.0},
        "blue": {"NPV_PC_50": 1.0},
    },
    "scale_range": [0.0, 100.0],
    "pq_masks": [
        {
            "band": "water",
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
}


style_fc_simple = {
    "name": "simple_fc",
    "title": "Fractional Cover",
    "abstract": "Fractional cover representation, with green vegetation in green, dead vegetation in blue, and bare soil in red",
    "components": {"red": {"BS": 1.0}, "green": {"PV": 1.0}, "blue": {"NPV": 1.0}},
    "scale_range": [0.0, 100.0],
    "pq_masks": [
        {
            "band": "water",
            "flags": {"dry": True},
        },
        {
            "band": "water",
            "flags": {"cloud_shadow": False, "cloud": False}
        },
    ],
    "legend": {
        "url": "https://data.digitalearth.africa/usgs/pc2/ga_ls8c_fractional_cover_2/FC_legend.png",
    },
}

style_fc_unmasked = {
    "name": "simple_fc_unmasked",
    "title": "Fractional Cover",
    "abstract": "Fractional cover representation, with green vegetation in green, dead vegetation in blue, and bare soil in red",
    "components": {"red": {"BS": 1.0}, "green": {"PV": 1.0}, "blue": {"NPV": 1.0}},
    "scale_range": [0.0, 100.0],
    "legend": {
        "url": "https://data.digitalearth.africa/usgs/pc2/ga_ls8c_fractional_cover_2/FC_legend.png",
    },
}

fc_layer = {
    "title": "Fractional Cover (Prototype)",
    "name": "fc_ls",
    "abstract": """
Fractional cover describes the landscape in terms of coverage by green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.) and bare soil. It provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time.
This product has a spatial resolution of 30 m and a temporal coverage of 1980s to current.
It is derived from Landsat Collection 2 surface reflectance product.
Fractional cover allows users to understand the large scale patterns and trends and inform evidence based decision making and policy on topics including wind and water erosion risk, soil carbon dynamics, land surface process monitoring, land management practices, vegetation studies, fuel load estimation, ecosystem modelling, and rangeland condition.
The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information see http://data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Seasonal+Fractional+Cover
This product is accessible through OGC Web Service (https://ows.digitalearth.africa/), for analysis in DE Africa Sandbox JupyterLab (https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/wiki) and for direct download from AWS S3 (https://data.digitalearth.africa/).
""",
    "product_name": "fc_ls",
    "bands": bands_fc,
    "resource_limits": reslim_srtm,
    "dynamic": True,
    "image_processing": {
        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
        "always_fetch_bands": [],
        "manual_merge": False,
    },
    "flags": [
        {
            "product": "wofs_ls",
            "band": "water",
            "fuse_func": "datacube_ows.wms_utils.wofls_fuser",
            "ignore_info_flags": [],
        },
    ],
    "native_crs": "EPSG:4326",
    "native_resolution": [30.0, -30.0],
    "wcs": {
        "default_bands": ["BS", "PV", "NPV"],
    },
    "styling": {
        "default_style": "simple_fc_unmasked",
        "styles": [style_fc_unmasked, style_fc_simple],
    },
}



bands_ls5_st = {
    "ST_B6": ["st"],
    "ST_QA": ["st_qa"],
    "QA_PIXEL": ["pq"]
}
bands_ls7_st = {
    "ST_B6": ["st"],
    "ST_QA": ["st_qa"],
    "QA_PIXEL": ["pq"]
}
bands_ls8_st = {
    "ST_B10": ["st"],
    "ST_QA": ["st_qa"],
    "QA_PIXEL": ["pq"]
}

style_lsc2_st = {
    "name": "surface_temperature",
    "title": "Surface temperature - Celsius",
    "abstract": "Surface temperature in degrees Celsius",
    "index_expression": "(0.00341802*st - 124.15)",
    "mpl_ramp": "magma",
    "range": [0.0, 50.0],
    "legend": {
        "begin": "0.0",
        "end": "50.0",
        "decimal_places": 1,
        "ticks": ["0.0", "10.0", "20.0", "30.0", "40.0", "50.0"],
        "tick_labels": {
            "0.0": {"prefix": "<"},
            "10.0": {"label": "10.0"},
            "20.0": {"label": "20.0"},
            "30.0": {"label": "30.0"},
            "40.0": {"label": "40.0"},
            "50.0": {"prefix": ">"},
        },
    },
}

style_lsc2_st_masked = {
    "name": "surface_temperature_masked",
    "title": "Surface temperature (cloud masked) - Celsius",
    "abstract": "Surface temperature in degrees Celsius",
    "index_expression": "(0.00341802*st - 124.15)",
    "mpl_ramp": "magma",
    "range": [0.0, 50.0],
    "pq_masks": [
        {
            "band": "pq",
            "flags": {
                "clear": True
            },
        },
    ],
    "legend": {
        "begin": "0.0",
        "end": "50.0",
        "decimal_places": 1,
        "ticks": ["0.0", "10.0", "20.0", "30.0", "40.0", "50.0"],
        "tick_labels": {
            "0.0": {"prefix": "<"},
            "10.0": {"label": "10.0"},
            "20.0": {"label": "20.0"},
            "30.0": {"label": "30.0"},
            "40.0": {"label": "40.0"},
            "50.0": {"prefix": ">"},
        },
    },
}

style_lsc2_st_masked_ls8 = {
    "name": "surface_temperature_masked_ls8",
    "title": "Surface temperature (cloud masked) - Celsius",
    "abstract": "Surface temperature in degrees Celsius",
    "index_expression": "(0.00341802*st - 124.15)",
    "mpl_ramp": "magma",
    "range": [0.0, 50.0],
    "pq_masks": [
        {
            "band": "pq",
            "flags": {
                "clear": True,
                "cirrus": "not_high_confidence"
            },
        },
    ],
    "legend": {
        "begin": "0.0",
        "end": "50.0",
        "decimal_places": 1,
        "ticks": ["0.0", "10.0", "20.0", "30.0", "40.0", "50.0"],
        "tick_labels": {
            "0.0": {"prefix": "<"},
            "10.0": {"label": "10.0"},
            "20.0": {"label": "20.0"},
            "30.0": {"label": "30.0"},
            "40.0": {"label": "40.0"},
            "50.0": {"prefix": ">"},
        },
    },
}

style_lsc2_st_qa = {
    "name": "surface_temperature_uncertainty",
    "title": "Surface temperature uncertainty - Celsius",
    "abstract": "Surface temperature uncertainty in degrees Celsius",
    "index_expression": "(0.01*st_qa)",
    "mpl_ramp": "viridis",
    "range": [0.0, 6.0],
    "legend": {
        "begin": "0.0",
        "end": "6.0",
        "decimal_places": 1,
        "ticks": ["0.0", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0"],
        "tick_labels": {
            "0.0": {"label": "0.0"},
            "1.0": {"label": "1.0"},
            "2.0": {"label": "2.0"},
            "3.0": {"label": "3.0"},
            "4.0": {"label": "4.0"},
            "5.0": {"label": "5.0"},
            "6.0": {"prefix": ">"},
        },
    },
}


st_layer_ls8 = {
    "title": "Surface Temperature Landsat 8 (USGS Collection 2)",
    "name": "ls8_st",
    "abstract": """
Surface temperature measures the Earth’s surface temperature and is an important geophysical parameter in global energy balance studies and hydrologic modeling. Surface temperature is also useful for monitoring crop and vegetation health, and extreme heat events such as natural disasters (e.g., volcanic eruptions, wildfires), and urban heat island effects.
DE Africa provides access to Landsat Collection 2 Level-2 Surface Temperature products over Africa. USGS Landsat Collection 2 offers improved processing, geometric accuracy, and radiometric calibration compared to previous Collection 1 products. The Level-2 products are endorsed by the Committee on Earth Observation Satellites (CEOS) to be Analysis Ready Data for Land (CARD4L)-compliant.
More techincal information about the Landsat Surface Temperature product can be found in the User Guide (https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_C2_ST_specs.html).
Landsat 8 product has a spatial resolution of 30 m and a temporal coverage of 2013 to present.
Landsat Level- 2 Surface Temperature Science Product courtesy of the U.S. Geological Survey.
For more information on Landsat products, see https://www.usgs.gov/core-science-systems/nli/landsat/landsat-collection-2-level-2-science-products.
This product is accessible through OGC Web Service (https://ows.digitalearth.africa/), for analysis in DE Africa Sandbox JupyterLab (https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/wiki) and for direct download from AWS S3 (https://data.digitalearth.africa/).
""",
    "product_name": "ls8_st",
    "bands": bands_ls8_st,
    "dynamic": True,
    "resource_limits": reslim_landsat,
    "image_processing": {
        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
        "always_fetch_bands": [],
        "manual_merge": False,  # True
        "apply_solar_corrections": False,
    },
    "flags": [
        {"band": "pq"}
    ],
    "native_crs": "EPSG:4326",
    "native_resolution": [30.0, -30.0],
    "wcs": {
        "default_bands": ["st", "st_qa"],
    },
    "styling": {
        "default_style": "surface_temperature",
        "styles": [
            style_lsc2_st,
            style_lsc2_st_qa,
            style_lsc2_st_masked_ls8
        ],
    },
}

st_layer_ls7 = {
    "title": "Surface Temperature Landsat 7 (USGS Collection 2)",
    "name": "ls7_st",
    "abstract": """
Surface temperature measures the Earth’s surface temperature and is an important geophysical parameter in global energy balance studies and hydrologic modeling. Surface temperature is also useful for monitoring crop and vegetation health, and extreme heat events such as natural disasters (e.g., volcanic eruptions, wildfires), and urban heat island effects.
DE Africa provides access to Landsat Collection 2 Level-2 Surface Temperature products over Africa. USGS Landsat Collection 2 offers improved processing, geometric accuracy, and radiometric calibration compared to previous Collection 1 products. The Level-2 products are endorsed by the Committee on Earth Observation Satellites (CEOS) to be Analysis Ready Data for Land (CARD4L)-compliant.
More techincal information about the Landsat Surface Temperature product can be found in the User Guide (https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_C2_ST_specs.html).
Landsat 7 product has a spatial resolution of 30 m and a temporal coverage of 1999 to present.
Landsat Level- 2 Surface Temperature Science Product courtesy of the U.S. Geological Survey.
For more information on Landsat products, see https://www.usgs.gov/core-science-systems/nli/landsat/landsat-collection-2-level-2-science-products.
This product is accessible through OGC Web Service (https://ows.digitalearth.africa/), for analysis in DE Africa Sandbox JupyterLab (https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/wiki) and for direct download from AWS S3 (https://data.digitalearth.africa/).
""",
    "product_name": "ls7_st",
    "bands": bands_ls7_st,
    "dynamic": True,
    "resource_limits": reslim_landsat,
    "image_processing": {
        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
        "always_fetch_bands": [],
        "manual_merge": False,  # True
        "apply_solar_corrections": False,
    },
    "flags": [
        {"band": "pq"}
    ],
    "native_crs": "EPSG:4326",
    "native_resolution": [30.0, -30.0],
    "wcs": {
        "default_bands": ["st", "st_qa"],
    },
    "styling": {
        "default_style": "surface_temperature",
        "styles": [
            style_lsc2_st,
            style_lsc2_st_qa,
            style_lsc2_st_masked,
        ],
    },
}

st_layer_ls5 = {
    "title": "Surface Temperature Landsat 5 (USGS Collection 2)",
    "name": "ls5_st",
    "abstract": """
Surface temperature measures the Earth’s surface temperature and is an important geophysical parameter in global energy balance studies and hydrologic modeling. Surface temperature is also useful for monitoring crop and vegetation health, and extreme heat events such as natural disasters (e.g., volcanic eruptions, wildfires), and urban heat island effects.
DE Africa provides access to Landsat Collection 2 Level-2 Surface Temperature products over Africa. USGS Landsat Collection 2 offers improved processing, geometric accuracy, and radiometric calibration compared to previous Collection 1 products. The Level-2 products are endorsed by the Committee on Earth Observation Satellites (CEOS) to be Analysis Ready Data for Land (CARD4L)-compliant.
More techincal information about the Landsat Surface Temperature product can be found in the User Guide (https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_C2_ST_specs.html).
Landsat 5 product has a spatial resolution of 30 m and a temporal coverage of 1984 to 2012.
Landsat Level- 2 Surface Temperature Science Product courtesy of the U.S. Geological Survey.
For more information on Landsat products, see https://www.usgs.gov/core-science-systems/nli/landsat/landsat-collection-2-level-2-science-products.
This product is accessible through OGC Web Service (https://ows.digitalearth.africa/), for analysis in DE Africa Sandbox JupyterLab (https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/wiki) and for direct download from AWS S3 (https://data.digitalearth.africa/).
""",
    "product_name": "ls5_st",
    "bands": bands_ls5_st,
    "resource_limits": reslim_landsat,
    "image_processing": {
        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
        "always_fetch_bands": [],
        "manual_merge": False,  # True
        "apply_solar_corrections": False,
    },
    "native_crs": "EPSG:4326",
    "native_resolution": [30.0, -30.0],
    "wcs": {
        "default_bands": ["st", "st_qa"],
    },
    "flags": [
        {"band": "pq"}
    ],
    "styling": {
        "default_style": "surface_temperature",
        "styles": [
            style_lsc2_st,
            style_lsc2_st_qa,
            style_lsc2_st_masked,
        ],
    },
}

folder_st = {
    "title": "Surface Temperature Layers",
    "abstract": "What it says on the tin.",
    "layers": [st_layer_ls5, st_layer_ls7, st_layer_ls8]
}

style_gals_irg = {
    "name": "infrared_green",
    "title": "False colour - Green, SWIR, NIR",
    "abstract": "False Colour image with SWIR1->Red, NIR->Green, and Green->Blue",
    "components": {
        "red": {"swir_1": 1.0},
        "green": {"nir": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

style_s2_irg = {
    "name": "infrared_green",
    "title": "False colour - Green, SWIR, NIR",
    "abstract": "False Colour image with SWIR1->Red, NIR->Green, and Green->Blue",
    "components": {
        "red": {"swir_1": 1.0},
        "green": {"nir": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": [0, 3000],
}

style_ls_irg = {
    "name": "infrared_green",
    "title": "False colour - Green, SWIR, NIR",
    "abstract": "False Colour image with SWIR1->Red, NIR->Green, and Green->Blue",
    "components": {
        "red": {"swir1": 1.0},
        "green": {"nir": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_ls_ndvi = {
    "name": "ndvi",
    "title": "NDVI - Red, NIR",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "nir", "band2": "red"},
    },
    "needed_bands": ["red", "nir"],
    "color_ramp": [
        {"value": -0.0, "color": "#8F3F20", "alpha": 0.0},
        {"value": 0.0, "color": "#8F3F20", "alpha": 1.0},
        {"value": 0.1, "color": "#A35F18"},
        {"value": 0.2, "color": "#B88512"},
        {"value": 0.3, "color": "#CEAC0E"},
        {"value": 0.4, "color": "#E5D609"},
        {"value": 0.5, "color": "#FFFF0C"},
        {"value": 0.6, "color": "#C3DE09"},
        {"value": 0.7, "color": "#88B808"},
        {"value": 0.8, "color": "#529400"},
        {"value": 0.9, "color": "#237100"},
        {"value": 1.0, "color": "#114D04"},
    ],
    "legend": legend_idx_0_1_5ticks,
}

style_ls_ndwi = {
    "name": "ndwi",
    "title": "NDWI - Green, NIR",
    "abstract": "Normalised Difference Water Index - a derived index that correlates well with the existence of water (McFeeters 1996)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "green", "band2": "nir"},
    },
    "needed_bands": ["green", "nir"],
    "color_ramp": [
        {"value": -0.1, "color": "#f7fbff", "alpha": 0.0},
        {"value": 0.0, "color": "#d8e7f5", "legend": {"prefix": "<"}},
        {"value": 0.1, "color": "#b0d2e8"},
        {"value": 0.2, "color": "#73b3d8", "legend": {}},
        {"value": 0.3, "color": "#3e8ec4"},
        {"value": 0.4, "color": "#1563aa", "legend": {}},
        {"value": 0.5, "color": "#08306b", "legend": {"prefix": ">"}},
    ],
    "legend": {
        "begin": "0.0",
        "end": "0.5",
        "decimal_places": 1,
        "ticks": ["0.0", "0.2", "0.4", "0.5"],
        "tick_labels": {
            "0.0": {"prefix": "<"},
            "0.2": {"label": "0.2"},
            "0.4": {"label": "0.4"},
            "0.5": {"prefix": ">"},
        },
    },
}

style_gals_mndwi = {
    "name": "mndwi",
    "title": "MNDWI - Green, SWIR",
    "abstract": "Modified Normalised Difference Water Index - a derived index that correlates well with the existence of water (Xu 2006)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "green", "band2": "swir_1"},
    },
    "needed_bands": ["green", "swir_1"],
    "color_ramp": [
        {"value": -0.1, "color": "#f7fbff", "alpha": 0.0},
        {"value": 0.0, "color": "#d8e7f5"},
        {"value": 0.2, "color": "#b0d2e8"},
        {"value": 0.4, "color": "#73b3d8"},
        {"value": 0.6, "color": "#3e8ec4"},
        {"value": 0.8, "color": "#1563aa"},
        {"value": 1.0, "color": "#08306b"},
    ],
    "legend": legend_idx_0_1_5ticks,
}

style_ls_mndwi = {
    "name": "mndwi",
    "title": "MNDWI - Green, SWIR",
    "abstract": "Modified Normalised Difference Water Index - a derived index that correlates "
    "well with the existence of water (Xu 2006)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "green", "band2": "swir1"},
    },
    "needed_bands": ["green", "swir1"],
    "color_ramp": [
        {"value": -0.1, "color": "#f7fbff", "alpha": 0.0},
        {"value": 0.0, "color": "#d8e7f5"},
        {"value": 0.2, "color": "#b0d2e8"},
        {"value": 0.4, "color": "#73b3d8"},
        {"value": 0.6, "color": "#3e8ec4"},
        {"value": 0.8, "color": "#1563aa"},
        {"value": 1.0, "color": "#08306b"},
    ],
    "legend": legend_idx_0_1_5ticks,
}

style_gals_pure_blue = {
    "name": "blue",
    "title": "Blue - 480",
    "abstract": "Blue band, centered on 480nm",
    "components": {"red": {"blue": 1.0}, "green": {"blue": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": [7272.0, 18181.0],
}

style_ls_pure_blue = {
    "name": "blue",
    "title": "Blue - 480",
    "abstract": "Blue band, centered on 480nm",
    "components": {"red": {"blue": 1.0}, "green": {"blue": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_sentinel_pure_blue = {
    "name": "blue",
    "title": "Blue - 490",
    "abstract": "Blue band, centered on 490nm",
    "components": {"red": {"blue": 1.0}, "green": {"blue": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_gals_pure_green = {
    "name": "green",
    "title": "Green - 560",
    "abstract": "Green band, centered on 560nm",
    "components": {
        "red": {"green": 1.0},
        "green": {"green": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

style_ls_pure_green = {
    "name": "green",
    "title": "Green - 560",
    "abstract": "Green band, centered on 560nm",
    "components": {
        "red": {"green": 1.0},
        "green": {"green": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_ls_simple_rgb = {
    "name": "simple_rgb",
    "title": "Simple RGB",
    "abstract": "Simple true-colour image, using the red, green and blue bands",
    "components": {"red": {"red": 1.0}, "green": {"green": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_gals_simple_rgb = {
    "name": "simple_rgb",
    "title": "Simple RGB",
    "abstract": "Simple true-colour image, using the red, green and blue bands",
    "components": {"red": {"red": 1.0}, "green": {"green": 1.0}, "blue": {"blue": 1.0}},
    # The raw band value range to be compressed to an 8 bit range for the output image tiles.
    # Band values outside this range are clipped to 0 or 255 as appropriate.
    "scale_range": [7272.0, 18181.0],
}


style_gals_pure_red = {
    "name": "red",
    "title": "Red - 660",
    "abstract": "Red band, centered on 660nm",
    "components": {"red": {"red": 1.0}, "green": {"red": 1.0}, "blue": {"red": 1.0}},
    "scale_range": [7272.0, 18181.0],
}

style_ls_pure_red = {
    "name": "red",
    "title": "Red - 660",
    "abstract": "Red band, centered on 660nm",
    "components": {"red": {"red": 1.0}, "green": {"red": 1.0}, "blue": {"red": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_gals_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 840",
    "abstract": "Near infra-red band, centered on 840nm",
    "components": {"red": {"nir": 1.0}, "green": {"nir": 1.0}, "blue": {"nir": 1.0}},
    "scale_range": [7272.0, 18181.0],
}

style_ls_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 840",
    "abstract": "Near infra-red band, centered on 840nm",
    "components": {"red": {"nir": 1.0}, "green": {"nir": 1.0}, "blue": {"nir": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_sentinel_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 870",
    "abstract": "Near infra-red band, centered on 870nm",
    "components": {"red": {"nir": 1.0}, "green": {"nir": 1.0}, "blue": {"nir": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_gals_pure_swir1 = {
    "name": "swir_1",
    "title": "Shortwave Infrared (SWIR) - 1610",
    "abstract": "Short wave infra-red band 1, centered on 1610nm",
    "components": {
        "red": {"swir_1": 1.0},
        "green": {"swir_1": 1.0},
        "blue": {"swir_1": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}


style_s2_pure_swir1 = {
    "name": "swir_1",
    "title": "Shortwave Infrared (SWIR) - 1610",
    "abstract": "Short wave infra-red band 1, centered on 1610nm",
    "components": {"red": {"B11": 1.0}, "green": {"B11": 1.0}, "blue": {"B11": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_ls_pure_swir1 = {
    "name": "swir1",
    "title": "Shortwave Infrared (SWIR) - 1650",
    "abstract": "Short wave infra-red band 1, centered on 1650nm",
    "components": {
        "red": {"swir1": 1.0},
        "green": {"swir1": 1.0},
        "blue": {"swir1": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_sentinel_pure_swir1 = {
    "name": "swir1",
    "title": "Shortwave Infrared (SWIR) - 1610",
    "abstract": "Short wave infra-red band 1, centered on 1610nm",
    "components": {
        "red": {"swir1": 1.0},
        "green": {"swir1": 1.0},
        "blue": {"swir1": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_gals_pure_swir2 = {
    "name": "swir_2",
    "title": "Shortwave Infrared (SWIR) - 2200",
    "abstract": "Short wave infra-red band 2, centered on 2200nm",
    "components": {
        "red": {"swir_2": 1.0},
        "green": {"swir_2": 1.0},
        "blue": {"swir_2": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

style_s2_pure_swir2 = {
    "name": "swir_2",
    "title": "Shortwave Infrared (SWIR) - 2200",
    "abstract": "Short wave infra-red band 2, centered on 2200nm",
    "components": {
        "red": {"swir_2": 1.0},
        "green": {"swir_2": 1.0},
        "blue": {"swir_2": 1.0},
    },
    "scale_range": [0, 3000.0],
}

style_ls_pure_swir2 = {
    "name": "swir2",
    "title": "Shortwave Infrared (SWIR) - 2220",
    "abstract": "Short wave infra-red band 2, centered on 2220nm",
    "components": {
        "red": {"swir2": 1.0},
        "green": {"swir2": 1.0},
        "blue": {"swir2": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_s2_ndci = {
    "name": "ndci",
    "title": "NDCI - Red Edge, Red",
    "abstract": "Normalised Difference Chlorophyll Index - a derived index that correlates well with the existence of chlorophyll",
    "index_function": {
        "function": "datacube_ows.band_utils.sentinel2_ndci",
        "mapped_bands": True,
        "kwargs": {
            "b_red_edge": "red_edge_1",
            "b_red": "red",
            "b_green": "green",
            "b_swir": "swir_2",
        },
    },
    "needed_bands": ["red_edge_1", "red", "green", "swir_2"],
    "color_ramp": [
        {"value": -0.1, "color": "#1696FF"},
        {"value": -0.1, "color": "#1696FF"},
        {"value": 0.0, "color": "#00FFDF"},
        {
            "value": 0.1,
            "color": "#FFF50E",
        },
        {"value": 0.2, "color": "#FFB50A"},
        {
            "value": 0.4,
            "color": "#FF530D",
        },
        {"value": 0.5, "color": "#FF0000"},
    ],
    "legend": {
        "begin": "-0.1",
        "end": "0.5",
        "decimal_places": 1,
        "ticks_every": 0.1,
        "tick_labels": {
            "-0.1": {"prefix": "<"},
            "0.5": {"prefix": ">"},
        },
    },
}

style_s2_pure_aerosol = {
    "name": "aerosol",
    "title": "Narrow Blue - 440",
    "abstract": "Coastal Aerosol or Narrow Blue band, approximately 435nm to 450nm",
    "components": {
        "red": {"coastal_aerosol": 1.0},
        "green": {"coastal_aerosol": 1.0},
        "blue": {"coastal_aerosol": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}


style_s2_pure_redge_1 = {
    "name": "red_edge_1",
    "title": "Vegetation Red Edge - 710",
    "abstract": "Near infra-red band, centred on 710nm",
    "components": {
        "red": {"red_edge_1": 1.0},
        "green": {"red_edge_1": 1.0},
        "blue": {"red_edge_1": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}


style_s2_pure_redge_2 = {
    "name": "red_edge_2",
    "title": "Vegetation Red Edge - 740",
    "abstract": "Near infra-red band, centred on 740nm",
    "components": {
        "red": {"red_edge_2": 1.0},
        "green": {"red_edge_2": 1.0},
        "blue": {"red_edge_2": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}


style_s2_pure_redge_3 = {
    "name": "red_edge_3",
    "title": "Vegetation Red Edge - 780",
    "abstract": "Near infra-red band, centred on 780nm",
    "components": {
        "red": {"red_edge_3": 1.0},
        "green": {"red_edge_3": 1.0},
        "blue": {"red_edge_3": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_s2_pure_narrow_nir = {
    "name": "narrow_nir",
    "title": "Narrow Near Infrared - 870",
    "abstract": "Near infra-red band, centred on 865nm",
    "components": {"red": {"nir": 1.0}, "green": {"nir": 1.0}, "blue": {"nir": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_sentinel_pure_swir2 = {
    "name": "swir2",
    "title": "Shortwave Infrared (SWIR) - 2200",
    "abstract": "Short wave infra-red band 2, centered on 2200nm",
    "components": {
        "red": {"swir2": 1.0},
        "green": {"swir2": 1.0},
        "blue": {"swir2": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_sentinel_count = {
    "name": "count",
    "title": "Included observation count",
    "abstract": "Count of observations included in geomedian/MAD calculations",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "count",
        },
    },
    "needed_bands": ["count"],
    "include_in_feature_info": False,
    "color_ramp": [
        {"value": 0, "color": "#666666", "alpha": 0},
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 0.2,
            "color": "#890000",
            "alpha": 1,
        },
        {"value": 20, "color": "#990000"},
        {"value": 30, "color": "#E38400"},
        {"value": 40, "color": "#E3DF00"},
        {"value": 50, "color": "#A6E300"},
        {"value": 60, "color": "#00E32D"},
        {"value": 70, "color": "#00E3C8"},
        {"value": 80, "color": "#0097E3"},
        {"value": 90, "color": "#005FE3"},
        {"value": 100, "color": "#000FE3"},
        {"value": 110, "color": "#000EA9"},
        {"value": 120, "color": "#5700E3"},
    ],
    "legend": {
        "begin": "0",
        "end": "120",
        "decimal_places": 0,
        "ticks_every": 20,
        "tick_labels": {
            "120": {"prefix": ">"},
        },
    },
}


# styles tmad
sdev_scaling = [0.020, 0.18]
edev_scaling = [6.2, 7.3]
bcdev_scaling = [0.025, 0.13]

style_tmad_sdev_std = {
    "name": "arcsec_sdev",
    "title": "SMAD",
    "abstract": "Good for cropland and forest",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band_arcsec",
        "mapped_bands": True,
        "kwargs": {"band": "sdev", "scale_from": sdev_scaling, "scale_to": [0.0, 4.0]},
    },
    "needed_bands": ["sdev"],
    "mpl_ramp": "coolwarm",
    "range": [0.0, 4.0],
    "legend": {
        "start": "0.0",
        "end": "4.0",
        "ticks": ["0.0", "4.0"],
        "tick_labels": {
            "0.0": {"label": "Low\ntmad"},
            "4.0": {"label": "High\ntmad"},
        },
    },
}

style_tmad_edev_std = {
    "name": "log_edev",
    "title": "EMAD",
    "abstract": "Good for cropland and forest",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band_offset_log",
        "mapped_bands": True,
        "kwargs": {"band": "edev", "scale_from": edev_scaling, "scale_to": [0.0, 4.0]},
    },
    "needed_bands": ["edev"],
    "mpl_ramp": "coolwarm",
    "range": [0.0, 4.0],
    "legend": {
        "start": "0.0",
        "end": "4.0",
        "ticks": ["0.0", "4.0"],
        "tick_labels": {
            "0.0": {"label": "Low\ntmad"},
            "4.0": {"label": "High\ntmad"},
        },
    },
}


style_tmad_bcdev_std = {
    "name": "log_bcdev",
    "title": "BCMAD",
    "abstract": "Good for cropland and forest",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band_offset_log",
        "mapped_bands": True,
        "kwargs": {
            "band": "bcdev",
            "scale_from": bcdev_scaling,
            "scale_to": [0.0, 4.0],
        },
    },
    "needed_bands": ["bcdev"],
    "mpl_ramp": "coolwarm",
    "range": [0.0, 4.0],
    "legend": {
        "start": "0.0",
        "end": "4.0",
        "ticks": ["0.0", "4.0"],
        "tick_labels": {
            "0.0": {"label": "Low\ntmad"},
            "4.0": {"label": "High\ntmad"},
        },
    },
}

style_tmad_rgb_std = {
    "name": "tmad_rgb_std",
    "title": "TMAD multi-band false-colour (standard)",
    "abstract": "Good for cropland and forest",
    "components": {
        "red": {
            "function": "datacube_ows.band_utils.single_band_arcsec",
            "mapped_bands": True,
            "kwargs": {
                "band": "sdev",
                "scale_from": sdev_scaling,
            },
        },
        "green": {
            "function": "datacube_ows.band_utils.single_band_offset_log",
            "mapped_bands": True,
            "kwargs": {
                "band": "edev",
                "scale_from": edev_scaling,
            },
        },
        "blue": {
            "function": "datacube_ows.band_utils.single_band_offset_log",
            "mapped_bands": True,
            "kwargs": {
                "band": "bcdev",
                "scale_from": bcdev_scaling,
            },
        },
    },
    "additional_bands": ["sdev", "bcdev", "edev"],
}

style_tmad_rgb_sens = {
    "inherits": style_tmad_rgb_std,
    "name": "tmad_rgb_sens",
    "title": "TMAD multi-band false-colour (sensitive)",
    "abstract": "Good for arid land and desert",
    "components": {
        "red": {
            "kwargs": {
                "scale_from": [0.0005, 0.11],
            }
        },
        "green": {
            "kwargs": {
                "scale_from": [5.9, 6.9],
            }
        },
        "blue": {
            "kwargs": {
                "scale_from": [0.008, 0.07],
            }
        },
    },
}

styles_ls8c_list = [
    style_gals_simple_rgb,
    style_gals_irg,
    style_gals_pure_blue,
    style_gals_pure_green,
    style_gals_pure_red,
    style_gals_pure_nir,
    style_gals_pure_swir1,
    style_gals_pure_swir2,
]

styles_s2_list = [
    style_ls_simple_rgb,
    style_s2_irg,
    style_ls_ndvi,
    style_ls_ndwi,
    style_gals_mndwi,
    style_s2_ndci,
    style_s2_pure_aerosol,
    style_sentinel_pure_blue,
    style_ls_pure_green,
    style_ls_pure_red,
    style_s2_pure_redge_1,
    style_s2_pure_redge_2,
    style_s2_pure_redge_3,
    style_ls_pure_nir,
    style_s2_pure_narrow_nir,
    style_s2_pure_swir1,
    style_s2_pure_swir2,
]

styles_gm_list = [
    style_ls_simple_rgb,
    style_s2_irg,
    style_ls_ndvi,
    style_ls_ndwi,
    style_gals_mndwi,
    style_s2_ndci,
    style_sentinel_pure_blue,
    style_ls_pure_green,
    style_ls_pure_red,
    style_s2_pure_redge_1,
    style_s2_pure_redge_2,
    style_s2_pure_redge_3,
    style_ls_pure_nir,
    style_s2_pure_narrow_nir,
    style_s2_pure_swir1,
    style_s2_pure_swir2,
    style_sentinel_count,
]

styles_tmads_list = [
    style_tmad_rgb_std,
    style_tmad_rgb_sens,
    style_tmad_sdev_std,
    style_tmad_edev_std,
    style_tmad_bcdev_std,
    style_sentinel_count,
]

styles_sr_list = [
    style_ls_simple_rgb,
    style_ls_irg,
    style_ls_ndvi,
    style_ls_ndwi,
    style_ls_mndwi,
    style_ls_pure_blue,
    style_ls_pure_green,
    style_ls_pure_red,
    style_sentinel_pure_nir,
    style_sentinel_pure_swir1,
    style_sentinel_pure_swir2,
]


layers = {
    "title": "Annual Geometric Median",
    "abstract": "Landsat Geomedian based on USGS Provisional Collection 2 Level 2 Scenes",
    "layers": [
        {
            "title": "Surface Reflectance Annual Geomedian Landsat 8 (Beta)",
            "name": "ga_ls8c_gm_2_annual",
            "abstract": """
Individual remote sensing images can be affected by noisy data, including clouds, cloud shadows, and haze. To produce cleaner images that can be compared more easily across time, we can create 'summary' images or 'composites' that combine multiple images into one image to reveal the median or 'typical' appearance of the landscape for a certain time period. One approach is to create a geomedian. A geomedian is based on a high-dimensional statistic called the 'geometric median' (Small 1990), which effectively trades a temporal stack of poor-quality observations for a single high-quality pixel composite with reduced spatial noise (Roberts et al. 2017).
In contrast to a standard median, a geomedian maintains the relationship between spectral bands. This allows for conducting further analysis on the composite images just as we would on the original satellite images (e.g. by allowing the calculation of common band indices like NDVI). An annual median image is calculated from the surface reflectance values drawn from a calendar year.
This product has a spatial resolution of 30 m and a temporal coverage of 2018. The surface reflectance values are scaled to be between 0 and 65,455.
It is derived from Landsat 8 satellite observations as part of a provisional Landsat Collection 2 surface reflectance product.
Annual geomedian images enable easy visual and algorithmic interpretation, e.g. understanding urban expansion, at annual intervals. They are also useful for characterising permanent landscape features such as woody vegetation.
For more information on the algorithm, see https://doi.org/10.1109/TGRS.2017.2723896
This product is accessible through OGC Web Service (https://ows.digitalearth.africa/), for analysis in DE Africa Sandbox JupyterLab (https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/wiki) and for direct download from AWS S3 (https://data.digitalearth.africa/).
""",
            "product_name": "ga_ls8c_gm_2_annual",
            "time_resolution": "year",
            "bands": bands_ls8c,
            "resource_limits": reslim_srtm,
            "image_processing": {
                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                "always_fetch_bands": [],
                "manual_merge": False,
            },
            "native_crs": "EPSG:6933",
            "native_resolution": [30.0, -30.0],
            "wcs": {
                "default_bands": ["red", "green", "blue"],
            },
            "styling": {
                "default_style": "simple_rgb",
                "styles": styles_ls8c_list,
            },
        },
        {
            "title": "Surface Reflectance Annual Geomedian Sentinel-2 (Beta)",
            "name": "ga_s2_gm",
            "abstract": """
Individual remote sensing images can be affected by noisy data, including clouds, cloud shadows, and haze. To produce cleaner images that can be compared more easily across time, we can create 'summary' images or 'composites' that combine multiple images into one image to reveal the median or 'typical' appearance of the landscape for a certain time period. One approach is to create a geomedian. A geomedian is based on a high-dimensional statistic called the 'geometric median' (Small 1990), which effectively trades a temporal stack of poor-quality observations for a single high-quality pixel composite with reduced spatial noise (Roberts et al. 2017).
In contrast to a standard median, a geomedian maintains the relationship between spectral bands. This allows for conducting further analysis on the composite images just as we would on the original satellite images (e.g. by allowing the calculation of common band indices like NDVI). An annual median image is calculated from the surface reflectance values drawn from a calendar year.
This product has a spatial resolution of 10 m and a temporal coverage of 2019.
It is derived from Surface Reflectance Sentinel-2 data. This product contains modified Copernicus Sentinel data 2019.
Annual geomedian images enable easy visual and algorithmic interpretation, e.g. understanding urban expansion, at annual intervals. They are also useful for characterising permanent landscape features such as woody vegetation.
For more information on the algorithm, see https://doi.org/10.1109/TGRS.2017.2723896
This product is accessible through OGC Web Service (https://ows.digitalearth.africa/), for analysis in DE Africa Sandbox JupyterLab (https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/wiki) and for direct download from AWS S3 (https://data.digitalearth.africa/).
 """,
            "product_name": "gm_s2_annual",
            # Low product name
            #
            # Leave commented until we have an appropriate summary product.
            # (Packaged like the main product, but with much much lower
            # resolution and much much higher area covered in each dataset.
            #
            "low_res_product_name": "gm_s2_annual_lowres",
            "bands": bands_s2_gm,
            "dynamic": False,
            "resource_limits": reslim_sentinel2,
            "time_resolution": "year",
            "image_processing": {
                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                "always_fetch_bands": [],
                "manual_merge": False,  # True
                "apply_solar_corrections": False,
            },
            "native_crs": "EPSG:6933",
            "native_resolution": [10.0, -10.0],
            "wcs": {
                "default_bands": ["red", "green", "blue"],
            },
            "styling": {
                "default_style": "simple_rgb",
                "styles": styles_gm_list,
            },
        },
        {
            "title": "Surface Reflectance Annual Median Absolute Deviations Sentinel-2 (Beta)",
            "name": "ga_s2_tmad",
            "abstract": """
Variability is an important characteric that can be used to map and distinguish different types of land surfaces. The median absolute deviation (MAD) is a robust measure (resilient to outliers) of the variability within a dataset. For multi-spectral Earth observation, deviation can be measured against the geomedian of a time-series using a number of distance metrics. Three of these metrics are adopted in this product: - Euclidean distance (EMAD), which is more sensitive to changes in target brightness. - Cosine (spectral) distance (SMAD), which is more sensitive to changes in target spectral response. - Bray Curtis dissimilarity (BCMAD), which is more sensitive to the distribution of the observation values through time. Together, the triple MADs provide information on variance in the input data over a given time period. The metrics are selected to highlight different types of changes in the landscape.
This product has a spatial resolution of 10 m and a temporal coverage of 2019.
It is derived from Surface Reflectance Sentinel-2 data. This product contains modified Copernicus Sentinel data 2019.
The MADs can be used on their own or together with geomedian to gain insights about the land surface, e.g. for land cover classificiation and for change detection from year to year.
For more information on the algorithm, see https://doi.org/10.1109/IGARSS.2018.8518312
This product is accessible through OGC Web Service (https://ows.digitalearth.africa/), for analysis in DE Africa Sandbox JupyterLab (https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/wiki) and for direct download from AWS S3 (https://data.digitalearth.africa/).
 """,
            "product_name": "gm_s2_annual",
            # Low product name
            #
            # Leave commented until we have an appropriate summary product.
            # (Packaged like the main product, but with much much lower
            # resolution and much much higher area covered in each dataset.
            #
            "low_res_product_name": "gm_s2_annual_lowres",
            "bands": bands_s2_gm,
            "dynamic": False,
            "resource_limits": reslim_sentinel2,
            "time_resolution": "year",
            "image_processing": {
                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                "always_fetch_bands": [],
                "manual_merge": False,  # True
                "apply_solar_corrections": False,
            },
            "native_crs": "EPSG:6933",
            "native_resolution": [10.0, -10.0],
            "wcs": {
                "default_bands": ["red", "green", "blue"],
            },
            "styling": {
                "default_style": "tmad_rgb_std",
                "styles": styles_tmads_list,
            },
        },
    ],
}

semiannual = {
    "title": "Surface Reflectance Semiannual GeoMAD Sentinel-2",
    "name": "gm_s2_semiannual",
    "abstract": """
Individual remote sensing images can be affected by noisy data, such as clouds, cloud shadows, and haze. To produce cleaner images that can be compared more easily across time, we can create 'summary' images or 'composites' that combine multiple images into one image to reveal the median or 'typical' appearance of the landscape for a certain time period.
One approach is to create a geomedian. A geomedian is based on a high-dimensional statistic called the 'geometric median' (Small 1990), which effectively trades a temporal stack of poor-quality observations for a single high-quality pixel composite with reduced spatial noise (Roberts et al. 2017). In contrast to a standard median, a geomedian maintains the relationship between spectral bands. This allows further analysis on the composite images, just as we would on the original satellite images (e.g. by allowing the calculation of common band indices like NDVI). An semiannual geomedian image is calculated from the surface reflectance values drawn from a 6 month period.
In addition, surface reflectance varabilities within the same time period can be measured to support characterization of the land surfaces. The median absolute deviation (MAD) is a robust measure (resilient to outliers) of the variability within a dataset. For multi-spectral Earth observation, deviation can be measured against the geomedian using a number of distance metrics.  Three of these metrics are adopted to highlight different types of changes in the landscape:
- Euclidean distance (EMAD), which is more sensitive to changes in target brightness.
- Cosine (spectral) distance (SMAD), which is more sensitive to changes in target spectral response.
- Bray Curtis dissimilarity (BCMAD), which is more sensitive to the distribution of the observation values through time.
More techincal information about the GeoMAD product can be found in the User Guide (https://docs.digitalearthafrica.org/en/latest/data_specs/GeoMAD_specs.html)
This product has a spatial resolution of 10 m and is available semiannually for 2017 to 2020.
It is derived from Surface Reflectance Sentinel-2 data. This product contains modified Copernicus Sentinel data 2017-2020.
Semiannual geomedian images and the MADs are useful for characterizing landscapes with seasonal changes.
For more information on the algorithm, see https://doi.org/10.1109/TGRS.2017.2723896 and https://doi.org/10.1109/IGARSS.2018.8518312
""",
    "product_name": "gm_s2_semiannual",
    # Low product name
    #
    # Leave commented until we have an appropriate summary product.
    # (Packaged like the main product, but with much much lower
    # resolution and much much higher area covered in each dataset.
    #
    # "low_res_product_name": "gm_s2_annual_lowres",
    "bands": bands_s2_gm,
    "dynamic": False,
    "resource_limits": reslim_sentinel2,
    "time_resolution": "month",
    "image_processing": {
        "extent_mask_func": f"{cfgbase}.africa_s2_local_cfg.lambdas.mask_by_emad_nan",
        # "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
        "always_fetch_bands": ["EMAD"],
        "manual_merge": False,  # True
        "apply_solar_corrections": False,
    },
    "native_crs": "EPSG:6933",
    "native_resolution": [10.0, -10.0],
    "wcs": {
        "default_bands": ["red", "green", "blue"],
    },
    "styling": {
        "default_style": "simple_rgb",
        "styles": styles_gm_list,
    },
}
# Actual Configuration

from local_cfg.africa_ls_sr_local_cfg.layers import layer_ls5, layer_ls7, layer_ls8

ows_cfg = {
    "global": {
        # Master config for all services and products.
        "response_headers": {
            "Access-Control-Allow-Origin": "*",  # CORS header
        },
        "services": {
            "wms": True,
            "wcs": True,
            "wmts": True,
        },
        "published_CRSs": {
            "EPSG:3857": {  # Web Mercator
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:4326": {"geographic": True, "vertical_coord_first": True},  # WGS-84
            "EPSG:3577": {  # GDA-94, INVALID FOR AFRICA!
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:6933": {  # Cylindrical equal area
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "ESRI:102022": {
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
        },
        "allowed_urls": [
            "https://ows.digitalearth.africa",
            "https://ows-latest.digitalearth.africa",
        ],
        # Metadata to go straight into GetCapabilities documents
        "title": "Digital Earth Africa - OGC Web Services",
        "abstract": """Digital Earth Africa OGC Web Services""",
        "info_url": "dea.ga.gov.au/",
        "keywords": [
            "landsat",
            "africa",
            "WOfS",
            "fractional-cover",
            "time-series",
        ],
        "contact_info": {
            "person": "Digital Earth Africa",
            "organisation": "Geoscience Australia",
            "position": "",
            "address": {
                "type": "postal",
                "address": "GPO Box 378",
                "city": "Canberra",
                "state": "ACT",
                "postcode": "2609",
                "country": "Australia",
            },
            "telephone": "+61 2 6249 9111",
            "fax": "",
            "email": "earth.observation@ga.gov.au",
        },
        "fees": "",
        "access_constraints": "© Commonwealth of Australia (Geoscience Australia) 2018. "
        "This product is released under the Creative Commons Attribution 4.0 International Licence. "
        "http://creativecommons.org/licenses/by/4.0/legalcode",
    },  # END OF global SECTION
    "wms": {
        # Config for WMS service, for all products/layers
        "s3_url": "https://data.digitalearth.africa",
        "s3_bucket": "deafrica-data",
        "s3_aws_zone": "ap-southeast-2",
        "max_width": 512,
        "max_height": 512,
    },  # END OF wms SECTION
    "wcs": {
        # Config for WCS service, for all products/coverages
        "default_geographic_CRS": "EPSG:4326",
        "formats": {
            "GeoTIFF": {
                # "renderer": "datacube_ows.wcs_utils.get_tiff",
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_tiff",
                    "2": "datacube_ows.wcs2_utils.get_tiff",
                },
                "mime": "image/geotiff",
                "extension": "tif",
                "multi-time": False,
            },
            "netCDF": {
                # "renderer": "datacube_ows.wcs_utils.get_netcdf",
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_netcdf",
                    "2": "datacube_ows.wcs2_utils.get_netcdf",
                },
                "mime": "application/x-netcdf",
                "extension": "nc",
                "multi-time": True,
            },
        },
        "native_format": "GeoTIFF",
    },  # END OF wcs SECTION
    "layers": [
                #layers, fc_layer, folder_st,
                {
                    "include": f"{cfgbase}.africa_s2_local_cfg.layers.s2_l2a",
                    "type": "python"
                },
                semiannual,
                {
                    "include": f"{cfgbase}.africa_ls_sr_local_cfg.layers.layer_ls5",
                    "type": "python"
                },
                {
                    "include": f"{cfgbase}.africa_ls_sr_local_cfg.layers.layer_ls7",
                    "type": "python"
                },
                {
                    "include": f"{cfgbase}.africa_ls_sr_local_cfg.layers.layer_ls8",
                    "type": "python"
                },
    ]
}

