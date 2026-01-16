============================
Experiments
============================

Introduction
============

The ``Experiment`` class is a high-level API for performing systematic analyses of  graphs. It allows you to run multiple simulations, compare different types of graphs, and extract metrics in an automated manner.

Key Features
============

Main Features
----------------

- **Declarative Configuration**: Define experiments using simple dictionaries
- **Multiple Simulations**: Run N simulations with different random seeds
- **Integrated Metrics**: Automatically extract topological and geometric metrics
- **Custom Metrics**: Define your own extraction functions
- **Automatic Aggregation**: Calculate statistics (mean, std, min, max) by graph type
- **Visualization**: Generate comparative plots automatically
- **Export**: Save results to CSV, Excel, JSON, or Pickle
- **Reproducibility**: Full control through random seeds

----

Quick Installation
==================

.. code-block:: python

    import proximitygraphs as pg
    from proximitygraphs import Experiment

----

Basic Usage
===========

Minimal Example
---------------

.. code-block:: python

    # Create experiment
    exp = Experiment(
        name="My First Experiment",
        point_config={
            'method': 'uniform_square',
            'params': {'n': 100}
        },
        graph_configs=[
            {'class': pg.GG, 'params': {'closed': True}},
            {'class': pg.RNG, 'params': {'closed': False}}
        ],
        n_simulations=30,
        seed=42
    )

    # Run
    results = exp.run()

    # View summary
    print(exp.summary())

    # Plot
    exp.plot_metric('mean_degree')

----

Detailed API
============

Constructor
-----------

.. code-block:: python

    Experiment(
        name: str = "Unnamed Experiment",
        point_config: dict = None,
        graph_configs: list = None,
        n_simulations: int = 30,
        seed: int = None,
        verbose: bool = True
    )

**Parameters:**

- ``name``: Descriptive name of the experiment
- ``point_config``: Point generation configuration
- ``graph_configs``: List of graph configurations
- ``n_simulations``: Number of independent simulations
- ``seed``: Master seed for reproducibility
- ``verbose``: Show progress during execution

Point Configuration
-------------------

The ``point_config`` must have the structure:

.. code-block:: python

    {
        'method': 'method_name',
        'params': {
            'param1': value1,
            'param2': value2
        },
        'transformations': [  # optional
            {
                'method': 'transformation_name',
                'params': {'param': value}
            }
        ]
    }

**Available methods** (from ``SetPoints``):

- ``uniform_square``: Uniform points in square [0,1]²
- ``uniform_sphere``: Uniform points in unit disk
- ``uniform_over_sphere``: Points on unit circumference
- ``normal_dist``: Bivariate normal distribution
- ``grid``: Regular grid
- ``hexagonal``: Hexagonal grid
- ``triangular``: Triangular grid
- ``poissonprocess_square``: Poisson process in square
- ``poissonprocess_circle``: Poisson process in circle
- ``poissonprocess_inhomogeneus``: Inhomogeneous Poisson process
- ``cluster_square``: Cluster process (Matern/Thomas)

**Examples:**

.. code-block:: python

    # Uniform points
    point_config = {
        'method': 'uniform_square',
        'params': {'n': 100}
    }

    # Poisson process
    point_config = {
        'method': 'poissonprocess_square',
        'params': {'intensity': 50, 'limit': 1}
    }

    # Regular grid
    point_config = {
        'method': 'grid',
        'params': {'shape': (10, 10)}
    }

    # Normal distribution
    point_config = {
        'method': 'normal_dist',
        'params': {'n': 80}
    }

Point Transformations
---------------------

After generating the points, you can apply sequential transformations. Available transformations are:

``rotation`` - Rotation
^^^^^^^^^^^^^^^^^^^^^^^^

Rotates points around the origin.

**Parameters:**

- ``angle``: float, rotation angle
- ``degree``: bool (optional), if True the angle is in degrees, if False in radians (default True)

.. code-block:: python

    {'method': 'rotation', 'params': {'angle': 45, 'degree': True}}

``scaling`` - Scaling
^^^^^^^^^^^^^^^^^^^^^

Scales points with respect to the origin.

**Parameters:**

- ``scale``: float or array-like, scaling factor(s)
  
  - If scalar: scales all dimensions uniformly
  - If array: scales each dimension independently

.. code-block:: python

    # Uniform scaling
    {'method': 'scaling', 'params': {'scale': 2.0}}

    # Non-uniform scaling
    {'method': 'scaling', 'params': {'scale': [2.0, 0.5]}}

``traslation`` - Translation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Translates points by a vector.

**Parameters:**

