# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


import os

if os.environ.get("DATACUBE_OWS_CFG", "").startswith("local"):
    cfgbase = "local_cfg"
    trans_dir = "."
else:
    cfgbase = "config"
    trans_dir = "/code"

# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2021 OWS Contributors
# SPDX-License-Identifier: Apache-2.0
import copy
# Migration of wms_cfg.py.  As at commit  c44c5e61c7fb9

# Reusable Chunks 1. Resource limit configurations

# Actual Configuration

reslim_c3_ls = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 15.0,
        # "max_datasets": 16, # Defaults to no dataset limit
    },
    "wcs": {
        # "max_datasets": 16, # Defaults to no dataset limit
    },
}

bands_c3_ls_8 = {
    "nbart_blue": ["nbart_blue"],
    "nbart_green": ["nbart_green"],
    "nbart_red": ["nbart_red"],
    "nbart_nir": ["nbart_nir", "nbart_near_infrared"],
    "nbart_swir_1": ["nbart_swir_1", "nbart_shortwave_infrared_1"],
    "nbart_swir_2": ["nbart_swir_2", "nbart_shortwave_infrared_2"],
    "oa_nbart_contiguity": ["oa_nbart_contiguity", "nbart_contiguity"],
    "oa_fmask": ["oa_fmask", "fmask"],
    "nbart_panchromatic": [],
    "nbart_coastal_aerosol": ["coastal_aerosol",  "nbart_coastal_aerosol"],
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
    "legend": {
        "begin": "0.0",
        "end": "1.0",
        "ticks_every": "0.2",
        "tick_labels": {
            "default": {
                "prefix": "+"
            },
            "0.0": {
                "prefix": "a ",
                "label": "bit"
            },
            "0.2": {
                "prefix": "d",
                "label": "000.2"
            },
            "0.8": {
                "prefix": "go"
            }
        },
        "title": "Nominal Inductance",
        "units": "microHenrys"
    }
# Define behaviour(s) for multi-date requests. If not declared, style only supports single-date requests.
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
    "legend": {
         "show_legend": True,
         "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Color_wheel_circle.png/440px-Color_wheel_circle.png"
    },
    "multi_date": [
        # A multi-date handler.  Different handlers can be declared for different numbers of dates in a request.
        {
            "preserve_user_date_order": True,
            # The count range for which this handler is to be used - a tuple of two ints, the smallest and
            # largest date counts for which this handler will be used.  Required.
            "allowed_count_range": [2, 12],
            "animate": True,
            "frame_duration": 1000,
            "legend": {
                "show_legend": True,
                "url": {
                    "en": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/The_British_Empire.png/720px-The_British_Empire.png",
                    "fr": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/France_cities.png/480px-France_cities.png"
                }
            }
        }
    ],
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
        "default_style": "ndvi",
        "styles": [style_c3_ndvi, style_c3_fmask, style_c3_simple_rgb]
    }
}

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


        "message_file": f"{trans_dir}/test_messages.po",
        "translations_directory": f"{trans_dir}/test_translations",
        "supported_languages": [
            "en", # Default
            "fr",
            "de",
            "sw",
        ],
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
        dea_c3_ls8_ard,
    ] # End of Layers List
} # End of ows_cfg object
