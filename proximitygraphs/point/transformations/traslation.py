"""Translation transformation for point sets."""

import numpy as np


def traslation(self, c):
    """
    Applies a translation to the set of points.

    This method shifts all points in the set by a given vector `c`.
    It's an affine transformation where the linear transformation matrix `M` is
    the identity matrix, and the translation vector is `c`.
    The transformation is: `P' = P + c_broadcasted`.
    For each point `P_i` in the set `P`, the new point `P'_i` is:
      `P'_i = P_i + c`

    If `c` is a scalar, it is treated as a vector where all components are equal
    to `c`. For example, if `dim=3` and `c=5`, the translation vector is `(5,5,5)`.

    Parameters:
    ----------
    c : float or array-like
        The translation vector or scalar.
        If a scalar (float), all dimensions are translated by this value.
        If an array-like (e.g., list, tuple, numpy.ndarray) of length `self.dim`,
        each dimension `j` is translated by the corresponding element `c_j`.

    Returns:
    -------
    SetPoints
        A new SetPoints object containing the translated points.

    Raises:
    ------
    ValueError
        If `c` is an array-like and its shape is not `(self.dim,)`.
    """
    if np.isscalar(c):
        c = np.full(self.dim, c)
    else:
        c = np.asarray(c)
        if c.shape != (self.dim,):
            raise ValueError(
                f"Translation vector must have shape ({self.dim},), but got {c.shape}"
            )

    return self._affin_transformation(c=c)
