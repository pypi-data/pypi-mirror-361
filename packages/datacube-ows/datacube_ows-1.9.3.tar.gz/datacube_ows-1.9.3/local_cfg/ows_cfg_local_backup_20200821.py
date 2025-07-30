# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


import copy
# Migration of wms_cfg.py.  As at commit  c44c5e61c7fb9

# Reusable Chunks 1. Resource limit configurations

reslim_landsat = {
    "wms": {
        "zoomed_out_fill_colour": [150,180,200,160],
        "min_zoom_factor": 35.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
    }
}

standard_resource_limits = reslim_landsat

reslim_mangrove = {
    "wms": {
        "zoomed_out_fill_colour": [150,180,200,160],
        "min_zoom_factor": 15.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        "max_datasets": 16, # Defaults to no dataset limit
    }
}

reslim_aster = {
    "wms": {
        "zoomed_out_fill_colour": [150,180,200,160],
        "min_zoom_factor": 10.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
    }
}

reslim_tmad = {
    "wms": {
        "zoomed_out_fill_colour": [150,180,200,160],
        "min_zoom_factor": 15.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
    }    
}

reslim_alos_palsar = {
    "wms": {
        "zoomed_out_fill_colour": [150,180,200,160],
        "min_zoom_factor": 10.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
    }
}

reslim_wofs = reslim_mangrove

reslim_wofs_obs = reslim_landsat

reslim_s2 = reslim_mangrove

reslim_s2_ard = reslim_landsat

reslim_multi_topog = reslim_landsat

reslim_weathering = reslim_mangrove

reslim_frac_cover = reslim_mangrove

reslim_nidem = reslim_mangrove

reslim_item = reslim_mangrove

reslim_wamm = reslim_mangrove

reslim_insar = reslim_nidem

reslim_ls_fc = reslim_aster

reslim_hap = {
    "wms": {
        "zoomed_out_fill_colour": [150,180,200,160],
        "min_zoom_factor": 500.0,
        "max_datasets": 6, 
    },
    "wcs": {
        "max_datasets": 16,
    }
}

# Reusable Chunks 2. Band lists.

bands_ls8 = {
    "red": [],
    "green": [],
    "blue": [ ],
    "nir": [ "near_infrared" ],
    "swir1": [ "shortwave_infrared_1", "near_shortwave_infrared" ],
    "swir2": [ "shortwave_infrared_2", "far_shortwave_infrared" ],
    "coastal_aerosol": [ ],
}

ls8_usgs_level1_bands = {
    "coastal_aerosol": ["band_1"],
    "blue": ["band_2"],
    "green": ["band_3"],
    "red": ["band_4"],
    "nir": ["band_5"],
    "swir1": ["band_6"],
    "swir2": ["band_7"],
    "panchromatic": ["band_8"],
    "cirrus": ["band_9"],
    "lwir1": ["band_10"],
    "lwir2": ["band_11"],
    "quality": ["QUALITY"]
}

bands_ls = {
    "red": [],
    "green": [],
    "blue": [ ],
    "nir": [ "near_infrared" ],
    "swir1": [ "shortwave_infrared_1", "near_shortwave_infrared" ],
    "swir2": [ "shortwave_infrared_2", "far_shortwave_infrared" ],
}

bands_mangrove = {
    "canopy_cover_class": [],
    "extent": [],
}

bands_wofs_filt_sum = {
    "confidence": [],
    "wofs_filtered_summary": []
}

bands_wofs_sum = {
    "count_wet": [],
    "count_clear": [],
    "frequency": [],
}

bands_wofs_obs = {
    "water": [],
}

bands_sentinel2 = {
    "nbar_coastal_aerosol": [ "nbar_narrow_blue" ],
    "nbar_blue": [],
    "nbar_green": [],
    "nbar_red": [],
    "nbar_red_edge_1": [],
    "nbar_red_edge_2": [],
    "nbar_red_edge_3": [],
    "nbar_nir_1":  [ "nbar_near_infrared_1" ],
    "nbar_nir_2":  [ "nbar_near_infrared_2" ],
    "nbar_swir_2": [ "nbar_shortwave_infrared_2" ],
    "nbar_swir_3": [ "nbar_shortwave_infrared_3" ],
    "nbart_coastal_aerosol": [ "coastal_aerosol", "nbart_narrow_blue", "narrow_blue"],
    "nbart_blue": [ "blue" ],
    "nbart_green": [ "green" ],
    "nbart_red": [ "red" ],
    "nbart_red_edge_1": [ "red_edge_1" ],
    "nbart_red_edge_2": [ "red_edge_2" ],
    "nbart_red_edge_3": [ "red_edge_3" ],
    "nbart_nir_1":  [ "nir", "nir_1", "nbart_near_infrared_1" ],
    "nbart_nir_2":  [ "nir_2", "nbart_near_infrared_2" ],
    "nbart_swir_2": [ "swir_2", "nbart_shortwave_infrared_2" ],
    "nbart_swir_3": [ "swir_3", "nbart_shortwave_infrared_3" ],
}

bands_multi_topog = {
    "regional": [], 
    "intermediate": [], 
    "local": [], 
}

bands_weathering = {
    "intensity": [], 
}

bands_fc_percentile = {
    "PV_PC_10": [], 
    "PV_PC_50": [], 
    "PV_PC_90": [], 
    "NPV_PC_10": [], 
    "NPV_PC_50": [], 
    "NPV_PC_90": [], 
    "BS_PC_10": [], 
    "BS_PC_50": [], 
    "BS_PC_90": [], 
}

bands_fc = {
    "BS": [ "bare_soil" ],
    "PV": [ "photosynthetic_vegetation", "green_vegetation" ],
    "NPV": [ "non_photosynthetic_vegetation", "brown_vegetation" ],
}

bands_tmad = {
    "sdev" : [],
    "edev": [],
    "bcdev": [],
}

bands_nidem = { 
    "nidem": [] 
}

bands_item = {
    "relative": [],
}

bands_item_conf = {
    "stddev": [],
}

bands_wamm = {
    "dam_id": [],
}

bands_hap = {
    "Band_1": [],
}

bands_aster = {
    "Band_1": [],
    "Band_2": [],
    "Band_3": [],
}

bands_aster_single_band = {
    "Band_1": [],
}

bands_alos = {
    "hh": [],
    "hv": [],
    "mask": []
}

insar_disp_bands = {
    "ew": [],
    "ud": [],
    "ewstd": [],
    "upstd": []
}

insar_vel_bands = {
    "ew": [],
    "ud": [],
    "ewstd": [],
    "upstd": []
}

# Reusable Chunks 3. Styles

style_ls_simple_rgb = {
        "name": "simple_rgb",
        "title": "Simple RGB",
        "abstract": "Simple true-colour image, using the red, green and blue bands",
        "components": {
            "red": {
                "red": 1.0
            },
            "green": {
                "green": 1.0
            },
            "blue": {
                "blue": 1.0
            }
        },
        "scale_range": [0.0, 3000.0]
}

style_ls_simple_rg = {
        "name": "simple_rg",
        "title": "Simple RG",
        "abstract": "Simple red-green image, using the red, green and blue bands",
        "components": {
            "red": {
                "red": 1.0
            },
            "green": {
                "green": 0.6,
                "blue": 0.4
            },
            "blue": {
            }
        },
        "scale_range": [0.0, 3000.0]
}

style_fc_simple_rgb  = {
        "name": "simple_rgb",
        "title": "Simple RGB",
        "abstract": "Simple true-colour image, using the red, green and blue bands",
        "components": {
            "red": {
                "BS_PC_50": 1.0
            },
            "green": {
                "PV_PC_50": 1.0
            },
            "blue": {
                "NPV_PC_50": 1.0
            }
        },
        "scale_range": [0.0, 100.0],
        "pq_masks": [
            {
                "flags": {
                    'sea': True,
                },
                "invert": True,
            },
        ],    
}
style_ls_irg = {
    "name": "infrared_green",
    "title": "False colour - Green, SWIR, NIR",
    "abstract": "False Colour image with SWIR1->Red, NIR->Green, and Green->Blue",
    "components": {
        "red": {
            "swir1": 1.0
        },
        "green": {
            "nir": 1.0
        },
        "blue": {
            "green": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_ls_rgbndvi = {
    "name": "rgb_ndvi",
    "title": "NDVI plus RGB",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "component_ratio": 0.6,
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nir",
            "band2": "red"
        }
    },
    "needed_bands": ["red", "nir"],
    "components": {
        "red": {
            "red": 1.0
        },
        "green": {
            "green": 1.0
        },
        "blue": {
            "blue": 1.0
        }
    },
    "scale_range": [0.0, 3000.0],
    "color_ramp": [
        {
            "value": -0.00000001,
            "color": "#8F3F20",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 1.0
        },
        {
            "value": 0.1,
            "color": "#A35F18"
        },
        {
            "value": 0.2,
            "color": "#B88512"
        },
        {
            "value": 0.3,
            "color": "#CEAC0E"
        },
        {
            "value": 0.4,
            "color": "#E5D609"
        },
        {
            "value": 0.5,
            "color": "#FFFF0C"
        },
        {
            "value": 0.6,
            "color": "#C3DE09"
        },
        {
            "value": 0.7,
            "color": "#88B808"
        },
        {
            "value": 0.8,
            "color": "#529400"
        },
        {
            "value": 0.9,
            "color": "#237100"
        },
        {
            "value": 1.0,
            "color": "#114D04"
        }
    ],
}

style_ls_ndvi = {
    "name": "ndvi",
    "title": "NDVI - Red, NIR",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nir",
            "band2": "red"
        }
    },
    "needed_bands": ["red", "nir"],
    "color_ramp": [
        {
            "value": -0.00000001,
            "color": "#8F3F20",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 1.0
        },
        {
            "value": 0.1,
            "color": "#A35F18"
        },
        {
            "value": 0.2,
            "color": "#B88512"
        },
        {
            "value": 0.3,
            "color": "#CEAC0E"
        },
        {
            "value": 0.4,
            "color": "#E5D609"
        },
        {
            "value": 0.5,
            "color": "#FFFF0C"
        },
        {
            "value": 0.6,
            "color": "#C3DE09"
        },
        {
            "value": 0.7,
            "color": "#88B808"
        },
        {
            "value": 0.8,
            "color": "#529400"
        },
        {
            "value": 0.9,
            "color": "#237100"
        },
        {
            "value": 1.0,
            "color": "#114D04"
        }
    ],
    "legend": {
       "begin": "0.0",
       #  "end": "1.0",
       "ticks_every": "0.2",

       "units": "unitless",

       "title": "Vegetation Index - Red/NIR",

       "decimal_places": 2,

       "tick_labels": {
           "default": {
               "prefix": "+",
               "suffix": ")"
           },
           "0.0": {
               "prefix": "(",
               "label": "Dead Desert"
           },
           "0.2": {
               "label": "0.2",
               "suffix": ""
           },
           "0.8": {
                "prefix": ":",
                "label": "-" 
           },
           "1.0": {
               "prefix": "(",
               "label": "Lush Jungle"
           }
        }
    }
}


style_ls8_nbr = {
    "name": "NBR",
    "title": "Normalised Burn Ratio",
    "abstract": "Normalised Burn Ratio - a derived index that that uses the differences in the way health green vegetation and burned vegetation reflect light to find burned area",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nir",
            "band2": "swir2"
        }
    },
    "needed_bands": ["nir", "swir2"],
    "color_ramp": [
        {
            "value": -1.0,
            "color": "#67001F",
            "alpha": 0.0,
        },
        {
            "value": -1.0,
            "color": "#67001F",
        },
        {
            "value": -0.8,
            "color": "#B2182B",
        },
        {
            "value": -0.4,
            "color": "#D6604D"
        },
        {
            "value": -0.2,
            "color": "#F4A582"
        },
        {
            "value": -0.1,
            "color": "#FDDBC7"
        },
        {
            "value": 0,
            "color": "#F7F7F7",
        },
        {
            "value": 0.2,
            "color": "#D1E5F0"
        },
        {
            "value": 0.4,
            "color": "#92C5DE"
        },
        {
            "value": 0.6,
            "color": "#4393C3"
        },
        {
            "value": 0.9,
            "color": "#2166AC"
        },
        {
            "value": 1.0,
            "color": "#053061",
        }
    ],
    "legend": {
        "show_legend": True,
        "start": "-1.0",
        "end": "-1.0",
        "ticks": [ "-1.0", "0.0", "1.0" ],
        "tick_labels": {
            "-1.0": { "prefix": "<"},
            "1.0": { "suffix": ">"}
        }
    },
    # Define behaviour(s) for multi-date requests. If not declared, style only supports single-date requests.
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            # The count range for which this handler is to be used - a tuple of two ints, the smallest and
            # largest date counts for which this handler will be used.  Required.
            "allowed_count_range": [2, 2],
            # A function, expressed in the standard format as described elsewhere in this example file.
            # The function is assumed to take one arguments, an xarray Dataset.
            # The function returns an xarray Dataset with a single band, which is the input to the
            # colour ramp defined below.
            "aggregator_function": {
                "function": "datacube_ows.band_utils.multi_date_delta"
            },

           "color_ramp": [
                {
                    "value": -0.5,
                    "color": "#768642",
                    "alpha": 0.0
                },
                {
                    "value": -0.5,
                    "color": "#768642",
                },
                {
                    "value": -0.25,
                    "color": "#768642",
                    "alpha": 1.0,
                },
                {
                    "value": -0.25,
                    "color": "#a4bd5f"
                },
                {
                    "value": -0.1,
                    "color": "#a4bd5f",
                },
                {
                    "value": -0.1,
                    "color": "#00e05d"
                },
                {
                    "value": 0.1,
                    "color": "#00e05d"
                },
                {
                    "value": 0.1,
                    "color": "#fdf950",
                },
                {
                    "value": 0.27,
                    "color": "#fdf950",
                },
                {
                    "value": 0.27,
                    "color": "#ffae52"
                },
                {
                    "value": 0.44,
                    "color": "#ffae52",
                },
                {
                    "value": 0.44,
                    "color": "#ff662e"
                },
                {
                    "value": 0.66,
                    "color": "#ff662e",
                },
                {
                    "value": 0.66,
                    "color": "#ad28cc"
                },
                {
                    "value": 0.88,
                    "color": "#ad28cc",
                },
            ],
            # The multi-date color ramp.  May be defined as an explicit colour ramp, as shown above for the single
            # date case; or may be defined with a range and unscaled color ramp as shown here.
            #
            # The range specifies the min and max values for the color ramp.  Required if an explicit color
            # ramp is not defined.
            # "range": [-1.0, 1.0],
            # The name of a named matplotlib color ramp.
            # Reference here: https://matplotlib.org/examples/color/colormaps_reference.html
            # Only used if an explicit colour ramp is not defined.  Optional - defaults to a simple (but
            # kind of ugly) blue-to-red rainbow ramp.
            # "mpl_ramp": "RdBu",
            # The feature info label for the multi-date index value.
            "feature_info_label": "nbr_delta",
            "legend": {
                "title": "Difference",
                "start": "-0.50",
                "end": "0.88",
                "ticks": ["-0.50", "-0.25", "-0.1", "0.27", "0.44", "0.66", "0.88"],
                "tick_labels": {
                    "-0.50": {"prefix": "<"},
                    "0.88": {"prefix": ">", "label": "1.30"},
                },
                "decimal_places": 2,
            }
        }
    ]
}

style_ls_ndvi_alt1 = {
    "name": "ndvi-alt1",
    "title": "NDVI - Red, NIR (alt1)",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nir",
            "band2": "red"
        }
    },
    "needed_bands": ["red", "nir"],
    "range": [0.0, 1.0],
    "mpl_ramp": "RdBu"
}

style_ls_ndvi_delta = {
    "name": "ndvi-delta",
    "title": "NDVI - Red, NIR (delta)",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nir",
            "band2": "red"
        }
    },
    "needed_bands": ["red", "nir"],
    "range": [0.0, 1.0],
    "mpl_ramp": "RdYlGn",
    "multi_date": [
        {
            "allowed_count_range": [2, 2],
            "aggregator_function": {
                "function": "datacube_ows.band_utils.multi_date_delta",
            },
            "range": [-0.25, 0.25],
            "mpl_ramp": "RdBu",
            "legend": {
                "start": "-1.0",
                "end": "1.0",
                "title": "NDVI Difference",
            }
        }
    ]
}



style_ls_ndvi_alt2 = {
    "name": "ndvi-alt2",
    "title": "NDVI - Red, NIR (alt2)",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nir",
            "band2": "red"
        }
    },
    "needed_bands": ["red", "nir"],
    "range": [0.0, 1.0],
    "mpl_ramp": "winter"
}

style_ls_ndvi_alt3 = {
    "name": "ndvi-alt3",
    "title": "NDVI - Red, NIR (alt2)",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nir",
            "band2": "red"
        }
    },
    "needed_bands": ["red", "nir"],
    "range": [0.0, 1.0],
    "mpl_ramp": "plasma"
}


style_ls_ndwi = {
    "name": "ndwi",
    "title": "NDWI - Green, NIR",
    "abstract": "Normalised Difference Water Index - a derived index that correlates well with the existence of water (McFeeters 1996)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "green",
            "band2": "nir"
        }
    },
    "needed_bands": ["green", "nir"],
    "color_ramp": [
        {
            "value": -0.1,
            "color": "#f7fbff",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#d8e7f5",
            "legend": {
                "prefix": "<"
            }
        },
        {
            "value": 0.1,
            "color": "#b0d2e8"
        },
        {
            "value": 0.2,
            "color": "#73b3d8",
            "legend": { }
        },
        {
            "value": 0.3,
            "color": "#3e8ec4"
        },
        {
            "value": 0.4,
            "color": "#1563aa",
            "legend": { }
        },
        {
            "value": 0.5,
            "color": "#08306b",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "start": "0.0",
        "end": "0.5",
        "ticks": ["0.0", "0.2", "0.4", "0.5"],
        "tick_labels": {
            "0.0": {"prefix": "<", "label": "0"},
            "0.5": {"prefix": ">"},
        }
    }
}

style_ls_mndwi = {
    "name": "mndwi",
    "title": "MNDWI - Green, SWIR",
    "abstract": "Modified Normalised Difference Water Index - a derived index that correlates well with the existence of water (Xu 2006)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "green",
            "band2": "swir1"
        }
    },
    "needed_bands": ["green", "swir1"],
    "color_ramp": [
        {
            "value": -0.1,
            "color": "#f7fbff",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#d8e7f5"
        },
        {
            "value": 0.2,
            "color": "#b0d2e8"
        },
        {
            "value": 0.4,
            "color": "#73b3d8"
        },
        {
            "value": 0.6,
            "color": "#3e8ec4"
        },
        {
            "value": 0.8,
            "color": "#1563aa"
        },
        {
            "value": 1.0,
            "color": "#08306b"
        }
    ]
}

