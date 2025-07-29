# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Change config file based on user input."""

import configparser

# Once inside directory containing user_change_me.cfg file


def user_change_me(
    gfortran_path,
    gcc_path,
    hdf4_path,
    hdf5_path,
    netcdf_path,
    himawari_path,
    rttov_path,
):
    """Modify configuration based on user input."""
    config = configparser.ConfigParser(delimiters=":", comment_prefixes="#")
    config.read("user_change_me.cfg")

    config.remove_option("Modules To Load", "Modules to (un)load (in order)")
    config.set(
        "Capabilities Which Require Special External Libraries",
        "NWP input can be in GRIB format?",
        "no",
    )
    config.set(
        "Capabilities Which Require Special External Libraries",
        "Use libHimawari (needed for HSD-format files only)?",
        "yes",
    )
    config.set(
        "Capabilities Which Require Special External Libraries",
        "Use RTTOV (radiative transfer code/data) when possible?",
        "yes",
    )
    config.set(
        "Capabilities Which Require Special External Libraries",
        "Use CRTM (radiative transfer code/data) when possible?",
        "no",
    )

    config.set("Preferred Compilers", "Fortran compiler", gfortran_path)
    config.set("Preferred Compilers", "C compiler", gcc_path)

    config.set(
        "Compiler/Linker Options For Debugging",
        "F preprocessor options (e.g. -D and -I)",
        f"-I{netcdf_path}/include -I{hdf4_path}/include -I{hdf5_path}/include",
    )
    config.set(
        "Compiler/Linker Options For Debugging",
        "F linker options (e.g. -L, -l)",
        f"-L{netcdf_path}/lib -L{hdf4_path}/lib -L{hdf5_path}/lib",
    )
    config.set(
        "Compiler/Linker Options For Debugging",
        "C preprocessor options (e.g. -D and -I)",
        f"-I{netcdf_path}/include -I{hdf4_path}/include -I{hdf5_path}/include",
    )
    config.set(
        "Compiler/Linker Options For Debugging",
        "C linker options (e.g. -L, -l)",
        f"-L{netcdf_path}/lib -L{hdf4_path}/lib -L{hdf5_path}/lib",
    )

    config.set(
        "Compiler/Linker Options For Production Use",
        "F preprocessor options (e.g. -D and -I)",
        f"-I{netcdf_path}/include -I{hdf4_path}/include -I{hdf5_path}/include",
    )
    config.set(
        "Compiler/Linker Options For Production Use",
        "F linker options (e.g. -L, -l)",
        f"-L{netcdf_path}/lib -L{hdf4_path}/lib -L{hdf5_path}/lib",
    )
    config.set(
        "Compiler/Linker Options For Production Use",
        "C preprocessor options (e.g. -D and -I)",
        f"-I{netcdf_path}/include -I{hdf4_path}/include -I{hdf5_path}/include",
    )
    config.set(
        "Compiler/Linker Options For Production Use",
        "C linker options (e.g. -L, -l)",
        f"-L{netcdf_path}/lib -L{hdf4_path}/lib -L{hdf5_path}/lib",
    )

    config.set(
        "Specs, libHimawari",
        "F include dirs",
        f"{himawari_path}/himawari/include {himawari_path}/himawari/src",
    )
    config.set("Specs, libHimawari", "F library dirs", f"{himawari_path}/himawari/src")
    config.set(
        "Specs, libHimawari",
        "F linker options (e.g. libraries)",
        f"-Wl,-rpath,{himawari_path}/himawari/src -lHimawari",
    )

    config.set(
        "Specs, RTTOV", "F include dirs", f"{rttov_path}/include {rttov_path}/mod"
    )
    config.set("Specs, RTTOV", "F library dirs", f"{rttov_path}/lib")
    config.set(
        "Specs, RTTOV",
        "F linker options (e.g. libraries)",
        "-lrttov_brdf_atlas -lrttov_emis_atlas -lrttov_mw_scatt -lrttov_other \
        -lrttov_coef_io -lrttov_parallel -lrttov_hdf -lrttov_main",
    )

    config.set("Specs, HDF4", "F include dirs", f"{hdf4_path}/include")
    config.set("Specs, HDF4", "F library dirs", f"{hdf4_path}/lib")
    config.set("Specs, HDF4", "F linker options", "-lmfhdf -ldz -ljpeg")

    config.set("Specs, HDF5", "F include dirs", f"{hdf5_path}/include")
    config.set("Specs, HDF5", "F library dirs", f"{hdf5_path}/lib")
    config.set(
        "Specs, HDF5",
        "F linker options",
        "-lhdf5_fortran -lhdf5hl_fortran -lhdf5_hl -lhdf5 -lz",
    )
    config.set("Specs, HDF5", "C include dirs", f"{hdf5_path}/include")
    config.set("Specs, HDF5", "C library dirs", f"{hdf5_path}/lib")
    config.set(
        "Specs, HDF5", "C linker options (e.g. libraries)", "-lhdf5_hl -lhdf5 -lz"
    )

    config.set("Specs, NetCDF", "F include dirs", f"{netcdf_path}/include")
    config.set("Specs, NetCDF", "F library dirs", f"{netcdf_path}/lib")
    config.set("Specs, NetCDF", "F linker options", "-lnetcdff -lnetcdf")
    config.set("Specs, NetCDF", "C include dirs", f"{netcdf_path}/include")
    config.set("Specs, NetCDF", "C library dirs", f"{netcdf_path}/lib")
    config.set("Specs, NetCDF", "C linker options (e.g. libraries)", "-lnetcdf")

    with open("user_change_me.cfg", "w") as file:
        config.write(file)
