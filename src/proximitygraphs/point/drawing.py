"""Drawing function attached to ``SetPoints``."""

from matplotlib.pyplot import savefig, subplots


def draw(
    self,
    figsize=(6, 6),
    v_size=8,
    v_color="#00072D",
    v_alpha=1,
    title=True,
    fontsize=10,
    details=False,
    axis=False,
    save=None,
    *,
    fig_kwargs=None,
    v_kwargs=None,
    title_kwargs=None,
    savefig_kwargs=None,
):
    """
    Draws 2D points using Matplotlib.

    Parameters
    ----------
    figsize : tuple of (float, float), optional
        Figure size in inches. Default (6, 6).
    v_size : float, optional
        Marker size for points. 0 disables scatter. Default 3.
    v_color : str, optional
        Point color passed to Matplotlib. Default "#00072D".
    v_alpha : float, optional
        Point alpha (transparency) in [0,1]. Default 1.
    title : bool, optional
        Whether to set a title. Default True.
    fontsize : float, optional
        Title font size. Default 10.
    details : bool, optional
        If True, appends self.details to the title (if present). Default False.
    axis : bool, optional
        If True, show axes. Default False.
    save : str or None, optional
        If set, saves a ".png" at save + ".png". If None, returns (fig, ax).

    Other Parameters
    ----------------
    fig_kwargs : dict, optional
        Extra keyword arguments passed to matplotlib.pyplot.subplots.
    v_kwargs : dict, optional
        Extra keyword arguments passed to ax.scatter.
        These override v_size, v_color, v_alpha if duplicated.
    title_kwargs : dict, optional
        Extra keyword arguments passed to ax.set_title.
        These override fontsize if duplicated.
    savefig_kwargs : dict, optional
        Extra keyword arguments passed to matplotlib.pyplot.savefig.

    Returns
    -------
    (fig, ax) : tuple
        Matplotlib figure and axes.
    """
    fig_kwargs = {} if fig_kwargs is None else dict(fig_kwargs)
    v_kwargs = {} if v_kwargs is None else dict(v_kwargs)
    title_kwargs = {} if title_kwargs is None else dict(title_kwargs)
    savefig_kwargs = {} if savefig_kwargs is None else dict(savefig_kwargs)

    # enforce 2D
    if not hasattr(self, "points"):
        raise AttributeError("Object has no attribute 'points'")
    if self.points.ndim != 2 or self.points.shape[1] != 2:
        raise ValueError(
            "draw() is 2D-only: expected points with shape (n, 2); got "
            f"{self.points.shape}"
        )

    # figure and axes (same as geometric graphs)
    fig, ax = subplots(figsize=figsize, **fig_kwargs)

    # points (same naming as vertices)
    if self.points.shape[0] > 0 and v_size > 0:
        scatter_kwargs = {
            "s": v_size,
            "c": v_color,
            "alpha": v_alpha,
            "linewidths": 0,  # no outline
            "edgecolors": "none",  # no outline
        }
        scatter_kwargs.update(v_kwargs)  # user overrides defaults
        ax.scatter(self.points[:, 0], self.points[:, 1], **scatter_kwargs)

    # title (same logic as geometric graphs)
    if title:
        plot_title = getattr(self, "name", self.__class__.__name__)
        if details and getattr(self, "details", None):
            plot_title += f"\n{self.details}"
        title_args = {"fontsize": fontsize}
        title_args.update(title_kwargs)
        ax.set_title(plot_title, **title_args)

    # axes (same as geometric graphs)
    if not axis:
        ax.set_axis_off()
    else:
        ax.set_axis_on()
    ax.set_aspect("equal", adjustable="box")

    # save or return (same as geometric graphs)
    if save is None:
        return fig, ax
    else:
        savefig(save + ".png", bbox_inches="tight", **savefig_kwargs)
        return fig, ax