style_ls_pure_blue = {
    "name": "blue",
    "title": "Blue - 480",
    "abstract": "Blue band, centered on 480nm",
    "components": {
        "red": {
            "blue": 1.0
        },
        "green": {
            "blue": 1.0
        },
        "blue": {
            "blue": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_sentinel_pure_blue = {
    "name": "blue",
    "title": "Blue - 490",
    "abstract": "Blue band, centered on 490nm",
    "components": {
        "red": {
            "blue": 1.0
        },
        "green": {
            "blue": 1.0
        },
        "blue": {
            "blue": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_ls_pure_green = {
    "name": "green",
    "title": "Green - 560",
    "abstract": "Green band, centered on 560nm",
    "components": {
        "red": {
            "green": 1.0
        },
        "green": {
            "green": 1.0
        },
        "blue": {
            "green": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_ls_pure_red = {
    "name": "red",
    "title": "Red - 660",
    "abstract": "Red band, centered on 660nm",
    "components": {
        "red": {
            "red": 1.0
        },
        "green": {
            "red": 1.0
        },
        "blue": {
            "red": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_ls_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 840",
    "abstract": "Near infra-red band, centered on 840nm",
    "components": {
        "red": {
            "nir": 1.0
        },
        "green": {
            "nir": 1.0
        },
        "blue": {
            "nir": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_sentinel_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 870",
    "abstract": "Near infra-red band, centered on 870nm",
    "components": {
        "red": {
            "nir": 1.0
        },
        "green": {
            "nir": 1.0
        },
        "blue": {
            "nir": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_ls_pure_swir1 = {
    "name": "swir1",
    "title": "Shortwave Infrared (SWIR) - 1650",
    "abstract": "Short wave infra-red band 1, centered on 1650nm",
    "components": {
        "red": {
            "swir1": 1.0
        },
        "green": {
            "swir1": 1.0
        },
        "blue": {
            "swir1": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_sentinel_pure_swir1 = {
    "name": "swir1",
    "title": "Shortwave Infrared (SWIR) - 1610",
    "abstract": "Short wave infra-red band 1, centered on 1610nm",
    "components": {
        "red": {
            "swir1": 1.0
        },
        "green": {
            "swir1": 1.0
        },
        "blue": {
            "swir1": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_ls_pure_swir2 = {
    "name": "swir2",
    "title": "Shortwave Infrared (SWIR) - 2220",
    "abstract": "Short wave infra-red band 2, centered on 2220nm",
    "components": {
        "red": {
            "swir2": 1.0
        },
        "green": {
            "swir2": 1.0
        },
        "blue": {
            "swir2": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_sentinel_pure_swir2 = {
    "name": "swir2",
    "title": "Shortwave Infrared (SWIR) - 2200",
    "abstract": "Short wave infra-red band 2, centered on 2200nm",
    "components": {
        "red": {
            "swir2": 1.0
        },
        "green": {
            "swir2": 1.0
        },
        "blue": {
            "swir2": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_nd_ferric_iron = {
    "name": "nd_ferric_iron",
    "title": "Ferric Iron",
    "abstract": "Normalised Difference Ferric Iron Index - a derived index that correlates well with the existence of Ferric Iron Content",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "red",
            "band2": "blue"
        }
    },
    "needed_bands": [ 'red', 'blue' ],
    "color_ramp": [
        {
            "value": -0.1,
            "color": "#3B97C3",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#6EA9B0",
            "alpha": 1.0
        },
        {
            "value": 0.1,
            "color": "#83B3A9"
        },
        {
            "value": 0.2,
            "color": "#9FC29D"
        },
        {
            "value": 0.3,
            "color": "#F3F56C"
        },
        {
            "value": 0.4,
            "color": "#FCDE56"
        },
        {
            "value": 0.5,
            "color": "#FCC54C"
        },
        {
            "value": 0.6,
            "color": "#F77F2F"
        },
        {
            "value": 0.7,
            "color": "#F55F25"
        },
        {
            "value": 0.8,
            "color": "#F25622"
        },
        {
            "value": 0.9,
            "color": "#EB1E15"
        },
        {
            "value": 1.0,
            "color": "#E81515"
        }
    ]
}

style_nd_soil = {
    "name": "nd_soil",
    "title": "Normalised Difference Soil Index",
    "abstract": "Normalised Difference Soil Index - a derived index that correlates well with the existence of bare Soil/Rock",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "swir1",
            "band2": "nir"
        }
    },
    "needed_bands": ["nir", "swir1"],
    "color_ramp": [
        {
            "value": -0.1,
            "color": "#f7fbff",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#d8e7f5"
        },
        {
            "value": 0.2,
            "color": "#b0d2e8"
        },
        {
            "value": 0.4,
            "color": "#73b3d8"
        },
        {
            "value": 0.6,
            "color": "#3e8ec4"
        },
        {
            "value": 0.8,
            "color": "#1563aa"
        },
        {
            "value": 1.0,
            "color": "#08306b"
        }
    ]
}

style_nd_clay_mica = {
    "name": "nd_clay_mica",
    "title": "Clay and Mica Minerals",
    "abstract": "Normalised Difference Clay and Mica Minerals Index - a derived index that correlates well with the existence of hydroxyl bearing minerals (clay and mica minerals)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "swir1",
            "band2": "swir2"
        }
    },
    "needed_bands": ["swir1", "swir2"],
    "color_ramp": [
        {
            "value": -0.1,
            "color": "#ffffb2",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#ffef97",
            "alpha": 1.0
        },
        {
            "value": 0.1,
            "color": "#ffe07d"
        },
        {
            "value": 0.2,
            "color": "#fecc5c"
        },
        {
            "value": 0.3,
            "color": "#feb450"
        },
        {
            "value": 0.4,
            "color": "#fd8d3c"
        },
        {
            "value": 0.5,
            "color": "#f86b30"
        },
        {
            "value": 0.6,
            "color": "#f44f26"
        },
        {
            "value": 0.7,
            "color": "#f03b20"
        },
        {
            "value": 0.8,
            "color": "#de2522"
        },
        {
            "value": 0.9,
            "color": "#cc1024"
        },
        {
            "value": 1.0,
            "color": "#bd0026"
        }
    ]
}

style_mangrove_cover_v2 = {
    "name": "mangrove",
    "title": "Mangrove Cover",
    "abstract": "",
    "value_map": {
        "canopy_cover_class": [
            {
                "title": "Not Observed",
                "abstract": "(Clear Obs < 3)",
                "flags": {
                    "notobserved": True
                },
                "color": "#BDBDBD"
            },
            {
                "title": "Woodland",
                "abstract": "(20% - 50% cover)",
                "flags": {
                    "woodland": True
                },
                "color": "#9FFF4C"
            },
            {
                "title": "Open Forest",
                "abstract": "(50% - 80% cover)",
                "flags": {
                    "open_forest": True
                },
                "color": "#5ECC00"
            },
            {
                "title": "Closed Forest",
                "abstract": "(>80% cover)",
                "flags": {
                    "closed_forest": True
                },
                "color": "#3B7F00"
            },
        ]
    },
    "legend": {}
}

style_wofs_filt_freq = {
    "name": "WOfS_filtered_frequency",
    "title": "Filtered Water Summary",
    "abstract": "WOfS filtered summary showing the frequency of Wetness",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "wofs_filtered_summary",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["wofs_filtered_summary"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.002,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.005,
            "color": "#8e0101",
            "alpha": 0.25
        },
        {
            "value": 0.01,
            "color": "#cf2200",
            "alpha": 0.75
        },
        {
            "value": 0.02,
            "color": "#e38400"
        },
        {
            "value": 0.05,
            "color": "#e3df00"
        },
        {
            "value": 0.1,
            "color": "#a6e300"
        },
        {
            "value": 0.2,
            "color": "#62e300"
        },
        {
            "value": 0.3,
            "color": "#00e32d"
        },
        {
            "value": 0.4,
            "color": "#00e384"
        },
        {
            "value": 0.5,
            "color": "#00e3c8"
        },
        {
            "value": 0.6,
            "color": "#00c5e3"
        },
        {
            "value": 0.7,
            "color": "#0097e3"
        },
        {
            "value": 0.8,
            "color": "#005fe3"
        },
        {
            "value": 0.9,
            "color": "#000fe3"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "url": "https://data.dea.ga.gov.au/WOfS/filtered_summary/v2.1.0/wofs_full_summary_legend.png",
    }
}

style_wofs_filt_freq_blue = {
    "name": "WOfS_filtered_frequency_blues_transparent",
    "title": "Water Summary (Blue)",
    "abstract": "WOfS filtered summary showing the frequency of Wetness",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "wofs_filtered_summary",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["wofs_filtered_summary"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#ffffff",
            "alpha": 0.0,
        },
        {
            "value": 0.001,
            "color": "#d5fef9",
            "alpha": 0.0,
        },
        {
            "value": 0.02,
            "color": "#d5fef9",
        },
        {
            "value": 0.2,
            "color": "#71e3ff"
        },
        {
            "value": 0.4,
            "color": "#01ccff"
        },
        {
            "value": 0.6,
            "color": "#0178ff"
        },
        {
            "value": 0.8,
            "color": "#2701ff"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "units": "%",
        "radix_point": 0,
        "scale_by": 100.0,
        "major_ticks": 0.1
    }
}

style_wofs_count_wet = {
    "name": "water_observations",
    "title": "Wet Count",
    "abstract": "WOfS summary showing the count of water observations",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "count_wet",
        }
    },
    "needed_bands": ["count_wet"],
    "include_in_feature_info": False,
    "color_ramp": [
        {
            "value": 0,
            "color": "#666666",
            "alpha": 0
        },
        {
            "value": 2,
            "color": "#890000"
        },
        {
            "value": 5,
            "color": "#990000"
        },
        {
            "value": 10,
            "color": "#E38400"
        },
        {
            "value": 25,
            "color": "#E3DF00"
        },
        {
            "value": 50,
            "color": "#A6E300"
        },
        {
            "value": 100,
            "color": "#00E32D"
        },
        {
            "value": 150,
            "color": "#00E3C8"
        },
        {
            "value": 200,
            "color": "#0097E3"
        },
        {
            "value": 250,
            "color": "#005FE3"
        },
        {
            "value": 300,
            "color": "#000FE3"
        },
        {
            "value": 350,
            "color": "#000EA9"
        },
        {
            "value": 400,
            "color": "#5700E3",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "radix_point": 0,
        "scale_by": 1,
        "major_ticks": 100
    }
}

style_wofs_count_clear = {
    "name": "clear_observations",
    "title": "Clear Count",
    "abstract": "WOfS summary showing the count of clear observations",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "count_clear",
        }
    },
    "needed_bands": ["count_clear"],
    "include_in_feature_info": False,
    "color_ramp": [
        {
            "value": 0,
            "color": "#FFFFFF",
            "alpha": 0
        },
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 10,
            "color": "#b21800",
            "alpha": 1
        },
        {
            "value": 100,
            "color": "#ef8500"
        },
        {
            "value": 200,
            "color": "#ffb800"
        },
        {
            "value": 300,
            "color": "#ffd300"
        },
        {
            "value": 400,
            "color": "#ffe300"
        },
        {
            "value": 500,
            "color": "#fff300"
        },
        {
            "value": 600,
            "color": "#d0f800"
        },
        {
            "value": 700,
            "color": "#a0fd00"
        },
        {
            "value": 800,
            "color": "#6ee100"
        },
        {
            "value": 901,
            "color": "#39a500"
        },
        {
            "value": 1000,
            "color": "#026900",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "radix_point": 0,
        "scale_by": 1,
        "major_ticks": 100,
        "axes_position": [0.05, 0.5, 0.89, 0.15]
    }
}


style_wofs_frequency = {
    "name": "WOfS_frequency",
    "title": " Water Summary",
    "abstract": "WOfS summary showing the frequency of Wetness",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "frequency",
        }
    },
    "needed_bands": ["frequency"],
    "include_in_feature_info": False,
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.002,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.005,
            "color": "#8e0101",
            "alpha": 0.25
        },
        {
            "value": 0.01,
            "color": "#cf2200",
            "alpha": 0.75
        },
        {
            "value": 0.02,
            "color": "#e38400"
        },
        {
            "value": 0.05,
            "color": "#e3df00"
        },
        {
            "value": 0.1,
            "color": "#a6e300"
        },
        {
            "value": 0.2,
            "color": "#62e300"
        },
        {
            "value": 0.3,
            "color": "#00e32d"
        },
        {
            "value": 0.4,
            "color": "#00e384"
        },
        {
            "value": 0.5,
            "color": "#00e3c8"
        },
        {
            "value": 0.6,
            "color": "#00c5e3"
        },
        {
            "value": 0.7,
            "color": "#0097e3"
        },
        {
            "value": 0.8,
            "color": "#005fe3"
        },
        {
            "value": 0.9,
            "color": "#000fe3"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "url": "https://data.dea.ga.gov.au/WOfS/filtered_summary/v2.1.0/wofs_full_summary_legend.png",
    }
}

style_wofs_frequency_blue = {
    "name": "WOfS_frequency_blues_transparent",
    "title": "Water Summary (Blue)",
    "abstract": "WOfS summary showing the frequency of Wetness",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "frequency",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["frequency"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#ffffff",
            "alpha": 0.0,
        },
        {
            "value": 0.001,
            "color": "#d5fef9",
            "alpha": 0.0,
        },
        {
            "value": 0.02,
            "color": "#d5fef9",
        },
        {
            "value": 0.2,
            "color": "#71e3ff"
        },
        {
            "value": 0.4,
            "color": "#01ccff"
        },
        {
            "value": 0.6,
            "color": "#0178ff"
        },
        {
            "value": 0.8,
            "color": "#2701ff"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "units": "%",
        "radix_point": 0,
        "scale_by": 100.0,
        "major_ticks": 0.1
    }

}

style_wofs_confidence = {
    "name": "wofs_confidence",
    "title": "Confidence",
    "abstract": "WOfS Confidence",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "confidence",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["confidence"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#000000",
        },
        {
            "value": 0.01,
            "color": "#000000"
        },
        {
            "value": 0.02,
            "color": "#990000"
        },
        {
            "value": 0.05,
            "color": "#CF2200"
        },
        {
            "value": 0.1,
            "color": "#E38400"
        },
        {
            "value": 0.25,
            "color": "#E3DF00"
        },
        {
            "value": 0.5,
            "color": "#A6E300"
        },
        {
            "value": 0.75,
            "color": "#62E300"
        },
        {
            "value": 1.0,
            "color": "#00E32D"
        }
    ],
    "legend": {
        "units": "%",
        "radix_point": 0,
        "scale_by": 100.0,
        "major_ticks": 0.25
    }
}

style_wofs_seasonal_wet = {
    "name": "seasonal_water_observations",
    "title": "Wet Count",
    "abstract": "WOfS seasonal summary showing the count of water observations",
    "needed_bands": ["count_wet"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "count_wet",
        }
    },
    "color_ramp": [
        {
            "value": 0,
            "color": "#666666",
            "alpha": 0
        },
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 0.2,
            "color": "#990000",
            "alpha": 1
        },
        {
            "value": 2,
            "color": "#990000"
        },
        {
            "value": 4,
            "color": "#E38400"
        },
        {
            "value": 6,
            "color": "#E3DF00"
        },
        {
            "value": 8,
            "color": "#00E32D"
        },
        {
            "value": 10,
            "color": "#00E3C8"
        },
        {
            "value": 12,
            "color": "#0097E3"
        },
        {
            "value": 14,
            "color": "#005FE3"
        },
        {
            "value": 16,
            "color": "#000FE3"
        },
        {
            "value": 18,
            "color": "#000EA9"
        },
        {
            "value": 20,
            "color": "#5700E3",
        }
    ],
    "legend": {
        "decimal_places": 0,
        "start": "0",
        "end": "20",
        "ticks_every": "10",
        "tick_labels": {
            "20": {"prefix": ">"},
        }
    }
}

style_wofs_summary_wet = {
    "name": "annual_water_observations",
    "title": "Wet Count",
    "abstract": "WOfS annual summary showing the count of water observations",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "count_wet",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["count_wet"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#666666",
            "alpha": 0
        },
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 0.2,
            "color": "#990000",
            "alpha": 1
        },
        {
            "value": 2,
            "color": "#990000"
        },
        {
            "value": 4,
            "color": "#E38400"
        },
        {
            "value": 6,
            "color": "#E3DF00"
        },
        {
            "value": 8,
            "color": "#00E32D"
        },
        {
            "value": 10,
            "color": "#00E3C8"
        },
        {
            "value": 12,
            "color": "#0097E3"
        },
        {
            "value": 14,
            "color": "#005FE3"
        },
        {
            "value": 16,
            "color": "#000FE3"
        },
        {
            "value": 18,
            "color": "#000EA9"
        },
        {
            "value": 20,
            "color": "#5700E3",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "radix_point": 0,
        "scale_by": 1,
        "major_ticks": 10
    }
}

style_wofs_summary_clear = {
    "name": "annual_clear_observations",
    "title": "Clear Count",
    "abstract": "WOfS annual summary showing the count of clear observations",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "count_clear",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["count_clear"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#FFFFFF",
            "alpha": 0
        },
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 0.2,
            "color": "#B21800",
            "alpha": 1
        },
        {
            "value": 1,
            "color": "#B21800"
        },
        {
            "value": 4,
            "color": "#ef8500"
        },
        {
            "value": 8,
            "color": "#ffb800"
        },
        {
            "value": 10,
            "color": "#ffd000"
        },
        {
            "value": 13,
            "color": "#fff300"
        },
        {
            "value": 16,
            "color": "#fff300"
        },
        {
            "value": 20,
            "color": "#c1ec00"
        },
        {
            "value": 24,
            "color": "#6ee100"
        },
        {
            "value": 28,
            "color": "#39a500"
        },
        {
            "value": 30,
            "color": "#026900",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "radix_point": 0,
        "scale_by": 1,
        "major_ticks": 10,
        "axes_position": [0.05, 0.5, 0.89, 0.15]
    }
}

style_wofs_seasonal_clear = {
    "name": "seasonal_clear_observations",
    "title": "Clear Count",
    "abstract": "WOfS seasonal summary showing the count of clear observations",
    "needed_bands": ["count_clear"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "count_clear",
        }
    },
    "color_ramp": [
        {
            "value": 0,
            "color": "#FFFFFF",
            "alpha": 0
        },
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 0.2,
            "color": "#B21800",
            "alpha": 1
        },
        {
            "value": 1,
            "color": "#B21800"
        },
        {
            "value": 4,
            "color": "#ef8500"
        },
        {
            "value": 8,
            "color": "#ffb800"
        },
        {
            "value": 10,
            "color": "#ffd000"
        },
        {
            "value": 13,
            "color": "#fff300"
        },
        {
            "value": 16,
            "color": "#fff300"
        },
        {
            "value": 20,
            "color": "#c1ec00"
        },
        {
            "value": 24,
            "color": "#6ee100"
        },
        {
            "value": 28,
            "color": "#39a500"
        },
        {
            "value": 30,
            "color": "#026900",
        }
    ],
    "legend": {
        "decimal_places": 0,
        "start": "0",
        "end": "30",
        "ticks_every": "10",
        "ticks_labels": {
            "30": {"prefix": "<"}
        },
        "strip_location": [0.05, 0.5, 0.89, 0.15]
    }
}

style_annual_wofs_summary_frequency = {
    "name": "annual_WOfS_frequency",
    "title": "Water Summary",
    "abstract": "WOfS annual summary showing the frequency of Wetness",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "frequency",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["frequency"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.02,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.05,
            "color": "#8e0101",
            "alpha": 0.25
        },
        {
            "value": 0.1,
            "color": "#cf2200",
            "alpha": 0.75
        },
        {
            "value": 0.2,
            "color": "#e38400"
        },
        {
            "value": 0.3,
            "color": "#e3df00"
        },
        {
            "value": 0.4,
            "color": "#62e300"
        },
        {
            "value": 0.5,
            "color": "#00e32d"
        },
        {
            "value": 0.6,
            "color": "#00e3c8"
        },
        {
            "value": 0.7,
            "color": "#0097e3"
        },
        {
            "value": 0.8,
            "color": "#005fe3"
        },
        {
            "value": 0.9,
            "color": "#000fe3"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "units": "%",
        "decimal_places": 1,
        "begin": "0.0",
        "end": "1.0",
        "ticks_every": "0.2",
        "tick_labels": {
            "0.0": {"label": "0"},
            "0.2": {"label": "20"},
            "0.4": {"label": "40"},
            "0.6": {"label": "60"},
            "0.8": {"label": "80"},
            "1.0": {"label": "100"},
        }
    } 
}

style_seasonal_wofs_summary_frequency = {
    "name": "seasonal_WOfS_frequency",
    "title": " Water Summary",
    "abstract": "WOfS seasonal summary showing the frequency of Wetness",
    "needed_bands": ["frequency"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "frequency",
        }
    },
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.02,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 0.05,
            "color": "#8e0101",
            "alpha": 0.25
        },
        {
            "value": 0.1,
            "color": "#cf2200",
            "alpha": 0.75
        },
        {
            "value": 0.2,
            "color": "#e38400"
        },
        {
            "value": 0.3,
            "color": "#e3df00"
        },
        {
            "value": 0.4,
            "color": "#62e300"
        },
        {
            "value": 0.5,
            "color": "#00e32d"
        },
        {
            "value": 0.6,
            "color": "#00e3c8"
        },
        {
            "value": 0.7,
            "color": "#0097e3"
        },
        {
            "value": 0.8,
            "color": "#005fe3"
        },
        {
            "value": 0.9,
            "color": "#000fe3"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "units": "%",
        "decimal_places": 1,
        "start": "0.0",
        "end": "1.0",
        "ticks_every": "0.1",
        "tick_labels": {
            "0.0": "0",
            "0.1": "10",
            "0.2": "20",
            "0.3": "30",
            "0.4": "40",
            "0.5": "50",
            "0.6": "60",
            "0.6": "60",
            "0.7": "70",
            "0.8": "80",
            "0.9": "90",
            "1.0": "100",
        }
    } 
}

style_annual_wofs_summary_frequency_blue = {
    "name": "annual_WOfS_frequency_blues_transparent",
    "title": "Water Summary (Blue)",
    "abstract": "WOfS annual summary showing the frequency of Wetness",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "frequency",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["frequency"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#ffffff",
            "alpha": 0.0,
        },
        {
            "value": 0.001,
            "color": "#d5fef9",
            "alpha": 0.0,
        },
        {
            "value": 0.02,
            "color": "#d5fef9",
        },
        {
            "value": 0.2,
            "color": "#71e3ff"
        },
        {
            "value": 0.4,
            "color": "#01ccff"
        },
        {
            "value": 0.6,
            "color": "#0178ff"
        },
        {
            "value": 0.8,
            "color": "#2701ff"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "units": "%",
        "decimal_places": 1,
        "start": "0.0",
        "end": "1.0",
        "ticks_every": "0.1",
        "tick_labels": {
            "0.0": "0",
            "0.1": "10",
            "0.2": "20",
            "0.3": "30",
            "0.4": "40",
            "0.5": "50",
            "0.6": "60",
            "0.6": "60",
            "0.7": "70",
            "0.8": "80",
            "0.9": "90",
            "1.0": "100",
        }
    } 
}

style_seasonal_wofs_summary_frequency_blue = {
    "name": "seasonal_WOfS_frequency_blues_transparent",
    "title": "Water Summary (Blue)",
    "abstract": "WOfS seasonal summary showing the frequency of Wetness",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "frequency",
        }
    },
    "needed_bands": ["frequency"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#ffffff",
            "alpha": 0.0,
        },
        {
            "value": 0.001,
            "color": "#d5fef9",
            "alpha": 0.0,
        },
        {
            "value": 0.02,
            "color": "#d5fef9",
        },
        {
            "value": 0.2,
            "color": "#71e3ff"
        },
        {
            "value": 0.4,
            "color": "#01ccff"
        },
        {
            "value": 0.6,
            "color": "#0178ff"
        },
        {
            "value": 0.8,
            "color": "#2701ff"
        },
        {
            "value": 1.0,
            "color": "#5700e3"
        }
    ],
    "legend": {
        "units": "%",
        "decimal_places": 1,
        "start": "0.0",
        "end": "1.0",
        "ticks_every": "0.1",
        "tick_labels": {
            "0.0": "0",
            "0.1": "10",
            "0.2": "20",
            "0.3": "30",
            "0.4": "40",
            "0.5": "50",
            "0.6": "60",
            "0.6": "60",
            "0.7": "70",
            "0.8": "80",
            "0.9": "90",
            "1.0": "100",
        }
    } 
}

style_wofs_obs = {
    "name": "observations",
    "title": "Observations",
    "abstract": "Observations",
    "value_map": {
        "water": [
            {
                "title": "Invalid",
                "abstract": "Slope or Cloud",
                "flags": {
                    "or": {
                      "terrain_or_low_angle": True,
                      "cloud_shadow": True,
                      "cloud": True,
                      "high_slope": True,
                      "noncontiguous": True
                    }
                },
                "color": "#707070"
            },
            {
                # Possible Sea Glint, also mark as invalid
                "title": "",
                "abstract": "",
                "flags": {
                    "dry": True,
                    "sea": True
                },
                "color": "#707070"
            },
            {
                "title": "Dry",
                "abstract": "Dry",
                "flags": {
                    "dry": True,
                    "sea": False,
                },
                "color": "#D99694"
            },
            {
                "title": "Wet",
                "abstract": "Wet or Sea",
                "flags": {
                  "or": {
                    "wet": True,
                    "sea": True
                  }
                },
                "color": "#4F81BD"
            }
        ]
    }
}

style_wofs_obs_wet_only = {
    "name": "wet",
    "title": "Wet Only",
    "abstract": "Wet Only",
    "value_map": {
        "water": [
            {
                "title": "Invalid",
                "abstract": "Slope or Cloud",
                "flags": {
                    "or": {
                      "terrain_or_low_angle": True,
                      "cloud_shadow": True,
                      "cloud": True,
                      "high_slope": True,
                      "noncontiguous": True
                    }
                },
                "color": "#707070",
                "mask": True
            },
            {
                # Possible Sea Glint, also mark as invalid
                "title": "",
                "abstract": "",
                "flags": {
                    "dry": True,
                    "sea": True
                },
                "color": "#707070",
                "mask": True
            },
            {
                "title": "Dry",
                "abstract": "Dry",
                "flags": {
                    "dry": True,
                    "sea": False,
                },
                "color": "#D99694",
                "mask": True
            },
            {
                "title": "Wet",
                "abstract": "Wet or Sea",
                "flags": {
                  "or": {
                    "wet": True,
                    "sea": True
                  }
                },
                "color": "#4F81BD"
            }
        ]
    }
}

style_s2_simple_rgb = style_ls_simple_rgb
style_s2_irg = {
    "name": "infrared_green",
    "title": "False colour - Green, SWIR, NIR",
    "abstract": "False Colour image with SWIR1->Red, NIR->Green, and Green->Blue",
    "components": {
        "red": {
            "nbart_swir_2": 1.0
        },
        "green": {
            "nbart_nir_1": 1.0
        },
        "blue": {
            "nbart_green": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_s2_ndvi = style_ls_ndvi
style_s2_ndwi = style_ls_ndwi
style_s2_mndwi = {
    # Cannot reuse landsat as we need swir_2 to landsat's swir_1
    "name": "mndwi",
    "title": "MNDWI - Green, SWIR",
    "abstract": "Modified Normalised Difference Water Index - a derived index that correlates well with the existence of water (Xu 2006)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nbart_green",
            "band2": "nbart_swir_2"
        }
    },
    "needed_bands": ["nbart_green", "nbart_swir_2"],
    "color_ramp": [
        {
            "value": -0.1,
            "color": "#f7fbff",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#d8e7f5"
        },
        {
            "value": 0.2,
            "color": "#b0d2e8"
        },
        {
            "value": 0.4,
            "color": "#73b3d8"
        },
        {
            "value": 0.6,
            "color": "#3e8ec4"
        },
        {
            "value": 0.8,
            "color": "#1563aa"
        },
        {
            "value": 1.0,
            "color": "#08306b"
        }
    ]
}
style_s2_ndci = {
    "name": "ndci",
    "title": "NDCI - Red Edge, Red",
    "abstract": "Normalised Difference Chlorophyll Index - a derived index that correlates well with the existence of chlorophyll",
    "index_function": {
        "function": "datacube_ows.band_utils.sentinel2_ndci",
        "pass_product_cfg": True,
        "kwargs": {
            "b_red_edge": "nbart_red_edge_1",
            "b_red": "nbart_red",
            "b_green": "nbart_green",
            "b_swir": "nbart_swir_2",
        }
    },
    "needed_bands": ["nbart_red_edge_1", "nbart_red", "nbart_green", "nbart_swir_2"],
    "color_ramp": [
        {
            "value": -0.1,
            "color": "#1696FF",
            "legend": {
                "prefix" : "<"
            }
        },
        {
            "value": -0.1,
            "color": "#1696FF"
        },
        {
            "value": 0.0,
            "color": "#00FFDF",
            "legend": { }
        },
        {
            "value": 0.1,
            "color": "#FFF50E",
        },
        {
            "value": 0.2,
            "color": "#FFB50A",
            "legend": { }
        },
        {
            "value": 0.4,
            "color": "#FF530D",
        },
        {
            "value": 0.5,
            "color": "#FF0000",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "start": "-0.1",
        "end": "0.5",
        "ticks": ["-0.1", "0.0", "0.2", "0.5"],
        "tick_labels": {
            "-0.1": {"prefix": "<"},
            "0.5": {"prefix": ">"},
        }
    }
}

style_s2_pure_aerosol = {
    "name": "aerosol",
    "title": "Narrow Blue - 440",
    "abstract": "Coastal Aerosol or Narrow Blue band, approximately 435nm to 450nm",
    "components": {
        "red": {
            "coastal_aerosol": 1.0
        },
        "green": {
            "coastal_aerosol": 1.0
        },
        "blue": {
            "coastal_aerosol": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_blue = {
    "name": "blue",
    "title": "Blue - 490",
    "abstract": "Blue band, approximately 453nm to 511nm",
    "components": {
        "red": {
            "blue": 1.0
        },
        "green": {
            "blue": 1.0
        },
        "blue": {
            "blue": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_green = {
    "name": "green",
    "title": "Green - 560",
    "abstract": "Green band, approximately 534nm to 588nm",
    "components": {
        "red": {
            "green": 1.0
        },
        "green": {
            "green": 1.0
        },
        "blue": {
            "green": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_red = {
    "name": "red",
    "title": "Red - 670",
    "abstract": "Red band, roughly 637nm to 672nm",
    "components": {
        "red": {
            "red": 1.0
        },
        "green": {
            "red": 1.0
        },
        "blue": {
            "red": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_redge_1 = {
    "name": "red_edge_1",
    "title": "Vegetation Red Edge - 710",
    "abstract": "Near infra-red band, centred on 710nm",

    "components": {
        "red": {
            "red_edge_1": 1.0
        },
        "green": {
            "red_edge_1": 1.0
        },
        "blue": {
            "red_edge_1": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_redge_2 = {
    "name": "red_edge_2",
    "title": "Vegetation Red Edge - 740",
    "abstract": "Near infra-red band, centred on 740nm",

    "components": {
        "red": {
            "red_edge_2": 1.0
        },
        "green": {
            "red_edge_2": 1.0
        },
        "blue": {
            "red_edge_2": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_redge_3 = {
    "name": "red_edge_3",
    "title": "Vegetation Red Edge - 780",
    "abstract": "Near infra-red band, centred on 780nm",

    "components": {
        "red": {
            "red_edge_3": 1.0
        },
        "green": {
            "red_edge_3": 1.0
        },
        "blue": {
            "red_edge_3": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 840",
    "abstract": "Near infra-red band, roughly 853nm to 876nm",
    "components": {
        "red": {
            "nir": 1.0
        },
        "green": {
            "nir": 1.0
        },
        "blue": {
            "nir": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_s2_pure_narrow_nir = {
    "name": "narrow_nir",
    "title": "Narrow Near Infrared - 870",
    "abstract": "Near infra-red band, centred on 865nm",
    "components": {
        "red": {
            "nir": 1.0
        },
        "green": {
            "nir": 1.0
        },
        "blue": {
            "nir": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_swir1 = {
    "name": "swir1",
    "title": "Shortwave Infrared (SWIR) - 1610",
    "abstract": "Short wave infra-red band 1, roughly 1575nm to 1647nm",
    "components": {
        "red": {
            "swir_2": 1.0
        },
        "green": {
            "swir_2": 1.0
        },
        "blue": {
            "swir_2": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}


style_s2_pure_swir2 = {
    "name": "swir2",
    "title": "Shortwave Infrared (SWIR) - 2190",
    "abstract": "Short wave infra-red band 2, roughly 2117nm to 2285nm",
    "components": {
        "red": {
            "swir_3": 1.0
        },
        "green": {
            "swir_3": 1.0
        },
        "blue": {
            "swir_3": 1.0
        }
    },
    "scale_range": [0.0, 3000.0]
}

style_s2_water_classifier = {
    "name": "water_classifier",
    "title": " Water Summary",
    "abstract": "WOfS NRT",
    "needed_bands": ["water"],
    "value_map": {
        "water": [
            {
                "title": "Wet",
                "abstract": "(100%)",
                "color": "#5700E3"
            },

        ]
    }
}

style_mstp_rgb = {
    "name": "mstp_rgb",
    "title": "Multi-scale Topographic Position",
    "abstract": "red regional, green intermediate and blue local",
    "components": {
        "red": {
            "regional": 1.0
        },
        "green": {
            "intermediate": 1.0
        },
        "blue": {
            "local": 1.0
        }
    },
    "scale_range": [0.0, 255.0]
}

style_wii = {
    "name": "wii",
    "title": "Weathering Intensity",
    "abstract": "Weather Intensity Index (0-6)",
    "needed_bands": ["intensity"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "intensity",
        }
    },
    "color_ramp": [
        {
            "value": 0,
            "color": "#ffffff",
            "alpha": 0
        },
        {
            "value": 1,
            "color": "#2972a8",
            "legend": {
                "label": "Low\nClass 1"
            }
        },
        {
            "value": 3.5,
            "color": "#fcf24b"
        },
        {
            "value": 6,
            "color": "#a02406",
            "legend": {
                "label": "High\nClass 6"
            }
        }
    ],
    "legend": {
        "axes_position": [0.1, 0.5, 0.8, 0.15]
    }
}

style_fc_gv_10 = {
    "name": "green_veg_10",
    "title": "10th Percentile",
    "abstract": "10th Percentile of Green Vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "PV_PC_10",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["PV_PC_10"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#ffffcc",
            "legend": {}
        },
        {
            "value": 25,
            "color": "#c2e699",
            "legend": {}
        },
        {
            "value": 50,
            "color": "#78c679",
            "legend": {}
        },
        {
            "value": 75,
            "color": "#31a354",
            "legend": {}
        },
        {
            "value": 100,
            "color": "#006837",
            "legend": {}
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
    "legend": {
        "units": "% / pixel",
        "title": "Percentage of Pixel that is Green Vegetation",
        "rcParams": {
            "font.size": 9
        },
        "start": 0,
        "end": 100,
        "decimal_places": 0,
        "ticks": [0, 25, 50, 75, 100]
    }
}

style_fc_gv_50 = {
    "name": "green_veg_50",
    "title": "50th Percentile",
    "abstract": "50th Percentile of Green Vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "PV_PC_50",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["PV_PC_50"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#ffffcc"
        },
        {
            "value": 25,
            "color": "#c2e699"
        },
        {
            "value": 50,
            "color": "#78c679"
        },
        {
            "value": 75,
            "color": "#31a354"
        },
        {
            "value": 100,
            "color": "#006837"
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
}

style_fc_gv_90 = {
    "name": "green_veg_90",
    "title": "90th Percentile",
    "abstract": "90th Percentile of Green Vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "PV_PC_90",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["PV_PC_90"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#ffffcc"
        },
        {
            "value": 25,
            "color": "#c2e699"
        },
        {
            "value": 50,
            "color": "#78c679"
        },
        {
            "value": 75,
            "color": "#31a354"
        },
        {
            "value": 100,
            "color": "#006837"
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
}

style_fc_ngv_10 = {
    "name": "non_green_veg_10",
    "title": "10th Percentile",
    "abstract": "10th Percentile of Non Green Vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "NPV_PC_10",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["NPV_PC_10"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#ffffd4",
        },
        {
            "value": 25,
            "color": "#fed98e",
        },
        {
            "value": 50,
            "color": "#fe9929",
        },
        {
            "value": 75,
            "color": "#d95f0e",
        },
        {
            "value": 100,
            "color": "#993404",
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
    "legend": {
        "units": "% / pixel",
        "title": "Percentage of Pixel that is Non-Green Vegetation",
        "rcParams": {
            "font.size": 9
        },
        "start": 0,
        "end": 100,
        "decimal_places": 0,
        "ticks": [0, 25, 50, 75, 100],
    }
}

style_fc_ngv_50 = {
    "name": "non_green_veg_50",
    "title": "50th Percentile",
    "abstract": "50th Percentile of Non Green Vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "NPV_PC_50",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["NPV_PC_50"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#ffffd4"
        },
        {
            "value": 25,
            "color": "#fed98e"
        },
        {
            "value": 50,
            "color": "#fe9929"
        },
        {
            "value": 75,
            "color": "#d95f0e"
        },
        {
            "value": 100,
            "color": "#993404"
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
}

style_fc_ngv_90 = {
    "name": "non_green_veg_90",
    "title": "90th Percentile",
    "abstract": "90th Percentile of Non Green Vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "NPV_PC_90",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["NPV_PC_90"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#ffffd4"
        },
        {
            "value": 25,
            "color": "#fed98e"
        },
        {
            "value": 50,
            "color": "#fe9929"
        },
        {
            "value": 75,
            "color": "#d95f0e"
        },
        {
            "value": 100,
            "color": "#993404"
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
}

style_fc_bs_10 = {
    "name": "bare_ground_10",
    "title": "10th Percentile",
    "abstract": "10th Percentile of Bare Soil",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "BS_PC_10",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["BS_PC_10"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#feebe2",
        },
        {
            "value": 25,
            "color": "#fbb4b9",
        },
        {
            "value": 50,
            "color": "#f768a1",
        },
        {
            "value": 75,
            "color": "#c51b8a",
        },
        {
            "value": 100,
            "color": "#7a0177",
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
    "legend": {
        "units": "% / pixel",
        "title": "Percentage of Pixel that is Bare Soil",
        "rcParams": {
            "font.size": 9
        },
        "start": 0,
        "end": 100,
        "ticks_every": 25,
    }
}

style_fc_bs_50 = {
    "name": "bare_ground_50",
    "title": "50th Percentile",
    "abstract": "50th Percentile of Bare Soil",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "BS_PC_50",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["BS_PC_50"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#feebe2"
        },
        {
            "value": 25,
            "color": "#fbb4b9"
        },
        {
            "value": 50,
            "color": "#f768a1"
        },
        {
            "value": 75,
            "color": "#c51b8a"
        },
        {
            "value": 100,
            "color": "#7a0177"
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
}

style_fc_bs_90 = {
    "name": "bare_ground_90",
    "title": "90th Percentile",
    "abstract": "90th Percentile of Bare Soil",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "BS_PC_90",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["BS_PC_90"],
    "color_ramp": [
        {
            "value": 0,
            "color": "#feebe2"
        },
        {
            "value": 25,
            "color": "#fbb4b9"
        },
        {
            "value": 50,
            "color": "#f768a1"
        },
        {
            "value": 75,
            "color": "#c51b8a"
        },
        {
            "value": 100,
            "color": "#7a0177"
        }
    ],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
}

style_fc_rgb =  {
    "name": "fc_rgb",
    "title": "Three-band fractional cover",
    "abstract": "Frachtional cover medians - red is bare soil, green is green vegetation and blue is non-green vegetation",
    "components": {
        "red": {
            "BS_PC_50": 1.0
        },
        "green": {
            "PV_PC_50": 1.0
        },
        "blue": {
            "NPV_PC_50": 1.0
        }
    },
    "scale_range": [0.0, 100.0],
    "pq_masks": [
        {
            "flags": {
                "sea": True,
            },
            "invert": True,
        },
    ],
    "legend": {
        "show_legend": True,
        "url": "https://data.dea.ga.gov.au/fractional-cover/FC_legend.png",
    }
}

style_nidem = {
    "name": "NIDEM",
    "title": "National Intertidal Digital Elevation Model",
    "abstract": "National Intertidal Digital Elevation Model 25 m v1.0.0",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "nidem",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["nidem"],
    "color_ramp": [
        {
            "value": -2.51,
            "color": "#440154"
        },
        {
            "value": -2.5,
            "color": "#440154",
        },
        {
            "value": -2.34,
            "color": "#460e61",
        },
        {
            "value": -2.18,
            "color": "#471b6e",
        },
        {
            "value": -2.02,
            "color": "#472877"
        },
        {
            "value": -1.86,
            "color": "#45347f"
        },
        {
            "value": -1.7,
            "color": "#413f85"
        },
        {
            "value": -1.58,
            "color": "#3b4d8a"
        },
        {
            "value": -1.42,
            "color": "#37578b"
        },
        {
            "value": -1.26,
            "color": "#32618c"
        },
        {
            "value": -1.1,
            "color": "#2e6b8d",
        },
        {
            "value": -0.94,
            "color": "#2a748e"
        },
        {
            "value": -0.78,
            "color": "#267d8e"
        },
        {
            "value": -0.62,
            "color": "#23868d"
        },
        {
            "value": -0.46,
            "color": "#208f8c"
        },
        {
            "value": -0.3,
            "color": "#1e9889"
        },
        {
            "value": -0.14,
            "color": "#1fa186"
        },
        {
            "value": 0.0,
            "color": "#26ac7f",
        },
        {
            "value": 0.14,
            "color": "#32b579"
        },
        {
            "value": 0.3,
            "color": "#41bd70"
        },
        {
            "value": 0.46,
            "color": "#54c566"
        },
        {
            "value": 0.62,
            "color": "#69cc59"
        },
        {
            "value": 0.78,
            "color": "#80d24b"
        },
        {
            "value": 0.94,
            "color": "#99d83c"
        },
        {
            "value": 1.1,
            "color": "#b2dc2c",
        },
        {
            "value": 1.26,
            "color": "#cce01e"
        },
        {
            "value": 1.42,
            "color": "#e5e31a"
        },
        {
            "value": 1.5,
            "color": "#fde724",
        }
    ],
    "legend": {
        "units": "metres",
        "ticks": ["-2.5", "-1.1", "0.0", "1.5"],
        "decimal_places": 1,
        "tick_labels": {
            "-2.5": {"prefix": "<"},
            "1.5": {"prefix": ">"},
        }
    }
}

style_item_relative = {
    "name": "relative_layer",
    "title": "relative layer",
    "abstract": "The Relative Extents Model (item_v2) 25m v2.0.0",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "relative",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["relative"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#000000",
            "alpha": 0.0
        },
        {
            "value": 1.0,
            "color": "#d7191c",
            "alpha": 1.0
        },
        {

            "value": 2.0,
            "color": "#ec6e43",
        },
        {
            "value": 3.0,
            "color": "#fdb96e",
        },
        {

            "value": 4.0,
            "color": "#fee7a4",
        },
        {
            "value": 5.0,
            "color": "#e7f5b7",
        },
        {

            "value": 6.0,
            "color": "#b7e1a7",
        },
        {
            "value": 7.0,
            "color": "#74b6ad",
        },
        {

            "value": 8.0,
            "color": "#2b83ba"
        },
        {
            "value": 9.0,
            "color": "#000000",
            "alpha": 0.0
        },
    ],
    "legend": {
        "units": "%",
        "decimal_places": 0,
        "start": 0,
        "end": 9,
        "ticks_every": 1
    }
}

style_item_confidence = {
    "name": "confidence_layer",
    "title": "confidence layer",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "stddev",
        }
    },
    "include_in_feature_info": False,
    "abstract": "The Confidence layer (item_v2_conf) 25m v2.0.0",
    "needed_bands": ["stddev"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#2b83ba",
            "alpha": 0.0
        },
        {

            "value": 0.01,
            "color": "#2b83ba",
        },
        {
            "value": 0.055,
            "color": "#55a1b2",
        },
        {
            "value": 0.1,
            "color": "#80bfab",
        },
        {
            "value": 0.145,
            "color": "#abdda4",
        },
        {
            "value": 0.19,
            "color": "#c7e8ad",
        },
        {
            "value": 0.235,
            "color": "#e3f3b6",
        },
        {
            "value": 0.28,
            "color": "#fdbf6f",
        },
        {
            "value": 0.325,
            "color": "#e37d1c",
        },
        {
            "value": 0.37,
            "color": "#e35e1c",
        },
        {
            "value": 0.415,
            "color": "#e31a1c",
        },
        {
            "value": 0.46,
            "color": "#e31a1c",
        },
        {
            "value": 0.505,
            "color": "#e31a1c",
        },
        {
            "value": 0.55,
            "color": "#e31a1c",
        },
    ],
    "legend": {
        "units": "NDWI standard deviation",
        "start": "0.01",
        "decimal_places": 2,
        "end": "0.55",
        "ticks": ["0.01", "0.55"],
        "tick_labels": {
            "0.01": {"prefix": "<"},
            "0.55": {"prefix": ">"},
        }
    }
}

style_wamm_dam_id = {
    "name": "dam_id",
    "title": "Water Body",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "dam_id",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["dam_id"],
    "color_ramp": [
        {
            'value': 0,
            'color': '#11ccff',
            'alpha': 1.0
        },
        {
            'value': 8388607,
            'color': '#11ccff',
            'alpha': 1.0
        },
    ],
    "legend": {
        "start": "0.0",
        "end": "1.0",
        "ticks_every": "0.2",
    }
}

style_hap_simple_gray = {
    "name": "simple_gray",
    "title": "Simple gray",
    "abstract": "Simple grayscale image",
    "components": {
        "red": {
            "Band_1": 1.0
        },
        "green": {
            "Band_1": 1.0
        },
        "blue": {
            "Band_1": 1.0
        }
    },
    "scale_range": [0.0, 255]
}

style_aster_false_colour = {
  "name": "false_colour",
    "title": "False Colour",
    "abstract": "Simple false-colour image using ASTER Bands 3 as red, 2 as green and 1 as blue",
    "components": {
        "red": {
            "Band_1": 1.0
        },
        "green": {
            "Band_2": 1.0
        },
        "blue": {
            "Band_3": 1.0
        }
    },
    "scale_range": [0.0, 255.0]
}

style_aster_b2_gray = {
    "name": "gray",
    "title": "B2 Grayscale",
    "abstract": "Simple grayscale image using ASTER Band 2",
    "components": {
        "red": {
            "Band_2": 1.0
        },
        "green": {
            "Band_2": 1.0
        },
        "blue": {
            "Band_2": 1.0
        }
    },
    "scale_range": [0.0, 255.0]
}

style_aster_simple_rgb = {
    "name": "simple_rgb",
    "title": "Simple RGB",
    "abstract": "Simple  true-colour image, using the red, green and blue bands",
    "components": {
        "red": {
            "Band_1": 1.0
        },
        "green": {
            "Band_2": 1.0
        },
        "blue": {
            "Band_3": 1.0
        }
    },
    "scale_range": [0.0, 255.0]
}

style_aster_aloh_comp_ramp = {
    "name": "ramp",
    "title": "B5/B7 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue is well ordered kaolinite,\nRed is Al-poor (Si-rich) muscovite (phengite)",
        "start": "0",
        "end": "255",
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.9"},
            "255": {"label": "1.3"},
        }
    }

}

style_aster_aloh_cont_ramp = {
    "name": "ramp",
    "title": "(B5+B7)/B6 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
            "legend": {
                "label": "2.0"
            }
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
            "legend": {
                "label": "2.25"
            }
        }
    ],
    "legend": {
        "units": "Blue is low content,\nRed is high content",
        "start": "0",
        "end": "255",
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "2.0"},
            "255": {"label": "2.25"},
        }
    }
}

style_aster_feoh_cont_ramp = {
    "name": "ramp",
    "title": "(B6+B8)/B7 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
            "legend": {
                "label": "2.03"
            }
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
            "legend": {
                "label": "2.25"
            }
        }
    ],
    "legend": {
        "units": "Blue is low content,\nRed is high content",
        "start": "0",
        "end": "255",
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "2.03"},
            "255": {"label": "2.25"},
        }
    }
}

style_aster_ferrox_comp_ramp = {
    "name": "ramp",
    "title": "B2/B1 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue-cyan is non-hematitie,\nRed-yellow is hematite-rich",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.5"},
            "255": {"label": "3.3"},
        },
    }
}

style_aster_ferrox_cont_ramp = {
    "name": "ramp",
    "title": "B4/B3 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue is low abundance,\nRed is high abundance",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "1.1"},
            "255": {"label": "2.1"},
        },
    }
}

style_aster_ferrous_mgoh_ramp = {
    "name": "ramp",
    "title": "B5/B4 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue is low ferrous iron content,\nRed is high ferrous iron content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.1"},
            "255": {"label": "2.0"},
        },
    }
}

style_aster_ferrous_idx_ramp = {
    "name": "ramp",
    "title": "B5/B4 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue is low abundance,\nRed is high abundance",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.75"},
            "255": {"label": "1.025"},
        },
    }
}

style_aster_green_veg_ramp = {
    "name": "ramp",
    "title": "B3/B2 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue is low content,\nRed is high content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "1.4"},
            "255": {"label": "4"},
        },
    }
}
                            
style_aster_gypsum_idx_ramp = {
    "name": "ramp",
    "title": "(B10+B12)/B11 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue is low content,\nRed is high content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.47"},
            "255": {"label": "0.5"},
        },
    }
}
                            
style_aster_kaolin_idx_ramp = {
    "name": "ramp",
    "title": "B6/B5 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue is low content,\nRed is high content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "1.0"},
            "255": {"label": "1.125"},
        },
    }
}

style_aster_mgoh_comp_ramp = {
    "name": "ramp",
    "title": "B7/B8 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue-cyan is magnesite-dolomite, amphibole, \nRed is calcite, epidote, amphibole",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.6"},
            "255": {"label": "1.4"},
        },
    }
}

style_aster_mgoh_cont_ramp = {
    "name": "ramp",
    "title": "(B6+B9/(B7+B8) ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue low content,\nRed is high content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "1.05"},
            "255": {"label": "1.2"},
        },
    }
}
                            
