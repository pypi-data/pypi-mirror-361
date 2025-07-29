# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Install rttov from tarfile."""

import os
import shutil
import logging
import re
import pathlib

# import tarfile

from install_utils import run_shell_command
from hdf5_installer import get_hdf5_install_dir


def get_rttov_install_dir(install_parent_dir, rttov_ver):
    """Generate a rttov path given a rttov version."""
    return os.path.join(install_parent_dir, "rttov", f"rttov{rttov_ver}")


def install_rttov(
    install_parent_dir,
    rttov_tar,
    hdf5_ver,
    overwrite=False,
):
    """Install rttov given a tarpath and hdf5 version."""
    rttov_tar_filepath = rttov_tar

    rttov_tar_filename = pathlib.PurePath(rttov_tar)
    rttov_tar_filename = rttov_tar_filename.name

    rttov_ver = re.findall(r"\d+", rttov_tar_filename)
    rttov_ver = rttov_ver[0]

    rttov_install_dir = get_rttov_install_dir(install_parent_dir, rttov_ver)

    if os.path.isfile((rttov_install_dir)) and not overwrite:
        logging.info(f"Using existing rttov installation at {rttov_install_dir}")
        return rttov_install_dir
    logging.info(f"Installing rttov at {rttov_install_dir}")
    if os.path.isdir(rttov_install_dir):
        shutil.rmtree(rttov_install_dir)
    os.makedirs(rttov_install_dir)

    # rttov tarball
    # rttov_tar_dir = os.path.join(tarball_dir, 'rttov')
    # os.makedirs(rttov_tar_dir, exist_ok=True)

    src_folder = rttov_install_dir
    if os.path.isdir(src_folder):
        shutil.rmtree(src_folder)
    os.makedirs(src_folder)

    os.chdir(rttov_install_dir)

    run_shell_command(
        f"tar -xf {rttov_tar_filepath} -C {rttov_install_dir}",
        "Untarring rttov tarball",
        env=None,
    )

    os.chdir(f"{rttov_install_dir}")

    rttov_build = f"{src_folder}/build"
    os.chdir(rttov_build)

    # editing Makefile.local
    hdf5_path = get_hdf5_install_dir(install_parent_dir, hdf5_ver)

    with open("Makefile.local", "r") as file:
        contents = file.read()

        contents = contents.replace(
            "HDF5_PREFIX  = path-to-hdf-install", f"HDF5_PREFIX  = {hdf5_path}"
        )

        contents = contents.replace(
            "# FFLAGS_HDF5  = -D_RTTOV_HDF $(FFLAG_MOD)$(HDF5_PREFIX)/include",
            "FFLAGS_HDF5  = -D_RTTOV_HDF $(FFLAG_MOD)$(HDF5_PREFIX)/include",
        )

        contents = contents.replace(
            "# LDFLAGS_HDF5 = -L$(HDF5_PREFIX)/lib -lhdf5hl_fortran"
            + " -lhdf5_hl -lhdf5_fortran -lhdf5",
            "LDFLAGS_HDF5 = -L$(HDF5_PREFIX)/lib -lhdf5hl_fortran"
            + " -lhdf5_hl -lhdf5_fortran -lhdf5",
        )

    with open("Makefile.local", "w") as file:
        file.write(contents)

    rttov_src = f"{src_folder}/src"
    os.chdir(rttov_src)

    run_shell_command(
        "(echo 'gfortran'; echo -e '\n'; echo -e 'y'; echo -e '\n';"
        + " echo -e 'y';) | ../build/rttov_compile.sh",
        "building rttov...",
        env=None,
    )

    os.chdir(os.pardir)

    return rttov_install_dir
