

ls_range = [1000.0, 4000.0]
s2_range = [0.0, 3000.0]


dataset_cache_rules = [
    {
        "min_datasets": 1,
        "max_age": 60 * 60 * 8,
    },
    {
        "min_datasets": 5,
        "max_age": 60 * 60 * 24,
    },
    {
        "min_datasets": 9,
        "max_age": 60 * 60 * 24 * 7,
    },
    {
        "min_datasets": 17,
        "max_age": 60 * 60 * 24 * 30,
    },
    {
        "min_datasets": 65,
        "max_age": 60 * 60 * 24 * 120,
    },
]

reslim_continental = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 10.0,
        "dataset_cache_rules": dataset_cache_rules,
    },
    "wcs": {
        "max_datasets": 32,  # Defaults to no dataset limit
    },
}

reslim_wofs = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 0.0,
        # "max_datasets": 16, # Defaults to no dataset limit
        "dataset_cache_rules": dataset_cache_rules,
    },
    "wcs": {
        "max_datasets": 32,  # Defaults to no dataset limit
    },
}


bands_wofs_summary = {
    "count_wet": [],
    "count_clear": [],
    "frequency": [],
    "frequency_masked": [],
}

bands_s2_geomad = {
    # "B01": ["coastal_aerosol"],
    "B02": ["blue"],
    "B03": ["green"],
    "B04": ["red"],
    "B05": ["red_edge_1"],
    "B06": ["red_edge_2"],
    "B07": ["red_edge_3"],
    "B08": ["nir", "nir_1"],
    "B8A": ["nir_narrow", "nir_2"],
    # "B09": ["water_vapour"],
    "B11": ["swir_1", "swir_16"],
    "B12": ["swir_2", "swir_22"],
    "smad": ["sdev"],
    "emad": ["edev"],
    "bcmad": ["bcdev"],
    "count": [],
}
legend_idx_percentage_by_10 = {
    "begin": "0.0",
    "end": "1.0",
    "ticks_every": "0.1",
    "units": "%",
    "tick_labels": {
        "0.0": {"label": "0"},
        "0.1": {"label": "10"},
        "0.2": {"label": "20"},
        "0.3": {"label": "30"},
        "0.4": {"label": "40"},
        "0.5": {"label": "50"},
        "0.6": {"label": "60"},
        "0.7": {"label": "70"},
        "0.8": {"label": "80"},
        "0.9": {"label": "90"},
        "1.0": {"label": "100"},
    },
}

legend_idx_0_1_5ticks = {
    "begin": "0.0",
    "end": "1.0",
    "ticks_every": "0.2",
    "units": "unitless",
}

style_wofs_summary_annual_frequency_masked = {
    "name": "wofs_summary_annual_frequency_masked",
    "title": "Water frequency",
    "abstract": "WOfS summary showing the frequency of water",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "frequency_masked",
        },
    },
    "needed_bands": ["frequency_masked"],
    "include_in_feature_info": False,
    "color_ramp": [
        {"value": 0.0, "color": "#FFFFFF", "alpha": 0.0},
        {"value": 0.02, "color": "#FFFFFF", "alpha": 0.0},
        {"value": 0.05, "color": "#aee3c0", "alpha": 0.25},
        {"value": 0.1, "color": "#6dd3ad", "alpha": 0.75},
        {"value": 0.2, "color": "#44bcad"},
        {"value": 0.3, "color": "#35a1ab"},
        {"value": 0.4, "color": "#3487a6"},
        {"value": 0.5, "color": "#366da0"},
        {"value": 0.6, "color": "#3d5296"},
        {"value": 0.7, "color": "#403974"},
        {"value": 0.8, "color": "#35264c"},
        {"value": 0.9, "color": "#231526"},
    ],
    "legend": legend_idx_percentage_by_10,
}

