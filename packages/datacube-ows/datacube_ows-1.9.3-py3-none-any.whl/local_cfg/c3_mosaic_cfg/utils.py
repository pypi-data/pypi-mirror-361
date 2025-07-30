# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
from typing import Sequence, Tuple


def rolling_window_6day(available_dates: Sequence[datetime.datetime], layer_cfg) -> Tuple[datetime.datetime, datetime.datetime]:
    days = available_dates[-6:]
    start, _ = layer_cfg.search_times(days[-6])
    _, end = layer_cfg.search_times(days[-1])
    return (start, end)