- ``c``: float or array-like, translation vector
  
  - If scalar: translates uniformly in all dimensions
  - If array: translates each dimension independently

.. code-block:: python

    # Uniform translation
    {'method': 'traslation', 'params': {'c': 0.5}}

    # Non-uniform translation
    {'method': 'traslation', 'params': {'c': [0.5, -0.3]}}

``perturb`` - Perturbation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adds random noise to each point.

**Parameters:**

- ``radius``: float, maximum perturbation radius

.. code-block:: python

    {'method': 'perturb', 'params': {'radius': 0.1}}

**Important note about** ``perturb``: This transformation uses the internal seed of the SetPoints object, so it will be different in each simulation even with the same configuration, which is useful for robustness studies.

Transformation Examples
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Example 1: Rotated grid
    point_config = {
        'method': 'grid',
        'params': {'shape': (10, 10)},
        'transformations': [
            {'method': 'rotation', 'params': {'angle': 45}}
        ]
    }

    # Example 2: Multiple transformations
    point_config = {
        'method': 'uniform_square',
        'params': {'n': 100},
        'transformations': [
            {'method': 'rotation', 'params': {'angle': 30}},
            {'method': 'scaling', 'params': {'scale': 2.0}},
            {'method': 'traslation', 'params': {'c': [0.5, 0.5]}}
        ]
    }

    # Example 3: Grid with perturbation (robustness)
    point_config = {
        'method': 'grid',
        'params': {'shape': (12, 12)},
        'transformations': [
            {'method': 'perturb', 'params': {'radius': 0.1}}
        ]
    }

    # Example 4: Poisson points scaled and translated
    point_config = {
        'method': 'poissonprocess_square',
        'params': {'intensity': 50, 'limit': 1},
        'transformations': [
            {'method': 'scaling', 'params': {'scale': [2.0, 1.5]}},
            {'method': 'traslation', 'params': {'c': [1.0, 0.5]}}
        ]
    }

Graph Configuration
-------------------

Each element of ``graph_configs`` must have:

.. code-block:: python

    {
        'class': GraphClass,
        'params': {
            'param1': value1,
            'param2': value2
        },
        'name': 'custom_name'  # optional
    }

**Available graphs:**

Proximity Graphs
^^^^^^^^^^^^^^^^

- ``DelaunayG``: Delaunay Triangulation
- ``GG``: Gabriel Graph
- ``RNG``: Relative Neighborhood Graph
- ``MST``: Minimum Spanning Tree
- ``Beta_Skeleton``: β-skeleton (β ≥ 0)
- ``Stepping_Stone``: Stepping Stone Graph
- ``NNG``: k-Nearest Neighbors
- ``Sigma_Graph``: σ-graph
- ``Unit_Disk``: Unit Disk Graph
- ``SIG``: Sphere of Influence Graph
- ``Convex_Hull``: Convex Hull
- ``Elliptic_GabrielG``: Elliptic Gabriel Graph
- ``Alpha_Shape``: α-shape
- ``Alpha_Hull``: α-hull
- ``Gamma_Graph``: γ-graph

Biological Graphs
^^^^^^^^^^^^^^^^^

- ``PhysarumGraph``: Physarum-inspired graph

**Examples:**

.. code-block:: python

    graph_configs = [
        # Gabriel Graph
        {
            'class': pg.GG,
            'params': {'closed': True},
            'name': 'Gabriel'
        },
        
        # RNG
        {
            'class': pg.RNG,
            'params': {'closed': False},
            'name': 'RNG'
        },
        
        # Beta-Skeleton with β=1.5
        {
            'class': pg.Beta_Skeleton,
            'params': {'beta': 1.5, 'type_region': 'lune'},
            'name': 'Beta-1.5'
        },
        
        # k-NN with k=3
        {
            'class': pg.NNG,
            'params': {'k': 3},
            'name': '3-NN'
        },
        
        # Physarum
        {
            'class': pg.PhysarumGraph,
            'params': {
                'sources': [0],
                'sinks': [50],
                'steps': 200,
                'gamma': 1.5
            },
            'name': 'Physarum'
        }
    ]

----

Main Methods
============

``run(store_graphs=False)``
----------------------------

Runs the complete experiment.

.. code-block:: python

    results = exp.run()

    # Or with graph storage
    results = exp.run(store_graphs=True)

**Returns:** pandas DataFrame with all metrics

**Automatically extracted metrics:**

