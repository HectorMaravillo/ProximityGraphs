"""Analysis and cached attribute functions attached to ``GeometricGraph``."""

import warnings

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import entropy as scipy_entropy


def copy(self):
    """Return a copy of the GeometricGraph instance."""
    new_setpoints = self.setpoints.copy()
    new_graph_instance = self.__class__.__new__(self.__class__)
    new_graph_instance._GeometricGraph__setpoints = new_setpoints
    new_graph_instance._GeometricGraph__graph = self.graph.copy()
    new_graph_instance._GeometricGraph__m = self.m
    new_graph_instance._GeometricGraph__name = self.name
    new_graph_instance._GeometricGraph__details = self.details
    return new_graph_instance


def _GeometricGraph__size(self):
    self._GeometricGraph__m = self._GeometricGraph__graph.ecount()
    return self._GeometricGraph__m


def _GeometricGraph__add_lengths(self):
    if self.m > 0:
        edges = np.array(self.graph.get_edgelist())
        points_for_calc = self.points
        if points_for_calc.ndim == 1:
            pass
        edges_pos_x = points_for_calc[edges[:, 0]]
        edges_pos_y = points_for_calc[edges[:, 1]]
        length = np.linalg.norm(edges_pos_x - edges_pos_y, axis=1)
        self.graph.es["dist_eucl"] = length
    else:
        self.graph.es["dist_eucl"] = []


def _GeometricGraph__add_orientation(self):
    if self.m == 0:
        return np.array([])
    calculated_orientations = np.array([])
    try:
        edges = self.graph.get_edgelist()
        if not edges:
            return np.array([])
        points_arr = self.points
        if (
            not isinstance(points_arr, np.ndarray)
            or points_arr.ndim < 2
            or points_arr.shape[0] < 2
            or points_arr.shape[1] < 2
        ):
            warnings.warn(
                "Orientation calculation requires a NumPy array of at least 2"
                "points in at least 2 dimensions.",
                stacklevel=2,
            )
            return np.array([])
        dim = points_arr.shape[1]
        coords_u = points_arr[np.array(edges)[:, 0]]
        coords_v = points_arr[np.array(edges)[:, 1]]
        if dim == 2:
            dx = coords_v[:, 0] - coords_u[:, 0]
            dy = coords_v[:, 1] - coords_u[:, 1]
            ang = np.degrees(np.arctan2(dy, dx))
            calculated_orientations = np.mod(ang, 360)
        elif dim == 3:
            dx = coords_v[:, 0] - coords_u[:, 0]
            dy = coords_v[:, 1] - coords_u[:, 1]
            dz = coords_v[:, 2] - coords_u[:, 2]
            azimuth = np.mod(np.degrees(np.arctan2(dy, dx)), 360)
            horiz_len = np.hypot(dx, dy)
            elevation = np.full_like(dz, 0.0, dtype=float)
            non_vertical_mask = horiz_len != 0
            elevation[non_vertical_mask] = np.degrees(
                np.arctan2(dz[non_vertical_mask], horiz_len[non_vertical_mask])
            )
            vertical_mask = horiz_len == 0
            elevation[vertical_mask] = np.copysign(90.0, dz[vertical_mask])
            calculated_orientations = np.column_stack((azimuth, elevation))
        else:
            msg = (
                "Orientation is defined only for 2-D or 3-D layouts "
                f"(received {dim}-D). No values were written."
            )
            warnings.warn(
                msg,
                stacklevel=2,
            )
        if calculated_orientations.size > 0 and hasattr(self.graph, "es"):
            self.graph.es["orientation"] = calculated_orientations.tolist()
        return calculated_orientations
    except Exception as exc:
        warnings.warn(
            f"Could not compute edge orientations due to exception: {exc}",
            stacklevel=2,
        )
        return np.array([])


def entropy(self, variable_name, bins=10):
    """
    Calculate the entropy of a specified variable (orientation, length, degree).

    Parameters
    ----------
    variable_name : str
        The name of the variable to calculate entropy for. Must be one of
        "orientation", "length", or "degree".
    bins : int or sequence of scalars or str, optional
        If variable_name is "orientation", bins can be an integer number of
        equal-width bins spanning the full range of orientations, a sequence of
        bin edges, or a string like 'auto' or 'fd' for automatic binning. For
        "length" and "degree", bins can be an integer number of equal-width bins
        spanning the data range, a sequence of bin edges, or a string for
        automatic binning. Default is 10.

    Returns
    -------
    float
        The calculated entropy of the specified variable in bits (base 2).

    Raises
    ------
    ValueError
        If variable_name is not one of "orientation", "length", or "degree".
    """
    if variable_name == "orientation":
        data = self.orientation
    elif variable_name == "length":
        data = self.lengths
    elif variable_name == "degree":
        if self.n == 0:
            return 0.0
        data = self.graph.degree()
    else:
        raise ValueError(
            "Unsupported variable_name for entropy: "
            f"{variable_name}. Choose from 'orientation', 'length', "
            "'degree'."
        )
    if len(data) == 0:
        return 0.0
    bin_counts, _ = np.histogram(data, bins=bins)
    bin_counts = bin_counts[bin_counts > 0]
    if len(bin_counts) == 0:
        return 0.0
    return scipy_entropy(bin_counts, base=2)


def _GeometricGraph__dist_nearest(self):
    if self.n == 0:
        return np.array([])
    i_indices = np.arange(self.n)
    if self.n <= self._GeometricGraph__limit_vec:
        dist_matrix = cdist(self.points, self.points)
        dist_matrix[i_indices, i_indices] = np.inf
        dist_min = np.min(dist_matrix, axis=1)
    else:
        dist_min = np.empty(self.n)
        for i in range(self.n):
            diffs = self.points - self.points[i]
            dists_sq = np.sum(diffs**2, axis=1)
            dists_sq[i] = np.inf
            dist_min[i] = np.sqrt(np.min(dists_sq))
    return dist_min
