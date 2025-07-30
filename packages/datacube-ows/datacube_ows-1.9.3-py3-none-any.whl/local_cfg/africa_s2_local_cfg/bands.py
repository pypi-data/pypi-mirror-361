# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0




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


# Reusable Chunks 3. Legends
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