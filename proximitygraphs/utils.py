import numpy as np

def points_on_sphere(n, dims, seed=73, rng=None):
    #https://mathworld.wolfram.com/SpherePointPicking.html
    #https://math.stackexchange.com/questions/444700/uniform-distribution-on-the-surface-of-unit-sphere
    if rng is None:
        rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, dims))
    X_norm = np.linalg.norm(X, axis=1, keepdims=True)
    Y = X / X_norm
    return Y