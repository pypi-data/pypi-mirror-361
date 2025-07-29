#!/usr/bin/env python

# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Downloads ancillary data."""

from datetime import datetime
import calendar
import requests
import logging
import os
import sys
from itertools import chain
from glob import glob


LOG = logging.getLogger(__name__)


key = "GEOIPS_DEPENDENCIES_DIR"
geoips_dependencies_dir = os.getenv(key)

# ancil_home = f"{geoips_dependencies_dir}/clavrx/ancillary/"
dynamic_dir = f"{geoips_dependencies_dir}/clavrx/ancillary/dynamic"
# static_dir = f"{geoips_dependencies_dir}/clavrx/ancillary/static"


def fetch_dynamic(user_date=None):
    """Fetch dynamic data for Clavrx.

    Parameters
    ----------
    user_date: datetime
        Defaults to current date if no date is supplied.
    """
    if user_date:
        input_date = datetime.strptime(str(user_date), "%Y%m%d")
    else:
        input_date = datetime.now()

    date_format = "%m/%d/%Y"
    year = input_date.year
    month = input_date.month
    day = input_date.day

    day_one = datetime.strptime(f"01/01/{year}", date_format)
    day_now = datetime.strptime(f"{month}/{day}/{year}", date_format)
    delta = day_now - day_one

    if calendar.isleap(year):
        day_total = delta.days + 1
    else:
        day_total = delta.days

    year_digits = year - 2000
    hour = ["00", "06", "12", "18"]
    forecast_time = ["03", "06", "09", "12", "15", "18", "21"]
    gfs_files = []

    if month - 1 < 10:
        z = 0
    else:
        z = ""
    if day < 10:
        x = 0
    else:
        x = ""

    t = 0
    # NWP data
    for h in hour:
        for f in forecast_time:
            gfs_files.append(f"gfs.{year_digits}{z}{month}{x}{day}{h}_F0{f}.hdf")

    print("Downloading GFS files: \n")
    for i in range(len(gfs_files)):

        t += 1
        print(str(i) + ") " + gfs_files[i] + ":")
        if os.path.exists(f"{dynamic_dir}/gfs/{gfs_files[i]}"):
            print("GFS file already downloaded")
            continue

        url = (
            "http://geodb.ssec.wisc.edu/ancillary/"
            + f"{year}_{z}{month}_{x}{day}_{day_total}/{gfs_files[i]}"
        )
        print(url + "\n\n")
        logging.info(f"Downloading {url}")
        r = requests.get(url, timeout=1)

        if r.status_code == 404:
            logging.debug("HTTP 404: File not found, trying tyr.ssec")
            url = (
                "http://tyr.ssec.wisc.edu/gfs/"
                + f"{year}/{z}{month}_{x}{day}_{day_total}/{gfs_files[i]}"
            )
            print("Reattempting download: ", url + "\n\n")
            logging.info(f"Downloading {url}")
            r = requests.get(url, timeout=1)
            if r.status_code == 404:
                logging.debug("HTTP 404: both failed :(")
                continue

        open(f"{dynamic_dir}/gfs/{gfs_files[i]}", "wb").write(r.content)

    # IMS data
    snow = f"snow_map_4km_{year_digits}{z}{month}{x}{day}.nc"
    url = (
        "http://geodb.ssec.wisc.edu/ancillary/"
        + f"{year}_{z}{month}_{x}{day}_{day_total}/{snow}"
    )
    logging.info(f"Downloading {url}")
    r = requests.get(url, timeout=3)
    # Need 404 check
    if r.status_code == 404:
        print("No file found, attempting different url download")
        url = "http://tyr.ssec.wisc.edu/snow/" + f"{year}/{snow}"
        r = requests.get(url, timeout=3)

    elif os.path.exists(f"{dynamic_dir}/snow/hires/{snow}"):
        print("Snow map file already downloaded.")
    else:
        print(f"{i + 1}) {snow}: \n")
        print(url + "\n\n")
        open(f"{dynamic_dir}/snow/hires/{snow}", "wb").write(r.content)

    # OISST data
    oisst = f"avhrr-only-v2.{year}{z}{month}{x}{day}.nc"
    url = (
        "http://geodb.ssec.wisc.edu/"
        + f"ancillary/{year}_{z}{month}_{x}{day}_{day_total}/{oisst}"
    )
    logging.info(f"Downloading {url}")
    r = requests.get(url, timeout=3)

    if r.status_code == 404:
        # oisst might be preliminary
        oisst = f"avhrr-only-v2.{year}{z}{month}{x}{day}_preliminary.nc"
        url = (
            "http://geodb.ssec.wisc.edu/"
            + f"ancillary/{year}_{z}{month}_{x}{day}_{day_total}/{oisst}"
        )
        r = requests.get(url, timeout=3)

        # ultimate fallback: tyr (hdf files?)
        if r.status_code == 404:
            url = "http://tyr.ssec.wisc.edu/oisst_nc/" + f"{year}/{oisst}"
            r = requests.get(url, timeout=3)

    if os.path.exists(f"{dynamic_dir}/oisst_nc/{year}/{oisst}"):
        print("AVHRR SST file already downloaded.")
    else:
        print(f"{i + 2}) {oisst}:\n")
        print(url + "\n\n")
        open(f"{dynamic_dir}/oisst_nc/{year}/{oisst}", "wb").write(r.content)

    return


def clean_dynamic():
    """Clean dynamic directory."""
    filelist = [
        chain.from_iterable(glob(os.path.join(x[0], "*")) for x in os.walk(dynamic_dir))
    ][0]

    for f in filelist:
        if os.path.isdir(f):
            continue
        elif os.path.getsize(f) == 196:
            # exact size of empty files
            print(f"Empty file, removing: {f}")
            os.remove(f)

    return None


if __name__ == "__main__":
    clean_dynamic()
    fetch_dynamic(sys.argv[1])
