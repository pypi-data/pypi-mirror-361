# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Downloads and installs all dependancies for clavrx."""

import os
import logging
from datetime import datetime
from subprocess import run
import re
from argparse import ArgumentParser

# Geoips packages
from geoips.filenames.base_paths import PATHS as gpaths

# Internal packages
from hdf4_installer import install_hdf4
from hdf5_installer import install_hdf5
from netcdf_installer import install_netcdf
from himawari_installer import install_libHimawari
from rttov_installer import install_rttov
from install_utils import run_shell_command, which, get_mamba_env
from user_change_me import user_change_me


env_dir = get_mamba_env()


def get_env(netcdf_dir, hdf4_dir, hdf5_dir):
    """Create env vars for building."""
    environ = dict(os.environ)
    environ["LDFLAGS"] = f"-L{hdf5_dir}/lib -L{env_dir}/lib"
    environ["PATH"] = (
        f"{netcdf_dir}/bin:{hdf4_dir}/bin:{hdf5_dir}/bin:{environ.get('PATH', '')}"
    )
    environ["LD_LIBRARY_PATH"] = (
        f"{netcdf_dir}/lib:{hdf4_dir}/lib:{env_dir}/lib:"
        + f"{hdf5_dir}/lib:{environ.get('LD_LIBRARY_PATH', '')}"
    )
    environ["LIBRARY_PATH"] = (
        f"{netcdf_dir}/lib:{hdf4_dir}/lib:{env_dir}/lib"
        + f"{hdf5_dir}/lib:{environ.get('LIBRARY_PATH', '')}"
    )

    environ["NCDIR"] = netcdf_dir
    environ["CPPFLAGS"] = f"-I{hdf5_dir}/include -I{env_dir}/include"
    return environ


def install_clavrx(
    install_parent_dir,
    clavrx_install_dir,
    tarball_dir,
    hdf4_ver,
    hdf5_ver,
    netcdf_ver,
    rttov_tar,
):
    """Installs all packages to set dependancy dirs."""
    if (
        os.path.exists(install_parent_dir)
        or os.path.exists(clavrx_install_dir)
        or os.path.exists(tarball_dir)
    ):
        print("Remove installation directories before installing clavrx")
        print(f"    {install_parent_dir}")
        print(f"    {clavrx_install_dir}")
        print(f"    {tarball_dir}")
        # check installs

        return 1
    else:
        os.makedirs(install_parent_dir, exist_ok=True)
        os.makedirs(clavrx_install_dir, exist_ok=True)
        os.makedirs(tarball_dir, exist_ok=True)
    start = datetime.now()
    # if binutils is installed in conda env, remove now
    # prompt for rttov registration and tar file download
    # prompt for ancillary data install
    #
    # Step 1: install hdf4
    # Step 2: install hdf5
    # Step 3: install netcdf4-c
    # Step 4: install netcdf-fortran
    # Step 5: install libHimawari
    # (install binutils to conda env, delete after libHimawair build)
    # Step 6: install rttov132
    # Step 7: Setup CLAVRx
    # Step 8: Build CLAVRx

    # rttov prompt here
    import sys

    registration_prompt = str(
        input(
            "\nThe rttov tar file is needed in order to build CLAVRx.\n"
            + "It is necessary to complete the free registration "
            + "process in order to download the rttov tar file.\n"
            + "Have you completed the free registration process, "
            + "and downloaded the rttov tar file ? (y/n): "
        )
    )

    if registration_prompt == "n":
        print(
            "\nInstructions to the free registration process as well as downloading\
            the rttov tar file can be found in the README.md file"
        )
        sys.exit()
    elif registration_prompt == "y":
        print(
            "\nInstalling CLAVRx and its prerequisite libraries...\
            (approx. 30 minutes to 1 hour to complete)\n"
        )

    print("Installing HDF4 (with C and Fortran Bindings)...")
    hdf4_start = datetime.now()
    hdf4_path = install_hdf4(
        install_parent_dir, hdf4_ver, tarball_dir, compiler_flags=None, overwrite=False
    )
    hdf4_end = datetime.now()
    print(f"Total time to install HDF4: {hdf4_end - hdf4_start}\n")

    print("Installing HDF5 (with C and F90+ Bindings)...")
    hdf5_start = datetime.now()
    hdf5_path = install_hdf5(
        install_parent_dir, hdf5_ver, tarball_dir, compiler_flags=None, overwrite=False
    )
    hdf5_end = datetime.now()
    print(f"Total time to install HDF5: {hdf5_end - hdf5_start}\n")

    print("Installing NetCDF4 (with C and F90+ Bindings)...")
    netcdf_start = datetime.now()
    netcdf_path = install_netcdf(
        install_parent_dir,
        netcdf_ver,
        hdf4_path,
        hdf5_path,
        tarball_dir,
        compiler_flags=None,
        overwrite=False,
    )
    netcdf_end = datetime.now()
    print(f"Total time to install NetCDF: {netcdf_end - netcdf_start}\n")

    himawari_start = datetime.now()
    print("Installing the Himawari Library...")
    himawari_path = install_libHimawari(install_parent_dir)
    himawari_end = datetime.now()
    print(f"Total time to install Himawari: {himawari_end - himawari_start}\n")

    rttov_start = datetime.now()
    print("Installing the RTTOV library...")
    rttov_path = install_rttov(install_parent_dir, rttov_tar, hdf5_ver, overwrite=False)
    rttov_end = datetime.now()
    print(f"Total time to install RTTOV: {rttov_end - rttov_start}\n")

    os.chdir(clavrx_install_dir)

    clavrx_start = datetime.now()
    print("Installing CLAVRx itself...")

    run_shell_command(
        "git clone https://gitlab.ssec.wisc.edu/clavrx/clavrx-dev.git CLAVRx",
        "cloning into CLAVRx...",
        env=None,
    )

    os.chdir(f"{clavrx_install_dir}/CLAVRx")

    run_shell_command("git checkout develop", "checking out develop branch", env=None)

    build_dir = f"{clavrx_install_dir}/CLAVRx/build"
    user_changes = f"{build_dir}/env_settings/examples/gfortran_gcc-linux"

    os.chdir(user_changes)

    gfortran_path = which("gfortran")
    gcc_path = which("gcc")

    # clean way to get gfortranversion
    gft_vers = str(run(["gfortran", "--version"], capture_output=True).stdout)
    gfortran_ver = re.search(r"\d\.\d.\d", gft_vers).group()

    if int(gfortran_ver[0]) <= 9:
        run_shell_command(
            "cp gfortran_9_or_earlier/user_change_me.cfg ../..",
            "copying user_change_me.cfg file over to env_settings directory",
            env=None,
        )
    else:
        run_shell_command(
            "cp gfortran_10_or_later/user_change_me.cfg ../..",
            "copying user_change_me.cfg file over to env_settings directory",
            env=None,
        )

    env_settings = f"{build_dir}/env_settings"
    os.chdir(env_settings)
    user_change_me(
        gfortran_path,
        gcc_path,
        hdf4_path,
        hdf5_path,
        netcdf_path,
        himawari_path,
        rttov_path,
    )

    os.chdir(build_dir)
    env = get_env(netcdf_path, hdf4_path, hdf5_path)

    run_shell_command("./admin clean", "cleaning...", env=env)

    run_shell_command("./admin build", "building CLAVR-x", env=env)

    clavrx_end = datetime.now()
    print(f"Total time to build and install CLAVRx: {clavrx_end - clavrx_start}\n")

    end = datetime.now()

    print(
        f"CLAVRx installation complete! \n \
        (Total time to build and install all necessary libraries: {end - start})"
    )
    os.chdir(os.pardir)

    print()


