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
        "min_zoom_factor": 15.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
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

bands_ls = {
    "red": ['pink'],
    "green": [],
    "blue": ['azure' ],
    "nir": [ "near_infrared" ],
    "swir1": [ "shortwave_infrared_1", "near_shortwave_infrared" ],
    "swir2": [ "shortwave_infrared_2", "far_shortwave_infrared" ],
}

# Reusable Chunks 3. Styles

style_ls_simple_rgb = {
        "name": "simple_rgb",
        "title": "Simple RGB",
        "abstract": "Simple true-colour image, using the red, green and blue bands",
        "components": {
            "red": {
                "pink": 1.0
            },
            "green": {
                "green": 1.0
            },
            "blue": {
                "azure": 1.0
            }
        },
        "scale_range": [0.0, 3000.0]
}


style_ls_simple_rg = {
    "inherits": {
        "layer": "ls8_nbart_geomedian_annual",
        "style": "simple_rgb",
    },
    "name": "simple_rg",
        "title": "Simple RG",
        "abstract": "Simple red-green image, using the red, green and blue bands",
        "components": {
            "green": {
                "green": 0.6,
                "blue": 0.4
            },
            "blue": {
            }
        },
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
style_ls_irr = {
    "inherits": style_ls_irg,
    "name": "infrared_red",
    "title": "False colour - Red, SWIR, NIR",
    "abstract": "False Colour image with SWIR1->Red, NIR->Green, and Red->Blue",
    "components": {
        "red": {
            "swir1": 1.0
        },
        "green": {
            "nir": 1.0
        },
        "blue": {
            "red": 1.0
        }
    },
}

style_ls_rgbndvi = {
    "name": "rgb_ndvi",
    "title": "NDVI plus RGB",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "component_ratio": 0.6,
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
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
        "mapped_bands": True,
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
    },
    # Define behaviour(s) for multi-date requests. If not declared, style only supports single-date requests.
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            # The count range for which this handler is to be used - a tuple of two ints, the smallest and
            # largest date counts for which this handler will be used.  Required.
            "allowed_count_range": [2, 8],
            # A function, expressed in the standard format as described elsewhere in this example file.
            # The function is assumed to take one arguments, an xarray Dataset.
            # The function returns an xarray Dataset with a single band, which is the input to the
            # colour ramp defined below.
            "animate": True,
            "aggregator_function": {
                "function": "datacube_ows.band_utils.multi_date_pass"
            },
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

style_ls_ndvi_expr = {
"name": "ndvi_expr",
"title": "NDVI - Red, NIR",
"abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
"index_expression": "(nir-red)/(nir+red)",
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


style_ls8_nbr = {
    "name": "NBR",
    "title": "Normalised Burn Ratio",
    "abstract": "Normalised Burn Ratio - a derived index that that uses the differences in the way health green vegetation and burned vegetation reflect light to find burned area",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
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
        "end": "1.0",
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
        "mapped_bands": True,
        "kwargs": {
            "band1": "near_infrared",
            "band2": "steve"
        }
    },
    "band_map": {
        "steve": "red"
    },
    "needed_bands": ["red", "near_infrared"],
    "range": [0.0, 1.0],
    "mpl_ramp": "RdBu"
}

style_ls_ndvi_delta = {
    "name": "ndvi-delta",
    "title": "NDVI - Red, NIR (delta)",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
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
        "mapped_bands": True,
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
        "mapped_bands": True,
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
        "mapped_bands": True,
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
        "mapped_bands": True,
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


layer_geomedian_ls8 = {
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
                    },
                    "user_band_math": True,
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
                            style_ls_irr,
                            style_ls_rgbndvi,
                            style_ls_ndvi,
                            style_ls_ndvi_expr,
                            style_ls8_nbr,
                            style_ls_ndvi_alt1, style_ls_ndvi_alt2, style_ls_ndvi_alt3, 
                            style_ls_ndvi_delta,
                            style_ls_ndwi, style_ls_mndwi,
                            style_ls_pure_blue, style_ls_pure_green, style_ls_pure_red,
                            style_sentinel_pure_nir, style_sentinel_pure_swir1, style_ls_pure_swir2,
                        ]
                    }
                }
layer_geomedian_ls8_ltd = {
                    "inherits": {"layer": "ls8_nbart_geomedian_annual"},
                    "title": "Surface Reflectance 25m Annual Geomedian (Landsat 8) (limit to Barest Earth)",
                    "name": "ls8_nbart_geomedian_annual_limited",
                    "low_res_product_name": "ls8_fc_albers",
                    "resource_limits": {
                        "wms": {
                            "min_zoom_factor": 1800.0,
                        },
                    }
                }

