Título:
Proximity Graphs: construcción de gráficas de proximidad y sus características asintóticas

Coautores:
Diego Villarreal de la Cerda, Héctor Saib Maravillo Gómez

Keywords:
Gráficas de proximidad, kernels de región vacía, propiedades asintóticas, gráficas geométricos aleatorias, longitud y grado esperado

Resumen:
Dada una nube finita de puntos $V$, una gráfica de proximidad conecta pares de puntos $p,q\in V$ mediante una regla geométrica local, generalmente la exclusión de otros puntos dentro de una región parametrizada por la distancia entre p y q. Ejemplos de estas gráficas son la gráfica de Gabriel (GG), $\beta$-esqueleto, la vecindad relativa (RNG) y familias tipo Stepping Stone graph. Sus características dependen del tipo de región que las define, por lo cual es posible comparar sus propiedades topológicas y geométricas (grado, conexidad, longitud, etc.) para diferente tipos de procesos de puntos, cuando $n=|V|$ crece asintóticamente.

En este trabajo se presenta una librería en Python para construir, visualizar y experimentar con múltiples gráficas de proximidad en $\mathbb{R}^{2}$ proporcionando una API común. Además, la contribución teórica central es que se obtienen expresiones explícitas para áreas de dos familias: 
i) el $\beta$-lune del $\beta$-esqueleto
ii) el Stepping Stone Diversion del Stepping-Stone

El área de estos kernels o regiones determina las características topológicas y geométricas de las gráficas de proximidad, por ejemplo, la distribución de la longitud de las aristas o el grado esperado.  Su estudio computacional y teórico permite calibrar parámetros para obtener gráficas que describan relaciones de vecindad y se usen como estructuras base para tareas de modelación espacial, interpolación/clusterización geométrica y análisis de redes en datos de puntos (p.ej., sensores, movilidad urbana o patrones espaciales)