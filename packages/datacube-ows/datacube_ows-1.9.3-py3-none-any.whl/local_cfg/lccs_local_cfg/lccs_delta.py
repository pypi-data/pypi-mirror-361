# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


from typing import Iterable, Tuple, Union

from xarray import Dataset


def lccs_map_delta(data: Dataset) -> Dataset:
    data1, data2 = (data.sel(time=dt) for dt in data.coords["time"].values)

    equality_mask = data1["level4"] != data2["level4"]
    data1["level4"] = data2["level4"].where(equality_mask, other=255)
    return data1

