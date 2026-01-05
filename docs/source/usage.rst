Usage
=====

.. _installation:

Installation
------------

To use the library, first install it using pip:

.. code-block:: console

   (.venv) $ pip install proximity_graphs

Quick Reference Guide
=====================


.. code-block:: python

    # Assuming the library is in your Python path
    from proximitygraphs import SetPoints
    from proximitygraphs import GeometricGraph
    from proximitygraphs import *

----------

Creating Points
---------------

Random Distributions
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Uniform in unit square
    points = SetPoints.uniform_square(n=100, dims=2, seed=42)

    # Uniform on unit circle
    circle = SetPoints.uniform_over_sphere(n=100, seed=42)

    # Uniform in unit disk
    disk = SetPoints.uniform_sphere(n=100, seed=42)

    # Standard normal distribution
    normal = SetPoints.normal_dist(n=100, seed=42)

Structured Patterns
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Regular grid
    grid = SetPoints.grid(shape=(10, 10))

    # Hexagonal lattice
    hex_lattice = SetPoints.hexagonal(n_x=5, n_y=5)

    # Triangular lattice
    tri_lattice = SetPoints.triangular(n_x=5, n_y=5)

Point Processes
~~~~~~~~~~~~~~~

.. code-block:: python

    # Poisson process in square
    poisson = SetPoints.poissonprocess_square(intensity=50, limit=1, seed=42)

    # Poisson on circle circumference
    poisson_circle = SetPoints.poissonprocess_circle(intensity=20, radius=1, seed=42)

    # Inhomogeneous Poisson
    intensity_fn = lambda x, y: 10 * (x**2 + y**2)
    inhom = SetPoints.poissonprocess_inhomogeneus(fun_lambda=intensity_fn, limit=1, seed=42)

    # Cluster process
    clusters = SetPoints.cluster_square(
        intensity=(5, 20),
        cluster={"name": "Matern", "param": 0.1},
        limit=1,
        seed=42
    )

----------

Transforming Points
-------------------

.. code-block:: python

    points = SetPoints.uniform_square(n=50, dims=2, seed=1)

    # Rotation
    rotated = points.rotation(45, degree=True)

    # Scaling
    scaled = points.scaling(2.0)  # Uniform
    scaled_aniso = points.scaling([2.0, 0.5])  # Non-uniform

    # Translation
    translated = points.traslation([1.0, -0.5])

    # Random perturbation
    noisy = points.perturb(radius=0.1)

    # Combine transformations
    transformed = points.rotation(30).scaling(1.5).traslation([0.5, 0.5])

----------

Creating Graphs
---------------

Basic Structures
~~~~~~~~~~~~~~~~

.. code-block:: python

    from proximitygraphs.proximitygraphs import *

    points = SetPoints.uniform_square(n=50, dims=2, seed=42)

    # Delaunay triangulation
    delaunay = DelaunayG(points)

    # Convex hull
    hull = Convex_Hull(points)

    # Minimum spanning tree
    mst = MST(points)

    # Complete graph
    complete = GeometricGraph.complete(points)

    # Random graph
    random_g = GeometricGraph.random_graph(points, p=0.2, seed=42)

Proximity Graphs
~~~~~~~~~~~~~~~~

.. code-block:: python

    # β-Skeleton family
    gabriel = GG(points, closed=True)  # β=1
    rng = RNG(points, closed=False)  # β=2
    beta_1_5 = Beta_Skeleton(points, beta=1.5, type_region="lune")

    # Distance-based
    unit_disk = Unit_Disk(points, dist_max=0.2, closed=True)
    sig = SIG(points, closed=False)
    sigma_g = Sigma_Graph(points, sigma=1.5)

    # Shape-based
    elliptic = Elliptic_GabrielG(points, alpha=1.5)
    alpha_shape = Alpha_Shape(points, alpha=2.0)
    alpha_hull = Alpha_Hull(points, alpha=1.5, n_points_per_arc=50)

    # Advanced
    stepping = Stepping_Stone(points, d=2, k=0)
    gamma = Gamma_Graph(points, gamma0=0.0, gamma1=0.5)

----------

Graph Operations
----------------

.. code-block:: python

    gabriel = GG(points)
    rng = RNG(points)

    # Set operations
    union = gabriel.union(rng)
    intersection = gabriel.intersection(rng)
    difference = gabriel.difference(rng)
    sym_diff = gabriel.symmetric_difference(rng)

    # Distance between graphs
    distance = gabriel.recovering(rng)
    print(f"Recovery distance: {distance:.4f}")

----------

Visualization
-------------

Basic Plotting
~~~~~~~~~~~~~~

.. code-block:: python

    # Simple visualization
    gabriel.draw()

    # Customized
    gabriel.draw(
        figsize=(10, 10),
        v_size=50,
        v_color='red',
        v_alpha=0.8,
        e_size=2,
        e_color='blue',
        e_alpha=0.6,
        title=True,
        details=True,
        axis=True
    )

    # Save to file
    gabriel.draw(save='gabriel_graph')  # Saves as gabriel_graph.png

Orientation Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Polar histogram of edge orientations
    fig, ax = delaunay.draw_orientation(
        num_bins=36,
        figsize=(8, 8),
        color='blue',
        area=True
    )

----------

Analysis
--------

Graph Properties
~~~~~~~~~~~~~~~~

.. code-block:: python

    print(f"Vertices: {gabriel.n}")
    print(f"Edges: {gabriel.m}")
    print(f"Connected components: {gabriel.cc}")
    print(f"Faces: {gabriel.f}")

    # Degree distribution
    degrees = gabriel.degrees
    print(f"Degree distribution: {degrees}")

    # Edge properties
    lengths = gabriel.lengths
    orientations = gabriel.orientation

    print(f"Mean edge length: {lengths.mean():.3f}")
    print(f"Max edge length: {lengths.max():.3f}")

