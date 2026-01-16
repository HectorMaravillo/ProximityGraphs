.. Proximity Graphs documentation master file, created by
   sphinx-quickstart on Sat Jul 26 15:04:04 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Proximity Graphs 
==============================
This directory contains comprehensive documentation for the Proximity Graphs Python library.



Library Overview
----------------

The Proximity Graphs library provides tools for:

- Generating and manipulating point sets in n-dimensional space
- Creating various types of geometric and proximity graphs
- Analyzing graph properties (degrees, lengths, orientations, entropy)
- Visualizing graphs and point patterns

Main Components
---------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   usage
   modules/points
   modules/geometricgraphs
   modules/proximitygraphs
   modules/Experiments
   modules/biologicalgraphs
   


SetPoints
~~~~~~~~~

Represents collections of points with methods for:

- Random generation (uniform, normal, Poisson processes, clusters)
- Geometric transformations (rotation, scaling, translation, perturbation)
- Visualization

GeometricGraph
~~~~~~~~~~~~~~

Base class for graphs embedded in geometric space with:

- Graph construction and manipulation
- Set operations (union, intersection, difference)
- Property analysis (entropy, orientation, lengths)
- Conversion to GeoPandas for GIS workflows

ProximityGraph
~~~~~~~~~~~~~~

Specialized geometric graphs based on proximity relationships:

- **Delaunay Triangulation** - Fundamental triangulation structure
- **Convex Hull** - Boundary of point sets
- **MST** (Minimum Spanning Tree) - Minimum cost connected graph
- **Gabriel Graph** - β-skeleton with β=1
- **RNG** (Relative Neighborhood Graph) - β-skeleton with β=2
- **β-Skeleton** - Parameterized family of proximity graphs
- **Unit Disk Graph** - Distance-based connectivity
- **Sphere of Influence Graph** - Based on nearest neighbor spheres
- **α-Shape** - Generalization of convex hull
- **α-Hull** - Hull with circular arcs
- **γ-Neighborhood Graph** - Veltkamp's generalized proximity graph
- **Elliptic Gabriel Graph** - Gabriel graph with elliptical regions
- **σ-Graph** - Scaled distance-based graph
- **Stepping Stone Graph** - Power-distance based connectivity

Getting Started
---------------

.. code-block:: python

    from proximitygraphs.points import SetPoints
    from proximitygraphs.proximitygraphs import DelaunayG, GG, RNG

    # Generate points
    points = SetPoints.uniform_square(n=100, dims=2, seed=42)

    # Create graphs
    delaunay = DelaunayG(points)
    gabriel = GG(points)
    rng = RNG(points)

    # Visualize
    gabriel.draw(figsize=(10, 10))

See individual documentation files for detailed information on each class and method.






