# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


from .bands import *
from .styles import *
from .resource_limits import reslim_c3_ls, reslim_c3_s2

dea_c3_ls_ard = {
        "title": "Geoscience Australia Landsat Nadir BRDF Adjusted Reflectance Terrain Collection 3",
        "name": "ga_ls_ard_3",
        "abstract": """
This product takes Landsat imagery captured over the Australian continent and corrects for inconsistencies across land and coastal fringes. The result is accurate and standardised surface reflectance data, which is instrumental in identifying and quantifying environmental change.
This product combines:
Landsat 8 imagery https://cmi.ga.gov.au/data-products/dea/365/dea-surface-reflectance-landsat-8-oli-tirs,
Landsat 7 imagery https://cmi.ga.gov.au/data-products/dea/475/dea-surface-reflectance-landsat-7-etm and
Landsat 5 Imagery https://cmi.ga.gov.au/data-products/dea/358/dea-surface-reflectance-landsat-5-tm
For service status information, see https://status.dea.ga.gov.au""",
        "multi_product": True,
        "product_names": [
            # "ga_ls5t_ard_3",
            "ga_ls7e_ard_3",
            "ga_ls8c_ard_3",
        ],
        "bands": bands_c3_ls_common,
        "resource_limits": reslim_c3_ls,
        "dynamic": True,
        "image_processing": {
            "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
            "always_fetch_bands": [],
            "manual_merge": False,
        },
        "default_time": "earliest",
        "time_axis": {
            "time_interval": 1
        },
        "flags": [
            {
                "band": "oa_fmask",
                "products": [
                    # "ga_ls5t_ard_3",
                    "ga_ls7e_ard_3",
                    "ga_ls8c_ard_3",
                ],
                "ignore_time": False,
                "ignore_info_flags": [],
            },
            {
                "band": "land",
                "products": [
                    "geodata_coast_100k",
                    "geodata_coast_100k",
                    "geodata_coast_100k",
                ],
                "ignore_time": True,
                "ignore_info_flags": []
            },
        ],
        "native_crs": "EPSG:3577",
        "native_resolution": [25, -25],
        "styling": {"default_style": "simple_rgb", "styles": styles_c3_ls_common},
}


dea_c3_ls8_ard = {
                            "title": "DEA C3 Landsat 8 ARD",
                            "abstract": """
This product takes Landsat 8 imagery captured over the Australian continent and corrects for inconsistencies across land and coastal fringes. The result is accurate and standardised surface reflectance data, which is instrumental in identifying and quantifying environmental change.
The imagery is captured using the Operational Land Imager (OLI) and Thermal Infra-Red Scanner (TIRS) sensors aboard Landsat 8.
This product is a single, cohesive Analysis Ready Data (ARD) package, which allows you to analyse surface reflectance data as is, without the need to apply additional corrections.
It contains three sub-products that provide corrections or attribution information:
Surface Reflectance NBAR 3 (Landsat 8 OLI-TIRS)
Surface Reflectance NBART 3 (Landsat 8 OLI-TIRS)
Surface Reflectance OA 3 (Landsat 8 OLI-TIRS)
The resolution is a 30 m grid based on the USGS Landsat Collection 1 archive.""",
                            # The WMS name for the layer
                            "name": "ga_ls8c_ard_3",
                            # The Datacube name for the associated data product
                            "product_name": "ga_ls8c_ard_3",
                            "bands": bands_c3_ls_8,
                            "resource_limits": reslim_c3_ls,
                            "default_time": "2020-01-01",
                            "image_processing": {
                                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                                "always_fetch_bands": [],
                                "manual_merge": False,
                            },
                            "flags": [
                                {
                                    "band": "oa_nbart_contiguity",
                                    "product": "ga_ls8c_ard_3",
                                    "ignore_time": False,
                                    "ignore_info_flags": [],
                                },
                                {
                                    "band": "oa_fmask",
                                    "product": "ga_ls8c_ard_3",
                                    "ignore_time": False,
                                    "ignore_info_flags": [],
                                },
                            ],
                            "native_crs": "EPSG:3577",
                            "native_resolution": [25, -25],
                            "styling": {
                                "default_style": "simple_rgb",
                                "styles": styles_c3_ls_8
                            },
                        }
