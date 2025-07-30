# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


from .legends import *

style_c3_pure_aerosol = {
    "name": "aerosol",
    "title": "Narrow Blue - 440",
    "abstract": "Coastal Aerosol or Narrow Blue band, approximately 435nm to 450nm",
    "components": {
        "red": {"nbart_coastal_aerosol": 1.0},
        "green": {"nbart_coastal_aerosol": 1.0},
        "blue": {"nbart_coastal_aerosol": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_c3_pure_panchromatic = {
    "name": "panchromatic",
    "title": "Narrow Blue - 440",
    "abstract": "panchromatic",
    "components": {
        "red": {"nbart_panchromatic": 1.0},
        "green": {"nbart_panchromatic": 1.0},
        "blue": {"nbart_panchromatic": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_c3_simple_rgb = {
    "name": "simple_rgb",
    "title": "Simple RGB",
    "abstract": "Simple true-colour image, using the red, green and blue bands",
    "components": {"red": {"nbart_red": 1.0}, "green": {"nbart_green": 1.0}, "blue": {"nbart_blue": 1.0}},
    "scale_range": [0.0, 3000.0],
    "pq_masks": [
        {
            "band": "oa_fmask",
            "values": [0],
            "invert": True,
        },
    ],
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            "preserve_user_date_order": True,
            # The count range for which this handler is to be used - a tuple of two ints, the smallest and
            # largest date counts for which this handler will be used.  Required.
            "allowed_count_range": [2, 12],
            "animate": True,
            "frame_duration": 1000,
        }
    ],
}

style_c3_fmask = {
    "name": "fmask",
    "title": "FMASK visualisation",
    "abstract": "Visualisation of fmask classification",
    "value_map": {
        "oa_fmask": [
            {
                "color": "#0000FF", # blue
                "title": "Water",
                "values": [5],
            },
            {
                "color": "#9090FF", # pale-blue
                "title": "Snow",
                "values": [4],
            },
            {
                "color": "#400000", # dark red
                "title": "Shadow",
                "values": [3],
            },
            {
                "color": "#E0FFF0", # pale green
                "title": "Cloud",
                "values": [2],
            },
            {
                "color": "#00C000", # bright green
                "title": "Valid",
                "values": [1],
            },
            {
                "color": "#000000",
                "title": "No Data",
                "values": [0],
            },
        ],
    },
    "legend": {
        "title": "FMASK categories",
        "ncols": 2
    }
}

style_c3_false_colour = {
    "name": "false_colour",
    "title": "False Colour",
    "abstract": "Simple false-colour image using ASTER Bands 3 as red, 2 as green and 1 as blue",
    "components": {
        "red": {"nbart_green": 1.0},
        "green": {"nbart_swir_1": 1.0},
        "blue": {"nbart_nir": 1.0},
    },
    "scale_range": [0.0, 255.0],
}

style_c3_nbr = {
    "name": "NBR",
    "title": "Normalised Burn Ratio",
    "abstract": "Normalised Burn Ratio - a derived index that that uses the differences in the way health green vegetation and burned vegetation reflect light to find burned area",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "nbart_nir", "band2": "nbart_swir_2"},
    },
    "needed_bands": ["nbart_nir", "nbart_swir_2"],
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
        {"value": -0.4, "color": "#D6604D"},
        {"value": -0.2, "color": "#F4A582"},
        {"value": -0.1, "color": "#FDDBC7"},
        {
            "value": 0,
            "color": "#F7F7F7",
        },
        {"value": 0.2, "color": "#D1E5F0"},
        {"value": 0.4, "color": "#92C5DE"},
        {"value": 0.6, "color": "#4393C3"},
        {"value": 0.9, "color": "#2166AC"},
        {
            "value": 1.0,
            "color": "#053061",
        },
    ],
    "pq_masks": [
        {
            "band": "oa_fmask",
            "values": [0,2,3],
            "invert": True,
        },
    ],
    "legend": {
        "show_legend": True,
        "begin": "-1.0",
        "end": "1.0",
        "ticks_every": "1.0",
        "decimal_places": 0,
        "tick_labels": {"-1.0": {"prefix": "<"}, "1.0": {"suffix": ">"}},
    },
    # Define behaviour(s) for multi-date requests. If not declared, style only supports single-date requests.
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            "preserve_user_date_order": True,
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
                {"value": -0.5, "color": "#768642", "alpha": 0.0},
                {"value": -0.5, "color": "#768642"},
                {
                    "value": -0.25,
                    "color": "#768642",
                    "alpha": 1.0,
                },
                {"value": -0.25, "color": "#a4bd5f"},
                {"value": -0.1, "color": "#a4bd5f"},
                {"value": -0.1, "color": "#00e05d"},
                {"value": 0.1, "color": "#00e05d"},
                {"value": 0.1, "color": "#fdf950"},
                {"value": 0.27, "color": "#fdf950"},
                {"value": 0.27, "color": "#ffae52"},
                {"value": 0.44, "color": "#ffae52"},
                {"value": 0.44, "color": "#ff662e"},
                {"value": 0.66, "color": "#ff662e"},
                {"value": 0.66, "color": "#ad28cc"},
                {"value": 0.88, "color": "#ad28cc"},
            ],
            "pq_masks": [
                {
                    "band": "oa_fmask",
                    "values": [0,2,3],
                    "invert": True,
                },
            ],
            "legend": {
                "begin": "-0.5",
                "end": "0.88",
                "ticks": [
                    "-0.5",
                    "-0.25",
                    "-0.1",
                    "0.1",
                    "0.27",
                    "0.44",
                    "0.66",
                    "0.88",
                ],
                "tick_labels": {
                    "-0.5": {"label": "<-0.5"},
                    "-0.25": {"label": "-0.25"},
                    "-0.1": {"label": "-0.1"},
                    "0.1": {"label": "0.1"},
                    "0.27": {"label": "0.27"},
                    "0.44": {"label": "0.44"},
                    "0.66": {"label": "0.66"},
                    "0.88": {"label": ">1.30"},
                },
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
            "feature_info_label": "nbr_delta",
        }
    ],
}

