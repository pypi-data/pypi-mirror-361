# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Module containing colormap for effective radius of cloud particles product."""
import logging

LOG = logging.getLogger(__name__)

interface = "colormappers"
family = "matplotlib"
name = "cmap_cldReff"


def call(data_range=[0, 160]):
    """Cloud Particle Effective Radius Colormap.

    Parameters
    ----------
    data_range : list of float, default=[0, 160]
        Min and max value for colormap.
        Ensure the data range matches the range of the algorithm specified
        for use with this colormap

    Returns
    -------
    mpl_colors_info : dict
        Dictionary of matplotlib plotting parameters, to ensure consistent image output
    """
    min_val = data_range[0]
    max_val = data_range[1]

    if min_val > 1 or max_val < 150:
        raise ("effective radius of cloud particles MUST include 1 and 150")

    from geoips.image_utils.colormap_utils import create_linear_segmented_colormap

    transition_vals = [
        (min_val, 5),
        (5, 10),
        (10, 15),
        (15, 20),
        (25, 30),
        (30, 40),
        (40, 50),
        (50, 100),
        (100, max_val),
    ]
    transition_colors = [
        ("white", "lightgray"),
        ("oldlace", "moccasin"),
        ("#F4CD03", "#F2F403"),
        ("#8CF303", "#0FB503"),
        ("#06DCFD", "#0708B5"),
        ("#FFFFCC", "#CCFFCC"),
        ("#CCFFCC", "#6666FF"),
        ("#CC99FF", "#FF99CC"),
        ("red", "black"),
    ]

    # ticks = [xx[0] for xx in transition_vals]

    # special selection of label

    ticks = [0, 10, 20, 30, 40, 50, 75, 100, 120, 160]

    # selection of min and max values for colormap if needed
    min_val = transition_vals[0][0]
    max_val = transition_vals[-1][1]

    LOG.info("Setting cmap")
    mpl_cmap = create_linear_segmented_colormap(
        "cmap_cldReff", min_val, max_val, transition_vals, transition_colors
    )

    LOG.info("Setting norm")
    from matplotlib.colors import Normalize

    mpl_norm = Normalize(vmin=min_val, vmax=max_val)

    cbar_label = "Effective Radius"

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
