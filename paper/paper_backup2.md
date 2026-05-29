---
title: "ProximityGraphs: A Python package for proximity and biological graphs in the plane"
tags:
  - Python
  - computational geometry
  - proximity graphs
  - geometric graphs
  - biological graphs
authors:
  - name: Héctor Maravillo
    affiliation: 1
    corresponding: true
  - name: Diego Villarreal De La Cerda
    affiliation: 2
  - name: Heriberto Espino Montelongo
    affiliation: 2
    orcid: 0009-0009-1230-2931
affiliations:
  - name: Universidad Autónoma de la Ciudad de México, Mexico
    index: 1
  - name: Universidad de las Américas Puebla, México
    index: 2
date: 28 May 2026
bibliography: paper.bib
---

# Summary

ProximityGraphs is a Python package for constructing, visualizing, and analyzing geometric graphs generated from finite point sets in the plane. Its current scope includes classical proximity graphs such as the Delaunay triangulation, the Gabriel graph, the Relative Neighborhood graph, the Sphere-of-Influence graph, and related empty-region graph families, together with complete graphs, Erdős--Rényi random graphs, and bio-inspired graph models. The package provides utilities for generating structured and random point sets, applying geometric transformations, constructing graph objects, computing graph-level summaries, and supporting computational experiments in computational geometry, network science, and biologically inspired spatial modeling.

The main goal of ProximityGraphs is to provide a unified and extensible software interface for proximity graph experimentation in Python. Instead of treating each graph family as an isolated implementation, the package organizes point-set generation, graph construction, geometric predicates, visualization, and empirical analysis into a common workflow. This makes the package useful for teaching, prototyping, reproducible numerical experiments, and exploratory research involving planar spatial graphs.

# Statement of need

Graphs built from spatial point sets are central in computational geometry, topological data analysis, spatial statistics, ecological modeling, network science, and pattern recognition. A proximity graph can be understood as a graph whose vertices are points in a metric or Euclidean space and whose edges are determined by a geometric rule, often involving a distance threshold, an empty region, or a nearest-neighbor relation. Classical examples include the Delaunay triangulation, the Gabriel graph, the Relative Neighborhood graph, and the Sphere-of-Influence graph [@Toussaint1980; @Jaromczyk1992; @PreparataShamos1985].

General-purpose graph libraries such as NetworkX [@Hagberg2008] and igraph [@Csardi2006] provide broad graph data structures and algorithms, but they do not focus on the geometric construction of proximity graph families from point sets. Numerical and geometric libraries such as SciPy [@Virtanen2020] provide essential computational primitives, including triangulations and spatial data structures, but they do not expose a unified interface for comparing multiple proximity graphs under common point-set, transformation, visualization, and experimental abstractions.

ProximityGraphs addresses this gap by providing a Python-centered framework for constructing and comparing planar proximity graphs in a consistent way. The package is intended for users who need to:

- generate finite point sets in the plane;
- construct several proximity graph families from the same point set;
- visualize and compare their edge structures;
- compute descriptive graph statistics;
- run reproducible computational experiments;
- extend the framework with new geometric graph constructors.

This is especially useful in research and teaching settings where the objective is not only to obtain one graph, but to compare how different geometric rules induce different network structures on the same spatial configuration.

# Package overview

The package is organized around the following conceptual workflow:

1. define or generate a finite set of planar points;
2. optionally transform or normalize the point set;
3. construct one or more geometric graph objects;
4. analyze graph properties such as edges, degrees, connectivity, and geometric structure;
5. visualize the resulting graph or export results for further analysis.

At a high level, a finite point set may be written as

[
X = {x_1,\ldots,x_n} \subset \mathbb{R}^2,
]

where each point (x_i = (x_{i1},x_{i2})) is a planar coordinate. A geometric graph generated from (X) is a pair

[
G_\theta(X) = (X,E_\theta),
]

where (E_\theta) is an edge set determined by a geometric rule indexed by a graph family or parameter (\theta). For an empty-region proximity graph, a typical rule has the form

[
{x_i,x_j}\in E_\theta
\quad\Longleftrightarrow\quad
\Omega_\theta(x_i,x_j)\cap (X\setminus{x_i,x_j})=\varnothing,
]

where (\Omega_\theta(x_i,x_j)) is a region associated with the candidate pair ((x_i,x_j)). This abstraction covers several classical proximity graph constructions and provides a common mathematical view for software design.

The package currently includes constructors and utilities for a collection of geometric graph families, including classical proximity graphs and bio-inspired variants. The exact set of implemented graph classes is documented in the package documentation and examples. The software is designed so that new graph constructors can be added without rewriting the surrounding point-set, plotting, and analysis workflow.

# Usage example

The following example illustrates the intended workflow. It generates a planar point set, constructs proximity graphs, and visualizes or analyzes the resulting graph objects.

python import proximitygraphs as pg  # Generate or define a finite planar point set. points = pg.SetPoints.random_uniform(n=100, seed=42)  # Construct selected proximity graphs. delaunay_graph = pg.DelaunayGraph(points) gabriel_graph = pg.GabrielGraph(points) rng_graph = pg.RelativeNeighborhoodGraph(points)  # Compute basic graph summaries. print("Delaunay edges:", delaunay_graph.number_of_edges()) print("Gabriel edges:", gabriel_graph.number_of_edges()) print("RNG edges:", rng_graph.number_of_edges())  # Visualize one of the graphs. gabriel_graph.plot() 

The exact names of constructors and methods may vary depending on the installed version. Full examples are available in the repository documentation.

# Research and educational applications

ProximityGraphs is intended to support computational experiments in which several proximity graph rules are applied to the same underlying point set. This enables empirical comparison of edge densities, degree distributions, connectivity behavior, inclusion relations among graph families, and sensitivity to geometric transformations.

In an educational setting, the package can be used to demonstrate how different local geometric rules produce different global network structures. For example, students can compare the Delaunay triangulation, Gabriel graph, and Relative Neighborhood graph on the same point cloud and observe how increasingly restrictive empty-region rules affect graph sparsity. In a research setting, the same workflow can be used to prototype new graph families, test conjectures numerically, or generate figures for geometric graph experiments.

# Related software

Several existing Python packages provide functionality related to parts of the ProximityGraphs workflow. NetworkX [@Hagberg2008] offers a broad collection of graph algorithms and data structures. igraph [@Csardi2006] provides efficient graph representations and graph-theoretic algorithms. SciPy [@Virtanen2020] includes numerical and spatial routines, including geometric primitives useful for Delaunay triangulations and distance-based computations.

ProximityGraphs is complementary to these tools. Its focus is not to replace general-purpose graph libraries or numerical libraries, but to provide a domain-specific interface for constructing and experimenting with planar proximity graphs. The package organizes geometric graph construction, point-set handling, visualization, and experimentation around proximity graph use cases.

# Acknowledgements

The authors received no external funding for this work.

# AI usage disclosure

The authors used ChatGPT for assistance with software engineering discussion, documentation drafting, manuscript editing, JOSS-preparation planning, and copy-editing. All AI-assisted outputs were reviewed, edited, and validated by the human authors. The authors made the core design decisions, implemented and tested the software, verified the mathematical and computational claims, and remain fully responsible for the accuracy, originality, licensing, and ethical/legal compliance of the submitted materials.

# References