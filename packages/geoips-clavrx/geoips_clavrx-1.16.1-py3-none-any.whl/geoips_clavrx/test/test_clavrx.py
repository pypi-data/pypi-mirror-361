# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Test the clavrx package and installation."""

# python packages
import os
import logging
from glob import glob
from argparse import ArgumentParser
from datetime import datetime

# geoips packages
from geoips_clavrx.clavrx.install_utils import run_shell_command
from geoips.filenames.base_paths import PATHS as gpaths

LOG = logging.getLogger(__name__)

geoips_dependencies_dir = gpaths["GEOIPS_DEPENDENCIES_DIR"]
geoips_outdir = gpaths["GEOIPS_OUTDIRS"]
geoips_testdata = gpaths["GEOIPS_TESTDATA_DIR"]
geoips_packages_dir = gpaths["GEOIPS_PACKAGES_DIR"]

inst_paths = {
    "VIIRS": [
        f"{geoips_testdata}/test_data_clavrx/data/clavrx_input/viirs_20240720/",
        f"{geoips_outdir}/clavrx_products/testing/viirs/",
        "GMTCO_*",
    ],
    "ABI": [
        f"{geoips_testdata}/test_data_clavrx/data/clavrx_input/goes16_20240607/",
        f"{geoips_outdir}/clavrx_products/testing/abi/",
        "OR_ABI-L1b-*C01_*",
    ],
    "AHI": [
        f"{geoips_testdata}/test_data_clavrx/data/clavrx_input/ahi_h09_20240606/",
        f"{geoips_outdir}/clavrx_products/testing/ahi/",
        "HS_H09*",
    ],
    "MODIS": [
        f"{geoips_testdata}/test_data_clavrx/data/clavrx_input/modis_20240607/",
        f"{geoips_outdir}/clavrx_products/testing/modis/",
        "MOD021KM*",
    ],
}


def get_env(clavrx_dir, netcdf_dir, hdf4_dir, hdf5_dir):
    """Set environment variables for testing."""
    # print(clavrx_dir, netcdf_dir, hdf4_dir, hdf5_dir)
    # raise
    environ = dict(os.environ)
    environ["LD_LIBRARY_PATH"] = (
        f"{netcdf_dir}/lib:{hdf4_dir}/lib:"
        + f"{hdf5_dir}/lib:{environ.get('LD_LIBRARY_PATH', '')}"
    )
    # Not sure if NCDIR and NFDIR are required, but can't hurt
    environ["NCDIR"] = netcdf_dir
    environ["NFDIR"] = netcdf_dir
    environ["CPPFLAGS"] = f"-I{netcdf_dir}/include -I{hdf5_dir}/include"
    environ["LDFLAGS"] = (
        f"-L{netcdf_dir}/lib -L{netcdf_dir}/lib -L{hdf4_dir}/lib -L{hdf5_dir}/lib"
    )
    environ["PATH"] = f"{clavrx_dir}/CLAVRx/run/bin:{environ.get('PATH', '')}"

    return environ