style_wofs_summary_annual_frequency = {
    "name": "wofs_summary_annual_frequency",
    "title": " Water frequency",
    "abstract": "WOfS summary showing the frequency of water",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "frequency",
        },
    },
    "needed_bands": ["frequency"],
    "include_in_feature_info": False,
    "color_ramp": [
        {"value": 0.0, "color": "#FFFFFF", "alpha": 0.0},
        {"value": 0.02, "color": "#FFFFFF", "alpha": 0.0},
        {"value": 0.05, "color": "#aee3c0", "alpha": 0.25},
        {"value": 0.1, "color": "#6dd3ad", "alpha": 0.75},
        {"value": 0.2, "color": "#44bcad"},
        {"value": 0.3, "color": "#35a1ab"},
        {"value": 0.4, "color": "#3487a6"},
        {"value": 0.5, "color": "#366da0"},
        {"value": 0.6, "color": "#3d5296"},
        {"value": 0.7, "color": "#403974"},
        {"value": 0.8, "color": "#35264c"},
        {"value": 0.9, "color": "#231526"},
    ],
    "legend": legend_idx_percentage_by_10,
}

style_wofs_summary_annual_clear = {
    "name": "wofs_summary_annual_clear",
    "title": "Count of clear observations",
    "abstract": "WOfS annual summary showing the count of clear observations",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "count_clear",
        },
    },
    "needed_bands": ["count_clear"],
    "include_in_feature_info": False,
    "color_ramp": [
        {"value": 0, "color": "#FFFFFF", "alpha": 0},
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 0,
            "color": "#FFFFFF",
            "alpha": 1,
        },
        {"value": 3, "color": "#f2fabc"},
        {"value": 6, "color": "#dcf1b2"},
        {"value": 10, "color": "#bbe4b5"},
        {"value": 12, "color": "#85cfba"},
        {"value": 15, "color": "#57bec1"},
        {"value": 18, "color": "#34a9c3"},
        {"value": 20, "color": "#1d8dbe"},
        {"value": 24, "color": "#2166ac"},
        {"value": 27, "color": "#24479d"},
        {"value": 30, "color": "#1d2e83"},
    ],
    "legend": {
        "begin": "0",
        "end": "30",
        "decimal_places": 0,
        "ticks_every": 10,
        "tick_labels": {
            "30": {"prefix": ">"},
        },
    },
}

style_wofs_summary_annual_wet = {
    "name": "wofs_summary_annual_wet",
    "title": "Count of wet observations",
    "abstract": "WOfS summary showing the count of water observations",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "count_wet",
        },
    },
    "needed_bands": ["count_wet"],
    "include_in_feature_info": False,
    "color_ramp": [
        {"value": 0, "color": "#FFFFFF", "alpha": 0},
        {
            # purely for legend display
            # we should not get fractional
            # values in this styles
            "value": 0.2,
            "color": "#FFFFFF",
            "alpha": 1,
        },
        {"value": 2, "color": "#f1ebf5"},
        {"value": 4, "color": "#e0dded"},
        {"value": 6, "color": "#c9cee4"},
        {"value": 8, "color": "#a9bfdc"},
        {"value": 10, "color": "#86b0d3"},
        {"value": 12, "color": "#5ea0ca"},
        {"value": 14, "color": "#328dbf"},
        {"value": 16, "color": "#0d75b3"},
        {"value": 18, "color": "#04649d"},
        {"value": 20, "color": "#03517e"},
    ],
    "legend": {
        "begin": 0,
        "end": 20,
        "decimal_places": 0,
        "ticks_every": 10,
        "tick_labels": {
            "20": {"prefix": ">"},
        },
    },
}