style_aster_opaque_idx_ramp = {
    "name": "ramp",
    "title": "B1/B4 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
            "legend": {
                "label": "0.4"
            }
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue low quartz content,\nRed is high quartz content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.4"},
            "255": {"label": "0.9"},
        },
    }
}
                            
style_aster_silica_idx_ramp = {
    "name": "ramp",
    "title": "B13/B10 ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
            "legend": {
                "label": "1.35"
            }
        }
    ],
    "legend": {
        "units": "Blue low quartz content,\nRed is high quartz content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "1.0"},
            "255": {"label": "1.35"},
        },
    }
}
                            
style_aster_quartz_idx_ramp = {
    "name": "ramp",
    "title": "B11/(B10+B12) ",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "Band_1",
        }
    },
    "include_in_feature_info": False,
    "needed_bands": ["Band_1"],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 0.0,
        },
        {
            "value": 1,
            "color": "#000000"
        },
        {
            "value": 10,
            "color": "#2d002b"
        },
        {
            "value": 25,
            "color": "#550071"
        },
        {
            "value": 60,
            "color": "#0400ff"
        },
        {
            "value": 90,
            "color": "#0098ff"
        },
        {
            "value": 110,
            "color": "#00ffff"
        },
        {
            "value": 130,
            "color": "#00ff94"
        },
        {
            "value": 150,
            "color": "#00ff2a"
        },
        {
            "value": 170,
            "color": "#3fff00"
        },
        {
            "value": 210,
            "color": "#ffee00"
        },
        {
            "value": 230,
            "color": "#ff8300"
        },
        {
            "value": 255.0,
            "color": "#ff0000",
        }
    ],
    "legend": {
        "units": "Blue low quartz content,\nRed is high quartz content",
        "start": "0",
        "end": "255",
        "decimal_places": 0,
        "ticks": ["0", "255"],
        "tick_labels": {
            "0": {"label": "0.50"},
            "255": {"label": "0.52"},
        },
    }
}

