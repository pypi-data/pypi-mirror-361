# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Absolute difference of CTH between two CLAVR-x files 1 timestep apart."""

import logging

import numpy as np
import xarray as xr

from geoips.data_manipulations.corrections import apply_data_range
from geoips.errors import PluginError

LOG = logging.getLogger(__name__)


name = "absdiff_cth"
interface = "algorithms"
family = "xarray_dict_to_xarray"


def call(
    xarray_dict,
    output_data_range=None,
    input_units=None,
    output_units=None,
    min_outbounds="crop",
    max_outbounds="crop",
    norm=False,
    inverse=False,
    sun_zen_correction=False,
    mask_night=False,
    max_day_zen=None,
    mask_day=False,
    min_night_zen=None,
    gamma_list=None,
    scale_factor=None,
):
    """Apply the absolute difference between cloud top height from two different times.

    Where cloud top height is 'cld_height_acha' coming from clavrx files.

    Parameters
    ----------
    xarray_dict : dictionary of xarray objects
        * dictionary of xarray.Datasets (3D in dimensions)
    output_data_range : list of float, default=None
        * list of min and max value for output data product.
        * This is applied LAST after all other corrections/adjustments
        * If None, use data min and max.
    input_units : str, default=None
        * Units of input data, for applying necessary conversions
        * If None, no conversion
    output_units : str, default=None
        * Units of output data, for applying necessary conversions
        * If None, no conversion
    min_outbounds : str, default='crop'
        * Method to use when applying bounds.  Valid values are:

            * retain: keep all pixels as is
            * mask: mask all pixels that are out of range
            * crop: set all out of range values to either min_val or max_val
              as appropriate
    max_outbounds : str, default='crop'
        * Method to use when applying bounds.  Valid values are:

            * retain: keep all pixels as is
            * mask: mask all pixels that are out of range
            * crop: set all out of range values to either min_val or max_val
              as appropriate
    norm : bool, default=False
        * Boolean flag indicating whether to normalize (True) or not (False)

            * If True, returned data will be in the range from 0 to 1
            * If False, returned data will be in the range from min_val to max_val
    inverse : bool, default=False
        * Boolean flag indicating whether to inverse (True) or not (False)

            * If True, returned data will be inverted
            * If False, returned data will not be inverted
    sun_zenith_correction : bool, default=False
        * Boolean flag indicating whether to apply solar zenith correction
          (True) or not (False)

            * If True, returned data will have solar zenith correction applied
              (see data_manipulations.corrections.apply_solar_zenith_correction)
            * If False, returned data will not be modified based on solar zenith
              angle
    """
    lon = np.asarray(xarray_dict["DATA"]["longitude"][0])
    lat = np.asarray(xarray_dict["DATA"]["latitude"][0])

    try:
        cth1 = np.asarray(xarray_dict["DATA"]["cld_height_acha"][0])
        cth2 = np.asarray(xarray_dict["DATA"]["cld_height_acha"][1])
    except KeyError:
        raise PluginError(
            "Error. Algorithm 'absdiff_cth' was requested to be applied to the incoming"
            " data but the data is missing 'cld_height_acha' from one or more files."
        )

    data = np.abs(cth2 - cth1)

    data = apply_data_range(
        data,
        min_val=output_data_range[0],
        max_val=output_data_range[1],
        min_outbounds=min_outbounds,
        max_outbounds=max_outbounds,
        norm=norm,
        inverse=inverse,
    )

    final_xobj = xr.Dataset(
        data_vars={"Absdiff-Cloud-Top-Height": (["y", "x"], data)},
        coords={
            "longitude": (["y", "x"], lon),
            "latitude": (["y", "x"], lat),
        },
        attrs=xarray_dict["METADATA"].attrs,
    )

    return final_xobj
