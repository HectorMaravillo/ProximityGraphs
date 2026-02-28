Título:

ProximityG: una herramienta en Python para explorar gráficas de proximidad y sus propiedades asintóticas.


Resumen

Dado un conjunto discreto de puntos $V$ en $R^n$, una gráfica de proximidad es una gráfica geométrica cuyo conjunto de vértices es $V$, y donde se establece una arista entre dos puntos si se satisface una relación geométrica local, usualmente definida por la exclusión de otros puntos de $V$ en una región determinada por la distancia entre ambos puntos. Ejemplos representativos incluyen la gráfica de Gabriel (GG), la gráfica de vecindad relativa (RNG), el diagrama de Delaunay y los $\beta$-esqueletos. En 1980, Godfried Toussaint planteó el siguiente problema, si $n$ puntos son generados aleatoriamente conforme a una cierta distribución, ¿cuál es la probabilidad de que ocurra cierto evento en la gráfica de proximidad de dichos puntos? Por ejemplo, ¿cuál es la probabilidad de que dicha gráfica sea un árbol? En esta plática se presentará una nueva librería de Python ‘ProximityG’, diseñada para construir y visualizar 15 gráficas de proximidad en $R^2$, y realizar experimentos sobre sus características asintóticas. Se ilustra su aplicación con la exploración computacional de algunas propiedades asintóticas de las gráficas de proximidad, como su grado y longitud esperada, y se compararán con algunos resultados teóricos conocidos.


Expositores: Héctor Saib Maravillo Gómez

Co-autores: Diego Villareal de la Cerda y Heriberto Espino Montelongo