- ``n_vertices``: Number of vertices
- ``n_edges``: Number of edges
- ``n_components``: Number of connected components
- ``n_faces``: Number of faces
- ``mean_degree``: Average degree
- ``std_degree``: Standard deviation of degree
- ``min_degree``: Minimum degree
- ``max_degree``: Maximum degree
- ``mean_length``: Average edge length
- ``std_length``: Standard deviation of edge length
- ``min_length``: Minimum edge length
- ``max_length``: Maximum edge length
- ``density``: Graph density
- ``entropy_degree``: Degree distribution entropy
- ``entropy_length``: Edge length distribution entropy
- ``entropy_orientation``: Edge orientation distribution entropy

``aggregate()``
---------------

Aggregates results by graph type.

.. code-block:: python

    aggregated = exp.aggregate()

**Returns:** DataFrame with mean, std, min, max for each metric and graph type

``summary()``
-------------

Generates a textual summary of the results.

.. code-block:: python

    print(exp.summary())

``plot_metric(metric_name, kind='box', save=None)``
----------------------------------------------------

Plots an individual metric.

.. code-block:: python

    # Box plot (default)
    exp.plot_metric('mean_degree')

    # Bar plot with error bars
    exp.plot_metric('n_edges', kind='bar')

    # Save figure
    exp.plot_metric('density', save='density_plot.png')

**Parameters:**

- ``metric_name``: Name of the metric to plot
- ``kind``: Type of plot ('box' or 'bar')
- ``save``: Path to save the figure (optional)

``compare_metrics(metrics, save=None)``
----------------------------------------

Compares multiple metrics in a grid of plots.

.. code-block:: python

    # Compare multiple metrics
    fig, axes = exp.compare_metrics([
        'mean_degree',
        'n_edges',
        'density',
        'mean_length'
    ])

    # Save figure
    exp.compare_metrics(['mean_degree', 'density'], save='comparison.png')

**Parameters:**

- ``metrics``: List of metric names to compare
- ``save``: Path to save the figure (optional)

``export_results(filename, format=None)``
------------------------------------------

Exports results to a file.

.. code-block:: python

    # CSV (inferred from extension)
    exp.export_results('results.csv')

    # Excel
    exp.export_results('results.xlsx')

    # JSON
    exp.export_results('results.json')

    # Pickle
    exp.export_results('results.pkl')

    # Explicit format
    exp.export_results('data', format='csv')

**Parameters:**

- ``filename``: Output file name
- ``format``: File format (optional, inferred from extension if not provided)

**Supported formats:**

- ``'csv'``: CSV file
- ``'xlsx'`` or ``'excel'``: Excel file
- ``'json'``: JSON file
- ``'pkl'`` or ``'pickle'``: Pickle file

``get_graph(simulation_idx, graph_name)``
------------------------------------------

Retrieves a specific graph from stored results.

.. code-block:: python

    # Run with storage
    exp.run(store_graphs=True)

    # Get specific graph
    g = exp.get_graph(0, 'Gabriel')

    # Use the graph
    g.draw()

**Parameters:**

- ``simulation_idx``: Index of the simulation (0 to n_simulations-1)
- ``graph_name``: Name of the graph type

**Note:** Requires ``run(store_graphs=True)``

----

Advanced Configuration
======================

``add_point_config(method, **params)``
---------------------------------------

Alternative way to configure points.

.. code-block:: python

    exp = Experiment(name="My Experiment", n_simulations=20)
    exp.add_point_config('uniform_square', n=100)

``add_graph_config(graph_class, name=None, **params)``
-------------------------------------------------------

Adds a graph configuration.

.. code-block:: python

    exp.add_graph_config(pg.GG, name='Gabriel', closed=True)
    exp.add_graph_config(pg.RNG, closed=False)

``add_custom_metric(name, function)``
--------------------------------------

Registers a custom metric function.

.. code-block:: python

    def custom_metric(graph):
        """Calculate custom metric"""
        # Your code here
        return value

    exp.add_custom_metric('my_metric', custom_metric)

**The function must:**

- Accept a single parameter (the graph)
- Return a numeric value
- Handle errors gracefully (return ``np.nan`` on failure)

**Example:**

.. code-block:: python

    import numpy as np

    def edge_vertex_ratio(graph):
        """Calculate edge-to-vertex ratio"""
        if graph.n == 0:
            return np.nan
        return graph.m / graph.n

    exp.add_custom_metric('ev_ratio', edge_vertex_ratio)

    def max_component_size(graph):
        """Size of largest connected component"""
        try:
            components = graph.graph.components()
            return max(len(c) for c in components) if components else 0
        except:
            return np.nan

    exp.add_custom_metric('max_component', max_component_size)

**Template for custom metrics:**

