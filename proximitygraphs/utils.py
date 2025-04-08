import numpy as np


def points_on_sphere(n, dims):
    #https://mathworld.wolfram.com/SpherePointPicking.html
    #https://math.stackexchange.com/questions/444700/uniform-distribution-on-the-surface-of-unit-sphere
    X = np.random.normal(size=(n, dims))
    X_norm = np.linalg.norm(X, axis=1, keepdims=True)
    Y = X / X_norm
    return Y