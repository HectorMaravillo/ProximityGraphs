References
==========

This page lists the main theoretical, algorithmic, and software references
used by the Proximity Graphs library.

Classical proximity graphs and computational geometry
-----------------------------------------------------

The Gabriel graph originates in the statistical geography work of
:cite:t:`Gabriel1969`, with later analysis by :cite:t:`Matula1980`.
The relative neighborhood graph was introduced by :cite:t:`Toussaint1980`
and further surveyed by :cite:t:`Jaromczyk2002`.

Alpha-shapes and related shape reconstruction methods are associated with
:cite:t:`Edelsbrunner1983`, while computational morphology and related
geometric frameworks are represented by :cite:t:`Kirkpatrick1985`,
:cite:t:`Radke1988`, and :cite:t:`Toussaint1988`.

Several expected-size and structural results for geometric graphs are
developed in :cite:t:`Devroye1988`, :cite:t:`Cimikowski1992`,
:cite:t:`Eppstein1997`, and :cite:t:`Chalker1999`.

Voronoi diagrams and Delaunay triangulations are classical geometric
structures used throughout the library; see :cite:t:`Aurenhammer2000`
and :cite:t:`deBerg2008`.

Specialized proximity graph families
------------------------------------

Unit disk graphs are treated in :cite:t:`Clark1990`.

The gamma-neighborhood graph implemented in this library follows
:cite:t:`Veltkamp1992`.

Elliptic Gabriel graphs and empty-ellipse graphs are represented by
:cite:t:`Park2006` and :cite:t:`Devillers2008`.

Empty-region graphs and related locality frameworks are discussed in
:cite:t:`Cardinal2009`, :cite:t:`Bose2010`, and :cite:t:`Bose2012`.

Beta-skeleton behavior and spectral properties are represented by
:cite:t:`Adamatzky2014` and :cite:t:`Alonso2019`.

Sphere-of-influence and relative-neighborhood applications are represented
by :cite:t:`Toussaint2014SIG` and :cite:t:`Toussaint2014RNG`.

For broader algorithmic background on proximity algorithms, see
:cite:t:`Mitchell2018`.

Machine learning, clustering, and manifold learning
---------------------------------------------------

Applications of proximity graphs to clustering and machine learning include
:cite:t:`Yang2002` and :cite:t:`Zemel2004`.

Biological and adaptive networks
--------------------------------

The biologically inspired graph components are motivated by adaptive network
models such as :cite:t:`Tero2010` and slime-mould transport approximations
such as :cite:t:`Adamatzky2011`.

Spatial networks, roads, and movement corridors
-----------------------------------------------

Applications of proximity graphs to road networks and movement corridors are
represented by :cite:t:`Watanabe2010`, :cite:t:`Osaragi2014`,
:cite:t:`Maniadakis2016`, :cite:t:`Kannangara2018`, and
:cite:t:`Kannangara2019`.

Software and scientific computing
---------------------------------

The library depends on standard scientific Python and graph-computing tools.
Relevant software references include :cite:t:`Csardi2006`,
:cite:t:`Hagberg2008`, :cite:t:`Harris2020`, and :cite:t:`Virtanen2020`.

General introductions
---------------------

For a general introduction to proximity graphs, see :cite:t:`Mathieson2019`.

Bibliography
------------

.. bibliography:: ../biblio.bib
   :style: plain