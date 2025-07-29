# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Downloads ancillary data."""

from datetime import datetime
import logging
import os
import subprocess
import sys

from geoips_clavrx.ancillary import update_dynamic

LOG = logging.getLogger(__name__)

today = datetime.now()

geoips_dependencies_dir = os.getenv("GEOIPS_DEPENDENCIES_DIR")

ancil_home = f"{geoips_dependencies_dir}/clavrx/ancillary/"
dynamic_dir = f"{geoips_dependencies_dir}/clavrx/ancillary/dynamic"
static_dir = f"{geoips_dependencies_dir}/clavrx/ancillary/static"


"""
Download of dynamic ancillary data required for CLAVRx to function.
"""

update_dynamic.fetch_dynamic()
print("Finished downloading dynamic data")

"""
Download static data for CLAVRx
"""
# download from CSPP (much more reliable)

static_prompt = str(
    input(
        "\nStatic data for CLAVRx utilizes roughly \n"
        + "410 GiB of space, do you want to proceed with install? (y/n): "
    )
)

if static_prompt == "n":
    print("\nEither link static data or install on system.")
    sys.exit()
elif static_prompt == "y":
    print("Started downloading static data, this may take a while....")


static_url = "ftp://epscloud.ssec.wisc.edu/clavrx_ancil_data/static"
print("Downloading static data from {}".format(static_url))
# GFS data http://tyr.ssec.wisc.edu/gfs/

wget_run = subprocess.run(
    ["wget", "-vr", static_url], capture_output=True, cwd=ancil_home
)

static_folders = (
    f"{geoips_dependencies_dir}/epscloud.ssec.wisc.edu/clavrx_ancil_data/static/"
)
# tar_path = os.path.join(ancil_home, "CSPP_CLAVRX_V3.0_STATIC.tar.xz")


subprocess.run(["mv", static_folders, static_dir])
subprocess.run(["rm", "-rf", static_folders])


subprocess.run(
    [
        "cp",
        f"{static_dir}/luts/ecm2/nb_cloud_mask_calipso_prior_new.nc",
        f"{static_dir}/luts/ecm2/nb_cloud_mask_calipso_prior.nc",
    ]
)
subprocess.run(["cp", f"{static_dir}", f"{static_dir}"])

print("Finished downloading static data")
