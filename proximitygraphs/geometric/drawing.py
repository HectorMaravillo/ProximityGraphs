"""Drawing functions attached to ``GeometricGraph``."""

import warnings

import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.pyplot import subplots


def draw_orientation(
    self,
    num_bins: int = 36,
    figsize: tuple[int, int] = (5, 5),
    color: str = "darkgreen",
    area: bool = False,
    component: str = "auto",
):
    """
    Draw a polar histogram of edge orientations.

    Parameters
    ----------

    num_bins : int, optional
        Number of bins in the histogram. Default 36 (10 degree bins).
    figsize : tuple of (float, float), optional
        Figure size in inches. Default (5, 5).
    color : str, optional
        Color for the bars in the histogram. Default "darkgreen".
    area : bool, optional
        If True, bar lengths are proportional to bin frequencies (area encoding).
        If False, bar lengths are proportional to the square root of frequencies
        (radius encoding). Default False.
    component : str, optional
        If orientation has 2 components, which to plot: "azimuth", "elevation
        or "auto". If "auto", plots azimuth if available, otherwise elevation.
        Default "auto". Ignored if orientation has 1 component or if orientation
        data is missing.

    Returns
    -------
    (fig, ax) : tuple
        Matplotlib figure and axes with the polar histogram.

    Notes
    -----
    - If orientation data is missing or has an unexpected shape,
        a warning is issued and an empty polar plot is returned.
    - If all bins are empty, a warning is issued and an empty polar plot is returned.
    """
    orientation = self.orientation
    if orientation.ndim == 1:
        angles = orientation
    elif orientation.ndim == 2 and orientation.shape[1] == 2:
        if component == "auto":
            component = "azimuth"
        comp_idx = {"azimuth": 0, "elevation": 1}.get(component)
        if comp_idx is None:
            raise ValueError(
                "component must be 'azimuth', 'elevation' or 'auto' "
                f"(received {component!r})"
            )
        angles = orientation[:, comp_idx]
        if component == "elevation":
            angles = (angles + 90) % 180
    else:
        msg = (
            f"Orientation array has unexpected shape {orientation.shape}; cannot plot."
        )
        warnings.warn(
            msg,
            stacklevel=2,
        )
        return None, None

    if angles.size == 0:
        warnings.warn("No orientation data to plot for draw_orientation.", stacklevel=2)
        fig, ax = subplots(figsize=figsize, subplot_kw={"projection": "polar"})
        ax.set_title("Edge orientation distribution (No data)")
        return fig, ax

    angles_doubled = (angles + 180) % 360
    angles_all = np.concatenate((angles, angles_doubled), axis=0)

    bin_counts, bin_edges = np.histogram(angles_all, range=(0, 360), bins=num_bins)
    if bin_counts.sum() == 0:
        warnings.warn("All bin counts are zero in draw_orientation.", stacklevel=2)
        fig, ax = subplots(figsize=figsize, subplot_kw={"projection": "polar"})
        ax.set_title("Edge orientation distribution (All bins empty)")
        return fig, ax

    bin_freq = bin_counts / bin_counts.sum()
    radius = np.sqrt(bin_freq) if area else bin_freq
    width = 2 * np.pi / num_bins
    positions = np.radians(bin_edges[:-1])
    fig, ax = subplots(figsize=figsize, subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction("clockwise")
    ax.set_ylim(top=radius.max() if radius.size > 0 else 1.0)
    ax.set_yticks(np.linspace(0, ax.get_ylim()[1], 5))
    ax.set_yticklabels(labels="")
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(["N", "", "E", "", "S", "", "W", ""])
    ax.tick_params(axis="x", which="major", pad=-2)
    ax.bar(
        positions,
        height=radius,
        width=width,
        align="center",
        bottom=0,
        zorder=2,
        color=color,
        edgecolor="black",
        linewidth=0.5,
        alpha=0.7,
    )
    ax.set_title(
        f"Edge {component} distribution"
        if orientation.ndim == 2
        else "Edge orientation distribution"
    )
    return fig, ax


def draw(
    self,
    figsize=(6, 6),
    v_size=3,
    v_color="#00072D",
    v_alpha=1,
    e_size=1,
    e_color="#0A2472",
    e_alpha=1,
    title=True,
    fontsize=10,
    details=False,
    axis=False,
    save=None,
    transparent=True,
    *,
    ax=None,
    fig_kwargs=None,
    v_kwargs=None,
    e_kwargs=None,
    title_kwargs=None,
    savefig_kwargs=None,
):
    """
    Draws the geometric graph using Matplotlib.

    Parameters
    ----------
    figsize : tuple of (float, float), optional
        Figure size in inches. Default ``(15, 15)``.
    v_size : float, optional
        Marker size for vertices. ``0`` disables vertex scatter. Default 5.
    v_color : str, optional
        Vertex color passed to Matplotlib. Default ``"black"``.
    v_alpha : float, optional
        Vertex alpha level between 0 (transparent) and 1 (opaque).
        Default 1.
    e_size : float, optional
        Line width for boundary edges. Default 1.
    e_color : str, optional
        Color for boundary edges. Default ``"black"``.
    e_alpha : float, optional
        Edge alpha level between 0 (transparent) and 1 (opaque).
        Default 1.
    title : bool, optional
        Whether to set a title. Default True.
    fontsize : float, optional
        Title font size. Default 12.
    details : bool, optional
        If True, appends ``details`` to the title. Default False.
    axis : bool, optional
        If True, show axes. Default False.
    save : str or None, optional
        If set, saves a ``.png`` at ``save + ".png"``.
        If ``None``, returns the live figure and axes. Default ``None``.
    transparent : bool, optional
        If True and ``save`` is set, saves the PNG with a transparent
        background. Default False.

    Other Parameters
    ----------------
    fig_kwargs : dict, optional
        Extra keyword arguments passed to ``matplotlib.pyplot.subplots``.
    v_kwargs : dict, optional
        Extra keyword arguments passed to ``ax.scatter`` (vertex scatter).
        These override ``v_size``, ``v_color``, ``v_alpha`` if duplicated.
    e_kwargs : dict, optional
        Extra keyword arguments passed to ``matplotlib.collections.LineCollection``.
        These override ``e_size``, ``e_color``, ``e_alpha`` if duplicated.
    title_kwargs : dict, optional
        Extra keyword arguments passed to ``ax.set_title``.
        These override ``fontsize`` if duplicated.
    savefig_kwargs : dict, optional
        Extra keyword arguments passed to ``matplotlib.pyplot.savefig``.

    Returns
    -------
    (fig, ax) : tuple
        Matplotlib figure and axes.
    """
    fig_kwargs = {} if fig_kwargs is None else dict(fig_kwargs)
    v_kwargs = {} if v_kwargs is None else dict(v_kwargs)
    e_kwargs = {} if e_kwargs is None else dict(e_kwargs)
    title_kwargs = {} if title_kwargs is None else dict(title_kwargs)
    savefig_kwargs = {} if savefig_kwargs is None else dict(savefig_kwargs)

    # figure and axes
    if ax is None:
        fig, ax = subplots(figsize=figsize, **fig_kwargs)
    else:
        fig = ax.figure

    # vertices
    if self.n > 0 and v_size > 0:
        scatter_kwargs = {"s": v_size, "c": v_color, "alpha": v_alpha}
        scatter_kwargs.update(v_kwargs)  # user overrides defaults
        ax.scatter(self.points[:, 0], self.points[:, 1], **scatter_kwargs)

    # boundary edges
    edges = self.graph.get_edgelist() if hasattr(self, "graph") else []
    if edges:
        segs = np.array(
            [[self.points[i], self.points[j]] for (i, j) in edges], dtype=float
        )
        line_kwargs = {"linewidths": e_size, "colors": e_color, "alpha": e_alpha}
        line_kwargs.update(e_kwargs)  # user overrides defaults
        lc = LineCollection(segs, **line_kwargs)
        ax.add_collection(lc)

    # title
    if title:
        plot_title = self.name
        if details and getattr(self, "details", None):
            plot_title += f"\n{self.details}"
        title_args = {"fontsize": fontsize}
        title_args.update(title_kwargs)
        ax.set_title(plot_title, **title_args)

    # axes
    if not axis:
        ax.set_axis_off()
    else:
        ax.set_axis_on()
    ax.set_aspect("equal", adjustable="box")

    # save or return
    if save is None:
        return fig, ax
    else:
        savefig_args = {"bbox_inches": "tight", "transparent": transparent}
        savefig_args.update(savefig_kwargs)
        fig.savefig(save + ".png", **savefig_args)
        fig.canvas.draw_idle()
        return fig, ax
