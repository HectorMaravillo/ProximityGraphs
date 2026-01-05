Points
======

SetPoints
---------
Overview

The SetPoints class represents an ordered collection of points in n-dimensional Euclidean space. It provides various methods for generating, transforming, and visualizing point sets.

Class: SetPoints

Represent an ordered collection of points in n-dimensional space.

Attributes:

- **n** (*int*):  
  The number of points in the collection.

- **dim** (*int*):  
  The dimensionality of the points.

- **points** (*numpy.ndarray*):  
  A 2-dimensional numpy array containing the point coordinates with shape ``(n, dim)``.

- **pos** (*dict*):  
  A dictionary mapping point indices to their coordinates.

- **centroid** (*numpy.ndarray*):  
  The centroid (mean position) of all points.

Constructor
-----------

``__init__(points, seed=None)``
...

Base constructor for SetPoints.

Parameters:


- **points** (*numpy.ndarray*):  
  A 2D numpy array of shape ``(n, dim)`` where ``n`` is the number of points and ``dim`` is the dimension of each point.

- **seed** (*int*, optional):  
  A seed for the random number generator to ensure reproducibility. If ``None``, a default random generator is used.

Raises
~~~~~~

- **TypeError**:  
  If ``points`` is not a ``numpy.ndarray``.

Returns
~~~~~~~

A ``SetPoints`` object containing the points.

Example
~~~~~~~

.. code-block:: python

   import numpy as np
   from proximitygraphs.points import SetPoints

   # Create from numpy array
   points_array = np.random.rand(100, 2)
   my_points = SetPoints(points_array, seed=42)

---

This is a basic overview of the SetPoints class. For detailed information on methods and additional functionalities, please refer to the specific method documentation.

Submodules
----------
   
.. toctree::
   :maxdepth: 1
   
   Points/uniform_square
   Points/uniform_over_sphere
   Points/uniform_sphere
   Points/normal_dist
   Points/grid
   Points/hexagonal
   Points/triangular
   Points/poissonprocess_square
   Points/poissonprocess_circle
   Points/poissonprocess_inhomogeneus
   Points/cluster_square
   Points/from_geopandas
   Points/transformations
   Points/draw

----

Usage Tips
==========

- Always use ``seed`` for reproducibility.
- ``draw()`` is only available for 2D data.
- Transformations are immutable: they return new objects.
- Large datasets may be memory-intensive.
- ``from_geopandas()`` integrates with GeoPandas workflows.

----

Common Workflows
================

Generate and Transform Points
-----------------------------

.. code-block:: python

   from proximitygraphs.points import SetPoints

   points = SetPoints.uniform_square(n=100, dims=2, seed=42)

   scaled = points.scaling(2.0)
   rotated = scaled.rotation(45)
   translated = rotated.traslation([1, 1])
   noisy = translated.perturb(radius=0.1)

   noisy.draw(figsize=(10, 10), v_color='blue', v_alpha=0.6)

Create Custom Point Patterns
----------------------------

.. code-block:: python

   from proximitygraphs.points import SetPoints

   uniform_bg = SetPoints.uniform_square(n=200, dims=2, seed=1)
   clusters = SetPoints.cluster_square(
       intensity=(3, 15),
       cluster={"name": "Thomas", "param": 0.05},
       limit=1,
       seed=2
   )

   combined = uniform_bg + clusters
   combined.draw(figsize=(10, 10), v_color='red', v_size=15)

---