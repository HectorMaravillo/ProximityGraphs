ProximityGraph 
=====================================

Overview
--------

Proximity graphs are geometric graphs where edges connect vertices based on geometric proximity criteria. This document covers all specialized proximity graph classes in the library.

----------

Base Class: ProximityGraph
---------------------------

Inherits from GeometricGraph and serves as the base class for all proximity graph types.

Constructor
~~~~~~~~~~~

.. code-block:: python

    ProximityGraph(setpoints)

Creates an empty proximity graph with the given points. Subclasses override this to implement specific proximity criteria.

Submodules
----------
   
.. toctree::
   :maxdepth: 1
   
   Proximity_graphs/delaunay
   Proximity_graphs/convex_hull
   Proximity_graphs/MST
   Proximity_graphs/beta_skeleton 
   Proximity_graphs/gabriel_graph
   Proximity_graphs/Eliptic_gg
   Proximity_graphs/RNG
   Proximity_graphs/KNN
   Proximity_graphs/unit_disk
   Proximity_graphs/alpha_shapes
   Proximity_graphs/alpha_hull
   Proximity_graphs/stepping_stone
   Proximity_graphs/gamma_graph
   


