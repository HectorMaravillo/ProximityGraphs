======================================
Biological Graphs
======================================



Introduction
============

The ``biologicalgraphs`` module provides biologically-inspired graph construction algorithms that mimic natural self-organizing systems. These graphs are particularly useful for:

- **Network optimization**: Creating efficient, fault-tolerant networks
- **Transportation systems**: Modeling biological transport networks
- **Adaptive routing**: Dynamic network adaptation and optimization
- **Bio-inspired computing**: Leveraging natural algorithms for graph construction

Unlike traditional proximity graphs that rely on geometric criteria alone, biological graphs incorporate dynamic processes and evolutionary principles observed in nature to create adaptive, efficient network structures.

Concept and Motivation
=======================

Biological Systems as Network Models
-------------------------------------

Natural systems have evolved remarkably efficient network structures over millions of years. The ``biologicalgraphs`` module draws inspiration from:

**Slime Mold Networks (Physarum polycephalum)**
   The Physarum organism creates optimal transport networks connecting food sources. Research by Tero et al. (2010) demonstrated that these networks approximate optimal solutions to complex routing problems, often matching or exceeding human-designed transportation systems.

**Fungal Mycelia Networks**
   Fungal networks exhibit efficient resource distribution while maintaining robustness through redundancy. They balance the trade-off between network cost (total edge length) and network efficiency (shortest paths).



Key Properties
--------------

Biological graphs typically exhibit:

1. **Adaptability**: Networks can reconfigure based on environmental conditions
2. **Efficiency**: Minimize total cost while maintaining connectivity
3. **Robustness**: Maintain functionality despite damage or failures
4. **Emergent Behavior**: Complex global patterns arise from simple local rules
5. **Multi-objective Optimization**: Balance competing objectives (cost vs. redundancy)


Available Implementations
=========================

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
   Biological_graphs/physarum
   Biological_graphs/fungal
   


Usage Patterns
==============

Basic Usage
-----------

All biological graphs follow a similar instantiation pattern:

.. code-block:: python

   import proximitygraphs as pg

   # Create point set
   points = pg.SetPoints.uniform_square(n=100, seed=42)

   # Create biological graph
   bio_graph = pg.PhysarumGraph(
       points,
       sources=[0],
       steps=200,
       gamma=1.5
   )

   # Access the resulting network
   print(f"Nodes: {bio_graph.n}")
   print(f"Edges: {bio_graph.m}")
   print(f"Components: {bio_graph.cc}")

   # Visualize
   bio_graph.draw()

Comparative Analysis
--------------------

Biological graphs can be compared with traditional proximity graphs:

.. code-block:: python

   from proximitygraphs import Experiment

   exp = Experiment(
       name="Biological vs Proximity Graphs",
       point_config={'method': 'uniform_square', 'params': {'n': 100}},
       n_simulations=30,
       seed=42
   )

   # Add biological graphs
   exp.add_graph_config(pg.PhysarumGraph, name='Physarum', 
                        sources=[0], steps=200)
   exp.add_graph_config(pg.FungalGraph, name='Fungal',
                        max_degree=6)

   # Add traditional graphs for comparison
   exp.add_graph_config(pg.MST, name='MST')
   exp.add_graph_config(pg.GG, name='Gabriel')
   exp.add_graph_config(pg.DelaunayG, name='Delaunay')

   results = exp.run()
   exp.compare_metrics(['n_edges', 'mean_degree', 'mean_length'])



Bio-Mathematics
---------------

- **Murray's Law**: Optimal vessel sizing in vascular systems
- **Fick's Laws**: Diffusion and transport in biological networks
- **Allometric Scaling**: Relationship between organism size and network properties

References
==========

Key Papers
----------

1. **Tero, A., Takagi, S., Saigusa, T., et al.** (2010). "Rules for Biologically Inspired Adaptive Network Design." *Science*, 327(5964), 439-442.
   
   - Original Physarum algorithm
   - Experimental validation
   - Applications to real-world networks

2. **Fricker, M. D., Boddy, L., Nakagaki, T., & Bebber, D. P.** (2017). "Adaptive Biological Networks." *Adaptive Networks*, 51-70.
   
   - Comparative analysis of biological networks
   - Evolutionary perspectives
   - Mathematical modeling approaches

3. **Bebber, D. P., Hynes, J., Darrah, P. R., Boddy, L., & Fricker, M. D.** (2007). "Biological solutions to transport network design." *Proceedings of the Royal Society B*, 274(1623), 2307-2315.
   
   - Fungal network analysis
   - Cost-benefit trade-offs
   - Network resilience

4. **Dorigo, M., & Stützle, T.** (2004). *Ant Colony Optimization*. MIT Press.
   
   - Theoretical foundations of ACO
   - Algorithm variants
   - Applications



Contributing
============

Future biological graph implementations are welcome! To contribute:

1. **Identify a biological system** with interesting network properties
2. **Implement the base algorithm** following the ``BiologicalGraph`` interface
3. **Add comprehensive tests** demonstrating correctness
4. **Document the algorithm** with mathematical details and references
5. **Submit a pull request** with examples and use cases

Guidelines
----------

- All implementations must inherit from ``BiologicalGraph``
- Implement the ``evolve()`` method for dynamic graphs
- Provide at least three usage examples
- Include parameter sensitivity analysis
- Add visualization capabilities
- Cite relevant biological/mathematical literature

----

.. note::
   This is an active area of development. The API may evolve as new biological
   graph types are added and existing implementations are refined based on
   user feedback and research advances.

.. warning::
   Biological graphs can be computationally intensive for large point sets.
   Consider using smaller networks for prototyping and parameter exploration
   before scaling to production applications.