layer_geomedian_ls7 = {
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
                            style_ls_irg, style_ls_irr, style_ls_ndvi, style_ls_ndvi_expr, style_ls_ndwi, style_ls_mndwi,
                            style_ls_ndvi_alt1, style_ls_ndvi_alt2, style_ls_ndvi_alt3, 
                            style_ls_ndvi_delta,
                            style_sentinel_pure_blue, style_ls_pure_green, style_ls_pure_red,
                            style_ls_pure_nir, style_ls_pure_swir1, style_ls_pure_swir2,
                        ]
                    }
                }

layer_geomedian_ls5 = {
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
                            style_ls_irg, style_ls_irr, style_ls_ndvi, style_ls_ndwi, style_ls_mndwi,
                            style_ls_ndvi_alt1, style_ls_ndvi_alt2, style_ls_ndvi_alt3, 
                            style_sentinel_pure_blue, style_ls_pure_green, style_ls_pure_red,
                            style_ls_pure_nir, style_ls_pure_swir1, style_ls_pure_swir2,
                        ]
                    }
                }
layer_barest_earth = {
            "title": "Landsat-8 Barest Earth",
            "abstract": """
A `weighted geometric median’ approach has been used to estimate the median surface reflectance of the barest state (i.e., least vegetation) observed through Landsat-8 OLI observations from 2013 to September 2018 to generate a six-band Landsat-8 Barest Earth pixel composite mosaic over the Australian continent.

The bands include BLUE (0.452 - 0.512), GREEN (0.533 - 0.590), RED, (0.636 - 0.673) NIR (0.851 - 0.879), SWIR1 (1.566 - 1.651) and SWIR2 (2.107 - 2.294) wavelength regions. The weighted median approach is robust to outliers (such as cloud, shadows, saturation, corrupted pixels) and also maintains the relationship between all the spectral wavelengths in the spectra observed through time. The product reduces the influence of vegetation and allows for more direct mapping of soil and rock mineralogy.

Reference: Dale Roberts, John Wilford, and Omar Ghattas (2018). Revealing the Australian Continent at its Barest, submitted.

Mosaics are available for the following years:
    Landsat 8: 2013 to 2017;
            """,
            "layers": [
                {
                    "title": "Landsat-8 Barest Earth 25m albers (Landsat-8)",
                    "name": "ls8_barest_earth_mosaic",
                    "abstract": """
A `weighted geometric median’ approach has been used to estimate the median surface reflectance of the barest state (i.e., least vegetation) observed through Landsat-8 OLI observations from 2013 to September 2018 to generate a six-band Landsat-8 Barest Earth pixel composite mosaic over the Australian continent.

The bands include BLUE (0.452 - 0.512), GREEN (0.533 - 0.590), RED, (0.636 - 0.673) NIR (0.851 - 0.879), SWIR1 (1.566 - 1.651) and SWIR2 (2.107 - 2.294) wavelength regions. The weighted median approach is robust to outliers (such as cloud, shadows, saturation, corrupted pixels) and also maintains the relationship between all the spectral wavelengths in the spectra observed through time. The product reduces the influence of vegetation and allows for more direct mapping of soil and rock mineralogy.

Reference: Dale Roberts, John Wilford, and Omar Ghattas (2018). Revealing the Australian Continent at its Barest, submitted.

Mosaics are available for the following years:
    Landsat 8: 2013 to 2017;

For service status information, see https://status.dea.ga.gov.au
                    """,
                    "product_name": "ls8_barest_earth_albers",
                    "bands": bands_ls,
                    "resource_limits": reslim_landsat,
                    "time_resolution": "year",
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                    },
                    "wcs": {
                        "native_crs": "EPSG:3577",
                        "native_resolution": [25, -25],
                        "default_bands": ["red", "green", "blue"]
                    },
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [
                            style_ls_simple_rgb,
                            style_ls_irg, style_ls_irr, style_ls_ndvi,
                            style_ls_pure_blue, style_ls_pure_green, style_ls_pure_red,
                            style_sentinel_pure_nir, style_sentinel_pure_swir1, style_ls_pure_swir2,
                        ]
                    }

                }
            ]
        }

layer_folder_sr = {
            "title": "Surface Reflectance",
            "abstract": "",
            "layers": [
                layer_geomedian_ls8,
                layer_geomedian_ls8_ltd,
                layer_geomedian_ls7,
                layer_geomedian_ls5,
                layer_barest_earth,
            ]
        }
