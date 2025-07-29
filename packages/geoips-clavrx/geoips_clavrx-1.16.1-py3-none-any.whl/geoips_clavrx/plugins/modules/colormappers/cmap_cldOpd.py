# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Module containing colormap for satellite cloud optical depth products."""
import logging

LOG = logging.getLogger(__name__)

interface = "colormappers"
family = "matplotlib"
name = "cmap_cldOpd"


def call(data_range=[-0.2, 8]):
    """Cloud Optical Depth Colormap.

    Parameters
    ----------
    data_range : list of float, default=[-0.2, 8]
        Min and max value for colormap.
        Ensure the data range matches the range of the algorithm specified
        for use with this colormap.
        CldPhase=0(clear),1(water),2(supercooled),3(mixed),4(ice),5(unknown)

    Returns
    -------
    mpl_colors_info : dict
        Dictionary of matplotlib plotting parameters, to ensure consistent image output
    """
    min_val = data_range[0]
    max_val = data_range[1]
    if min_val >= 1 or max_val <= 6:
        raise ("cloud OPD must at least gave a range of 0 - 6")
    ticks = [min_val, 0, 1, 2, 3, 4, 5, 6, 7, max_val]
    colorlist = [
        "ghostwhite",
        "slategray",
        "blue",
        "royalblue",
        "cyan",
        "green",
        "yellow",
        "lightsalmon",
        "red",
        "black",
    ]

    from matplotlib.colors import BoundaryNorm, ListedColormap

    mpl_cmap = ListedColormap(colorlist, N=len(colorlist))

    LOG.info("Setting norm")
    bounds = ticks + [max_val + 1]
    mpl_norm = BoundaryNorm(bounds, mpl_cmap.N)

    cbar_label = r"Cloud OPD"

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = "uniform"  # for discrete bounds of a  color bar
    mpl_tick_labels = None
    mpl_boundaries = None

    # from geoips.image_utils.mpl_utils import create_colorbar
    # only create colorbar for final imagery
    # cbar = create_colorbar(fig, mpl_cmap, mpl_norm, ticks, cbar_label=cbar_label)
    mpl_colors_info = {
        "cmap": mpl_cmap,
        "norm": mpl_norm,
        "cbar_ticks": ticks,
        "cbar_tick_labels": mpl_tick_labels,
        "cbar_label": cbar_label,
        "boundaries": mpl_boundaries,
        "cbar_spacing": cbar_spacing,
        "colorbar": True,
        "cbar_full_width": True,
    }

    # return cbar, min_val, max_val
    return mpl_colors_info
