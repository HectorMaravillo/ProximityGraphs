GeometricGraphs
===================================

Overview
--------

The ``GeometricGraph`` class represents a graph embedded in geometric space where vertices have coordinates. This class serves as the base for all proximity graphs and provides fundamental graph operations, property analysis, and visualization capabilities.

----------

Class: GeometricGraph
---------------------

Represents a graph embedded in a geometric space with vertices having coordinates.

Attributes
~~~~~~~~~~

- **points** (numpy.ndarray): The coordinates of vertices as an (n × dim) array
- **setpoints** (SetPoints): The underlying SetPoints object containing vertex coordinates
- **n** (int): The number of vertices in the graph
- **m** (int): The number of edges in the graph
- **cc** (int): The number of connected components
- **f** (int): The number of faces (calculated using Euler's formula: F = C - V + E + 1)
- **graph** (igraph.Graph): The underlying igraph Graph object
- **name** (str): The name of the geometric graph type
- **details** (str): Additional details or parameters used to construct the graph
- **degrees** (numpy.ndarray): The degree distribution (count of vertices with each degree)
- **lengths** (numpy.ndarray): Array of Euclidean lengths for all edges
- **orientation** (numpy.ndarray): Array of orientations (angles in degrees) for all edges

----------

Constructors
------------

``__init__(setpoints)``
~~~~~~~~~~~~~~~~~~~~~~~

Base constructor for GeometricGraph.

Parameters
^^^^^^^^^^

- **setpoints** (SetPoints): An instance of SetPoints containing the vertex coordinates.

Raises
^^^^^^

- **TypeError**: If setpoints is not an instance of SetPoints.

Returns
^^^^^^^

A GeometricGraph object with vertices but no edges initially.

Example
^^^^^^^

.. code-block:: python

    from proximitygraphs.points import SetPoints
    from proximitygraphs.geometricgraphs import GeometricGraph

    # Create points
    points = SetPoints.uniform_square(n=50, dims=2, seed=42)

    # Create empty geometric graph
    g = GeometricGraph(points)
    print(f"Graph has {g.n} vertices and {g.m} edges")  # 50 vertices, 0 edges

Submodules
----------
   
.. toctree::
    :maxdepth: 1

    Geometric_graphs/complete
    Geometric_graphs/from_graph
    Geometric_graphs/random_graph
    Geometric_graphs/instance_methods
    Geometric_graphs/draw
    Geometric_graphs/graph_operations
    Geometric_graphs/data_export