style_tmad_sdev = {
    "name": "log_sdev",
    "title": "sdev",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band_log",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "sdev",
            "scale_factor": -100.0,
            "exponent": 1/1000.0
        }
    },
    "needed_bands": ["sdev"],
    "color_ramp": [
        {
            'value': 0.0,
            'color': '#ffffff',
            'alpha': 0
        },
        {
            'value': 0.1,
            'color': '#A02406',
        },
        {
            'value': 0.5,
            'color': '#FCF24B'
        },
        {
            'value': 0.9,
            'color': '#0CCD1D',
        }
    ],
    "legend": {
        "start": "0.1",
        "end": "0.9",
        "ticks": ["0.1", "0.9"],
        "tick_labels": {
            "0.1": {"label": "High\ntmad"},
            "0.9": {"label": "Low\ntmad"},
        }
    }
}

style_tmad_edev = {
    "name": "log_edev",
    "title": "edev",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band_log",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "edev",
            "scale_factor": -100.0,
            "exponent": 1/1000.0
        }
    },
    "needed_bands": ["edev"],
    "color_ramp": [
        {
            'value': 0.0,
            'color': '#ffffff',
            'alpha': 0
        },
        {
            'value': 0.1,
            'color': '#A02406',
        },
        {
            'value': 0.5,
            'color': '#FCF24B'
        },
        {
            'value': 0.9,
            'color': '#0CCD1D',
        }
    ],
    "legend": {
        "start": "0.1",
        "end": "0.9",
        "ticks": ["0.1", "0.9"],
        "tick_labels": {
            "0.1": {"label": "High\ntmad"},
            "0.9": {"label": "Low\ntmad"},
        }
    }
}

style_tmad_bcdev = {
    "name": "log_bcdev",
    "title": "bcdev",
    "abstract": "",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band_log",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "bcdev",
            "scale_factor": -100.0,
            "exponent": 1/1000.0
        }
    },
    "needed_bands": ["bcdev"],
    "color_ramp": [
        {
            'value': 0.0,
            'color': '#ffffff',
            'alpha': 0
        },
        {
            'value': 0.1,
            'color': '#A02406',
        },
        {
            'value': 0.5,
            'color': '#FCF24B'
        },
        {
            'value': 0.9,
            'color': '#0CCD1D',
        }
    ],
    "legend": {
        "start": "0.1",
        "end": "0.9",
        "ticks": ["0.1", "0.9"],
        "tick_labels": {
            "0.1": {"label": "High\ntmad"},
            "0.9": {"label": "Low\ntmad"},
        }
    }
}

style_fc_simple = {
    "name": "simple_fc",
    "title": "Fractional Cover",
    "abstract": "Fractional cover representation, with green vegetation in green, dead vegetation in blue, and bare soil in red",
    "components": {
        "red": {
            "BS": 1.0
        },
        "green": {
            "PV": 1.0
        },
        "blue": {
            "NPV": 1.0
        }
    },
    "scale_range": [0.0, 100.0],
    "pq_masks": [
        {
            "flags": {
                'dry': True
            },
        },
        {
            "flags": {
                "terrain_or_low_angle": False,
                "high_slope": False,
                "cloud_shadow": False,
                "cloud": False,
                "sea": False
            }
        },
    ]
}


style_alos_hh = {
    "name": "hh",
    "title": "HH",
    "abstract": "HH band",
    "needed_bands": ["hh"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "hh",
        }
    },
    "color_ramp": [
        {
            "value": 0,
            "color": "#f7fcf5"
        },
        {
            "value": 750,
            "color": "#e2f4dd"
        },
        {
            "value": 1000,
            "color": "#c0e6b9"
        },
        {
            "value": 1500,
            "color": "#94d390"
        },
        {
            "value": 2500,
            "color": "#60ba6c"
        },
        {
            "value": 4000,
            "color": "#329b51"
        },
        {
            "value": 6000,
            "color": "#0c7835"
        },
        {
            "value": 8000,
            "color": "#00441b",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "radix_point": 0,
        "scale_by": 1,
        "major_ticks": 500
    }
}

style_alos_hv = {
    "name": "hv",
    "title": "HV",
    "abstract": "HV band",
    "needed_bands": ["hv"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "hv",
        }
    },
    "color_ramp": [
        {
            "value": 0,
            "color": "#f7fcf5"
        },
        {
            "value": 250,
            "color": "#e2f4dd"
        },
        {
            "value": 300,
            "color": "#c0e6b9"
        },
        {
            "value": 500,
            "color": "#94d390"
        },
        {
            "value": 800,
            "color": "#60ba6c"
        },
        {
            "value": 2000,
            "color": "#329b51"
        },
        {
            "value": 3500,
            "color": "#0c7835"
        },
        {
            "value": 4500,
            "color": "#00441b",
            "legend": {
                "prefix": ">"
            }
        }
    ],
    "legend": {
        "radix_point": 0,
        "scale_by": 1,
        "major_ticks": 500
    }    
}

style_alos_hh_over_hv = {
    "name": "hh_hv_hh_over_hv",
    "title": "HH, HV and HH/HV",
    "abstract": "False colour representation of HH, HV and HH over HV for R, G and B respectively",
    # Mixing ratio between linear components and colour ramped index. 1.0 is fully linear components, 0.0 is fully colour ramp.
    "component_ratio": 0.5,
    "index_function": {
        "function": "datacube_ows.band_utils.band_quotient",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "hh",
            "band2": "hv"
        }
    },
    "needed_bands": ["hh", "hv"],
    "range": [0.01, 2.0],
    "components": {
        "red": {
            "hh": 1.0
        },
        "green": {
            "hv": 1.0
        },
        "blue": {
            "hh": 0.0
        }
    },
    "scale_range": [0.0, 5000.0],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#000000",
        },
        {
            "value": 6.0,
            "color": "#0000ff"
        }
    ],
}

style_alos_hv_over_hh = {
    "name": "hh_hv_hv_over_hh",
    "title": "HH, HV and HV/HH",
    "abstract": "False colour representation of HH, HV and HV over HH for R, G and B respectively",
    # Mixing ratio between linear components and colour ramped index. 1.0 is fully linear components, 0.0 is fully colour ramp.
    "component_ratio": 0.5,
    "index_function": {
        "function": "datacube_ows.band_utils.band_quotient",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "hh",
            "band2": "hv"
        }
    },
    "needed_bands": ["hh", "hv"],
    "range": [0.01, 2.0],
    "components": {
        "red": {
            "hh": 1.0
        },
        "green": {
            "hv": 1.0
        },
        "blue": {
            "hh": 0.0
        }
    },
    "scale_range": [0.0, 5000.0],
    "color_ramp": [
        {
            "value": 0.0,
            "color": "#000000",
        },
        {
            "value": 0.6,
            "color": "#0000ff"
        }    
    ]
}


