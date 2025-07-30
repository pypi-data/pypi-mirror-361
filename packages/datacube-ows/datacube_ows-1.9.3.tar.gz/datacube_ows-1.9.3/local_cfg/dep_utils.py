import numpy  # pylint: disable=import-error


def mask_by_nan(data, band):
    return ~numpy.isnan(data[band])


def mask_by_emad_nan(data, band):
    return ~numpy.isnan(data["emad"])