style_lsc2_sr_simple_rgb = {
    "name": "simple_rgb",
    "title": "True colour - RGB",
    "abstract": "True-colour image, using the red, green and blue bands",
    "components": {"red": {"red": 1.0}, "green": {"green": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": [7272.0, 18181.0],
}

style_lsc2_sr_irg = {
    "name": "infrared_green",
    "title": "False colour - SWIR, NIR, Green",
    "abstract": "False colour image with SWIR1->Red, NIR->Green, and Green->Blue",
    "components": {
        "red": {"swir_1": 1.0},
        "green": {"nir": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

# Loose range from min to max
sdev_scaling = [0.00, 0.10]
bdev_scaling = [0.01, 0.10]
edev_scaling = [250.0, 2000]

# Percentiles at 0.05 and 0.95
sdev_scaling_2 = [0.0, 0.05]
bdev_scaling_2 = [0.02257398, 0.07464499]
edev_scaling_2 = [533.782714, 1695.34313]

style_tmad_sdev_std = {
    "name": "arcsec_sdev",
    "title": "Spectral MAD (SMAD)",
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
            "0.0": {"label": "Low\nSMAD"},
            "4.0": {"label": "High\nSMAD"},
        },
    },
}

style_tmad_edev_std = {
    "name": "log_edev",
    "title": "Euclidean MAD (EMAD)",
    "abstract": "Good for cropland and forest",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
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
            "0.0": {"label": "Low\nEMAD"},
            "4.0": {"label": "High\nEMAD"},
        },
    },
}


style_tmad_bcdev_std = {
    "name": "log_bcdev",
    "title": "Bray-Curtis MAD (BCMAD)",
    "abstract": "Good for cropland and forest",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band_offset_log",
        "mapped_bands": True,
        "kwargs": {
            "band": "bcdev",
            "scale_from": bdev_scaling,
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
            "0.0": {"label": "Low\nBCMAD"},
            "4.0": {"label": "High\nBCMAD"},
        },
    },
}

style_tmad_rgb_std = {
    "name": "tmad_rgb_std",
    "title": "MADs - SMAD, EMAD, BCMAD",
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
            "function": "datacube_ows.band_utils.single_band",
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
                "scale_from": bdev_scaling,
            },
        },
    },
    "additional_bands": ["sdev", "bcdev", "edev"],
}

style_tmad_rgb_sens = {
    "inherits": style_tmad_rgb_std,
    "name": "tmad_rgb_sens",
    "title": "MADs (alt.) - SMAD, EMAD, BCMAD",
    "abstract": "Good for arid land and desert",
    "components": {
        "red": {
            "kwargs": {
                "scale_from": sdev_scaling_2,
            }
        },
        "green": {
            "kwargs": {
                "scale_from": edev_scaling_2,
            }
        },
        "blue": {
            "kwargs": {
                "scale_from": bdev_scaling_2,
            }
        },
    },
}

style_ndvi = {
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
    "multi_date": [
        {
            "allowed_count_range": [2, 2],
            "animate": False,
            "preserve_user_date_order": True,
            "aggregator_function": {
                "function": "datacube_ows.band_utils.multi_date_delta",
            },
            "mpl_ramp": "RdYlBu",
            "range": [-1.0, 1.0],
            "legend": {
                "begin": "-1.0",
                "end": "1.0",
                "ticks": [
                    "-1.0",
                    "0.0",
                    "1.0",
                ],
            },
            "feature_info_label": "ndvi_delta",
        },
        {"allowed_count_range": [3, 4], "animate": True},
    ],
}

