# Test Suite

Este directorio contiene las pruebas automatizadas de `proximitygraphs`.
La suite esta pensada para preparar el paquete para release en PyPI sin hacer
que las dependencias opcionales sean obligatorias.

## Como correr las pruebas

Core, sin GIS:

```bash
python -m pytest -q -m "not gis"
```

Todas las pruebas disponibles en el entorno actual:

```bash
python -m pytest -q
```

Pruebas GIS opcionales:

```bash
python -m pytest -q -m gis
```

Reporte de warnings visible:

```bash
python -m pytest -q -W default
```

Validacion de dependencias instaladas:

```bash
python -m pip check
```

## Politica de warnings

La politica esta configurada en `pyproject.toml`, en
`[tool.pytest.ini_options]`.

La regla es:

- Warnings de `proximitygraphs` deben fallar la suite.
- Warnings de dependencias de terceros deben quedar visibles en el log.
- No se deben silenciar warnings propios del paquete.
- Si un warning externo se vuelve muy ruidoso, se debe filtrar de forma
  especifica y documentada, no con una supresion global.

Actualmente pytest trata como error:

```toml
error::DeprecationWarning:proximitygraphs.*
error::FutureWarning:proximitygraphs.*
```

Y muestra warnings generales de deprecacion/futuro con:

```toml
default::DeprecationWarning
default::FutureWarning
```

En CI hay un job separado llamado `warnings` que ejecuta:

```bash
python -m pytest -q -m "not gis" -W default
```

Ese job existe para que cambios en `numpy`, `scipy`, `pandas`, `igraph`,
`matplotlib` u otras dependencias sean visibles antes de que se conviertan en
errores reales.

## Archivos de pruebas

### `test_package.py`

Smoke tests basicos del paquete. Verifica importacion, version publica y un
caso pequeno de `Unit_Disk` sobre una grilla `2x2`.

### `test_core_api.py`

Cobertura deterministica de la API publica principal:

- `import proximitygraphs`
- existencia y tipo de `__version__`
- constructores de `SetPoints`
- reproducibilidad con seeds
- invariantes generales de grafos
- `MST`, `Unit_Disk`, `GG`, `RNG`, `DelaunayG`, `Gamma_Graph`
- configuraciones pequenas como 2 puntos, triangulo, grilla `2x2` y `3x3`
- importacion core sin requerir `geopandas` ni `shapely`

### `test_edge_cases.py`

Casos limite y validacion de parametros:

- constructores de puntos invalidos
- `SetPoints` con tipo incorrecto
- parametros invalidos en `Unit_Disk`, `Beta_Skeleton` y `Gamma_Graph`
- comportamiento con pocos puntos
- puntos colineales
- puntos duplicados en grafos basados en distancias
- dibujo con backend no interactivo, sin abrir ventanas

Los grafos basados en Delaunay pueden levantar `scipy.spatial.QhullError` en
entradas degeneradas. Esos tests documentan el comportamiento actual sin
cambiar la API.

### `test_gis.py`

Pruebas opcionales de exportacion GIS. Estan marcadas con:

```python
pytestmark = pytest.mark.gis
```

Tambien usan:

```python
pytest.importorskip("geopandas")
pytest.importorskip("shapely")
```

Esto permite que la suite core corra sin dependencias GIS. Estas pruebas cubren:

- `to_gpd_lines`
- `to_gpd_polygons`
- tipo de retorno `GeoDataFrame`
- numero de geometria/filas
- columna `geometry`
- caso de grafo vacio
- CRS actual, que por ahora es `None`

### `test_examples_and_graphs.py`

Pruebas de ejemplos y comportamientos estables:

- reproducibilidad de `uniform_square`
- estructura de `MST` sobre grilla `2x2`
- casos extremos documentados de `Gamma_Graph`
- salida esperada del ejemplo `examples/quickstart.py`

### `test_gamma_graph_fast_path.py`

Pruebas especificas del camino rapido de `Gamma_Graph`:

- compara fast path contra fallback
- verifica `Gamma_Graph.from_graph`
- documenta cuando debe usarse fallback
- cubre entradas degeneradas que no deben romper el constructor

### `test_proximity_graph_regression.py`

Suite de regresion sembrada contra `tests/data/proximity_graph_regression.json`.
Construye varios grafos, corre `Experiment`, y compara:

- puntos generados
- orden de grafos
- metricas enteras y flotantes
- listas de aristas

Esta prueba protege contra cambios accidentales en algoritmos, metricas o
ordenamiento de resultados.

### `benchmark_gamma_graph_fast_path.py`

Script de benchmark manual para comparar rendimiento del fast path de
`Gamma_Graph`. No es parte de la suite normal de pytest.

## CI

El workflow principal esta en `.github/workflows/ci.yml`.

La estructura esperada es:

- `test`: matriz Python 3.10-3.14, dependencias core y dev, excluye GIS.
- `warnings`: Python estable, warnings visibles, falla en warnings propios.
- `gis`: Python estable, instala `.[dev,gis]`, corre solo `-m gis`.
- `build`: construye paquete, corre `twine check` y smoke test de instalacion.

El workflow de documentacion esta en `.github/workflows/docs.yml` y tambien
ejecuta `python -m pip check`.

## Smoke test de instalacion

El script `scripts/smoke_test_install.py` valida una instalacion ligera del
paquete:

- importa `proximitygraphs`
- imprime la version
- crea un conjunto pequeno de puntos deterministico
- construye `MST`, `Unit_Disk`, `GG`, `RNG`, `DelaunayG` y `Gamma_Graph`
- verifica invariantes simples

No abre ventanas, no usa red y no requiere dependencias GIS.