style_insar_velocity = {
    "name": "insar_velocity",
    "title": "InSAR Velocity",
    "abstract": "Average InSAR Velocity in mm/year",
    "needed_bands": ["velocity"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "velocity",
        }
    },
    # Should the index_function value be shown as a derived band in GetFeatureInfo responses.
    # Defaults to true for style types with an index function.
    "include_in_feature_info": False,
    "range": [-30.0, 30.0],
    "mpl_ramp": "RdBu_r",
    "legend": {
        "units": "mm/year",
        "radix_point": 0,
        "scale_by": 1.0,
        "major_ticks": 5,
        "offset": 0.0
    }
}

style_insar_velocity_ud = copy.deepcopy(style_insar_velocity)
style_insar_velocity_ud["name"] = "insar_velocity_ud"
style_insar_velocity_ud["title"] = "InSAR Velocity Up-Down "
style_insar_velocity_ud["needed_bands"] = ["ud"]
style_insar_velocity_ud["index_function"]["kwargs"]["band"] = "ud"

style_insar_velocity_ew = copy.deepcopy(style_insar_velocity)
style_insar_velocity_ew["name"] = "insar_velocity_ew"
style_insar_velocity_ew["title"] = "InSAR Velocity East-West "
style_insar_velocity_ew["needed_bands"] = ["ew"]
style_insar_velocity_ew["index_function"]["kwargs"]["band"] = "ew"

style_insar_displacement = {
    "name": "insar_displacement",
    "title": "InSAR Cumulative Displacement",
    "abstract": "Cumulative InSAR Displacment mm",
    "needed_bands": ["displacement"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "displacement",
        }
    },
    # Should the index_function value be shown as a derived band in GetFeatureInfo responses.
    # Defaults to true for style types with an index function.
    "include_in_feature_info": False,
    "range": [-100.0, 100.0],
    "mpl_ramp": "RdBu_r",
    "legend": {
        "units": "mm",
        "decimal_places": 0,
        "start": "-100",
        "end": "100",
        "ticks_every": "20",
    }
}

style_insar_disp_ud = copy.deepcopy(style_insar_displacement)
style_insar_disp_ud["name"] = "insar_disp_ud"
style_insar_disp_ud["title"] = "InSAR Displacement Up-Down "
style_insar_disp_ud["needed_bands"] = ["ud"]
style_insar_disp_ud["index_function"]["kwargs"]["band"] = "ud"

style_insar_disp_ew = copy.deepcopy(style_insar_displacement)
style_insar_disp_ew["name"] = "insar_disp_ew"
style_insar_disp_ew["title"] = "InSAR Displacement East-West "
style_insar_disp_ew["needed_bands"] = ["ew"]
style_insar_disp_ew["index_function"]["kwargs"]["band"] = "ew"

style_insar_stddev_l = {
    "name": "insar_stddev_l",
    "title": "InSAR Cumulative Displacement Uncertainty",
    "abstract": "Uncertainty in mm",
    "needed_bands": ["disp_std"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "disp_std",
        }
    },
    # Should the index_function value be shown as a derived band in GetFeatureInfo responses.
    # Defaults to true for style types with an index function.
    "include_in_feature_info": False,
    "range": [0.0, 80.0],
    "mpl_ramp": "Reds",
    "legend": {
        "units": "mm",
        "start": "0",
        "end": "80",
        "decimal_places": 0,
        "ticks_every": "5",
    }
}

# Create up-down/east-west varieties using deepcopy
style_insar_stddev_l_ud = copy.deepcopy(style_insar_stddev_l)
style_insar_stddev_l_ud["name"] = "insar_disp_ud_std"
style_insar_stddev_l_ud["title"] = "InSAR Displacement Uncertainty Up-Down "
style_insar_stddev_l_ud["needed_bands"] = ["upstd"]
style_insar_stddev_l_ud["index_function"]["kwargs"]["band"] = "upstd"

style_insar_stddev_l_ew = copy.deepcopy(style_insar_stddev_l)
style_insar_stddev_l_ew["name"] = "insar_disp_ew_std"
style_insar_stddev_l_ew["title"] = "InSAR Displacement Uncertainty East-West "
style_insar_stddev_l_ew["needed_bands"] = ["ewstd"]
style_insar_stddev_l_ew["index_function"]["kwargs"]["band"] = "ewstd"

# Create C-band style using a copy constructor
style_insar_stddev_c_ud = copy.copy(style_insar_stddev_l_ud)
style_insar_stddev_c_ud["range"] = [0.0, 20.0]

style_insar_stddev_c_ew = copy.copy(style_insar_stddev_l_ew)
style_insar_stddev_c_ew["range"] = [0.0, 20.0]

style_insar_stddev_lv = {
    "name": "insar_stddev_lv",
    "title": "InSAR Velocity Uncertainty",
    "abstract": "Uncertainty in mm",
    "needed_bands": ["vel_std"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "pass_product_cfg": True,
        "kwargs": {
            "band": "vel_std",
        }
    },
    # Should the index_function value be shown as a derived band in GetFeatureInfo responses.
    # Defaults to true for style types with an index function.
    "include_in_feature_info": False,
    "range": [0.0, 24.0],
    "mpl_ramp": "Reds",
    "legend": {
        "units": "mm/year",
        "decimal_places": 0,
        "start": "0",
        "end": "24",
        "major_ticks": "2",
    }
}

# Create up-down/east-west varieties using deepcopy
style_insar_stddev_lv_ud = copy.deepcopy(style_insar_stddev_lv)
style_insar_stddev_lv_ud["name"] = "insar_vel_ud_std"
style_insar_stddev_lv_ud["title"] = "InSAR Velocity Uncertainty Up-Down "
style_insar_stddev_lv_ud["needed_bands"] = ["upstd"]
style_insar_stddev_lv_ud["index_function"]["kwargs"]["band"] = "upstd"

style_insar_stddev_lv_ew = copy.deepcopy(style_insar_stddev_lv)
style_insar_stddev_lv_ew["name"] = "insar_vel_ew_std"
style_insar_stddev_lv_ew["title"] = "InSAR Velocity Uncertainty East-West "
style_insar_stddev_lv_ew["needed_bands"] = ["ewstd"]
style_insar_stddev_lv_ew["index_function"]["kwargs"]["band"] = "ewstd"

# Create C-band style using a copy constructor
style_insar_stddev_cv_ud = copy.copy(style_insar_stddev_lv_ud)
style_insar_stddev_cv_ud["range"] = [0.0, 6.0]

style_insar_stddev_cv_ew = copy.copy(style_insar_stddev_lv_ew)
style_insar_stddev_cv_ew["range"] = [0.0, 6.0]



style_s2_nbr = {
    "name": "NBR",
    "title": "Normalised Burn Ratio",
    "abstract": "Normalised Burn Ratio - a derived index that that uses the differences in the way health green vegetation and burned vegetation reflect light to find burned area",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "pass_product_cfg": True,
        "kwargs": {
            "band1": "nbart_nir_1",
            "band2": "nbart_swir_3"
        }
    },
    "needed_bands": ["nbart_nir_1", "nbart_swir_3"],
    "color_ramp": [
        {
            "value": -1.0,
            "color": "#67001F",
            "alpha": 0.0,
        },
        {
            "value": -1.0,
            "color": "#67001F",
        },
        {
            "value": -0.8,
            "color": "#B2182B",
        },
        {
            "value": -0.4,
            "color": "#D6604D"
        },
        {
            "value": -0.2,
            "color": "#F4A582"
        },
        {
            "value": -0.1,
            "color": "#FDDBC7"
        },
        {
            "value": 0,
            "color": "#F7F7F7",
        },
        {
            "value": 0.2,
            "color": "#D1E5F0"
        },
        {
            "value": 0.4,
            "color": "#92C5DE"
        },
        {
            "value": 0.6,
            "color": "#4393C3"
        },
        {
            "value": 0.9,
            "color": "#2166AC"
        },
        {
            "value": 1.0,
            "color": "#053061",
        }
    ],
    "legend": {
        "show_legend": True,
        "start": "-1.0",
        "end": "1.0",
        "decimal_places": 1,
        "ticks": ["-0.1", "0.0", "0.1"],
        "tick_labels": {
            "-0.1": {"prefix": "<"},
            "0.0": {"label": "0"},
            "0.1": {"suffix": ">"},
        }
    },
    # Define behaviour(s) for multi-date requests. If not declared, style only supports single-date requests.
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            # The count range for which this handler is to be used - a tuple of two ints, the smallest and
            # largest date counts for which this handler will be used.  Required.
            "allowed_count_range": [2, 2],
            # A function, expressed in the standard format as described elsewhere in this example file.
            # The function is assumed to take one arguments, an xarray Dataset.
            # The function returns an xarray Dataset with a single band, which is the input to the
            # colour ramp defined below.
            "aggregator_function": {
                "function": "datacube_ows.band_utils.multi_date_delta"
            },

           "color_ramp": [
                {
                    "value": -0.5,
                    "color": "#768642",
                    "alpha": 0.0
                },
                {
                    "value": -0.5,
                    "color": "#768642",
                },
                {
                    "value": -0.25,
                    "color": "#768642",
                    "alpha": 1.0,
                },
                {
                    "value": -0.25,
                    "color": "#a4bd5f"
                },
                {
                    "value": -0.1,
                    "color": "#a4bd5f",
                },
                {
                    "value": -0.1,
                    "color": "#00e05d"
                },
                {
                    "value": 0.1,
                    "color": "#00e05d"
                },
                {
                    "value": 0.1,
                    "color": "#fdf950",
                },
                {
                    "value": 0.27,
                    "color": "#fdf950",
                },
                {
                    "value": 0.27,
                    "color": "#ffae52"
                },
                {
                    "value": 0.44,
                    "color": "#ffae52",
                },
                {
                    "value": 0.44,
                    "color": "#ff662e"
                },
                {
                    "value": 0.66,
                    "color": "#ff662e",
                },
                {
                    "value": 0.66,
                    "color": "#ad28cc"
                },
                {
                    "value": 0.88,
                    "color": "#ad28cc",
                },
            ],
            "legend": {
                    "start": "-0.50",
                    "end": "-0.88",
                    "decimal_places": 2,
                    "ticks": ["-0.50", "-0.25", "-0.10", "0.10", "0.27", "0.44", "0.66", "1.30"],
                    "tick_labels": {
                        "-0.50": {"prefix": "<"},
                        "1.30": {"prefix": ">"},
                    }
            },
            # The multi-date color ramp.  May be defined as an explicit colour ramp, as shown above for the single
            # date case; or may be defined with a range and unscaled color ramp as shown here.
            #
            # The range specifies the min and max values for the color ramp.  Required if an explicit color
            # ramp is not defined.
            # "range": [-1.0, 1.0],
            # The name of a named matplotlib color ramp.
            # Reference here: https://matplotlib.org/examples/color/colormaps_reference.html
            # Only used if an explicit colour ramp is not defined.  Optional - defaults to a simple (but
            # kind of ugly) blue-to-red rainbow ramp.
            # "mpl_ramp": "RdBu",
            # The feature info label for the multi-date index value.
            "feature_info_label": "nbr_delta"
        }
    ]
}



