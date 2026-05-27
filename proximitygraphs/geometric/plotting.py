"""Convenience plotting helpers for collections of graphs."""

from matplotlib.pyplot import subplots


def _unwrap_singleton(x):
    # unwrap (obj,) or [obj]
    if isinstance(x, (tuple, list)) and len(x) == 1:
        return x[0]
    return x


def draw_grid(
    graphs,
    nrows,
    ncols,
    *,
    figsize=None,
    constrained_layout=True,
    hide_unused=True,
    **draw_kwargs,
):
    """
    Draw a list of graph objects into an (nrows x ncols) matplotlib subplot grid.

    Parameters
    ----------
    graphs : list
        List of objects exposing .draw(ax=..., **draw_kwargs).
    nrows, ncols : int
        Grid shape.
    figsize : tuple or None
        Passed to plt.subplots.
    constrained_layout : bool
        Passed to plt.subplots.
    hide_unused : bool
        If graphs < nrows*ncols, hide remaining axes.
    draw_kwargs : dict
        Forwarded to each graph.draw(...).

    Returns
    -------
    (fig, axs)
    """

    fig, axs = subplots(
        nrows, ncols, figsize=figsize, constrained_layout=constrained_layout
    )

    axs_flat = axs.flat  # works for (nrows,ncols) and for 1D cases

    for ax, G in zip(axs_flat, graphs, strict=False):
        G = _unwrap_singleton(G)
        if not hasattr(G, "draw"):
            raise TypeError(
                f"Each item must have a .draw(...). Got {type(G)} after unwrapping."
            )
        G.draw(ax=ax, **draw_kwargs)

    if hide_unused:
        for ax in axs_flat:
            ax.set_visible(False)

    return fig, axs
