# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


reslim_landsat = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 35.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
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

bands_ls = {
    "red": [],
    "green": [],
    "blue": [],
    "nir": ["near_infrared"],
    "swir1": ["shortwave_infrared_1", "near_shortwave_infrared"],
    "swir2": ["shortwave_infrared_2", "far_shortwave_infrared"],
}

# new styles for C2 Landsat

bands_ls5_sr = {
    "SR_B1": ["blue"],
    "SR_B2": ["green"],
    "SR_B3": ["red"],
    "SR_B4": ["nir"],
    "SR_B5": ["swir_1"],
    "SR_B7": ["swir_2"],
    "QA_PIXEL": ["pq"],
}

bands_ls7_sr = {
    "SR_B1": ["blue"],
    "SR_B2": ["green"],
    "SR_B3": ["red"],
    "SR_B4": ["nir"],
    "SR_B5": ["swir_1"],
    "SR_B7": ["swir_2"],
    "QA_PIXEL": ["pq"],
}

bands_ls8_sr = {
    "SR_B2": ["blue"],
    "SR_B3": ["green"],
    "SR_B4": ["red"],
    "SR_B5": ["nir"],
    "SR_B6": ["swir_1"],
    "SR_B7": ["swir_2"],
    "QA_PIXEL": ["pq"],
}

legend_idx_0_1_5ticks = {
    "begin": "0.0",
    "end": "1.0",
    "ticks_every": "0.2",
    "units": "unitless",
}

legend_idx_percentage_by_10 = {
    "begin": "0.0",
    "end": "1.0",
    "ticks_every": 0.1,
    "units": "%",
    "tick_labels": {
        "0.0": {"label": "0"},
        "0.2": {"label": "20"},
        "0.4": {"label": "40"},
        "0.6": {"label": "60"},
        "0.8": {"label": "80"},
        "1.0": {"label": "100"},
    },
}
