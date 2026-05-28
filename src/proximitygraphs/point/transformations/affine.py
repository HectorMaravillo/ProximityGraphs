"""General affine transformation helper."""

import numpy as np


def _affin_transformation(self, matrix=None, c=None):
    """
    Applies a general affine transformation to the set of points.

    An affine transformation combines a linear transformation (like rotation,
    scaling, or shear) and a translation. If `P` is the original `n x dim` matrix
    of points (where `n` is the number of points and `dim` is their dimension),
    `M` is a `dim x dim` transformation matrix, and `t` is a `1 x dim` translation
    vector, the new set of points `P'` is computed as:

    `P'_i = P_i @ M + t` for each point `P_i` (row in `P`).

    Or, in matrix form for all points:
    `P' = P @ M + t_broadcasted`
    where `t_broadcasted` is the translation vector `t` broadcasted to apply
    to each row of `P @ M`.

    This method is a general helper used by more specific transformations like
    rotation, scaling, and translation.

    Parameters:
    ----------
    matrix : numpy.ndarray, optional
        The `dim x dim` linear transformation matrix. If None, an identity matrix
        of the appropriate dimension is used (implying no linear transformation).
        Defaults to None.
    c : numpy.ndarray, optional
        The `1 x dim` translation vector. If None, a zero vector is used
        (implying no translation). Defaults to None.

    Returns:
    -------
    SetPoints
        A new SetPoints object containing the transformed points.
    """
    if matrix is None:
        matrix = np.eye(self.dim)
    if c is None:
        c = np.zeros(self.dim)

    matrix = np.asarray(matrix)
    c = np.asarray(c)
    trasnformation = self.points @ matrix + c
    return self.__class__(np.asanyarray(trasnformation))
