# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Installation utilities."""

import os
import sys
from glob import glob
from subprocess import Popen, PIPE, STDOUT
import logging

LOG = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
handler.setFormatter(formatter)
LOG.addHandler(handler)

compiler_keys = [
    "LD_LIBRARY_PATH",
    "LIBS",
    "PATH",
    "LIBRARY_PATH",
    "FC",
    "CC",
    "F9X",
    "CXX",
    "LDFLAGS",
    "FCFLAGS",
]


def run_shell_command(command_str, description, env=None):
    """Run a shell command, sending errors to log file."""
    LOG.info(description)
    # Don't make dict(os.environ) the default value
    # in the function definition, since this needs
    # to be re-evaluated at every function call
    # rather than just once when the module is loaded
    if not env:
        env = dict(os.environ)
    for env_variable in compiler_keys:
        LOG.debug(f"{env_variable}: {env.get(env_variable, 'N/A')}")

    process = Popen(
        command_str, env=env, stderr=STDOUT, stdout=PIPE, shell=True
    )  # nosec

    with process.stdout as pipe:
        for line in iter(pipe.readline, b""):  # b'\n'-separated lines
            LOG.info(line.decode().rstrip())

    process.wait()

    if process.returncode > 0:

        print(
            f"{description} failed. For more information look in clavrx.log"
            + " in $GEOIPS_OUTDIRS/clavrx_install_log/"
        )

        LOG.critical(
            f"{description} failed. For more information look in clavrx.log"
            + " in $GEOIPS_OUTDIRS/clavrx_install_log/"
        )
        sys.exit()


def check_compiler(arch):
    """Check compliers for version problems."""
    if arch == "gfortran-openmp":
        # bit to check what gcc version is available, if not > 6. Problem. exit.
        p = Popen(["gfortran", "--version"], stdout=PIPE, stderr=PIPE)
        p.wait()
        (so, se) = p.communicate()

        if int(so.split()[3].decode("utf-8").split(".")[0]) < 6:
            LOG.critical(
                "Compiler too old. Need something that can do f2008.\
                Tested with gcc 9.3, but might work with gcc >= 6"
            )
            sys.exit()


def get_compiler_flags(arch):
    """Check complier flags."""
    check_compiler(arch)
    compiler_flags = {}
    if arch == "gfortran-openmp":
        compiler_flags["Compiler"] = "gfortran"
        full_gfortran_path = which("gfortran")
        if full_gfortran_path == "":
            LOG.critical("No gfortran found in path.")
            sys.exit()

        gcc_bin_path = os.path.split(full_gfortran_path)[0]
        gcc_path = os.path.split(gcc_bin_path)[0]
        gcc_lib_path = os.path.join(gcc_path, "lib64")
        print(gcc_lib_path)
        gcc_gomp_path = os.path.join(
            glob(os.path.join(gcc_path, "lib", "gcc", "*", "*"))[0], "finclude"
        )
        if not os.path.exists(os.path.join(gcc_gomp_path, "omp_lib.mod")):
            LOG.critical(
                f"Can't find gomp in {gcc_gomp_path}. Correct GCC module loaded?"
            )
            sys.exit()

        compiler_flags["FC"] = "gfortran"
        compiler_flags["CC"] = "gcc"
        compiler_flags["CXX"] = "g++"
        compiler_flags["FCFLAGS1"] = (
            "-fimplicit-none -ffree-form -fPIC -fopenmp \
        -fno-second-underscore -frecord-marker=4 -std=f2008"
        )
        compiler_flags["FCFLAGS2"] = f" -lgomp -I{gcc_gomp_path} -L{gcc_lib_path}"
        compiler_flags["LDFLAGS"] = "-Wall -g -shared -lgomp"
        compiler_flags["F2PY_COMPILER"] = "gnu95"
        compiler_flags["omplib"] = "-lgomp"

    elif arch == "ifort-openmp":
        compiler_flags["Compiler"] = "ifort"
        full_ifort_path = which("ifort")
        if full_ifort_path == "":
            LOG.critical("No ifort found.")
            sys.exit()
        compiler_flags["FC"] = "ifort"
        compiler_flags["CC"] = "icc"
        compiler_flags["CXX"] = "icpc"
        compiler_flags["FCFLAGS1"] = (
            "-fopenmp -fPIC -O3 -fp-model source -free -assume byterecl,realloc_lhs"
        )
        compiler_flags["FCFLAGS2"] = " -liomp5"
        compiler_flags["LDFLAGS"] = "-Wall -g -liomp5"
        compiler_flags["F2PY_COMPILER"] = "intelem"
        compiler_flags["omplib"] = "-liomp5"
    else:
        LOG.critical(f"Unknown compiler {arch}.")
        sys.exit()
    return compiler_flags


def which(name):
    """Pull path for a given name."""
    for path in os.getenv("PATH").split(os.path.pathsep):
        full_path = f"{path}{os.sep}{name}"
        if os.path.exists(full_path):
            return full_path
    return ""


def get_mamba_env():
    """Find current mamba env."""
    mamba_py = which("python")
    if mamba_py == "":
        raise ValueError(f"Conda env not installed with python {mamba_py}")

    mamba_dir = os.path.dirname(mamba_py) + "/../"
    mamba_path = os.path.abspath(mamba_dir)
    return mamba_path
