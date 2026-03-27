---
title: "ProximityGraphs: Python tools for constructing and comparing proximity graphs on planar point sets"
tags:
  - Python
  - computational geometry
  - proximity graphs
  - geometric graphs
authors:
  - name: Héctor Maravillo
    affiliation: 1
    corresponding: true
    orcid: Universidad Autónoma de la Ciudad de México, Mexico
  - name: Diego Villarreal De La Cerda
    affiliation: 2
    orcid: Universidad de las Américas Puebla, México
  - name: Heriberto Espino-Montelongo
    affiliation: 2
    orcid: Universidad de las Américas Puebla, México
date: 28 February 2026
bibliography: paper.bib
---

# Summary

ProximityGraphs is a Python package for constructing, inspecting, and comparing graph families defined on planar point sets. The package combines point-set generators, graph constructors, lightweight experiment tooling, and visualization helpers behind a shared object model. Its current scope includes classical proximity graphs such as Delaunay triangulations, minimum spanning trees, Gabriel graphs, relative neighborhood graphs, unit disk graphs, sphere-of-influence graphs, beta-skeletons, gamma-neighborhood graphs, alpha shapes, alpha hulls, and stepping stone graphs, together with a small collection of bio-inspired models such as a Physarum-like adaptive graph. The implementation relies on widely used scientific Python components including NumPy, SciPy, pandas, matplotlib, and igraph [@Harris2020; @Virtanen2020; @Csardi2006].

The package is designed for exploratory computational geometry rather than as a single-purpose implementation of one graph class. A user can generate or load a planar point pattern, build multiple graph families on the same point set, compare structural summaries, and export or visualize the results with a consistent API. This workflow is useful in teaching, rapid prototyping, and empirical studies where several neighborhood rules must be evaluated side by side.

# Statement of need

Proximity graphs are standard objects in computational geometry, spatial statistics, and network-based modeling. Classical examples such as the relative neighborhood graph [@Toussaint1980], beta-skeletons [@Kirkpatrick1983], alpha shapes [@Edelsbrunner1983], unit disk graphs [@Clark1990], nearest-neighbor graphs [@Eppstein1997], and gamma-neighborhood graphs [@Veltkamp1992] are used to study geometric structure, support routing or spatial inference tasks, and build simplified models of interaction in embedded systems. They also appear in empirical and asymptotic analyses of random geometric structures [@Devroye1988].

In practice, researchers and students often need more than a single implementation of one graph family. A typical workflow involves repeatedly generating planar point sets, constructing several candidate graphs on the same data, comparing graph size or connectivity, and plotting the resulting structures. General scientific Python libraries provide many of the necessary building blocks, but they do not by themselves offer a compact, domain-focused interface for switching among multiple proximity graph definitions while keeping point generation, graph comparison, and plotting consistent.

ProximityGraphs addresses that gap with a single package focused on planar point sets and multiple proximity rules. It provides:

- point-set generation methods for regular and random planar configurations;
- graph constructors exposed as Python classes with shared graph-analysis methods;
- experiment helpers for repeated simulation and metric aggregation; and
- optional geospatial export hooks for workflows that need GeoPandas or Shapely.

This scope is intentionally modest. The package does not claim to be the most optimized implementation of every graph family, nor does it replace full-featured graph-analysis platforms. Its contribution is a reusable and reasonably uniform interface for building and comparing proximity graphs in a single codebase.

# State of the field

The Python ecosystem already contains strong general-purpose tools relevant to this domain. SciPy exposes foundational geometric routines such as Delaunay triangulations and convex hulls through `scipy.spatial` [@Virtanen2020]. NetworkX and igraph provide broad graph data structures and algorithms that support analysis and manipulation once a graph has been constructed [@Hagberg2008; @Csardi2006]. These libraries are appropriate choices for many workflows, and ProximityGraphs depends directly on SciPy and igraph rather than duplicating their lower-level functionality.

However, these libraries are not primarily organized around proximity graph families as a comparative unit of study. A user who wants to move from a Gabriel graph to a relative neighborhood graph, a unit disk graph, an alpha shape, and then a small experiment over repeated point simulations usually has to combine several libraries and custom scripts. ProximityGraphs packages that domain workflow into one library: point generation, graph construction, plotting, common metrics, and experiment bookkeeping are available under one namespace and operate on compatible data structures.

The package also includes simple bio-inspired graph models motivated by adaptive transport networks, including a Physarum-like graph class related to biologically inspired network design rules [@Tero2010]. These models are included as exploratory tools rather than as a claim of biological completeness.

# Software design and functionality

The package is centered on a small set of classes. `SetPoints` stores planar coordinates and provides random and structured point generators. `GeometricGraph` wraps an igraph object together with the embedding coordinates, exposing operations such as graph unions, intersections, distance-style comparisons, geometric summaries, and plotting. `ProximityGraph` then specializes this base for graph families whose edges are determined by spatial neighborhood rules. Concrete classes implement individual constructions such as `MST`, `GG`, `RNG`, `Unit_Disk`, `Alpha_Shape`, and `Gamma_Graph`.

This design gives users a consistent workflow:

1. generate or load a planar point set;
2. construct one or more graph families on that same set;
3. compute or compare summary statistics; and
4. visualize or export the resulting geometry.

The package also includes an `Experiment` helper for repeated simulations. Rather than forcing each user to write one-off loops for parameter sweeps or repeated random trials, the helper stores graph configurations and point-generation settings together, then aggregates metrics across runs. This is useful in classroom demonstrations and exploratory studies where the relative behavior of several graph classes matters more than a single optimized implementation.

Optional GIS support is kept separate from the core install. Users who need GeoPandas or Shapely can enable that extra and export edge or polygon geometries, while basic package imports and core graph algorithms remain available without the heavier geospatial stack. This separation helps keep editable installs and automated testing lighter.

# Research impact / intended use

ProximityGraphs is intended for users who need a practical comparison environment for proximity graphs on planar point sets: instructors preparing examples, students learning the differences among neighborhood rules, and researchers prototyping geometric-network experiments before moving to problem-specific code. The package is especially suitable when the main goal is to compare several graph definitions on shared data rather than to deploy a single graph algorithm at maximum scale.

Because the codebase exposes both graph constructors and lightweight experiment infrastructure, it can also serve as a reproducible supplement for methods sections where proximity graphs are part of a broader computational workflow. The package should therefore be understood as research-enabling software: it lowers the amount of custom scripting required to move from a point pattern to a set of comparable geometric graphs.

# AI usage disclosure

Repository-facing documentation and some draft prose for the JOSS submission materials were prepared with assistance from a generative AI tool and then reviewed in-repository. Scientific claims, package descriptions, and bibliography entries should still be verified by the authors before submission.

# References
