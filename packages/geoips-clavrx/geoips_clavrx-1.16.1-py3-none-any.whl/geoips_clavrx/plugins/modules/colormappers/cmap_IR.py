# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Colormap for IR Brightness Temperatures."""
import logging

LOG = logging.getLogger(__name__)

interface = "colormappers"
family = "matplotlib"
name = "cmap_IR"


def call(data_range=[180, 340]):
    """Brightness Temperatures Colormap for IR frequency channel data.

    Parameters
    ----------
    data_range : list of float, default=[180, 340]
        Min and max value for colormap.
        Ensure the data range matches the range of the algorithm specified
        for use with this colormap
        The cloud top temperature MUST include 180 and 300 (k)

    Returns
    -------
    mpl_colors_info : dict
        Dictionary of matplotlib plotting parameters, to ensure consistent image output
    """
    min_val = data_range[0]
    max_val = data_range[1]

    if min_val > 180 or max_val < 300:
        raise ("IR temperature range MUST include 180 and 300")

    from geoips.image_utils.colormap_utils import create_linear_segmented_colormap

    transition_vals = [
        (min_val, 190),
        (190, 200),
        (200, 210),
        (210, 220),
        (220, 240),
        (240, 260),
        (260, 280),
        (280, 300),
        (300, max_val),
    ]
    transition_colors = [
        ("darkorange", "yellow"),
        ("darkred", "red"),
        ("green", "palegreen"),
        ("navy", "deepskyblue"),
        ("#FFFFCC", "#CCFFCC"),
        ("whitesmoke", "silver"),
        ("silver", "grey"),
        ("grey", "dimgrey"),
        ("dimgrey", "black"),
    ]

    # ticks = [xx[0] for xx in transition_vals]

    # special selection of label

    ticks = [180, 190, 200, 210, 220, 240, 260, 280, 300, 340]

    # selection of min and max values for colormap if needed
    min_val = transition_vals[0][0]
    max_val = transition_vals[-1][1]

    LOG.info("Setting cmap")
    mpl_cmap = create_linear_segmented_colormap(
        "cmap_IR", min_val, max_val, transition_vals, transition_colors
    )

    LOG.info("Setting norm")
    from matplotlib.colors import Normalize

    mpl_norm = Normalize(vmin=min_val, vmax=max_val)

    cbar_label = "Brightness Temperature (K)"

    # Must be uniform or proportional, None not valid for Python 3
    cbar_spacing = "proportional"
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

    return mpl_colors_info
