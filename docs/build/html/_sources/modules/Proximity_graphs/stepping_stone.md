# Stepping_Stone

A **d-diversion / stepping-stone proximity graph** defined by **d-neighborhood emptiness**: two sites $p,q$ are adjacent when a super-elliptic “lens” neighborhood around segment $pq$ contains at most $k$ other sites.

## Constructor

```python
Stepping_Stone(setpoints, d=2, k=0, closed=True)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points $P=\{p_1,\dots,p_n\}\subset\mathbb{R}^D$.
- **d** (float): Shape exponent (must satisfy $d\ge 1$).
  - $d=2$: the neighborhood equals the **Gabriel diametral ball** (see Special Cases).
  - Larger $d$ yields a *larger* neighborhood, typically producing a *sparser* graph for fixed $k$.
- **k** (int): Allowed number of other sites inside the neighborhood (must satisfy $k\ge 0$).
- **closed** (bool): If True, uses $\le$ (closed neighborhood). If False, uses $<$ (open neighborhood).

## Mathematical Definition:

Let $P\subset\mathbb{R}^D$ with Euclidean norm $\|\cdot\|$. For two distinct sites $p,q\in P$, define the **d-diversion neighborhood**

$$
N_d(p,q)=\begin{cases}
\{x\in\mathbb{R}^D: \|x-p\|^d+\|x-q\|^d\le \|p-q\|^d\}, & \text{if }\texttt{closed}=\texttt{True},\\
\{x\in\mathbb{R}^D: \|x-p\|^d+\|x-q\|^d< \|p-q\|^d\}, & \text{if }\texttt{closed}=\texttt{False}.
\end{cases}
$$

Define the interior count

$$
\operatorname{count}_d(p,q)=\bigl|\{x\in P\setminus\{p,q\}: x\in N_d(p,q)\}\bigr|.
$$

The stepping-stone graph is

$$
\mathrm{SS}_{d,k}(P)=\{(p,q): \operatorname{count}_d(p,q)\le k\}.
$$

## Special Cases:

- **$d=2$ (Gabriel neighborhood):** writing $m=(p+q)/2$ and $L=\|p-q\|$, the inequality
  $\|x-p\|^2+\|x-q\|^2\le L^2$ is equivalent to $\|x-m\|\le L/2$. Hence
  $N_2(p,q)$ is the **diametral ball** with center $m$ and radius $L/2$, i.e. the Gabriel test region.
- **Limits:**
  - $d\to 1^+$: by the triangle inequality, $\|x-p\|+\|x-q\|\le\|p-q\|$ forces $x$ to lie essentially on the segment $[p,q]$ (degenerate “thin corridor”).
  - $d\to\infty$: the condition approaches $\max(\|x-p\|,\|x-q\|)\le \|p-q\|$, i.e. $x$ lies in the **intersection** of the two radius-$\|p-q\|$ balls centered at $p$ and $q$ (a lens).

## Properties:

- **Monotonicity in $d$:** for fixed $p,q$, increasing $d$ enlarges $N_d(p,q)$, so the emptiness constraint is stricter; thus edges typically **disappear** as $d$ increases (for fixed $k$).
- **Monotonicity in $k$:** increasing $k$ relaxes the emptiness constraint; thus edges typically **appear** as $k$ increases.
- **Containment for $d\ge 2$:** in fixed dimension, $\ell_p$ norm monotonicity implies
  $N_2(p,q)\subseteq N_d(p,q)$ for $d\ge 2$. Consequently, when $k=0$,
  $\mathrm{SS}_{d,0}(P)\subseteq \mathrm{GG}(P)$ for $d\ge 2$, and in nondegenerate 2D cases this is also a subgraph of the Delaunay triangulation.

## Value Errors / Limitations:

- Raises `ValueError` if $d < 1$.
- Raises `ValueError` if $k < 0$.
- Raises `TypeError` if `k` is not an integer.
- Raises `TypeError` if `closed` is not boolean.

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.uniform_square(n=300, seed=11)

G1 = pg.Stepping_Stone(pts, d=1.3, k=0, closed=True)
G2 = pg.Stepping_Stone(pts, d=2.0, k=0, closed=False)
G3 = pg.Stepping_Stone(pts, d=3.0, k=0, closed=True)
G4 = pg.Stepping_Stone(pts, d=3.0, k=2, closed=True)

graphs = [G1, G2, G3, G4]
pg.draw_grid(graphs, 2, 2, figsize=(10, 10), details=True)
```

![Example graphs](images/stepping_stone.png)