style_ndwi = {
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
        {"value": 0.0, "color": "#d8e7f5"},
        {"value": 0.1, "color": "#b0d2e8"},
        {"value": 0.2, "color": "#73b3d8"},
        {"value": 0.3, "color": "#3e8ec4"},
        {"value": 0.4, "color": "#1563aa"},
        {"value": 0.5, "color": "#08306b"},
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
    "multi_date": [
        {
            "allowed_count_range": [2, 2],
            "animate": False,
            "preserve_user_date_order": True,
            "aggregator_function": {
                "function": "datacube_ows.band_utils.multi_date_delta",
            },
            "mpl_ramp": "RdYlBu",
            "range": [-1.0, 1.0],
            "legend": {
                "begin": "-1.0",
                "end": "1.0",
                "ticks": [
                    "-1.0",
                    "0.0",
                    "1.0",
                ],
            },
            "feature_info_label": "ndwi_delta",
        },
        {"allowed_count_range": [3, 4], "animate": True},
    ],
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



style_lsc2_sr_pure_blue = {
    "name": "blue",
    "title": "Blue",
    "abstract": "Blue band",
    "components": {"red": {"blue": 1.0}, "green": {"blue": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": [7272.0, 18181.0],
}

style_lsc2_sr_pure_green = {
    "name": "green",
    "title": "Green",
    "abstract": "Green band",
    "components": {
        "red": {"green": 1.0},
        "green": {"green": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

style_lsc2_sr_pure_red = {
    "name": "red",
    "title": "Red",
    "abstract": "Red band",
    "components": {
        "red": {"red": 1.0},
        "green": {"red": 1.0},
        "blue": {"red": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

style_s2_pure_red = {
    "name": "red",
    "title": "Red",
    "abstract": "Red band",
    "components": {
        "red": {"red": 1.0},
        "green": {"red": 1.0},
        "blue": {"red": 1.0},
    },
    "scale_range": s2_range,
}

style_lsc2_sr_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR)",
    "abstract": "Near infra-red band",
    "components": {"red": {"nir": 1.0}, "green": {"nir": 1.0}, "blue": {"nir": 1.0}},
    "scale_range": [7272.0, 18181.0],
}

style_lsc2_sr_swir_1 = {
    "name": "swir_1",
    "title": "Shortwave Infrared 1 (SWIR1)",
    "abstract": "Shortwave infrared band 1",
    "components": {
        "red": {"swir_1": 1.0},
        "green": {"swir_1": 1.0},
        "blue": {"swir_1": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

style_lsc2_sr_swir_2 = {
    "name": "swir_2",
    "title": "Shortwave Infrared 2 (SWIR2)",
    "abstract": "Shortwave infrared band 2",
    "components": {
        "red": {"swir_2": 1.0},
        "green": {"swir_2": 1.0},
        "blue": {"swir_2": 1.0},
    },
    "scale_range": [7272.0, 18181.0],
}

style_gm_ls_count = {
    "name": "count",
    "title": "Clear observation count",
    "abstract": "Count of observations included in Geomedian/MAD calculations",
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
        # set transparency for no data (0 counts)
        {"value": 0, "color": "#666666", "alpha": 0},
        {
            # purely for legend display
            # simulates transparency at 0
            # we should not get fractional
            # values in this styles
            "value": 0.2,
            "color": "#FFFFFF",
            "alpha": 1,
        },
        {"value": 5, "color": "#edf8b1"},
        {"value": 10, "color": "#c6e9b4"},
        {"value": 15, "color": "#7ecdbb"},
        {"value": 20, "color": "#40b5c4"},
        {"value": 25, "color": "#1d90c0"},
        {"value": 30, "color": "#225da8"},
        {"value": 35, "color": "#243392"},
        {"value": 40, "color": "#081d58"},
    ],
    "legend": {
        "begin": "0",
        "end": "40",
        "decimal_places": 0,
        "ticks_every": 5,
        "tick_labels": {
            "40": {"suffix": "<"},
        },
    },
}


style_gm_simple_s2_rgb = {
    "name": "simple_rgb",
    "title": "Geomedian - Red, Green, Blue",
    "abstract": "Simple true-colour image, using the red, green and blue bands",
    "components": {"red": {"red": 1.0}, "green": {"green": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": s2_range,
    "multi_date": [{"allowed_count_range": [2, 4], "animate": True}],
}


style_gm_s2_count = {
    "name": "count",
    "title": "Clear observation count",
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
            "color": "#FFFFFF",
            "alpha": 1,
        },
        {"value": 10, "color": "#f3fabf"},
        {"value": 20, "color": "#e1f3b2"},
        {"value": 30, "color": "#c6e9b4"},
        {"value": 40, "color": "#97d6b9"},
        {"value": 50, "color": "#6bc6be"},
        {"value": 60, "color": "#42b6c4"},
        {"value": 70, "color": "#299dc1"},
        {"value": 80, "color": "#1f80b8"},
        {"value": 90, "color": "#225da8"},
        {"value": 100, "color": "#24419a"},
        {"value": 110, "color": "#1b2c80"},
        {"value": 120, "color": "#081d58"},
    ],
    "legend": {
        "begin": "0",
        "end": "120",
        "decimal_places": 0,
        "ticks_every": 20,
        "tick_labels": {
            "120": {"suffix": "<"},
        },
    },
}


style_gm_s2_irg = {
    "name": "infrared_green",
    "title": "Geomedian - SWIR, NIR, Green",
    "abstract": "False Colour image with SWIR1->Red, NIR->Green, and Green->Blue",
    "components": {
        "red": {"swir_1": 1.0},
        "green": {"nir": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": s2_range,
}

style_s2_pure_blue = {
    "name": "blue",
    "title": "Blue - 490",
    "abstract": "Blue band, centered on 490nm",
    "components": {"red": {"blue": 1.0}, "green": {"blue": 1.0}, "blue": {"blue": 1.0}},
    "scale_range": s2_range,
}

style_s2_pure_green = {
    "name": "green",
    "title": "Green - 560",
    "abstract": "Green band, centered on 560nm",
    "components": {
        "red": {"green": 1.0},
        "green": {"green": 1.0},
        "blue": {"green": 1.0},
    },
    "scale_range": s2_range,
}

style_s2_pure_nir = {
    "name": "nir",
    "title": "Near Infrared (NIR) - 870",
    "abstract": "Near infra-red band, centered on 870nm",
    "components": {"red": {"nir": 1.0}, "green": {"nir": 1.0}, "blue": {"nir": 1.0}},
    "scale_range": s2_range,
}

style_s2_pure_swir1 = {
    "name": "swir_1",
    "title": "Shortwave Infrared (SWIR) - 1610",
    "abstract": "Short wave infra-red band 1, centered on 1610nm",
    "components": {"red": {"B11": 1.0}, "green": {"B11": 1.0}, "blue": {"B11": 1.0}},
    "scale_range": s2_range,
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
    "scale_range": s2_range,
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
        "ticks": ["-0.1", "0.0", "0.2", "0.5"],
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
    "scale_range": s2_range,
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
    "scale_range": s2_range,
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
    "scale_range": s2_range,
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
    "scale_range": s2_range,
}

style_s2_pure_narrow_nir = {
    "name": "narrow_nir",
    "title": "Narrow Near Infrared - 870",
    "abstract": "Near infra-red band, centred on 865nm",
    "components": {"red": {"nir": 1.0}, "green": {"nir": 1.0}, "blue": {"nir": 1.0}},
    "scale_range": s2_range,
}

style_s2_mndwi = {
    "name": "mndwi",
    "title": "MNDWI - Green, SWIR",
    "abstract": "Modified Normalised Difference Water Index - a derived index that correlates "
    "well with the existence of water (Xu 2006)",
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

styles_s2_geomad = [
    style_gm_simple_s2_rgb,
    style_gm_s2_irg,
    style_tmad_rgb_std,
    style_tmad_rgb_sens,
    style_ndvi,
    style_ndwi,
    style_s2_mndwi,
    style_s2_ndci,
    style_s2_pure_blue,
    style_s2_pure_green,
    style_s2_pure_red,
    style_s2_pure_redge_1,
    style_s2_pure_redge_2,
    style_s2_pure_redge_3,
    style_s2_pure_nir,
    style_s2_pure_narrow_nir,
    style_s2_pure_swir1,
    style_s2_pure_swir2,
    style_tmad_sdev_std,
    style_tmad_edev_std,
    style_tmad_bcdev_std,
    style_gm_s2_count,
]


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
            "EPSG:3577": {  # GDA-94, Australian Albers. Not sure why, but it's required!
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:4326": {"geographic": True, "vertical_coord_first": True},  # WGS-84
            "EPSG:3832": {  # Some Pacific projection
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
        },
        "allowed_urls": [
            "http://localhost:8000",
            "https://ows.staging.digitalearthpacific.io",
            "https://ows-uncached.staging.digitalearthpacific.io",
            "https://ows.prod.digitalearthpacific.io",
            "https://ows-uncached.prod.digitalearthpacific.io",
            "https://ows.digitalearthpacific.org",
        ],
        # Metadata to go straight into GetCapabilities documents
        "title": "Digital Earth Pacific Web Services",
        "abstract": """TODO...""",
        "info_url": "",
        "keywords": ["Digital Earth Pacific"],
        "contact_info": {
            "person": "TODO",
            "organisation": "Digital Earth Pacific",
            "position": "",
            "address": {
                "type": "postal",
                "address": "TODO",
                "city": "TODO",
                "state": "TODO",
                "postcode": "TODO",
                "country": "New Caledonia",
            },
            "telephone": "TODO",
            "fax": "",
            "email": "TODO",
        },
        "fees": "",
        "access_constraints": "TODO",
    },  # END OF global SECTION
    "wms": {
        # Config for WMS service, for all products/layers
        # "s3_aws_zone": "us-west-2",
        "max_width": 512,
        "max_height": 512,
        # Allow the WMS/WMTS GetCapabilities responses to be cached for 1 hour
        "caps_cache_maxage": 60 * 60,
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
        {
            "title": "Digital Earth Pacific OWS",
            "abstract": "TODO",
            "layers": [
                # Hierarchical list of layers
                {
                    "title": "Surface water",
                    "abstract": """Surface water""",
                    "layers": [
                        {
                            "title": "Annual surface water",
                            "abstract": """Annual surface water""",
                            "layers": [
                                {
                                    "title": "Water Observations from Space annual summary",
                                    "name": "wofs_ls_summary_annual",
                                    "abstract": """
Annual water summary is one of the statistical summaries of the Water Observation from Space (WOfS) product that shows what percentage of clear observations were detected as wet (ie. the ration of wet to clear as a percentage) from each calendar year.

This product has a spatial resolution of 30 m and a temporal coverage of 1980s to last calender year.

It is derived from Landsat Collection 2 surface reflectance product.

The annual summaries can be used to understand year to year changes in surface water extent.

WOfS shows surface water on the day and time that satellite passed overhead, which might be before, during or after a flood peak. Given the time between satellite passes (approximately once every 16 days) it is unlikely that the satellite will capture the maximum extent of any given flood. Instead, it aims to provide large scale, regional information on surface water.

For more information on the algorithm, see https://doi.org/10.1016/j.rse.2015.11.003
""",
                                    "product_name": "dep_ls_wofs_summary_annual",
                                    "time_resolution": "summary",
                                    "bands": bands_wofs_summary,
                                    "resource_limits": reslim_wofs,
                                    "image_processing": {
                                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                                        "always_fetch_bands": [],
                                        "manual_merge": False,
                                    },
                                    "native_crs": "EPSG:3832",
                                    "native_resolution": [30.0, -30.0],
                                    "styling": {
                                        "default_style": "wofs_summary_annual_frequency",
                                        "styles": [
                                            style_wofs_summary_annual_frequency_masked,
                                            style_wofs_summary_annual_frequency,
                                            style_wofs_summary_annual_wet,
                                            style_wofs_summary_annual_clear,
                                        ],
                                    },
                                },
                                {
                                    "title": "Annual GeoMAD (Sentinel-2)",
                                    "name": "dep_s2_geomad",
                                    "abstract": """
                                TODO
                                """,
                                    "product_name": "dep_s2_geomad",
                                    "bands": bands_s2_geomad,
                                    "dynamic": False,
                                    "resource_limits": reslim_continental,
                                    "time_resolution": "summary",
                                    "image_processing": {
                                        "extent_mask_func": "config.dep_utils.mask_by_emad_nan",
                                        "always_fetch_bands": ["emad"],
                                        "manual_merge": False,
                                        "apply_solar_corrections": False,
                                    },
                                    "native_crs": "EPSG:3832",
                                    "native_resolution": [10, -10],
                                    "styling": {
                                        "default_style": "simple_rgb",
                                        "styles": styles_s2_geomad,
                                    },
                                }
                            ],
                        },
                    ],
                },

            ],
        },
    ],
}