def main(args):
    """Pipe args to the install clavrx function."""
    install_parent_dir = args.install_parent_dir
    clavrx_install_dir = args.clavrx_install_dir
    tarball_dir = args.tarball_dir
    hdf4_ver = args.hdf4_ver
    hdf5_ver = args.hdf5_ver
    netcdf_ver = args.netcdf_ver
    rttov_tar = args.rttov_tar

    install_clavrx(
        install_parent_dir,
        clavrx_install_dir,
        tarball_dir,
        hdf4_ver,
        hdf5_ver,
        netcdf_ver,
        rttov_tar,
    )


if __name__ == "__main__":

    geoips_dependencies_dir = gpaths["GEOIPS_DEPENDENCIES_DIR"]
    geoips_outdir = gpaths["GEOIPS_OUTDIRS"]

    log_path = os.path.join(geoips_outdir, "clavrx_install_logs")
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    log_name = "clavrx_install_{}.log".format(
        datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    )
    log_filepath = f"{log_path}/{log_name}"

    logging.basicConfig(
        filename=log_filepath,
        encoding="utf-8",
        level=logging.INFO,
    )

    parser = ArgumentParser()

    parser.add_argument(
        "--install_parent_dir",
        type=str,
        default=f"{geoips_dependencies_dir}/clavrx/lib",
        help="Directory to hold everything regarding CLAVRx",
    )

    parser.add_argument(
        "--clavrx_install_dir",
        type=str,
        default=f"{geoips_dependencies_dir}/clavrx",
        help="Directory to hold CLAVRx build",
    )

    parser.add_argument(
        "--tarball_dir",
        type=str,
        default=f"{geoips_dependencies_dir}/clavrx/tar",
        help="Directory to hold tarballs for CLAVRx build",
    )

    parser.add_argument(
        "--hdf4_ver", type=str, default="4.2.15", help="hdf4 version e.g. 4.2.15"
    )

    parser.add_argument(
        "--hdf5_ver", type=str, default="1.14.2", help="hdf5 version e.g. 1.14.1"
    )

    # 4.9.2
    parser.add_argument(
        "--netcdf_ver", type=str, default="4.8.1", help="netcdf4 version e.g. 4.9.0"
    )

    parser.add_argument(
        "--rttov_tar",
        required=True,
        type=str,
        help="path that contains the downloaded rttov tar file",
    )

    args = parser.parse_args()

    main(args)