.. code-block:: python

    def my_custom_metric(graph):
        """
        Brief description of what this metric calculates.

        Parameters
        ----------
        graph : GeometricGraph
            The graph to analyze

        Returns
        -------
        float
            The calculated metric value, or np.nan if calculation fails
        """
        # Your code here
        return value

----

Complete Examples
=================

1. Simple Comparison
--------------------

.. code-block:: python

    exp = Experiment(
        name="Gabriel vs RNG",
        point_config={'method': 'uniform_square', 'params': {'n': 100}},
        graph_configs=[
            {'class': pg.GG, 'params': {'closed': True}},
            {'class': pg.RNG, 'params': {'closed': False}}
        ],
        n_simulations=30,
        seed=42
    )

    results = exp.run()
    print(exp.summary())
    exp.plot_metric('mean_degree')

2. Multiple Graphs
------------------

.. code-block:: python

    exp = Experiment(
        name="Multiple Comparison",
        point_config={'method': 'normal_dist', 'params': {'n': 80}},
        n_simulations=40,
        seed=123
    )

    exp.add_graph_config(pg.GG, name='Gabriel', closed=True)
    exp.add_graph_config(pg.RNG, name='RNG', closed=False)
    exp.add_graph_config(pg.DelaunayG, name='Delaunay')
    exp.add_graph_config(pg.MST, name='MST')
    exp.add_graph_config(pg.Beta_Skeleton, name='Beta-1.5', beta=1.5)

    results = exp.run()
    fig, axes = exp.compare_metrics([
        'mean_degree', 'n_edges', 'mean_length', 'density'
    ])

3. Parameter Sweep
------------------

.. code-block:: python

    # Beta-skeleton with different beta values
    beta_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

    exp = Experiment(
        name="Beta Sweep",
        point_config={'method': 'uniform_square', 'params': {'n': 100}},
        n_simulations=20,
        seed=2024
    )

    for beta in beta_values:
        exp.add_graph_config(
            pg.Beta_Skeleton,
            name=f'Beta-{beta}',
            beta=beta,
            type_region='lune' if beta >= 1 else 'intersection'
        )

    results = exp.run()
    exp.plot_metric('mean_degree', kind='bar')

4. Biological Graphs
--------------------

.. code-block:: python

    exp = Experiment(
        name="Physarum Analysis",
        point_config={'method': 'uniform_square', 'params': {'n': 50}},
        n_simulations=15,
        seed=777
    )

    exp.add_graph_config(pg.GG, name='Gabriel')
    exp.add_graph_config(pg.MST, name='MST')

    exp.add_graph_config(
        pg.PhysarumGraph,
        name='Physarum-Short',
        sources=[0],
        sinks=[49],
        steps=100,
        gamma=1.5
    )

    exp.add_graph_config(
        pg.PhysarumGraph,
        name='Physarum-Long',
        sources=[0],
        sinks=[49],
        steps=300,
        gamma=2.0
    )

    results = exp.run()
    exp.compare_metrics(['n_edges', 'mean_degree', 'mean_length'])

5. Entropy Analysis
-------------------

.. code-block:: python

    exp = Experiment(
        name="Entropy Analysis",
        point_config={'method': 'uniform_square', 'params': {'n': 120}},
        n_simulations=40,
        seed=888
    )

    exp.add_graph_config(pg.GG, name='Gabriel')
    exp.add_graph_config(pg.RNG, name='RNG')
    exp.add_graph_config(pg.DelaunayG, name='Delaunay')

    results = exp.run()

    # Focus on entropy metrics
    entropy_metrics = ['entropy_degree', 'entropy_length', 'entropy_orientation']
    print(results.groupby('graph_type')[entropy_metrics].mean())

    exp.compare_metrics(entropy_metrics)

6. Point Transformations
-------------------------