# Actual Configuration

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
            "EPSG:4326": {  # WGS-84
                "geographic": True,
                "vertical_coord_first": True
            },
            "EPSG:3577": {  # GDA-94, internal representation
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:3111": {  # VicGrid94 for delwp.vic.gov.au
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
        },
        "allowed_urls": [
                "http://localhost:8000",
                "http://ows-configrefactor.dev.dea.ga.gov.au",
                "https://ows.services.dea.ga.gov.au",
                "https://ows.services.dev.dea.ga.gov.au",
                "https://ows.dev.dea.ga.gov.au",
                "https://ows.dea.ga.gov.au",
                "https://ows.services.devkube.dea.ga.gov.au",
                "https://nrt.services.dea.ga.gov.au",
                "https://geomedian.services.dea.ga.gov.au",
                "https://geomedianau.dea.ga.gov.au",
                "https://geomedian.dea.ga.gov.au",
                "https://nrt.dea.ga.gov.au",
                "https://nrt-au.dea.ga.gov.au"],

        # Metadata to go straight into GetCapabilities documents
        "title": "Paul's Earth Australia - OGC Web Services",
        "abstract": "Digital Earth Australia OGC Web Services",
        "info_url": "dea.ga.gov.au/",
        "keywords": [
            "geomedian",
            "WOfS",
            "mangrove",
            "bare-earth",
            "NIDEM",
            "HLTC",
            "landsat",
            "australia",
            "time-series",
            "fractional-cover"
        ],
        "contact_info": {
            "person": "Digital Earth Australia",
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
        "access_constraints": "Copyright Commonwealth of Australia Geoscience Australia:2018",
        "use_extent_views": True,
    }, # END OF global SECTION
    "wms": {
        # Config for WMS service, for all products/layers
        "s3_url": "https://data.dea.ga.gov.au",
        "s3_bucket": "dea-public-data",
        "s3_aws_zone": "ap-southeast-2",

        "max_width": 512,
        "max_height": 512,
    }, # END OF wms SECTION
    "wcs": {
        # Config for WCS service, for all products/coverages
        "default_geographic_CRS": "EPSG:4326",
        "formats": {
            "GeoTIFF": {
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_tiff",
                    "2": "datacube_ows.wcs2_utils.get_tiff",
                },
#               "renderer": "datacube_ows.wcs_utils.get_tiff",
                "mime": "image/geotiff",
                "extension": "tif",
                "multi-time": False
            },
            "netCDF": {
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_netcdf",
                    "2": "datacube_ows.wcs2_utils.get_netcdf",
                },
                # "renderer": "datacube_ows.wcs_utils.get_netcdf",
                "mime": "application/x-netcdf",
                "extension": "nc",
                "multi-time": True,
            },
        },
        "native_format": "GeoTIFF",
    }, # END OF wcs SECTION
    "layers": [
                        {
                    "title": "Digital Earth Australia - OGC Web Services",
                    "abstract": "Digital Earth Australia OGC Web Services",
                    "layers": [
        # Hierarchical list of layers.  May be a combination of unnamed/unmappable folder-layers or named mappable layers.
        {
            "title": "Surface Reflectance",
            "abstract": "",
            "layers": [

                {
                    "title": "Surface Reflectance 25m Annual Geomedian (Landsat 8)",
                    "name": "ls8_nbart_geomedian_annual",
                    "abstract": """
Data is only visible at higher resolutions; when zoomed-out the available area will be displayed
as a shaded region. The surface reflectance geometric median (geomedian) is a pixel composite
mosaic of a time series of earth observations. The value of a pixel in a an annual geomedian
image is the statistical median of all observations for that pixel from a calendar year.
Annual mosaics are available for the following years:

Landsat 8: 2013 to 2017;

For more information, see http://pid.geoscience.gov.au/dataset/ga/120374

For service status information, see https://status.dea.ga.gov.au
                    """,
                    "product_name": "ls8_nbart_geomedian_annual",
                    "bands": bands_ls,
                    "resource_limits": reslim_landsat,
                    "time_resolution": "year",
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_resolution": [25.0, -25.0],
                        "default_bands": ["red", "green", "blue"],
                        "native_crs": "EPSG:3577"
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_ls_simple_rgb,
                            style_ls_simple_rg,
                            style_ls_irg, 
                            style_ls_rgbndvi, 
                            style_ls_ndvi, 
                            style_ls8_nbr,
                            style_ls_ndvi_alt1, style_ls_ndvi_alt2, style_ls_ndvi_alt3, 
                            style_ls_ndvi_delta,
                            style_ls_ndwi, style_ls_mndwi,
                            style_ls_pure_blue, style_ls_pure_green, style_ls_pure_red,
                            style_sentinel_pure_nir, style_sentinel_pure_swir1, style_sentinel_pure_swir2,
                        ]
                    }
                },
                {
                    "title": "Surface Reflectance 25m Annual Geomedian (Landsat 7)",
                    "name": "ls7_nbart_geomedian_annual",
                    "abstract": """
Data is only visible at higher resolutions; when zoomed-out the available area will be displayed
as a shaded region. The surface reflectance geometric median (geomedian) is a pixel composite
mosaic of a time series of earth observations. The value of a pixel in a an annual geomedian
image is the statistical median of all observations for that pixel from a calendar year.
Annual mosaics are available for the following years:

Landsat 7: 2000 to 2017;

For more information, see http://pid.geoscience.gov.au/dataset/ga/120374

For service status information, see https://status.dea.ga.gov.au
                    """,
                    "product_name": "ls7_nbart_geomedian_annual",
                    "bands": bands_ls,
                    "resource_limits": reslim_landsat,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "manual_merge": True,
                    },
                    "wcs": {
                        "native_resolution": [25.0, -25.0],
                        "default_bands": ["red", "green", "blue"],
                        "native_crs": "EPSG:3577"
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_ls_simple_rgb,
                            style_ls_irg, style_ls_ndvi, style_ls_ndwi, style_ls_mndwi,
                            style_ls_ndvi_alt1, style_ls_ndvi_alt2, style_ls_ndvi_alt3, 
                            style_ls_ndvi_delta,
                            style_sentinel_pure_blue, style_ls_pure_green, style_ls_pure_red,
                            style_ls_pure_nir, style_ls_pure_swir1, style_ls_pure_swir2,
                        ]
                    }
                },
                {
                    "title": "Surface Reflectance 25m Annual Geomedian (Landsat 5)",
                    "name": "ls5_nbart_geomedian_annual",
                    "abstract": """
Data is only visible at higher resolutions; when zoomed-out the available area will be displayed
as a shaded region. The surface reflectance geometric median (geomedian) is a pixel composite
mosaic of a time series of earth observations. The value of a pixel in a an annual geomedian
image is the statistical median of all observations for that pixel from a calendar year.
Annual mosaics are available for the following years:

Landsat 5: 1988 to 1999, 2004 to 2007, 2009 to 2011;

For more information, see http://pid.geoscience.gov.au/dataset/ga/120374

For service status information, see https://status.dea.ga.gov.au
                    """,
                    "product_name": "ls5_nbart_geomedian_annual",
                    "bands": bands_ls,
                    "resource_limits": reslim_landsat,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "manual_merge": True,
                    },
                    "wcs": {
                        "native_resolution": [25.0, -25.0],
                        "default_bands": ["red", "green", "blue"],
                        "native_crs": "EPSG:3577"
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_ls_simple_rgb,
                            style_ls_irg, style_ls_ndvi, style_ls_ndwi, style_ls_mndwi,
                            style_ls_ndvi_alt1, style_ls_ndvi_alt2, style_ls_ndvi_alt3, 
                            style_sentinel_pure_blue, style_ls_pure_green, style_ls_pure_red,
                            style_ls_pure_nir, style_ls_pure_swir1, style_ls_pure_swir2,
                        ]
                    }
                },
            ]
        },
        {
            "title": "Intertidal Extents Model",
            "abstract": """
The Intertidal Extents Model (ITEM) product is a national dataset of the exposed intertidal zone;
the land between the observed highest and lowest tide. ITEM provides the extent and topography of 
the intertidal zone of Australia's coastline (excluding off-shore Territories). 
This information was collated using observations in the Landsat archive since 1986. 
ITEM can be a valuable complimentary dataset to both onshore LiDAR survey data and coarser offshore 
bathymetry data, enabling a more realistic representation of the land and ocean interface.
""",
            "layers": [
                {
                    "title": "Intertidal Extents Model 25m ITEM v2.0.0 (Relative Layer)",
                    "name": "ITEM_V2.0.0",
                    "abstract": """
The Intertidal Extents Model (ITEM v2.0) product analyses GA’s historic archive of satellite imagery to derive a model of the spatial extents of the intertidal zone throughout the tidal cycle. The model can assist in understanding the relative elevation profile of the intertidal zone, 
delineating exposed areas at differing tidal heights and stages.

The product differs from previous methods used to map the intertidal zone which have been predominately focused on analysing a small number of individual satellite images per location (e.g Ryu et al., 2002; Murray et al., 2012). 
By utilising a full 30 year time series of observations and a global tidal model (Egbert and Erofeeva, 2002), the methodology enables us to overcome the requirement for clear, high quality observations acquired concurrent to the time of high and low tide.

*Accuracy and limitations*
                  
Due the sun-synchronous nature of the various Landsat sensor observations; it is unlikely that the full physical extents of the tidal range in any cell will be observed. Hence, terminology has been adopted for the product to reflect the highest modelled tide observed in a given cell (HOT) and the lowest modelled tide observed (LOT) (see Sagar et al. 2017). These measures are relative to Mean Sea Level, and have no consistent relationship to Lowest (LAT) and Highest Astronomical Tide (HAT).

The inclusion of the lowest (LMT) and highest (HMT) modelled tide values for each tidal polygon indicates the highest and lowest tides modelled for that location across the full time series by the OTPS model. The relative difference between the LOT and LMT (and HOT and HMT) heights gives an indication of the extent of the tidal range represented in the Relative Extents Model.

As in ITEM v1.0, v2.0 contains some false positive land detection in open ocean regions. These are a function of the lack of data at the extremes of the observed tidal range, and features like glint and undetected cloud in these data poor regions/intervals. Methods to isolate and remove these features are in development for future versions. Issues in the DEA archive and data noise in the Esperance, WA region off Cape Le Grande and Cape Arid (Polygons 236,201,301) has resulted in significant artefacts in the model, and use of the model in this area is not recommended.
                
The Confidence layer is designed to assess the reliability of the Relative Extent Model. Within each tidal range percentile interval, the pixel-based standard deviation of the NDWI values for all observations in the interval subset is calculated. The average standard deviation across all tidal range intervals is then calculated and retained as a quality indicator in this product layer.

The Confidence Layer reflects the pixel based consistency of the NDWI values within each subset of observations, based on the tidal range. Higher standard deviation values indicate water classification changes not based on the tidal cycle, and hence lower confidence in the extent model.

Possible drivers of these changes include:

Inadequacies of the tidal model, due perhaps to complex coastal bathymetry or estuarine structures not captured in the model. These effects have been reduced in ITEM v2.0 compared to previous versions, through the use of an improved tidal modelling frameworkChange in the structure and exposure of water/non-water features NOT driven by tidal variation. 
For example, movement of sand banks in estuaries, construction of man-made features (ports etc.).Terrestrial/Inland water features not influenced by the tidal cycle.
File naming:
THE RELATIVE EXTENTS MODEL v2.0
ITEM_REL_<TIDAL POLYGON NUMBER>_<LONGITUDE>_<LATITUDE>
TIDAL POLYGON NUMBER relates to the id of the tidal polygon referenced by the file
LONGITUDE is the longitude of the centroid of the tidal polygon
LATITUDE is the latitude of the centroid of the tidal polygon

THE CONFIDENCE LAYER v2.0
ITEM_STD_<TIDAL POLYGON NUMBER>_<LONGITUDE>_<LATITUDE>
TIDAL POLYGON NUMBER relates to the id of the tidal polygon referenced by the file
LONGITUDE is the longitude of the centroid of the tidal polygon
LATITUDE is the latitude of the centroid of the tidal polygon

*Overview*

The Intertidal Extents Model product is a national scale gridded dataset characterising the spatial extents of the exposed intertidal zone, at intervals of the observed tidal range (Sagar et al. 2017).The current version (2.0) utilises all Landsat observations (5, 7, and 8) for Australian coastal regions (excluding off-shore Territories) between 1986 and 2016 (inclusive).

ITEM v2.0 has implemented an improved tidal modelling framework (see Sagar et al. 2018) over that utilised in ITEM v1.0. The expanded Landsat archive within the Digital Earth Australia (DEA) has also enabled the model extent to be increased to cover a number of offshore reefs, including the full Great Barrier Reef and southern sections of the Torres Strait Islands. 
The DEA archive and new tidal modelling framework has improved the coverage and quality of the ITEM v2.0 relative extents model, particularly in regions where AGDC cell boundaries in ITEM v1.0 produced discontinuities or the imposed v1.0 cell structure resulted in poor quality tidal modelling (see Sagar et al. 2017).
For service status information, see https://status.dea.ga.gov.au""",
                    "product_name": "item_v2",
                    "bands": bands_item,
                    "resource_limits": reslim_item,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["relative"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "relative_layer",
                        "styles": [
                            style_item_relative,
                        ]
                    }
                },
                {
                    "title": "Intertidal Extents Model 25m ITEM v2.0.0 (Confidence Layer)",
                    "name": "ITEM_V2.0.0_Conf",
                    "abstract": """
The Intertidal Extents Model (ITEM v2.0) product analyses GA’s historic archive of satellite imagery to derive a model of the spatial extents of the intertidal zone throughout the tidal cycle. The model can assist in understanding the relative elevation profile of the intertidal zone, 
delineating exposed areas at differing tidal heights and stages.

The product differs from previous methods used to map the intertidal zone which have been predominately focused on analysing a small number of individual satellite images per location (e.g Ryu et al., 2002; Murray et al., 2012). 
By utilising a full 30 year time series of observations and a global tidal model (Egbert and Erofeeva, 2002), the methodology enables us to overcome the requirement for clear, high quality observations acquired concurrent to the time of high and low tide.

*Accuracy and limitations*
                  
Due the sun-synchronous nature of the various Landsat sensor observations; it is unlikely that the full physical extents of the tidal range in any cell will be observed. Hence, terminology has been adopted for the product to reflect the highest modelled tide observed in a given cell (HOT) and the lowest modelled tide observed (LOT) (see Sagar et al. 2017). These measures are relative to Mean Sea Level, and have no consistent relationship to Lowest (LAT) and Highest Astronomical Tide (HAT).

The inclusion of the lowest (LMT) and highest (HMT) modelled tide values for each tidal polygon indicates the highest and lowest tides modelled for that location across the full time series by the OTPS model. The relative difference between the LOT and LMT (and HOT and HMT) heights gives an indication of the extent of the tidal range represented in the Relative Extents Model.

As in ITEM v1.0, v2.0 contains some false positive land detection in open ocean regions. These are a function of the lack of data at the extremes of the observed tidal range, and features like glint and undetected cloud in these data poor regions/intervals. Methods to isolate and remove these features are in development for future versions. Issues in the DEA archive and data noise in the Esperance, WA region off Cape Le Grande and Cape Arid (Polygons 236,201,301) has resulted in significant artefacts in the model, and use of the model in this area is not recommended.
                
The Confidence layer is designed to assess the reliability of the Relative Extent Model. Within each tidal range percentile interval, the pixel-based standard deviation of the NDWI values for all observations in the interval subset is calculated. The average standard deviation across all tidal range intervals is then calculated and retained as a quality indicator in this product layer.

The Confidence Layer reflects the pixel based consistency of the NDWI values within each subset of observations, based on the tidal range. Higher standard deviation values indicate water classification changes not based on the tidal cycle, and hence lower confidence in the extent model.

Possible drivers of these changes include:

Inadequacies of the tidal model, due perhaps to complex coastal bathymetry or estuarine structures not captured in the model. These effects have been reduced in ITEM v2.0 compared to previous versions, through the use of an improved tidal modelling frameworkChange in the structure and exposure of water/non-water features NOT driven by tidal variation. 
For example, movement of sand banks in estuaries, construction of man-made features (ports etc.).Terrestrial/Inland water features not influenced by the tidal cycle.
File naming:
THE RELATIVE EXTENTS MODEL v2.0
ITEM_REL_<TIDAL POLYGON NUMBER>_<LONGITUDE>_<LATITUDE>
TIDAL POLYGON NUMBER relates to the id of the tidal polygon referenced by the file
LONGITUDE is the longitude of the centroid of the tidal polygon
LATITUDE is the latitude of the centroid of the tidal polygon

THE CONFIDENCE LAYER v2.0
ITEM_STD_<TIDAL POLYGON NUMBER>_<LONGITUDE>_<LATITUDE>
TIDAL POLYGON NUMBER relates to the id of the tidal polygon referenced by the file
LONGITUDE is the longitude of the centroid of the tidal polygon
LATITUDE is the latitude of the centroid of the tidal polygon

*Overview*

The Intertidal Extents Model product is a national scale gridded dataset characterising the spatial extents of the exposed intertidal zone, at intervals of the observed tidal range (Sagar et al. 2017).The current version (2.0) utilises all Landsat observations (5, 7, and 8) for Australian coastal regions (excluding off-shore Territories) between 1986 and 2016 (inclusive).

ITEM v2.0 has implemented an improved tidal modelling framework (see Sagar et al. 2018) over that utilised in ITEM v1.0. The expanded Landsat archive within the Digital Earth Australia (DEA) has also enabled the model extent to be increased to cover a number of offshore reefs, including the full Great Barrier Reef and southern sections of the Torres Strait Islands. 
The DEA archive and new tidal modelling framework has improved the coverage and quality of the ITEM v2.0 relative extents model, particularly in regions where AGDC cell boundaries in ITEM v1.0 produced discontinuities or the imposed v1.0 cell structure resulted in poor quality tidal modelling (see Sagar et al. 2017).
For service status information, see https://status.dea.ga.gov.au""",
                    "product_name": "item_v2_conf",
                    "bands": bands_item_conf,
                    "resource_limits": reslim_item,
                    "time_resolution": "month",
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": True,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["stddev"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "confidence_layer",
                        "styles": [
                            style_item_confidence,
                        ]
                    }
                },
            ]
        },
        {
                "name": "low_tide_composite",
                "title": "High Tide Low Tide Composite 25m Tidal Composite (Low Tide)",
                "abstract":"""
High Tide and Low Tide Composites 2.0.0
           
The High and Low Tide Composites product is composed of two surface reflectance composite mosaics of Landsat TM and ETM+ (Landsat 5 and Landsat 7 respectively) and OLI (Landsat 8) surface reflectance data (Li et al., 2012). These products have been produced using Digital Earth Australia (DEA). 
The two mosaics allow cloud free and noise reduced visualisation of the shallow water and inter-tidal coastal regions of Australia, as observed at high and low tide respectively (Sagar et al. 2018).
            
The composites are generated utilising the geomedian approach of Roberts et al (2017) to ensure a valid surface reflectance spectra suitable for uses such as habitat mapping. 
The time range used for composite generation in each polygon of the mosaic is tailored to ensure dynamic coastal features are captured whilst still allowing a clean and cloud free composite to be generated. The concepts of the Observed Tidal Range (OTR), and Highest and Lowest Observed Tide (HOT, LOT) are discussed and described fully in Sagar et al. (2017) and the product description for the ITEM v 1.0 product (Geoscience Australia, 2016).
                        
*Overview*
            
Inter-tidal zones are difficult regions to characterise due to the dynamic nature of the tide. They are highly changeable environments, subject to forcings from the land, sea and atmosphere and yet they form critical habitats for a wide range of organisms from birds to fish and sea grass. 
By harnessing the long archive of satellite imagery over Australia's coastal zones in the DEA and pairing the images with regional tidal modelling, the archive can be sorted by tide height rather than date, enabling the inter-tidal zone to be viewed at any stage of the tide regime.
            
The High Low Tide Composites (HLTC_25) product is composed of two mosaics, distinguished by tide height, representing a composite image of the synthetic geomedian surface reflectance from Landsats 5 TM, Landsat 7 ETM+ and Landsat 8 OLI NBAR data (Li et al., 2012; Roberts et al., 2017). Oregon State Tidal Prediction (OTPS) software (Egbert and Erofeeva, 2002, 2010) was used to generate tide heights, relative to mean sea level, for the Australian continental coastline, split into 306 distinct tidal regions. 
These time and date stamped tidal values were then attributed to all coastal tile observations for their time of acquisition, creating a range of observed tide heights for the Australian coastline. The two mosaics in HLTC_25 are composited from the highest and lowest 20 % of observed tide in the ensemble and are termed HOT and LOT respectively. 
A geomedian composite for each Landsat band is calculated from the tiles in each ensemble subset to produce the respective HOT and LOT composites. Note that Landsat 7 ETM+ observations are excluded after May 2003 due to a large number of data artifacts.
            
The time range used for composite generation in each of the 306 polygons of the mosaics are tailored to ensure dynamic coastal features are captured whilst still allowing a clean and cloud free composite to be generated. 
The maximum epoch for which the products are calculated is between 1995-2017, although this varies due to data resolution and observation quality. The product also includes a count of clear observations per pixel for both mosaics and attribute summaries per polygon that include the date range, the highest and lowest modeled astronomical tide as well as the highest and lowest observed tide for that time range, the total observation count and the maximum count of observations for any one pixel in the polygon, the polygon ID number (from 1 to 306), the polygon centroid in longitude and latitude and the count of tide stages attributed to every observation used in that polygon of the mosaic. For the count of tidal stage observations, e = ebbing tide, f = flowing tide, ph = peak high tide and pl = peak low tide. 
The tide stages were calculated bycomparison to the modeled tide data for 15 minutes either side of the observation to determine the ebb, flow or peak movement of the tide.
            
Observations are filtered to remove poor quality observations including cloud, cloud shadow and band saturation (of any band).
For service status information, see https://status.dea.ga.gov.au""",
                "product_name": "low_tide_comp_20p",
                "bands": bands_ls,
                "resource_limits": reslim_landsat,
                "image_processing": {
                    "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                    "always_fetch_bands": [ ],
                    "manual_merge": True,
                },
                "wcs": {
                        "native_crs": "EPSG:3577",
                    "default_bands": ["red", "green", "blue"],
                    "native_resolution": [ 25.0, -25.0 ],
                },
                "styling": {
                    "default_style": "simple_rgb",
                    "styles": [
                        style_ls_simple_rgb, 
                        style_ls_irg, style_ls_ndvi, style_ls_ndwi, style_ls_mndwi,
                        style_sentinel_pure_blue, style_ls_pure_green, style_ls_pure_red,
                        style_ls_pure_nir, style_ls_pure_swir1, style_ls_pure_swir2,
                    ]
                }
            },
            {
            "title": "National Intertidal Digital Elevation Model",
            "abstract": "",
            "layers": [
                {
                    "name": "NIDEM",
                    "title": "National Intertidal Digital Elevation Model nidem_v1.0.0 grid (NIDEM 25m)",
                    "abstract": """            
The National Intertidal Digital Elevation Model (NIDEM; Bishop-Taylor et al. 2019) is a continental-scale elevation dataset for Australia's exposed intertidal zone. NIDEM provides the first three-dimensional representation of Australia's intertidal sandy beaches and shores, tidal flats and rocky shores and reefs at 25 m spatial resolution, addressing a key gap between the availability of sub-tidal bathymetry and terrestrial elevation data. NIDEM was generated by combining global tidal modelling with a 30-year time series archive of spatially and spectrally calibrated Landsat satellite data managed within the Digital Earth Australia (DEA) platform. NIDEM complements existing intertidal extent products, and provides data to support a new suite of use cases that require a more detailed understanding of the three-dimensional topography of the intertidal zone, such as hydrodynamic modelling, coastal risk management and ecological habitat mapping.
                            
*Overview*
                
Intertidal environments support important ecological habitats (e.g. sandy beaches and shores, tidal flats and rocky shores and reefs), and provide many valuable benefits such as storm surge protection, carbon storage and natural resources for recreational and commercial use. However, intertidal zones are faced with increasing threats from coastal erosion, land reclamation (e.g. port construction), and sea level rise. Accurate elevation data describing the height and shape of the coastline is needed to help predict when and where these threats will have the greatest impact. However, this data is expensive and challenging to map across the entire intertidal zone of a continent the size of Australia.

The rise and fall of the ocean can be used to describe the three-dimensional shape of the coastline by mapping the land-sea boundary (or 'waterline') across a range of known tides (e.g. low tide, high tide). Assuming that these waterlines represent lines of constant height relative to mean sea level (MSL), elevations can be modelled for the area of coastline located between the lowest and highest observed tide. To model the elevation of Australia's entire intertidal zone, 30 years of satellite images of the coastline (between 1986 and 2016 inclusive) were obtained from the archive of spatially and spectrally calibrated Landsat observations managed within the Digital Earth Australia (DEA) platform. Using the improved tidal modelling framework of the Intertidal Extents Model v2.0 (ITEM 2.0; Sagar et al. 2017, 2018), each satellite observation in the 30 year time series could be accurately associated with a modelled tide height using the global TPX08 ocean tidal model. These satellite observations were converted into a water index (NDWI), composited into discrete ten percent intervals of the observed tide range (e.g. the lowest 10% of observed tides etc), and used to extract waterlines using a spatially consistent and automated waterline extraction procedure. Triangulated irregular network (TIN) interpolation was then used to derive elevations relative to modelled mean sea level for each 25 x 25 m Landsat pixel across approximately 15,387 sq. km of intertidal terrain along Australia's entire coastline.

NIDEM differs from previous methods used to model the elevation of the intertidal zone which have predominately focused on extracting waterlines from a limited selection of satellite images using manual digitisation and visual interpretation (e.g. Chen and Rau 1998; Zhao et al. 2008; Liu et al. 2013; Chen et al. 2016). This manual process introduces subjectivity, is impractical to apply at a continental-scale, and has inherent restrictions based on the availability of high quality image data at appropriate tidal stages. By developing an automated approach to generating satellite-derived elevation data based on a 30 year time series of observations managed within the Digital Earth Australia (DEA) platform, it was possible to produce the first continental-scale three-dimensional model of the intertidal zone.

*Accuracy*

To assess the accuracy of NIDEM, we compared modelled elevations against three independent elevation and bathymetry validation datasets: the DEM of Australia derived from LiDAR 5 Metre Grid (Geoscience Australia, 2015), elevation data collected from Real Time Kinematic (RTK) GPS surveys (Danaher & Collett, 2006; HydroSurvey Australia, 2009), and 1.0 m resolution multibeam bathymetry surveys (Solihuddin et al., 2016). We assessed overall accuracy across three distinct intertidal environments: sandy beaches and shores, tidal flats, and rocky shores and reefs:

 - Sandy beaches and shores, 5 sites: Pearson's correlation = 0.92, Spearman's correlation = 0.93, RMSE +/- 0.41 m
 - Tidal flats, 9 sites: Pearson's correlation = 0.78, Spearman's correlation = 0.81, RMSE +/- 0.39 m
 - Rocky shores and reefs, 7 sites: Pearson's correlation = 0.46, Spearman's correlation = 0.79, RMSE +/- 2.98 m

*Limitations*

NIDEM covers the exposed intertidal zone which includes sandy beaches and shores, tidal flats and rocky shores and reefs. The model excludes intertidal vegetation communities such as mangroves.

Areas with comparatively steep coastlines and small tidal ranges are poorly captured in the 25 m spatial resolution input Landsat data and resulting NIDEM model. This includes much of the south eastern and southern Australian coast (e.g. New South Wales, Victoria, Tasmania).

Poor validation results for rocky shore and reef sites within the southern Kimberly region highlighted limitations in the NIDEM model that occur when the global OTPS TPX08 Atlas Tidal Model was unable to predict complex and asynchronous local tidal patterns. This is likely to also reduce model accuracy in complex estuaries and coastal wetlands where river flow or vegetative resistance causes hydrodynamic attenuation in tidal flow.

The complex temporal behaviour of tides mean that a sun synchronous sensor like Landsat does not observe the full range of the tidal cycle at all locations. This causes spatial bias in the proportion of the tidal range observed in different regions, which can prevent NIDEM from providing elevation data for areas of the intertidal zone exposed or inundated at the extremes of the tidal range. Accordingly, NIDEM provides elevation data for the portion of the tidal range observed by Landsat, rather than the full tidal range.

While image compositing and masking methods have been applied to remove the majority of noise and non-tidal artefacts from NIDEM, issues remain in several locations. It is recommended that the data be used with caution in the following areas: 

 - The Recherche Archipelago in southern Western Australia
 - Port Phillip Bay in Victoria
 - The eastern coast of Tasmania and King Island
 - Saunders Reef and surrounds in the northern Coral Sea
 
*Data access and additional information*

 - Journal article: Bishop-Taylor et al. 2019 (https://doi.org/10.1016/j.ecss.2019.03.006) 
 - Data available on THREDDS: http://dapds00.nci.org.au/thredds/catalogs/fk4/nidem_1_0.html
 - eCat catalogue listing including data access: http://pid.geoscience.gov.au/dataset/ga/123678
 - CMI listing for extended metadata: https://cmi.ga.gov.au/pd/NIDEM_25_1.0.0 

For service status information, see https://status.dea.ga.gov.au""",
                    "product_name": "nidem",
                    "bands": bands_nidem,
                    "resource_limits": reslim_nidem,
                    "time_resolution": "year",
                    "flags": {
                        "band": "land",
                        "product": "geodata_coast_100k",
                        "ignore_time": True,
                        "ignore_info_flags": [],
                    },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["nidem"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "NIDEM",
                        "styles": [
                            style_nidem,
                        ]
                    }
                },
            ]
        },
        {
            "title": "Mangrove Canopy Cover",
            "abstract": "",
            "layers": [
                {
                    "name": "mangrove_cover_v2_0_2",
                    "title": "Mangrove Canopy Cover 25m 100km tile (Mangrove Canopy Cover V2.0.2)",
                    "abstract": """
Mangrove canopy cover version 2.0.2, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region.

The mangrove canopy cover product provides valuable information about the extent and canopy density of mangroves for each year between 1987 and 2016 for the entire Australian coastline.
The canopy cover classes are:
20-50% (pale green), 50-80% (mid green), 80-100% (dark green).

The product consists of  a sequence (one per year) of 25 meter resolution maps that are generated by analysing the Landsat fractional cover (https://doi.org/10.6084/m9.figshare.94250.v1) developed by the Joint Remote Sensing Research Program and the Global Mangrove Watch layers (https://doi.org/10.1071/MF13177) developed by the Japanese Aerospace Exploration Agency.

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "mangrove_cover",
                    "bands": bands_mangrove,
                    "resource_limits": reslim_mangrove,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_extent_val",
                        "always_fetch_bands": [ "extent" ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [25.0, -25.0],
                        "default_bands": ["canopy_cover_class", "extent"]
                    },
                    "styling": {
                        "default_style": "mangrove",
                        "styles": [
                            style_mangrove_cover_v2,
                        ]
                    }
                },
            ]
        },

        {
            "title": "Fractional Cover",
            "abstract": """
Fractional Cover version 2.2.1, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region.
Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover

Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena. To be considered in the FCP product a pixel must have had at least 10 clear observations over the year.

For service status information, see https://status.dea.ga.gov.au
""",
            "layers": [
                {
                    "title": "Fractional Cover 25m 100km tile (Fractional Cover Landsat 5)",
                    "name": "ls5_fc_albers",
                    "abstract": """
Fractional Cover version 2.2.1, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region.
Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover

Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena.

This product contains Fractional Cover dervied from the Landsat 5 satellite

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "ls5_fc_albers",
                    "bands": bands_fc,
                    "resource_limits": reslim_aster,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "flags": {
                        "band": "water",
                        "product": "wofs_albers",
                        "ignore_time": False,
                        "ignore_info_flags": [],
                        "fuse_func": "datacube_ows.wms_utils.wofls_fuser",
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["BS", "PV", "NPV"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "simple_fc",
                        "styles": [
                            style_fc_simple,
                        ]
                    }
                },
                {
                    "title": "Fractional Cover 25m 100km tile (Fractional Cover Landsat 7)",
                    "name": "ls7_fc_albers",
                    "abstract": """
Fractional Cover version 2.2.1, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region.
Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover

Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena.

This product contains Fractional Cover dervied from the Landsat 7 satellite

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "ls7_fc_albers",
                    "bands": bands_fc,
                    "resource_limits": reslim_aster,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "flags": {
                        "band": "water",
                        "product": "wofs_albers",
                        "ignore_time": False,
                        "ignore_info_flags": [],
                        "fuse_func": "datacube_ows.wms_utils.wofls_fuser",
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["BS", "PV", "NPV"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "simple_fc",
                        "styles": [
                            style_fc_simple,
                        ]
                    }
                },
                {
                    "title": "Fractional Cover 25m 100km tile (Fractional Cover Landsat 8)",
                    "name": "ls8_fc_albers",
                    "abstract": """
Fractional Cover version 2.2.1, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region.
Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover

Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena.

This product contains Fractional Cover dervied from the Landsat 8 satellite

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "ls8_fc_albers",
                    "bands": bands_fc,
                    "resource_limits": reslim_aster,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "flags": {
                        "band": "water",
                        "product": "wofs_albers",
                        "ignore_time": False,
                        "ignore_info_flags": [],
                        "fuse_func": "datacube_ows.wms_utils.wofls_fuser",
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["BS", "PV", "NPV"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "simple_fc",
                        "styles": [
                            style_fc_simple,
                        ]
                    }
                },
                {
                    "title": "Fractional Cover 25m 100km tile (Fractional Cover Combined)",
                    "name": "fc_albers_combined",
                    "abstract": """
Fractional Cover version 2.2.1, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region. Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena. This product contains Fractional Cover dervied from the Landsat 5, 7 and 8 satellites For service status information, see https://status.dea.ga.gov.au	
""",
                    "multi_product": True,
                    "product_names": [ "ls5_fc_albers", "ls7_fc_albers", "ls8_fc_albers" ],
                    "bands": bands_fc,
                    "resource_limits": reslim_aster,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "flags": {
                        "band": "water",
                        "products": ['wofs_albers', 'wofs_albers', 'wofs_albers'],
                        "ignore_time": False,
                        "ignore_info_flags": [],
                        "fuse_func": "datacube_ows.wms_utils.wofls_fuser",
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["BS", "PV", "NPV"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "simple_fc",
                        "styles": [
                            style_fc_simple,
                        ]
                    }
                },
            ]
        },
{
            "title": "Fractional Cover Percentiles Seasonal",
            "abstract": "",
            "layers": [
                {
                    "title": "Fractional Cover Percentiles Seasonal 25m 100km tile (Green Vegetation)",
                    "name": "fcp_green_veg",
                    "abstract": """
Fractional Cover Percentiles version 2.2.0, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region.
Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The percentile summaries are designed to make it easier to analyse and interpret fractional cover. Percentiles provide an indicator of where an observation sits, relative to the rest of the observations for the pixel. For example, the 90th percentile is the value below which 90% of the observations fall. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover

 FC-PERCENTILE-SEASONAL-SUMMARY, this contains a (10th, 50th and 90th percentile) of BS, PV and NPV of observations acquired within each calendar season (DJF, MAM, JJA, SON). This product is available for the most recent 8 seasons

Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena. To be considered in the FCP product a pixel must have had at least 10 clear observations over the year.

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "fc_percentile_albers_seasonal",
                    "bands": bands_fc_percentile,
                    "resource_limits": reslim_frac_cover,
                    "flags": {
                        "band": "land",
                        "product": "geodata_coast_100k",
                        "ignore_time": True,
                        "ignore_info_flags": [],
                    },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["NPV_PC_10", "NPV_PC_50", "NPV_PC_90"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "green_veg_10",
                        "styles": [
                            style_fc_gv_10, style_fc_gv_50, style_fc_gv_90,
                        ]
                    }
                },
                {
                    "title": "Fractional Cover Percentiles Seasonal 25m 100km tile (Non Green Vegetation)",
                    "name": "fcp_seasonal_non_green_veg",
                    "abstract": """
Fractional Cover Percentiles version 2.2.0, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region.
Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The percentile summaries are designed to make it easier to analyse and interpret fractional cover. Percentiles provide an indicator of where an observation sits, relative to the rest of the observations for the pixel. For example, the 90th percentile is the value below which 90% of the observations fall. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program, for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover

 FC-PERCENTILE-SEASONAL-SUMMARY, this contains a (10th, 50th and 90th percentile) of BS, PV and NPV of observations acquired within each calendar season (DJF, MAM, JJA, SON). This product is available for the most recent 8 seasons

Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena. To be considered in the FCP product a pixel must have had at least 10 clear observations over the year.

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "fc_percentile_albers_seasonal",
                    "bands": bands_fc_percentile,
                    "resource_limits": reslim_frac_cover,
                    "flags": {
                        "band": "land",
                        "product": "geodata_coast_100k",
                        "ignore_time": True,
                        "ignore_info_flags": [],
                    },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["NPV_PC_10", "NPV_PC_50", "NPV_PC_90"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "non_green_veg_10",
                        "styles": [
                            style_fc_ngv_10, style_fc_ngv_50, style_fc_ngv_90,
                        ]
                    }
                },
                {
                    "title": "Fractional Cover Percentiles Seasonal 25m 100km tile (Bare Soil)",
                    "name": "fcp_seasonal_bare_ground",
                    "abstract": """
	Fractional Cover Percentiles version 2.2.0, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region. Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The percentile summaries are designed to make it easier to analyse and interpret fractional cover. Percentiles provide an indicator of where an observation sits, relative to the rest of the observations for the pixel. For example, the 90th percentile is the value below which 90% of the observations fall. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program for more information please see data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Fractional+Cover FC-PERCENTILE-SEASONAL-SUMMARY, this contains a (10th, 50th and 90th percentile) of BS, PV and NPV of observations acquired within each calendar season (DJF, MAM, JJA, SON). This product is available for the most recent 8 seasons Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena. To be considered in the FCP product a pixel must have had at least 10 clear observations over the year. For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "fc_percentile_albers_seasonal",
                    "bands": bands_fc_percentile,
                    "resource_limits": reslim_frac_cover,
                    "flags": {
                        "band": "land",
                        "product": "geodata_coast_100k",
                        "ignore_time": True,
                        "ignore_info_flags": [],
                    },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["BS_PC_10", "BS_PC_50", "BS_PC_90"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "bare_ground_10",
                        "styles": [
                            style_fc_bs_10, style_fc_bs_50, style_fc_bs_90,
                        ]
                    }
                },
                {
                    "title": "Fractional Cover Percentiles Seasonal 25m 100km tile (Median)",
                    "name": "fcp_seasonal_rgb",
                    "abstract": """
	Fractional Cover Percentiles version 2.2.0, 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577). Data is only visible at higher resolutions; when zoomed-out the available area will be displayed as a shaded region. Fractional cover provides information about the the proportions of green vegetation, non-green vegetation (including deciduous trees during autumn, dry grass, etc.), and bare areas for every 25m x 25m ground footprint. Fractional cover provides insight into how areas of dry vegetation and/or bare soil and green vegetation are changing over time. The percentile summaries are designed to make it easier to analyse and interpret fractional cover. Percentiles provide an indicator of where an observation sits, relative to the rest of the observations for the pixel. For example, the 90th percentile is the value below which 90% of the observations fall. The fractional cover algorithm was developed by the Joint Remote Sensing Research Program. FC-PERCENTILE-SEASONAL-SUMMARY, this contains a (10th, 50th and 90th percentile) of BS, PV and NPV of observations acquired within each calendar season (DJF, MAM, JJA, SON). This product is available for the most recent 8 seasons Fractional Cover products use Water Observations from Space (WOfS) to mask out areas of water, cloud and other phenomena. To be considered in the FCP product a pixel must have had at least 10 clear observations over the year. For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "fc_percentile_albers_seasonal",
                    "bands": bands_fc_percentile,
                    "resource_limits": reslim_frac_cover,
                    "flags": {
                        "band": "land",
                        "product": "geodata_coast_100k",
                        "ignore_time": True,
                        "ignore_info_flags": [],
                    },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "default_bands": ["BS_PC_50", "PV_PC_50", "NPV_PC_90"],
                        "native_resolution": [ 25.0, -25.0 ],
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_fc_simple_rgb
                        ]
                    }
                },
            ]
        },
        {
                    "title": "Water Observations from Space 25m Water Summary (WOfS November - March Statistics)",
                    "name": "wofs_nov_mar_summary_statistics",
                    "abstract": """
Water Observations from Space - Seasonal Statistics is a set of seasonal statistical summaries of the water observations contained in WOfS. The layers available are: the count of clear observations; the count of wet observations; the percentage of wet observations over time. This product is Water Observations from Space - November to March Statistics, a set of seasonal statistical summaries of the WOfS product that combines the many years of WOfS observations into summary products that help the understanding of surface water across Australia. As no confidence filtering is applied to this product, it is affected by noise where misclassifications have occurred in the WOfS water classifications, and hence can be difficult to interpret on its own. The confidence layer and filtered summary are contained in the Water Observations from Space Statistics - Filtered Summary product, which provide a noise-reduced view of the water summary. This layer contains Water Summary: what percentage of clear observations were detected as wet (ie. the ratio of wet to clear as a percentage). No clear observations of water causes an area to appear transparent, few clear observations of water correlate with red and yellow colours, deep blue and purple correspond to an area being wet through 90%-100% of clear observations. For service status information, see https://status.dea.ga.gov.au	
""",
                    "product_name": "wofs_nov_mar_summary",
                    "bands": bands_wofs_sum,
                    "resource_limits": reslim_wofs,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [25.0, -25.0],
                        "default_bands": ["frequency"]
                    },
                    "styling": {
                        "default_style": "seasonal_WOfS_frequency",
                        "styles": [
                            style_seasonal_wofs_summary_frequency,
                            style_seasonal_wofs_summary_frequency_blue,
                        ]
                    }
                },
        {
                    "title": "Water Observations from Space 25m Water Summary (WOfS Annual Statistics)",
                    "name": "wofs_annual_summary_statistics",
                    "abstract": """
Water Observations from Space - Annual Statistics is a set of annual statistical summaries of the water observations contained in WOfS. The layers available are: the count of clear observations; the count of wet observations; the percentage of wet observations over time.

This product is Water Observations from Space - Annual Statistics, a set of annual statistical summaries of the WOfS product that combines the many years of WOfS observations into summary products that help the understanding of surface water across Australia. As no confidence filtering is applied to this product, it is affected by noise where misclassifications have occurred in the WOfS water classifications, and hence can be difficult to interpret on its own.
The confidence layer and filtered summary are contained in the Water Observations from Space Statistics - Filtered Summary product, which provide a noise-reduced view of the water summary.

This layer contains Water Summary: what percentage of clear observations were detected as wet (ie. the ratio of wet to clear as a percentage). No clear observations of water causes an area to appear transparent, few clear observations of water correlate with red and yellow colours, deep blue and purple correspond to an area being wet through 90%-100% of clear observations.
For more information please see: https://data.dea.ga.gov.au/WOfS/annual_summary/v2.1.5/Product%20Description.pdf

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "wofs_annual_summary",
                    "bands": bands_wofs_sum,
                    "resource_limits": reslim_wofs,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [25.0, -25.0],
                        "default_bands": ["frequency"]
                    },
                    "styling": {
                        "default_style": "annual_WOfS_frequency",
                        "styles": [
                            style_annual_wofs_summary_frequency,
                            style_annual_wofs_summary_frequency_blue,
                        ]
                    }
                },

#         {
#                    "title": "ALOS/PALSAR",
#                    "abstract": """Annual mosaic of ALOS/PALSAR and ALOS-2/PALSAR-2 data""",
#                    "layers": [
#                    {
#                        "title": "ALOS/PALSAR Synthetic aperture radar (JAXA)",
#                        "name": "alos_palsar_mosaic",
#                        "abstract": """The ALOS/PALSAR annual mosaic is a global 25 m resolution dataset that combines data from many images captured by JAXA's PALSAR and PALSAR two sensors on ALOS-1 and ALOS-2 satellites respectively. For more information, see: https://www.eorc.jaxa.jp/ALOS/en/palsar_fnf/DatasetDescription_PALSAR2_Mosaic_FNF_revH.pdf""",
#                        "product_name": "alos_palsar_mosaic",
#                        "bands": bands_alos,
#                        "resource_limits": reslim_alos_palsar,
#                        "image_processing": {
#                            "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
#                            "always_fetch_bands": [],
#                            "manual_merge": True,
#                        },
#                        "flags":{
#                            "dataset": "alos_palsar_mosaic",
#                            "band": "mask",
#                            "ignore_info_flags": [],
#                        },
#                        "wcs": {
#                            "native_crs": "EPSG:3577",
#                            "native_resolution": [25.0, 25.0],
#                            "default_bands": ["hh", "hv", "mask"]
#                        },
#                        "styling": {
#                            "default_style": "hh",
#                            "styles": [
#                                style_alos_hh, style_alos_hv, style_alos_hh_over_hv, style_alos_hv_over_hh
#                            ]
#                        }
#                    },
#                    
#                ]
#            },

            {
                    "name": "s2a_ard_granule_nbar_t",
                    "title": "Sentinel Definitive Surface Reflectance (Sentinel 2A)",
                    "abstract": """
	This is a definitive archive of daily Sentinel-2 data. This is processed using correct ancillary data to provide a more accurate product than the Near Real Time. The Surface Reflectance product has been corrected to account for variations caused by atmospheric properties, sun position and sensor view angle at time of image capture. These corrections have been applied to all satellite imagery in the Sentinel-2 archive. For more information see http://pid.geoscience.gov.au/dataset/ga/129684 The Normalised Difference Chlorophyll Index (NDCI) is based on the method of Mishra & Mishra 2012, and adapted to bands on the Sentinel-2A & B sensors. The index indicates levels of chlorophyll-a (chl-a) concentrations in complex turbid productive waters such as those encountered in many inland water bodies. The index has not been validated in Australian waters, and there are a range of environmental conditions that may have an effect on the accuracy of the derived index values in this test implementation, including: - Influence on the remote sensing signal from nearby land and/or atmospheric effects - Optically shallow water - Cloud cover Mishra, S., Mishra, D.R., 2012. Normalized difference chlorophyll index: A novel model for remote estimation of chlorophyll-a concentration in turbid productive waters. Remote Sensing of Environment, Remote Sensing of Urban Environments 117, 394–406. https://doi.org/10.1016/j.rse.2011.10.016 For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "s2a_ard_granule",
                    "bands": bands_sentinel2,
                    "resource_limits": reslim_s2_ard,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [ 10.0, -10.0 ],
                        "default_bands": [ "nbart_red", "nbart_green", "nbart_blue" ]
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_s2_simple_rgb,
                            style_s2_irg,
                            style_s2_ndvi, style_s2_ndwi, style_s2_mndwi, style_s2_ndci,
                            style_s2_pure_aerosol,
                            style_s2_pure_blue, style_s2_pure_green, style_s2_pure_red,
                            style_s2_pure_redge_1, style_s2_pure_redge_2, style_s2_pure_redge_3,
                            style_s2_pure_nir, style_s2_pure_narrow_nir,
                            style_s2_pure_swir1, style_s2_pure_swir2, 
                            style_s2_nbr
                        ]
                    }
                },
            {
                    "name": "s2b_ard_granule_nbar_t",
                    "title": "Sentinel Definitive Surface Reflectance (Sentinel 2B)",
                    "abstract": """
	This is a definitive archive of daily Sentinel-2 data. This is processed using correct ancillary data to provide a more accurate product than the Near Real Time. The Surface Reflectance product has been corrected to account for variations caused by atmospheric properties, sun position and sensor view angle at time of image capture. These corrections have been applied to all satellite imagery in the Sentinel-2 archive. For more information see http://pid.geoscience.gov.au/dataset/ga/129684 The Normalised Difference Chlorophyll Index (NDCI) is based on the method of Mishra & Mishra 2012, and adapted to bands on the Sentinel-2A & B sensors. The index indicates levels of chlorophyll-a (chl-a) concentrations in complex turbid productive waters such as those encountered in many inland water bodies. The index has not been validated in Australian waters, and there are a range of environmental conditions that may have an effect on the accuracy of the derived index values in this test implementation, including: - Influence on the remote sensing signal from nearby land and/or atmospheric effects - Optically shallow water - Cloud cover Mishra, S., Mishra, D.R., 2012. Normalized difference chlorophyll index: A novel model for remote estimation of chlorophyll-a concentration in turbid productive waters. Remote Sensing of Environment, Remote Sensing of Urban Environments 117, 394–406. https://doi.org/10.1016/j.rse.2011.10.016 For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "s2b_ard_granule",
                    "bands": bands_sentinel2,
                    "resource_limits": reslim_s2_ard,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [ 10.0, -10.0 ],
                        "default_bands": [ "nbart_red", "nbart_green", "nbart_blue" ]
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_s2_simple_rgb,
                            style_s2_irg,
                            style_s2_ndvi, style_s2_ndwi, style_s2_mndwi, style_s2_ndci,
                            style_s2_pure_aerosol,
                            style_s2_pure_blue, style_s2_pure_green, style_s2_pure_red,
                            style_s2_pure_redge_1, style_s2_pure_redge_2, style_s2_pure_redge_3,
                            style_s2_pure_nir, style_s2_pure_narrow_nir,
                            style_s2_pure_swir1, style_s2_pure_swir2, 
                            style_s2_nbr
                        ]
                    }
                },

