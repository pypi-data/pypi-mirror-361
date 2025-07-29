# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""CLAVR-x NetCDF4 Reader."""
import logging

LOG = logging.getLogger(__name__)

interface = "readers"
family = "standard"
name = "clavrx_netcdf4"


def call(fnames, metadata_only=False, chans=None, area_def=None, self_register=False):
    """Unsupported CLAVR-x NetCDF4 reader."""
    LOG.exception("READER NOT IMPLEMENTED")
    return None