style_c3_ndvi = {
    "name": "ndvi",
    "title": "NDVI - Red, NIR",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "nbart_nir", "band2": "nbart_red"},
    },
    "needed_bands": ["nbart_red", "nbart_nir"],
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
    "pq_masks": [
        {
            "band": "oa_fmask",
            "values": [1,4,5],
            "invert": True,
        },
    ],
    "legend": legend_idx_0_1_5ticks,
    # Define behaviour(s) for multi-date requests. If not declared, style only supports single-date requests.
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            "preserve_user_date_order": True,
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
                {"value": -0.5, "color": "#768642", "alpha": 0.0},
                {"value": -0.5, "color": "#768642"},
                {
                    "value": -0.25,
                    "color": "#768642",
                    "alpha": 1.0,
                },
                {"value": -0.25, "color": "#a4bd5f"},
                {"value": -0.1, "color": "#a4bd5f"},
                {"value": -0.1, "color": "#00e05d"},
                {"value": 0.1, "color": "#00e05d"},
                {"value": 0.1, "color": "#fdf950"},
                {"value": 0.27, "color": "#fdf950"},
                {"value": 0.27, "color": "#ffae52"},
                {"value": 0.44, "color": "#ffae52"},
                {"value": 0.44, "color": "#ff662e"},
                {"value": 0.66, "color": "#ff662e"},
                {"value": 0.66, "color": "#ad28cc"},
                {"value": 0.88, "color": "#ad28cc"},
            ],
            "pq_masks": [
                {
                    "band": "oa_fmask",
                    "values": [0, 2, 3],
                    "invert": True,
                },
            ],
            "legend": {
                "begin": "-0.5",
                "end": "0.88",
                "ticks": [
                    "-0.5",
                    "-0.25",
                    "-0.1",
                    "0.1",
                    "0.27",
                    "0.44",
                    "0.66",
                    "0.88",
                ],
                "tick_labels": {
                    "-0.5": {"label": "<-0.5"},
                    "-0.25": {"label": "-0.25"},
                    "-0.1": {"label": "-0.1"},
                    "0.1": {"label": "0.1"},
                    "0.27": {"label": "0.27"},
                    "0.44": {"label": "0.44"},
                    "0.66": {"label": "0.66"},
                    "0.88": {"label": ">1.30"},
                },
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
            "feature_info_label": "nbr_delta",
        }
    ],
}

