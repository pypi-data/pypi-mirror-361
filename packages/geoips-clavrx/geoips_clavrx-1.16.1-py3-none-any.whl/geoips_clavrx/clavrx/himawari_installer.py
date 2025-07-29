# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Install Himawari library."""

import os
import shutil
import logging

from install_utils import run_shell_command


def get_libHimawari_install_dir(install_parent_dir):
    """Create and join a path."""
    return os.path.join(install_parent_dir, "libHimawari")


def install_libHimawari(install_parent_dir):
    """Install libHimawari from gitlab."""
    libHimawari_install_dir = get_libHimawari_install_dir(install_parent_dir)

    logging.info(f"Installing libHimawari at {libHimawari_install_dir}")
    if os.path.isdir(libHimawari_install_dir):
        shutil.rmtree(libHimawari_install_dir)
    os.makedirs(libHimawari_install_dir)

    os.chdir(libHimawari_install_dir)

    run_shell_command(
        "conda install -c conda-forge binutils --yes",
        "installing binutils (Only necessary for libHimawari build)",
        env=None,
    )
    # cloning from github
    run_shell_command(
        "git clone https://gitlab.ssec.wisc.edu/rayg/himawari.git",
        "cloning into libHimawari...",
        env=None,
    )

    src_folder = f"{libHimawari_install_dir}/himawari/src"

    os.chdir(src_folder)
    run_shell_command("make", "Compiling libHimawari", env=None)

    os.chdir(os.pardir)

    run_shell_command(
        "conda remove binutils --yes",
        "removing binutils (Only necessary for libHimawari build)",
    )

    return libHimawari_install_dir
