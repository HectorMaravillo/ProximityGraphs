"""Rotation transformation for point sets."""

import numpy as np


def rotation(self, angle, degree=True):
    """
    Applies a 2D rotation to the set of points around the origin (0,0).

    This method rotates the points counter-clockwise by a given angle `theta`.
    The transformation is only defined for 2D points (i.e., `self.dim` must be 2).

    The rotation is achieved by applying an affine transformation with a specific
    rotation matrix and no translation. The 2D counter-clockwise rotation matrix is:
      M = [[cos(theta),  sin(theta)],
           [-sin(theta), cos(theta)]]
    If `P_i = (x_i, y_i)` is an original point, the rotated point
    `P'_i = (x'_i, y'_i)` is calculated as:
      x'_i = x_i * cos(theta) - y_i * sin(theta)
      y'_i = x_i * sin(theta) + y_i * cos(theta)

    This corresponds to `P' = P @ M.T`
    if using row vectors for points, or `P' = M @ P` if using column vectors.
    The code implements `P @ matrix` where `matrix` is as defined above.

    Parameters:
    ----------
    angle : float
        The angle of rotation.
    degree : bool, optional
        If True (default), the `angle` is interpreted as degrees and will be
        converted to radians. If False, the `angle` is interpreted as radians.

    Returns:
    -------
    SetPoints
        A new SetPoints object containing the rotated points.

    Raises:
    ------
    ValueError
        If the dimension of the points is not 2.
    """
    if self.dim != 2:
        raise ValueError("Rotation is only implemented for 2D points.")
    if degree:
        angle = np.radians(angle)
    cos = np.cos(angle)
    sin = np.sin(angle)
    matrix = np.matrix([[cos, sin], [-sin, cos]])
    return self._affin_transformation(matrix)
