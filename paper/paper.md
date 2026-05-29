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

ProximityGraphs is a Python-based computational geometry package for constructing and analyzing proximity and biological graphs, facilitating computational experimentation. It provides tools to generate and transform random and structured point sets and to build graphs from them. Its current scope comprises  13 geometric graphs, most of them proximity graphs—such as the Delaunay triangulation, the Gabriel graph, the Relative Neighborhood graph, and the Sphere-of-Influence graph—as well as the complete graph, the Erdős-Rényi random graph and two bio-inspired graphs.


# Statement of need

Proximity graphs are standard objects in computational geometry, spatial statistics, and network-based modeling. Classical examples such as the relative neighborhood graph [@Toussaint1980], beta-skeletons [@Kirkpatrick1983], alpha shapes [@Edelsbrunner1983], unit disk graphs [@Clark1990], nearest-neighbor graphs [@Eppstein1997], and gamma-neighborhood graphs [@Veltkamp1992] are used to study geometric structure, support routing or spatial inference tasks, and build simplified models of interaction in embedded systems. They also appear in empirical and asymptotic analyses of random geometric structures [@Devroye1988].

Applications: clustering and manifold learning [Zemel2004]

Machine learning [Yang2002]

Asymptotic analysis of proximity graphs  [Devroye1988, Chalker1999]

Probabilistic properties of the $k$-nearest-neighbors graph [Eppstein1997]

recomender systems [Mathieson2019]

Street network characterization [Watanabe2010, Osaragi2014, Maniadakis2016]

See references about applications of the SIG (computer vision, cluster analysis, pattern recognition, SIG, modeling visual illusions, streaming process in music perception) in [Toussaint2014SIG]

See references about applications of RNG, GG and $\beta$-skeletons (Morphology and computer vision, geographic analysis, pattern classification) [Jaromczyk2002]

See references about applications of the RNG (vision, cluster analysis, shape boundary detection, visualization and computer graphics, archaeology, natural computing, cosmology, urban planning, machine learning, percolation theory, wireless ad-hoc networks, graph theory ) [Toussaint2014RNG]

graph theory about proximity graphs [Cimikowski1992, Bose2012]

transport and fungi networks [Adamatzky2011]

computational experiment about Asymptotic properties of $\beta$-skeletons [Adamatzky2014, Alonso2019]

# Package overview

# Usage example

# Acknowledgements

# Software design and functionality

The package is centered on a small set of classes. `SetPoints` stores planar coordinates and provides random and structured point generators. `GeometricGraph` wraps an igraph object together with the embedding coordinates, exposing operations such as graph unions, intersections, distance-style comparisons, geometric summaries, and plotting. `ProximityGraph` then specializes this base for graph families whose edges are determined by spatial neighborhood rules. Concrete classes implement individual constructions such as `MST`, `GG`, `RNG`, `Unit_Disk`, `Alpha_Shape`, and `Gamma_Graph`.

This design gives users a consistent workflow:

1. generate or load a planar point set;
2. construct one or more graph families on that same set;
3. compute or compare summary statistics; and
4. visualize or export the resulting geometry.

The package also includes an `Experiment` helper for repeated simulation storing graph configurations and point-generation settings together, then aggregates metrics across runs. 

Optional GIS support is kept separate from the core install. Users who need GeoPandas or Shapely can enable that extra and export edge or polygon geometries, while basic package imports and core graph algorithms remain available without the heavier geospatial stack. 

# Related software

Several existing Python packages provide functionality related to parts of the ProximityGraphs workflow. NetworkX [@Hagberg2008] offers a broad collection of graph algorithms and data structures. igraph [@Csardi2006] provides efficient graph representations and graph-theoretic algorithms. SciPy [@Virtanen2020] includes numerical and spatial routines, including geometric primitives useful for Delaunay triangulations and distance-based computations.

ProximityGraphs is complementary to these tools. Its focus is to provide a domain-specific interface for constructing and experimenting with planar proximity graphs. The package organizes geometric graph construction, point-set handling, visualization, and experimentation around proximity graph use cases.

# Acknowledgements

The authors received no external funding for this work.

# AI usage disclosure

The authors used ChatGPT for assistance with software engineering discussion, documentation drafting, manuscript editing, JOSS-preparation planning, and copy-editing. All AI-assisted outputs were reviewed, edited, and validated by the human authors. The authors made the core design decisions, implemented and tested the software, verified the mathematical and computational claims, and remain fully responsible for the accuracy, originality, licensing, and ethical/legal compliance of the submitted materials.

# References