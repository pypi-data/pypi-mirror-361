    # # # This source code is subject to the license referenced at
    # # # https://github.com/NRLMMD-GEOIPS.

CLAVR-x GeoIPS Plugin Package
=============================

The geoips_clavrx package is a GeoIPS-compatible plugin, intended to be used
within the GeoIPS ecosystem.
Please see the
[GeoIPS Documentation](https://github.com/NRLMMD-GEOIPS/geoips#readme)
for more information on the GeoIPS plugin architecture and base infrastructure.

Package Overview
----------------

The geoips_clavrx package provides the capability for reading and plotting
data files produced from the Clouds for AVHRR Extended package.

This package does not currently include installation of clavrx itself, but
expects you are able to produce CLAVR-x outputs for ingest into geoips_clavrx.

System Requirements
-------------------

* geoips >= 1.10.2
* Test data repos contained in $GEOIPS_TESTDATA_DIR for tests to pass.

IF REQUIRED: Install base geoips package
----------------------------------------
SKIP IF YOU HAVE ALREADY INSTALLED BASE GEOIPS ENVIRONMENT

If GeoIPS Base is not yet installed, follow the
[installation instructions](https://github.com/NRLMMD-GEOIPS/geoips#installation)
within the geoips source repo documentation.

Install geoips_clavrx package
-----------------------------
```bash

    # Ensure GeoIPS Python environment is enabled.

    git clone https://github.com/NRLMMD-GEOIPS/geoips_clavrx $GEOIPS_PACKAGES_DIR/geoips_clavrx
    pip install -e $GEOIPS_PACKAGES_DIR/geoips_clavrx
    create_plugin_registries
```

Install CLAVR-x and required dependencies
-----------------------------------------

Follow installation of full pipeline on the 
[CLAVRx pipeline](./geoips_clavrx/README.md) docs



Install CLAVR-x and required dependencies
-----------------------------------------

Follow installation of full pipeline on the 
[CLAVRx pipeline](./geoips_clavrx/README.md) docs



Test geoips_clavrx installation
-------------------------------
```bash

    # Ensure GeoIPS Python environment is enabled.

    # Install the clavrx test data repo
    $GEOIPS_PACKAGES_DIR/geoips/setup/check_system_requirements.sh test_data test_data_clavrx

    # Run all tests
    $GEOIPS_PACKAGES_DIR/geoips_clavrx/tests/test_all.sh
```