dea_c3_ls7_ard =        {
                            "title": "DEA C3 Landsat 7 ARD",
                            "abstract": """
The United States Geological Survey's (USGS) Landsat satellite program has been capturing images of the Australian continent for more than 30 years. This data is highly useful for land and coastal mapping studies.
In particular, the light reflected from the Earth’s surface (surface reflectance) is important for monitoring environmental resources – such as agricultural production and mining activities – over time.
We need to make accurate comparisons of imagery acquired at different times, seasons and geographic locations. However, inconsistencies can arise due to variations in atmospheric conditions, sun position, sensor view angle, surface slope and surface aspect. These need to be reduced or removed to ensure the data is consistent and can be compared over time.
For service status information, see https://status.dea.ga.gov.au""",
                            # The WMS name for the layer
                            "name": "ga_ls7e_ard_3",
                            # The Datacube name for the associated data product
                            "product_name": "ga_ls7e_ard_3",
                            "bands": bands_c3_ls_7,
                            "resource_limits": reslim_c3_ls,
                            "image_processing": {
                                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                                "always_fetch_bands": [],
                                "manual_merge": False,
                            },
                            "flags": [
                                {
                                    "band": "oa_nbart_contiguity",
                                    "product": "ga_ls8c_ard_3",
                                    "ignore_time": False,
                                    "ignore_info_flags": [],
                                },
                                {
                                    "band": "oa_fmask",
                                    "product": "ga_ls8c_ard_3",
                                    "ignore_time": False,
                                    "ignore_info_flags": [],
                                },
                            ],
                            "native_crs": "EPSG:3577",
                            "native_resolution": [25, -25],
                            "styling": {
                                "default_style": "simple_rgb",
                                "styles": styles_c3_ls_7
                            },
                        }
dea_c3_ls5_ard =        {
                            "title": "DEA C3 Landsat 5 ARD",
                            "abstract": """
The United States Geological Survey's (USGS) Landsat satellite program has been capturing images of the Australian continent for more than 30 years. This data is highly useful for land and coastal mapping studies.
In particular, the light reflected from the Earth’s surface (surface reflectance) is important for monitoring environmental resources – such as agricultural production and mining activities – over time.
We need to make accurate comparisons of imagery acquired at different times, seasons and geographic locations. However, inconsistencies can arise due to variations in atmospheric conditions, sun position, sensor view angle, surface slope and surface aspect. These need to be reduced or removed to ensure the data is consistent and can be compared over time.
For service status information, see https://status.dea.ga.gov.au""",
                            # The WMS name for the layer
                            "name": "ga_ls5t_ard_3",
                            # The Datacube name for the associated data product
                            "product_name": "ga_ls5t_ard_3",
                            "bands": bands_c3_ls_common,
                            "resource_limits": reslim_c3_ls,
                            "time_resolution": "subday",
                            "image_processing": {
                                "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                                "always_fetch_bands": [],
                                "manual_merge": False,
                            },
                            "flags": [
                                {
                                    "band": "oa_nbart_contiguity",
                                    "product": "ga_ls5t_ard_3",
                                    "ignore_time": False,
                                    "ignore_info_flags": [],
                                },
                                {
                                    "band": "oa_fmask",
                                    "product": "ga_ls5t_ard_3",
                                    "ignore_time": False,
                                    "ignore_info_flags": [],
                                },
                            ],
                            "native_crs": "EPSG:3577",
                            "native_resolution": [25, -25],
                            "styling": {
                                "default_style": "simple_rgb",
                                "styles": styles_c3_ls_common,
                            },
                        }



s2_wofs_3 = {
    "title": "Prototype Sentinel 2 Water Observations",
    "name": "ga_s2_wo_3",
    "abstract": """ Prototype Sentinel 2 Water Observations""",
    "product_name": "ga_s2_wo_3",
    "bands": bands_wofs_obs,
    "resource_limits": reslim_c3_s2,
    "dynamic": True,
    "flags": [
        {
            "band": "land",
            "product": "geodata_coast_100k",
            "ignore_time": True,
            "ignore_info_flags": [],
        },
        {
            "band": "water",
            "product": "ga_s2_wo_3",
            "ignore_time": False,
            "ignore_info_flags": [],
            "fuse_func": "datacube_ows.wms_utils.wofls_fuser",
        },
    ],
    "image_processing": {
        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_bitflag",
        "always_fetch_bands": [],
        "manual_merge": False,
        "fuse_func": "datacube_ows.wms_utils.wofls_fuser",
    },
    "native_crs": "EPSG:3577",
    "native_resolution": [10, -10],
    "styling": {
        "default_style": "observations",
        "styles": [style_c3_wofs_obs, style_s2_wofs_obs_wet_only],
    },
}