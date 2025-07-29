# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Downloads and installs hdf4."""

import os
import shutil

# import tarfile
import logging
import requests
from install_utils import run_shell_command, get_mamba_env

env_dir = get_mamba_env()

LOG = logging.getLogger(__name__)


def get_hdf4_install_dir(install_parent_dir, hdf4_ver):
    """Return a path given an hdf4 version."""
    return os.path.join(install_parent_dir, "hdf4", f"hdf-{hdf4_ver}")


def get_hdf4_verify_path(hdf4_dir):
    """Return a path that should be present if the version of HDF4 is installed."""
    return os.path.join(hdf4_dir, "bin", "h4dump")


def install_hdf4(
    install_parent_dir,
    hdf4_ver,
    tarball_dir,
    compiler_flags,
    overwrite=False,
):
    """Installs hdf4 given directories and a tarball as input."""
    hdf4_install_dir = get_hdf4_install_dir(install_parent_dir, hdf4_ver)

    if os.path.isfile(get_hdf4_verify_path(hdf4_install_dir)) and not overwrite:
        logging.info(f"Using existing hdf4 installation at {hdf4_install_dir}")
        return hdf4_install_dir
    logging.info(f"Installing hdf4 at {hdf4_install_dir}")
    if os.path.isdir(hdf4_install_dir):
        shutil.rmtree(hdf4_install_dir)
    os.makedirs(hdf4_install_dir)

    # download hdf4 tarball
    hdf4_tar_dir = os.path.join(tarball_dir, "hdf4")
    os.makedirs(hdf4_tar_dir, exist_ok=True)
    hdf4_tar_filepath = os.path.join(hdf4_tar_dir, f"hdf-{hdf4_ver}.tar.gz")
    if not os.path.isfile(hdf4_tar_filepath):
        url = (
            "https://support.hdfgroup.org/ftp/HDF/"
            + f"releases/HDF{hdf4_ver}/src/hdf-{hdf4_ver}.tar.gz"
        )
        logging.info(f"Downloading {url}")
        r = requests.get(url, timeout=3)
        open(hdf4_tar_filepath, "wb").write(r.content)

    logging.info("Untarring hdf4 tarball")
    src_folder = f"hdf-{hdf4_ver}"
    if os.path.isdir(src_folder):
        shutil.rmtree(src_folder)

    run_shell_command(
        f"tar -xf {hdf4_tar_filepath} -C {hdf4_install_dir}/..",
        "Untarring hdf4 tarball",
        env=None,
    )

    os.chdir(f"{hdf4_install_dir}")
    run_shell_command(
        f"./configure --enable-fortran --prefix={hdf4_install_dir} "
        + f"--with-jpeg={env_dir}/ "
        + f"--with-zlib={env_dir}/ "
        + "--disable-netcdf",
        "Configuring hdf4 build",
        env=None,
    )
    run_shell_command(
        "make -j 12", "Compiling hdf4 (this will likely take a while)", env=None
    )
    run_shell_command("make install", "Installing hdf4", env=None)

    os.chdir(os.pardir)

    return hdf4_install_dir