style_c3_ndvi_animations = {
    "name": "ndvi_anim",
    "title": "NDVI - Red, NIR",
    "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "nbart_nir", "band2": "nbart_red"},
    },
    "needed_bands": ["nbart_red", "nbart_nir"],
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
    "pq_masks": [
          {
            "band": "oa_fmask",
            "values": [0, 1, 2, 3],
            "invert": True,
        },
    ],
    "legend": legend_idx_0_1_5ticks,
    # Define behaviour(s) for multi-date requests. If not declared, style only supports single-date requests.
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            "preserve_user_date_order": True,
            # The count range for which this handler is to be used - a tuple of two ints, the smallest and
            # largest date counts for which this handler will be used.  Required.
            "allowed_count_range": [2, 2],
            "animate": True,
        }
    ],
}

style_c3_ndwi = {
    "name": "ndwi",
    "title": "NDWI - Green, NIR",
    "abstract": "Normalised Difference Water Index - a derived index that correlates well with the existence of water (McFeeters 1996)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "nbart_green", "band2": "nbart_nir"},
    },
    "needed_bands": ["nbart_green", "nbart_nir"],
    "color_ramp": [
        {"value": -0.1, "color": "#f7fbff", "alpha": 0.0},
        {
            "value": 0.0,
            "color": "#d8e7f5",
        },
        {"value": 0.1, "color": "#b0d2e8"},
        {
            "value": 0.2,
            "color": "#73b3d8",
        },
        {"value": 0.3, "color": "#3e8ec4"},
        {
            "value": 0.4,
            "color": "#1563aa",
        },
        {
            "value": 0.5,
            "color": "#08306b",
        },
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

style_c3_mndwi = {
    "name": "mndwi",
    "title": "MNDWI - Green, SWIR",
    "abstract": "Modified Normalised Difference Water Index - a derived index that correlates well with the existence of water (Xu 2006)",
    "index_function": {
        "function": "datacube_ows.band_utils.norm_diff",
        "mapped_bands": True,
        "kwargs": {"band1": "nbart_green", "band2": "nbart_swir_1"},
    },
    "needed_bands": ["nbart_green", "nbart_swir_1"],
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

style_c3_pure_blue = {
    "name": "blue",
    "title": "Blue - 480",
    "abstract": "Blue band, centered on 480nm",
    "components": {"red": {"nbart_blue": 1.0}, "green": {"nbart_blue": 1.0}, "blue": {"nbart_blue": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_c3_pure_green = {
    "name": "green",
    "title": "Green - 560",
    "abstract": "Green band, centered on 560nm",
    "components": {
        "red": {"nbart_green": 1.0},
        "green": {"nbart_green": 1.0},
        "blue": {"nbart_green": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_c3_pure_red = {
    "name": "red",
    "title": "Red - 660",
    "abstract": "Red band, centered on 660nm",
    "components": {"red": {"nbart_red": 1.0}, "green": {"nbart_red": 1.0}, "blue": {"nbart_red": 1.0}},
    "scale_range": [0.0, 3000.0],
}


style_c3_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 840",
    "abstract": "Near infra-red band, centered on 840nm",
    "components": {"red": {"nbart_nir": 1.0}, "green": {"nbart_nir": 1.0}, "blue": {"nbart_nir": 1.0}},
    "scale_range": [0.0, 3000.0],
}

style_s2_cloudless_prob = {
    "name": "s2cloudless_prob",
    "title": "S2 Cloudless Mask Probability",
    "abstract": "S2 Cloudless Probabilities given for s2cloudless_mask classification",
    "include_in_feature_info": False,
    "needed_bands": ["s2cloudless_prob"],
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {"band": "s2cloudless_prob"},
    },
    "mpl_ramp": "inferno",
    "range": [0.0, 1.0]
}


style_c3_pure_swir1 = {
    "name": "swir1",
    "title": "Shortwave Infrared (SWIR) - 1650",
    "abstract": "Short wave infra-red band 1, centered on 1650nm",
    "components": {
        "red": {"nbart_swir_1": 1.0},
        "green": {"nbart_swir_1": 1.0},
        "blue": {"nbart_swir_1": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

style_c3_pure_swir2 = {
    "name": "swir2",
    "title": "Shortwave Infrared (SWIR) - 2220",
    "abstract": "Short wave infra-red band 2, centered on 2220nm",
    "components": {
        "red": {"nbart_swir_2": 1.0},
        "green": {"nbart_swir_2": 1.0},
        "blue": {"nbart_swir_2": 1.0},
    },
    "scale_range": [0.0, 3000.0],
}

styles_c3_ls_common = [
    style_c3_simple_rgb,
    style_c3_false_colour,
    style_c3_ndvi,
    style_c3_ndvi_animations,
    style_c3_ndwi,
    style_c3_mndwi,
    style_c3_pure_blue,
    style_c3_pure_green,
    style_c3_pure_red,
    style_c3_pure_nir,
    style_c3_pure_swir1,
    style_c3_pure_swir2,
    style_c3_nbr,
    style_c3_fmask,
]


styles_c3_ls_7 = styles_c3_ls_common.copy()
styles_c3_ls_7.append(style_c3_pure_panchromatic)

styles_c3_ls_8 = styles_c3_ls_7.copy()
styles_c3_ls_8.append(style_c3_pure_aerosol)


style_c3_wofs_obs = {
    "name": "observations",
    "title": "Observations",
    "abstract": "Observations",
    "value_map": {
        "water": [
            {
                "title": "",
                "abstract": "",
                "flags": {
                    "and": {
                        "noncontiguous": True,
                        "low_solar_angle": True
                    }
                },
                "alpha": 0.0,
                "color": "#707070",
            },
            {
                "title": "Cloudy Steep Terrain",
                "abstract": "",
                "flags": {
                    "and": {
                        "cloud": True,
                        "high_slope": True
                    }
                },
                "color": "#f2dcb4",
            },
            {
                "title": "Cloudy Water",
                "abstract": "",
                "flags": {
                    "and": {
                        "wet": True,
                        "cloud": True
                    }
                },
                "color": "#bad4f2",
            },
            {
                "title": "Shaded Water",
                "abstract": "",
                "flags": {
                    "and": {
                        "wet": True,
                        "cloud_shadow": True
                    }
                },
                "color": "#335277",
            },
            {
                "title": "Cloud",
                "abstract": "",
                "flags": {"cloud": True},
                "color": "#c2c1c0",
            },
            {
                "title": "Cloud Shadow",
                "abstract": "",
                "flags": {"cloud_shadow": True},
                "color": "#4b4b37",
            },
            {
                "title": "Terrain Shadow",
                "abstract": "",
                "flags": {"terrain_shadow": True},
                "color": "#2f2922",
            },
            {
                "title": "Steep Terrain",
                "abstract": "",
                "flags": {"high_slope": True},
                "color": "#776857",
            },
            {
                "title": "Water",
                "abstract": "",
                "flags": {"wet": True},
                "color": "#4F81BD",
            },
            {
                "title": "Dry",
                "abstract": "",
                "flags": {
                    "dry": True,
                },
                "color": "#96966e",
            },
        ],
    },
    "pq_masks": [
        {
            "band": "land",
            "invert": True,
            "values": [0],
        }
    ],
    "legend": {"width": 3.0, "height": 2.1},
}

style_s2_wofs_obs_wet_only = {
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
                        "terrain_shadow": True,
                        "low_solar_angle": True,
                        "cloud_shadow": True,
                        "cloud": True,
                        "high_slope": True,
                        "noncontiguous": True,
                    }
                },
                "color": "#707070",
                "alpha": 0.0,
            },
            {
                # Possible Sea Glint, also mark as invalid
                "title": "Dry",
                "abstract": "Dry",
                "flags": {
                    "dry": True,
                },
                "color": "#D99694",
                "alpha": 0.0,
            },
            {
                "title": "Wet",
                "abstract": "Wet",
                "flags": {"wet": True},
                "color": "#4F81BD",
            },
        ],
    },
    "pq_masks": [
        {
            "band": "land",
            "invert": True,
            "values": [1],
        },
    ],
}