def run_clavrxorb(clavrx_dir, hdf4_dir, hdf5_dir, netcdf_dir, test_inst):
    """Run shell commands to setup options and testing directories."""
    # Changing to the run directory within CLAVRx
    os.chdir(f"{clavrx_dir}/CLAVRx/run/")

    run_shell_command(
        "cp example_runscripts/run_clavrxorb .",
        "copying run_clavrxorb executable to run directory",
        env=None,
    )

    run_shell_command(
        "cp examples-clavrx_options/clavrx_options .",
        "copying clavrx_options test example to run directory",
        env=None,
    )

    run_shell_command(
        "cp examples-file_list/file_list .",
        "copying file_list test example to run directory",
        env=None,
    )

    run_shell_command(
        "cp examples-level2_list/level2_list_cspp_viirs ./level2_list",
        "copying level2_list test example to run directory",
        env=None,
    )

    dcomp_mode = "1   !E1 ALG DCOMP\n"
    if test_inst == "AHI":
        dcomp_mode = "0   !E1 ALG DCOMP\n"

    # UNCOMMENT ONCE TEST DATA IS GOOD
    indir, outdir, infile = inst_paths[test_inst]
    infile = os.path.basename(glob(indir + infile)[0])

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # edit input file
    filelist_lines = [indir + "\n", outdir + "\n", infile + "\n"]
    with open(f"{geoips_dependencies_dir}/clavrx/CLAVRx/run/file_list", "w") as f:
        f.writelines(filelist_lines)

    # options were derived from the clavrx_user_guide_v_current

    with open(f"{geoips_dependencies_dir}/clavrx/CLAVRx/run/clavrx_options") as f:
        lines = f.readlines()
        lines[0] = f"{geoips_dependencies_dir}/clavrx/ancillary/\n"
        lines[3] = "9   !E1 Messaging Control Flag (VERBOSE = 9)\n"
        lines[4] = "2   !E1 ALG Mask mode bayesian cloud mask (2 = ECM2)\n"
        lines[5] = dcomp_mode
        lines[6] = "default  !E1 ALG ACHA\n"
        lines[19] = "2 !E2 RTM rtm option  (0=crtm,1=pfast, (2=rttov))\n"
        lines[22] = "0   !E2 MASK read auxilary cloud mask 1b (0 = don't read)\n"
        lines[39] = (
            "2 1 1 !E6 native res sample(0)/average(1),\
        average+stats(2), X_stride(>=1), Y_Stride (>=1))\n"
        )
        lines[13] = "0   !E2 OUTPUT format flag (0= hdf4, 1 = netcdf4)\n"
        lines[41] = "1 1 1 1 1 1    !E6 chan on flags of channels 7,8,9,10,11,12\n"
        lines[42] = "1 1 1 1 1 1    !E6 chan on flags of channels 13,14,15,16,17,18\n"
        lines[43] = "1 1 1 1 1 1    !E6 chan on flags of channels 19,20,21,22,23,24\n"
        lines[44] = "1 1 1 1 1 1    !E6 chan on flags of channels 25,26,27,28,29,30\n"
        lines[45] = "1 1 1 1 1 1    !E6 chan on flags of channels 31,32,33,34,35,36\n"
        lines[46] = "1 1 1 1 1 1    !E6 chan on flags of channels\n"
        lines[47] = (
            "1 1 1 1 1 1    !E6 chan on flags of channels 43(I5),44(DNB),45-48(Spare)\n"
        )
        lines[48] = (
            "225 !ISCCP-NG WMO 270=g16, 271=g17, 173=HIM8, 70 = MET11, 55 = MET8\n"
        )

    with open(f"{geoips_dependencies_dir}/clavrx/CLAVRx/run/clavrx_options", "w") as f:
        f.writelines(lines)

    env = get_env(clavrx_dir, hdf4_dir, hdf5_dir, netcdf_dir)
    LOG.info("Running clavrx")
    run_shell_command(
        "./run_clavrxorb",
        "running clavrxorb executable to test CLAVRx installation",
        env=env,
    )


if __name__ == "__main__":
    """Set arguments and runs test suite."""
    parser = ArgumentParser()

    # find needed libraries to default to
    hdf4_default = os.listdir(f"{geoips_dependencies_dir}/clavrx/lib/hdf4/")[0]
    hdf5_default = os.listdir(f"{geoips_dependencies_dir}/clavrx/lib/hdf5/")[0]
    netcdf_default = os.listdir(f"{geoips_dependencies_dir}/clavrx/lib/netcdf/")[0]

    # print("Found {},{},{}".format(hdf4_default,hdf5_default,netcdf_default))
    # raise

    parser.add_argument(
        "--clavrx_dir",
        type=str,
        default=f"{geoips_dependencies_dir}/clavrx/",
        help="directory containing clavrx build",
    )
    # 4.2.15
    parser.add_argument(
        "--hdf4_dir",
        type=str,
        default=f"{geoips_dependencies_dir}/clavrx/lib/hdf4/{hdf4_default}/",
        help="directory containing hdf4",
    )
    # 1.10.9
    parser.add_argument(
        "--hdf5_dir",
        type=str,
        default=f"{geoips_dependencies_dir}/clavrx/lib/hdf5/{hdf5_default}/",
        help="directory containing hdf5",
    )
    # 4.9.0
    parser.add_argument(
        "--netcdf_dir",
        type=str,
        default=f"{geoips_dependencies_dir}/clavrx/lib/netcdf/{netcdf_default}/",
        help="directory containing netcdf",
    )

    parser.add_argument("-l", "--log", type=str, default="INFO", help="Log level")

    parser.add_argument(
        "-i", "--inst", type=str, default="MODIS", help="Instrument to test"
    )

    args = parser.parse_args()

    clavrx_dir = args.clavrx_dir
    hdf4_dir = args.hdf4_dir
    hdf5_dir = args.hdf5_dir
    netcdf_dir = args.netcdf_dir

    log_dir = os.path.join(geoips_outdir, "clavrx_products", "test_clavrx_logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    logname = log_dir + "/clavrx_test_{}.log".format(
        datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    )

    logging.basicConfig(
        filename=logname,
        encoding="utf-8",
        level=logging.INFO,
    )

    LOG.info("Starting Clavrx run, log file in {}".format(logname))
    run_clavrxorb(clavrx_dir, hdf4_dir, hdf5_dir, netcdf_dir, args.inst)