{
            "title": "Near Real-Time",
            "abstract": """
This is a 90-day rolling archive of daily Sentinel-2 Near Real Time data.

The Near Real-Time capability provides analysis-ready data that is processed on receipt using
the best-available ancillary information at the time to provide atmospheric corrections.

For more information see http://pid.geoscience.gov.au/dataset/ga/122229
""",
            "layers": [
                {
                    "name": "s2_nrt_granule_nbar_t",
                    "title": "Near Real-Time Surface Reflectance (Sentinel 2 (A and B combined))",
                    "abstract": """
This is a 90-day rolling archive of daily Sentinel-2 Near Real Time data. The Near Real-Time capability provides analysis-ready data that is processed on receipt using the best-available ancillary information at the time to provide atmospheric corrections.

For more information see http://pid.geoscience.gov.au/dataset/ga/122229

The Normalised Difference Chlorophyll Index (NDCI) is based on the method of Mishra & Mishra 2012, and adapted to bands on the Sentinel-2A & B sensors.
The index indicates levels of chlorophyll-a (chl-a) concentrations in complex turbid productive waters such as those encountered in many inland water bodies. The index has not been validated in Australian waters, and there are a range of environmental conditions that may have an effect on the accuracy of the derived index values in this test implementation, including:
- Influence on the remote sensing signal from nearby land and/or atmospheric effects
- Optically shallow water
- Cloud cover
Mishra, S., Mishra, D.R., 2012. Normalized difference chlorophyll index: A novel model for remote estimation of chlorophyll-a concentration in turbid productive waters. Remote Sensing of Environment, Remote Sensing of Urban Environments 117, 394–406. https://doi.org/10.1016/j.rse.2011.10.016

For service status information, see https://status.dea.ga.gov.au
""",
                    "multi_product": True,
                    "product_names": [ "s2a_nrt_granule", "s2b_nrt_granule" ],
                    "bands": bands_sentinel2,
                    "resource_limits": reslim_s2,
                    "dynamic": True,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [ 10.0, -10.0 ],
                        "default_bands": [ "nbart_red", "nbart_green", "nbart_blue" ]
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_s2_simple_rgb,
                            style_s2_irg,
                            style_s2_ndvi, style_s2_ndwi, style_s2_mndwi, style_s2_ndci,
                            style_s2_pure_aerosol,
                            style_s2_pure_blue, style_s2_pure_green, style_s2_pure_red,
                            style_s2_pure_redge_1, style_s2_pure_redge_2, style_s2_pure_redge_3,
                            style_s2_pure_nir, style_s2_pure_narrow_nir,
                            style_s2_pure_swir1, style_s2_pure_swir2, style_s2_nbr
                        ]
                    }
                },
                {
                    "name": "s2_nrt_granule_nbar_nondyn",
                    "title": "Near Real-Time Surface Reflectance (Sentinel 2 (A and B combined)(nondyn))",
                    "abstract": """
This is a 90-day rolling archive of daily Sentinel-2 Near Real Time data. The Near Real-Time capability provides analysis-ready data that is processed on receipt using the best-available ancillary information at the time to provide atmospheric corrections.
(nondyn)
For more information see http://pid.geoscience.gov.au/dataset/ga/122229

The Normalised Difference Chlorophyll Index (NDCI) is based on the method of Mishra & Mishra 2012, and adapted to bands on the Sentinel-2A & B sensors.
The index indicates levels of chlorophyll-a (chl-a) concentrations in complex turbid productive waters such as those encountered in many inland water bodies. The index has not been validated in Australian waters, and there are a range of environmental conditions that may have an effect on the accuracy of the derived index values in this test implementation, including:
- Influence on the remote sensing signal from nearby land and/or atmospheric effects
- Optically shallow water
- Cloud cover
Mishra, S., Mishra, D.R., 2012. Normalized difference chlorophyll index: A novel model for remote estimation of chlorophyll-a concentration in turbid productive waters. Remote Sensing of Environment, Remote Sensing of Urban Environments 117, 394–406. https://doi.org/10.1016/j.rse.2011.10.016

For service status information, see https://status.dea.ga.gov.au
""",
                    "multi_product": True,
                    "product_names": [ "s2a_nrt_granule", "s2b_nrt_granule" ],
                    "bands": bands_sentinel2,
                    "resource_limits": reslim_s2,
                    "dynamic": False,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [ 10.0, -10.0 ],
                        "default_bands": [ "nbart_red", "nbart_green", "nbart_blue" ]
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_s2_simple_rgb,
                            style_s2_irg,
                            style_s2_ndvi, style_s2_ndwi, style_s2_mndwi, style_s2_ndci,
                            style_s2_pure_aerosol,
                            style_s2_pure_blue, style_s2_pure_green, style_s2_pure_red,
                            style_s2_pure_redge_1, style_s2_pure_redge_2, style_s2_pure_redge_3,
                            style_s2_pure_nir, style_s2_pure_narrow_nir,
                            style_s2_pure_swir1, style_s2_pure_swir2, style_s2_nbr
                        ]
                    }
                },
                {
                    "name": "s2b_nrt_granule_nbar_t",
                    "title": "Near Real-Time Surface Reflectance (Sentinel 2B)",
                    "abstract": """
This is a 90-day rolling archive of daily Sentinel-2 Near Real Time data. The Near Real-Time capability provides analysis-ready data that is processed on receipt using the best-available ancillary information at the time to provide atmospheric corrections.

For more information see http://pid.geoscience.gov.au/dataset/ga/122229

The Normalised Difference Chlorophyll Index (NDCI) is based on the method of Mishra & Mishra 2012, and adapted to bands on the Sentinel-2A & B sensors.
The index indicates levels of chlorophyll-a (chl-a) concentrations in complex turbid productive waters such as those encountered in many inland water bodies. The index has not been validated in Australian waters, and there are a range of environmental conditions that may have an effect on the accuracy of the derived index values in this test implementation, including:
- Influence on the remote sensing signal from nearby land and/or atmospheric effects
- Optically shallow water
- Cloud cover
Mishra, S., Mishra, D.R., 2012. Normalized difference chlorophyll index: A novel model for remote estimation of chlorophyll-a concentration in turbid productive waters. Remote Sensing of Environment, Remote Sensing of Urban Environments 117, 394–406. https://doi.org/10.1016/j.rse.2011.10.016

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "s2b_nrt_granule",
                    "bands": bands_sentinel2,
                    "resource_limits": reslim_s2,
                    "dynamic": True,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [ 10.0, -10.0 ],
                        "default_bands": [ "nbart_red", "nbart_green", "nbart_blue" ]
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_s2_simple_rgb,
                            style_s2_irg,
                            style_s2_ndvi, style_s2_ndwi, style_s2_mndwi, style_s2_ndci,
                            style_s2_pure_aerosol,
                            style_s2_pure_blue, style_s2_pure_green, style_s2_pure_red,
                            style_s2_pure_redge_1, style_s2_pure_redge_2, style_s2_pure_redge_3,
                            style_s2_pure_nir, style_s2_pure_narrow_nir,
                            style_s2_pure_swir1, style_s2_pure_swir2,
                        ]
                    }
                },
                {
                    "name": "s2a_nrt_granule_nbar_t",
                    "title": "Near Real-Time Surface Reflectance (Sentinel 2A)",
                    "abstract": """
This is a 90-day rolling archive of daily Sentinel-2 Near Real Time data. The Near Real-Time capability provides analysis-ready data that is processed on receipt using the best-available ancillary information at the time to provide atmospheric corrections.

For more information see http://pid.geoscience.gov.au/dataset/ga/122229

The Normalised Difference Chlorophyll Index (NDCI) is based on the method of Mishra & Mishra 2012, and adapted to bands on the Sentinel-2A & B sensors.
The index indicates levels of chlorophyll-a (chl-a) concentrations in complex turbid productive waters such as those encountered in many inland water bodies. The index has not been validated in Australian waters, and there are a range of environmental conditions that may have an effect on the accuracy of the derived index values in this test implementation, including:
- Influence on the remote sensing signal from nearby land and/or atmospheric effects
- Optically shallow water
- Cloud cover
Mishra, S., Mishra, D.R., 2012. Normalized difference chlorophyll index: A novel model for remote estimation of chlorophyll-a concentration in turbid productive waters. Remote Sensing of Environment, Remote Sensing of Urban Environments 117, 394–406. https://doi.org/10.1016/j.rse.2011.10.016

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "s2a_nrt_granule",
                    "bands": bands_sentinel2,
                    "resource_limits": reslim_s2,
                    "dynamic": True,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [ 10.0, -10.0 ],
                        "default_bands": [ "nbart_red", "nbart_green", "nbart_blue" ]
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_s2_simple_rgb,
                            style_s2_irg,
                            style_s2_ndvi, style_s2_ndwi, style_s2_mndwi, style_s2_ndci,
                            style_s2_pure_aerosol,
                            style_s2_pure_blue, style_s2_pure_green, style_s2_pure_red,
                            style_s2_pure_redge_1, style_s2_pure_redge_2, style_s2_pure_redge_3,
                            style_s2_pure_nir, style_s2_pure_narrow_nir,
                            style_s2_pure_swir1, style_s2_pure_swir2, style_s2_nbr
                        ]
                    }
                },
                {
                    "name": "s2_nrt_wofs",
                    "title": "	Near Real-Time Water Classifier (Sentinel 2 WOfS NRT)",
                    "abstract": """	Sentinel 2 NRT Water Classifier. For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "sentinel2_wofs_nrt",
                    "bands": bands_wofs_obs,
                    "resource_limits": reslim_wofs,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [ 10.0, -10.0 ],
                        "default_bands": [ "water" ]
                    },
                    "styling": {
                        "default_style": "water_classifier",
                        "styles": [ style_s2_water_classifier ],
                    }
                }
            ]
        },


                {
                    "title": "Surface Reflectance Triple Median Absolute Deviation",
                    "abstract": "Surface Reflectance Triple Median Absolute Deviation 25 metre, 100km tile, Australian Albers Equal Area projection (EPSG:3577)",
                    "layers": [
                        {
                            "title": "Surface Reflectance Triple Median Absolute Deviation (Landsat 8 Annual Surface Reflectance TMAD)",
                            "abstract": """
        The three layers of the TMAD are calculated by computing the multidimensional distance between each observation in a
        time series of multispectral (or higher dimensionality such as hyperspectral) satellite imagery with the
        multidimensional median of the time series. The median used for this calculation is the geometric median corresponding
        to the time series.  The TMAD is calculated over annual time periods on Earth observations from a single sensor by
        default (such as the annual time series of Landsat 8 observations); however, it is applicable to multi-sensor time
        series of any length that computing resources can support. For the purposes of the default Digital Earth Australia
        product, TMADs are computed per calendar year, per sensor (Landsat 5, Landsat 7 and Landsat 8) from
        terrain-illumination-corrected surface reflectance data (Analysis Ready Data), compared to the annual geometric
        median of that data.
        For more information, see http://pid.geoscience.gov.au/dataset/ga/130482
        For service status information, see https://status.dea.ga.gov.au""",
                            # The WMS name for the layer
                            "name": "ls8_nbart_tmad_annual",
                            # The Datacube name for the associated data product
                            "product_name": "ls8_nbart_tmad_annual",
                            "bands": bands_tmad,
                            "resource_limits": reslim_tmad,
                            "image_processing": {
                                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                                "always_fetch_bands": [ ],
                                "manual_merge": False,
                            },
                            "wcs": {
                                "native_crs": "EPSG:3577",
                                "default_bands": ["sdev", "edev", "bcdev"],
                                "native_resolution": [ 25.0, -25.0 ],
                            },
                            "styling": {
                                "default_style": "log_sdev",
                                "styles": [
                                    style_tmad_sdev, style_tmad_edev, style_tmad_bcdev
                                ]
                            }
                        },
                        {
                            "title": "Surface Reflectance Triple Median Absolute Deviation (Landsat 7 Annual Surface Reflectance TMAD)",
                            "abstract": """
        The three layers of the TMAD are calculated by computing the multidimensional distance between each observation in a
        time series of multispectral (or higher dimensionality such as hyperspectral) satellite imagery with the
        multidimensional median of the time series. The median used for this calculation is the geometric median corresponding
        to the time series.  The TMAD is calculated over annual time periods on Earth observations from a single sensor by
        default (such as the annual time series of Landsat 8 observations); however, it is applicable to multi-sensor time
        series of any length that computing resources can support. For the purposes of the default Digital Earth Australia
        product, TMADs are computed per calendar year, per sensor (Landsat 5, Landsat 7 and Landsat 8) from
        terrain-illumination-corrected surface reflectance data (Analysis Ready Data), compared to the annual geometric
        median of that data.
        For more information, see http://pid.geoscience.gov.au/dataset/ga/130482
        For service status information, see https://status.dea.ga.gov.au""",
                            # The WMS name for the layer
                            "name": "ls7_nbart_tmad_annual",
                            # The Datacube name for the associated data product
                            "product_name": "ls7_nbart_tmad_annual",
                            "bands": bands_tmad,
                            "resource_limits": reslim_tmad,
                            "image_processing": {
                                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                                "always_fetch_bands": [ ],
                                "manual_merge": False,
                            },
                            "wcs": {
                                "native_crs": "EPSG:3577",
                                "default_bands": ["sdev", "edev", "bcdev"],
                                "native_resolution": [ 25.0, -25.0 ],
                            },
                            "styling": {
                                "default_style": "log_sdev",
                                "styles": [
                                    style_tmad_sdev, style_tmad_edev, style_tmad_bcdev
                                ]
                            }
                        },
                        {
                            "title": "Surface Reflectance Triple Median Absolute Deviation (Landsat 5 Annual Surface Reflectance TMAD)",
                            "abstract": """
        The three layers of the TMAD are calculated by computing the multidimensional distance between each observation in a
        time series of multispectral (or higher dimensionality such as hyperspectral) satellite imagery with the
        multidimensional median of the time series. The median used for this calculation is the geometric median corresponding
        to the time series.  The TMAD is calculated over annual time periods on Earth observations from a single sensor by
        default (such as the annual time series of Landsat 8 observations); however, it is applicable to multi-sensor time
        series of any length that computing resources can support. For the purposes of the default Digital Earth Australia
        product, TMADs are computed per calendar year, per sensor (Landsat 5, Landsat 7 and Landsat 8) from
        terrain-illumination-corrected surface reflectance data (Analysis Ready Data), compared to the annual geometric
        median of that data.
        For more information, see http://pid.geoscience.gov.au/dataset/ga/130482
        For service status information, see https://status.dea.ga.gov.au""",
                            # The WMS name for the layer
                            "name": "ls5_nbart_tmad_annual",
                            # The Datacube name for the associated data product
                            "product_name": "ls5_nbart_tmad_annual",
                            "bands": bands_tmad,
                            "resource_limits": reslim_tmad,
                            "image_processing": {
                                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                                "always_fetch_bands": [ ],
                                "manual_merge": False,
                            },
                            "wcs": {
                                "native_crs": "EPSG:3577",
                                "default_bands": ["sdev", "edev", "bcdev"],
                                "native_resolution": [ 25.0, -25.0 ],
                            },
                            "styling": {
                                "default_style": "log_sdev",
                                "styles": [
                                    style_tmad_sdev, style_tmad_edev, style_tmad_bcdev
                                ]
                            }
                        },
                    ]
                },

            ]
        },
 {
        "title": "ALOS Displacement",
        "abstract": """
            Cumulative displacement time series derived from combination of
             ascending and descending line-of-sight InSAR data from six ALOS data stacks in
             the Sydney Basin area. Original data points were interpolated to 50 m pixel spacing.
             The time series spans the period 2008-02-11 to 2010-10-22, interpolated to 12-day sampling.
             The reference (i.e. zero displacement) for the time series is 2008-04-23.
            """,
        "name": "alos_displacement",
        # The ODC product name for the associated data product
        "product_name": "cemp_insar_alos_displacement",

        "bands": insar_disp_bands,
        "resource_limits": reslim_insar,
        "image_processing": {
            "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
        },
        "styling": {
            "default_style": "insar_disp_ud",
            "styles": [style_insar_disp_ud,
                       style_insar_disp_ew,
                       style_insar_stddev_l_ud,
                       style_insar_stddev_l_ew]
        }
    },
{
                    "title": "Water Observations from Space 25m Wet Count (WOfS April - October Statistics)",
                    "name": "wofs_apr_oct_summary_wet",
                    "abstract": """
Water Observations from Space - April to October Statistics is a set of seasonal statistical summaries of the water observations contained in WOfS. The layers available are: the count of clear observations; the count of wet observations; the percentage of wet observations over time.

This product is Water Observations from Space - April to October Statistics, a set of seasonal statistical summaries of the WOfS product that combines the many years of WOfS observations into summary products that help the understanding of surface water across Australia. As no confidence filtering is applied to this product, it is affected by noise where misclassifications have occurred in the WOfS water classifications, and hence can be difficult to interpret on its own.
The confidence layer and filtered summary are contained in the Water Observations from Space Statistics - Filtered Summary product, which provide a noise-reduced view of the water summary.

This layer contains Water Summary: what percentage of clear observations were detected as wet (ie. the ratio of wet to clear as a percentage). No clear observations of water causes an area to appear transparent, 1-50 total clear observations of water correlate with red and yellow colours, 100 clear observations of water correlate with green, 200 clear observations of water correlates with light blue, 300 clear observations of water correlates to deep blue and 400 and over observations of clear water correlate to purple.

For service status information, see https://status.dea.ga.gov.au
""",
                    "product_name": "wofs_apr_oct_summary",
                    "bands": bands_wofs_sum,
                    "resource_limits": reslim_wofs,
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [ ],
                        "manual_merge": False,
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [25.0, -25.0],
                        "default_bands": ["count_wet"]
                    },
                    "styling": {
                        "default_style": "seasonal_water_observations",
                        "styles": [
                            style_wofs_seasonal_wet,
                        ]
                    }
                },

    ] # End of Layers List
} # End of ows_cfg object
