# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0




bands_c3_ls_common = {
    "nbart_blue": ["nbart_blue"],
    "nbart_green": ["nbart_green"],
    "nbart_red": ["nbart_red"],
    "nbart_nir": ["nbart_nir", "nbart_near_infrared"],
    "nbart_swir_1": ["nbart_swir_1", "nbart_shortwave_infrared_1"],
    "nbart_swir_2": ["nbart_swir_2", "nbart_shortwave_infrared_2"],
    "oa_nbart_contiguity": ["oa_nbart_contiguity", "nbart_contiguity"],
    "oa_fmask": ["oa_fmask", "fmask"],
}

bands_c3_ls_7 = bands_c3_ls_common.copy()
bands_c3_ls_7.update({
    "nbart_panchromatic": [],
})


bands_c3_ls_8 = bands_c3_ls_7.copy()
bands_c3_ls_8.update({
    "nbart_coastal_aerosol": ["coastal_aerosol",  "nbart_coastal_aerosol"],
})


bands_wofs_filt_sum = {"confidence": [], "wofs_filtered_summary": []}

bands_wofs_sum = {
    "count_wet": [],
    "count_clear": [],
    "frequency": [],
}

bands_wofs_obs = {
    "water": [],
}

bands_s2_ls_combo = {
    "nbart_red": ["nbart_red", "red"],
    "nbart_green": ["nbart_green", "green"],
    "nbart_blue": ["nbart_blue", "blue"],
    "nbart_common_nir": ["nbart_common_nir", "nir"],
    "nbart_common_swir_1": ["nbart_common_swir_1", "swir_1"],
    "nbart_common_swir_2": ["nbart_common_swir_2", "swir_2"],
    "oa_fmask": ["oa_fmask"],
}
