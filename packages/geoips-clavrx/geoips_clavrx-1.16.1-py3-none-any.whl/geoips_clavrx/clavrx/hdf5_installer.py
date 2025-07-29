# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Download and install hdf5."""

import os
import shutil

# import tarfile
import logging
import requests

from install_utils import run_shell_command, get_mamba_env

env_dir = get_mamba_env()


def get_hdf5_install_dir(install_parent_dir, hdf5_ver):
    """Return a path with the hdf5 version."""
    return os.path.join(install_parent_dir, "hdf5", f"hdf5-{hdf5_ver}")


def get_hdf5_verify_path(hdf5_dir):
    """Return a path that should be present if the version of HDF5 is installed."""
    return os.path.join(hdf5_dir, "bin", "h5dump")


def install_hdf5(
    install_parent_dir,
    hdf5_ver,
    tarball_dir,
    compiler_flags,
    overwrite=False,
):
    """Install hdf5, checking for existing installations."""
    hdf5_install_dir = get_hdf5_install_dir(install_parent_dir, hdf5_ver)

    if os.path.isfile(get_hdf5_verify_path(hdf5_install_dir)) and not overwrite:
        logging.info(f"Using existing hdf5 installation at {hdf5_install_dir}")
        return hdf5_install_dir
    logging.info(f"Installing hdf5 at {hdf5_install_dir}")
    if os.path.isdir(hdf5_install_dir):
        shutil.rmtree(hdf5_install_dir)
    os.makedirs(hdf5_install_dir)

    # download hdf5 tarball
    hdf5_ver_major = ".".join(hdf5_ver.split(".")[:2])
    hdf5_tar_dir = os.path.join(tarball_dir, "hdf5")
    os.makedirs(hdf5_tar_dir, exist_ok=True)
    hdf5_tar_filepath = os.path.join(hdf5_tar_dir, f"hdf5-{hdf5_ver}.tar.gz")
    if not os.path.isfile(hdf5_tar_filepath):
        url = (
            "https://support.hdfgroup.org/ftp/HDF5/"
            + f"releases/hdf5-{hdf5_ver_major}/hdf5-{hdf5_ver}"
            + f"/src/hdf5-{hdf5_ver}.tar.gz"
        )
        logging.info(f"Downloading {url}")
        r = requests.get(url, timeout=3)
        open(hdf5_tar_filepath, "wb").write(r.content)

    logging.info("Untarring hdf5 tarball")
    src_folder = f"hdf5-{hdf5_ver}"
    if os.path.isdir(src_folder):
        shutil.rmtree(src_folder)

    run_shell_command(
        f"tar -xf {hdf5_tar_filepath} -C {hdf5_install_dir}/..",
        "Untarring hdf5 tarball",
        env=None,
    )

    os.chdir(f"{hdf5_install_dir}")

    run_shell_command(
        "./configure --enable-fortran --enable-cxx "
        + f"--with-zlib={env_dir}/ "
        + f"--enable-hl --prefix={hdf5_install_dir} ",
        "Configuring hdf5 build",
        env=None,
    )

    run_shell_command(
        "make -j 8", "Compiling hdf5 (this will likely take a while)", env=None
    )

    run_shell_command("make -i install", "Installing hdf5", env=None)

    os.chdir(os.pardir)

    return hdf5_install_dir
