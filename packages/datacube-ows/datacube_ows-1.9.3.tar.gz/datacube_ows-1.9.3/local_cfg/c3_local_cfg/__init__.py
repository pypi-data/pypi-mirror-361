# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


from .layers import dea_c3_ls_ard, dea_c3_ls5_ard, dea_c3_ls7_ard, dea_c3_ls8_ard, s2_wofs_3

folder_c3_landsat = {
        "title": "Collection 3 Landsat Surface Relectance",
        "abstract": """
        """,
        "layers": [dea_c3_ls_ard, dea_c3_ls5_ard, dea_c3_ls7_ard, dea_c3_ls8_ard],
}

folder_c3_s2 = {
        "title": "Collection 3 Sentinel-2 Derived Products",
        "abstract": """
        """,
        "layers": [s2_wofs_3],
}

