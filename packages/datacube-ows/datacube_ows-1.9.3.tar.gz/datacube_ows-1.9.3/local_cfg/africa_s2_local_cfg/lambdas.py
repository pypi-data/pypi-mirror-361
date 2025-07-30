# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


import numpy  # pylint: disable=import-error


def mask_by_nan(data, band):
    return ~numpy.isnan(data[band])


def mask_by_emad_nan(data, band, band_mapper=None):
    if band_mapper:
        emad = band_mapper("EMAD")
    else:
        emad = "EMAD"
    return ~numpy.isnan(data[emad])