Entropy
~~~~~~~

.. code-block:: python

    # Calculate entropy of various properties
    orient_entropy = gabriel.entropy('orientation', bins=36)
    length_entropy = gabriel.entropy('length', bins=10)
    degree_entropy = gabriel.entropy('degree')

    print(f"Orientation entropy: {orient_entropy:.3f} bits")
    print(f"Length entropy: {length_entropy:.3f} bits")
    print(f"Degree entropy: {degree_entropy:.3f} bits")

----------

Data Export
-----------

Save/Load Graphs
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Save graph
    gabriel.save('/path/to/directory', 'my_graph')

    # Load graph
    from proximitygraphs.geometricgraphs import load_graph
    loaded = load_graph('/path/to/directory', 'my_graph')

Export to GeoPandas
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Export edges as LineStrings
    gdf_lines = gabriel.to_gpd_lines()
    gdf_lines.to_file('edges.shp')

    # Export faces as Polygons
    gdf_polygons = delaunay.to_gpd_polygons()
    gdf_polygons.to_file('faces.shp')

    # Add attributes
    gdf_polygons['area'] = gdf_polygons.geometry.area
    gdf_polygons['perimeter'] = gdf_polygons.geometry.length

----------

Common Patterns
---------------

Compare Multiple Graphs
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    points = SetPoints.uniform_square(n=100, dims=2, seed=42)

    graphs = {
        'MST': MST(points),
        'RNG': RNG(points),
        'Gabriel': GG(points),
        'Delaunay': DelaunayG(points)
    }

    for name, g in graphs.items():
        print(f"{name}:")
        print(f"  Edges: {g.m}")
        print(f"  Components: {g.cc}")
        print(f"  Orientation entropy: {g.entropy('orientation', bins=36):.3f}")
        print()

Parameter Sweeps
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Sweep over β parameter
    points = SetPoints.uniform_square(n=50, dims=2, seed=42)

    for beta in [0.5, 1.0, 1.5, 2.0, 2.5]:
        if beta < 1:
            g = Beta_Skeleton(points, beta=beta, type_region="intersection")
        else:
            g = Beta_Skeleton(points, beta=beta, type_region="lune")
        print(f"β={beta}: {g.m} edges, {g.cc} components")

Network Analysis
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Find minimum range for connectivity
    points = SetPoints.uniform_square(n=100, dims=2, seed=42)

    for r in np.linspace(0.05, 0.5, 20):
        udg = Unit_Disk(points, dist_max=r)
        if udg.cc == 1:
            print(f"Minimum range: {r:.3f}")
            print(f"Edges at connectivity: {udg.m}")
            break

Shape Extraction
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Extract boundary at different resolutions
    points = SetPoints.uniform_sphere(n=200, seed=42)

    for alpha in [0.1, 0.5, 1.0, 2.0]:
        shape = Alpha_Shape(points, alpha=alpha)
        print(f"α={alpha}: {shape.m} boundary edges")
        shape.draw(save=f'shape_alpha_{alpha}')

----------

Tips and Tricks
---------------

1. **Always use seeds** for reproducible results:

   .. code-block:: python

       points = SetPoints.uniform_square(n=100, dims=2, seed=42)

2. **Check connectivity** for network applications:

   .. code-block:: python

       if graph.cc == 1:
           print("Graph is connected")

3. **Use from_graph()** for efficiency:

   .. code-block:: python

       # Start with Delaunay, then filter
       delaunay = DelaunayG(points)
       gabriel = GG.from_graph(delaunay, beta=1, closed=True)

4. **Combine operations**:

   .. code-block:: python

       # Create transformed points and graph in one go
       points = SetPoints.uniform_square(n=50, dims=2, seed=1).rotation(45).scaling(2)
       gabriel = GG(points)

5. **Export for external tools**:

   .. code-block:: python

       gdf = gabriel.to_gpd_lines()
       gdf.to_file('my_graph.geojson', driver='GeoJSON')

----------

Performance Considerations
--------------------------

- **Small datasets** (n < 1000): All methods work efficiently
- **Medium datasets** (1000 < n < 10000): Use Delaunay-based filtering
- **Large datasets** (n > 10000):
  
  - Avoid all-pairs methods (β < 1, complete graph)
  - Use spatial indexing
  - Consider working with subsets

----------

Troubleshooting
---------------

Issue: "TypeError: Input 'setpoints' must be an instance of SetPoints"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Always create points using SetPoints constructors

.. code-block:: python

    # Wrong
    points = np.random.rand(100, 2)
    gabriel = GG(points)  # Error!

    # Correct
    points = SetPoints(np.random.rand(100, 2))
    gabriel = GG(points)  # Works!

Issue: Graph has no edges
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Check parameters (dist_max too small, β too large, etc.)

.. code-block:: python

    # Debug
    print(f"Points: {points.n}")
    print(f"Point cloud extent: x∈[{points.points[:,0].min():.2f}, {points.points[:,0].max():.2f}], "
          f"y∈[{points.points[:,1].min():.2f}, {points.points[:,1].max():.2f}]")

Issue: Visualization looks wrong
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Check if points are 2D and properly scaled

.. code-block:: python

    # Check dimensionality
    print(f"Dimensions: {points.dim}")

    # Check scale
    print(f"Point range: {points.points.min():.3f} to {points.points.max():.3f}")

----------

Further Reading
---------------

- See individual class documentation for detailed API reference
- Check examples directory for complete workflows
- Refer to academic papers for theoretical background