"""Scaling transformation for point sets."""

import numpy as np


def scaling(self, scale):
    """
    Applies a scaling transformation to the set of points, relative to the origin.

    This method scales the coordinates of each point. The scaling can be uniform
    across all dimensions (if `scale` is a scalar) or different for each
    dimension (if `scale` is a vector).

    The transformation is an affine transformation `P' = P @ M`, where `M` is a
    diagonal matrix.
    If `scale` is a scalar `s`, then `M` is `s * I`, where `I` is the identity
    matrix. Each coordinate of each point is multiplied by `s`.
      `p'_j = p_j * s` for each coordinate `j`.
    If `scale` is a vector `(s_0, s_1, ..., s_{dim-1})`, then `M` is a diagonal
    matrix with these scaling factors on its diagonal:
      M = [[s_0,   0, ...,   0],
           [  0, s_1, ...,   0],
           [  ..., ..., ..., ...],
           [  0,   0, ..., s_{dim-1}]]
    Each coordinate `j` of a point `p` is multiplied by the corresponding
    scaling factor `s_j`:
      `p'_j = p_j * s_j`.

    The scaling is performed relative to the origin (0,0,...,0).

    Parameters:
    ----------
    scale : float or array-like
        The scaling factor(s).
        If a scalar (float), all dimensions are scaled by this factor.
        If an array-like (e.g., list, tuple, numpy.ndarray) of length `self.dim`,
        each dimension is scaled by the corresponding element in the array.

    Returns:
    -------
    SetPoints
        A new SetPoints object containing the scaled points.

    Raises:
    ------
    ValueError
        If `scale` is an array-like and its shape is not `(self.dim,)`.
    """
    if np.isscalar(scale):
        scale = np.full(self.dim, scale)

    scale = np.asarray(scale)
    if scale.shape != (self.dim,):
        raise ValueError(
            f"Scale vector must have shape ({self.dim},), but got {scale.shape}"
        )

    matrix = np.diag(scale)
    return self._affin_transformation(matrix=matrix)