.. code-block:: python

    # Example 1: Rotated grid
    exp1 = Experiment(
        name="Rotated Grid",
        point_config={
            'method': 'grid',
            'params': {'shape': (10, 10)},
            'transformations': [
                {'method': 'rotation', 'params': {'angle': 45}}
            ]
        },
        graph_configs=[{'class': pg.GG, 'name': 'Gabriel'}],
        n_simulations=10,
        seed=111
    )

    results = exp1.run()

    # Example 2: Multiple transformations
    exp2 = Experiment(
        name="Multiple Transformations",
        n_simulations=20,
        seed=222
    )

    exp2.add_point_config(
        'uniform_square',
        n=100,
        transformations=[
            {'method': 'rotation', 'params': {'angle': 30}},
            {'method': 'scaling', 'params': {'scale': 2.0}},
            {'method': 'traslation', 'params': {'c': [0.5, 0.5]}}
        ]
    )

    exp2.add_graph_config(pg.GG, name='Gabriel')
    exp2.add_graph_config(pg.RNG, name='RNG')

    results = exp2.run()

    # Example 3: Perturbation for robustness
    exp3 = Experiment(
        name="Grid with Perturbation",
        n_simulations=25,
        seed=333
    )

    exp3.add_point_config(
        'grid',
        shape=(12, 12),
        transformations=[
            {'method': 'perturb', 'params': {'radius': 0.1}}
        ]
    )

    exp3.add_graph_config(pg.GG, name='Gabriel')
    exp3.add_graph_config(pg.DelaunayG, name='Delaunay')

    results = exp3.run()
    exp3.plot_metric('mean_degree', kind='box')

----

Typical Workflow
================

.. code-block:: python

    # 1. Create experiment
    exp = Experiment(
        name="My Analysis",
        n_simulations=30,
        seed=42
    )

    # 2. Configure points
    exp.add_point_config('uniform_square', n=100)

    # 3. Add graphs
    exp.add_graph_config(pg.GG, name='Gabriel', closed=True)
    exp.add_graph_config(pg.RNG, name='RNG', closed=False)

    # 4. (Optional) Add custom metrics
    def my_metric(g):
        return g.m / g.n if g.n > 0 else 0
    exp.add_custom_metric('edge_vertex_ratio', my_metric)

    # 5. Run
    results = exp.run()

    # 6. Analyze
    print(exp.summary())
    exp.aggregate()
    exp.plot_metric('mean_degree')
    exp.compare_metrics(['mean_degree', 'n_edges', 'density'])

    # 7. Export
    exp.export_results('my_results.csv')

----

Tips and Best Practices
========================

1. Reproducibility
------------------

Always use ``seed`` for reproducible results:

.. code-block:: python

    exp = Experiment(..., seed=42)

2. Number of Simulations
-------------------------

- For quick tests: ``n_simulations=5-10``
- For exploratory analysis: ``n_simulations=20-30``
- For publishable results: ``n_simulations=50-100``

3. Graph Storage
----------------

Only use ``store_graphs=True`` when you need access to individual graphs:

.. code-block:: python

    # High memory consumption
    results = exp.run(store_graphs=True)

4. Custom Metrics
-----------------

Include error handling in your metrics:

.. code-block:: python

    def safe_metric(graph):
        try:
            # Your calculation
            return value
        except Exception as e:
            return np.nan

5. Incremental Export
---------------------

For long experiments, export results periodically:

.. code-block:: python

    for i in range(0, n_total, batch_size):
        exp.n_simulations = batch_size
        exp.run()
        exp.export_results(f'results_batch_{i}.csv')

6. Configuration Validation
----------------------------

Validate your configuration before running:

.. code-block:: python

    exp = Experiment(...)
    # Review configuration
    print(f"Points: {exp.point_config}")
    print(f"Graphs: {len(exp.graph_configs)}")
    print(f"Total runs: {exp.n_simulations * len(exp.graph_configs)}")

----

Troubleshooting
===============

Error: "No results available"
------------------------------

.. code-block:: python

    # Run the experiment first
    exp.run()

Error: "point_config must contain 'method' key"
------------------------------------------------

.. code-block:: python

    # Correct configuration
    exp.add_point_config('uniform_square', n=100)

    # Not this:
    exp.point_config = {'n': 100}  # Missing method

Warning: "Graphs were not stored"
----------------------------------

.. code-block:: python

    # To retrieve individual graphs:
    exp.run(store_graphs=True)
    g = exp.get_graph(0, 'Gabriel')

Error: Custom metric fails
---------------------------

.. code-block:: python

    # Add error handling
    def my_metric(graph):
        try:
            return calculate_something(graph)
        except:
            return np.nan  # Or a default value

----

Quick Reference
===============

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Method
     - Description
   * - ``Experiment()``
     - Constructor
   * - ``add_point_config()``
     - Configure point generation
   * - ``add_graph_config()``
     - Add graph type
   * - ``add_custom_metric()``
     - Register custom metric
   * - ``run()``
     - Run experiment
   * - ``aggregate()``
     - Aggregate results
   * - ``summary()``
     - Generate textual summary
   * - ``plot_metric()``
     - Plot individual metric
   * - ``compare_metrics()``
     - Compare multiple metrics
   * - ``export_results()``
     - Export to file
   * - ``get_graph()``
     - Retrieve specific graph

----
