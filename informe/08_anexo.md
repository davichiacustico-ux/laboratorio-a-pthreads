# Anexo A. Archivos del laboratorio y repositorio

Repositorio público con todo el código, scripts, mediciones, figuras y comparativas:
[`https://github.com/davichiacustico-ux/laboratorio-a-pthreads`](https://github.com/davichiacustico-ux/laboratorio-a-pthreads)

| Archivo | Contenido |
|:--|:--|
| `p1sec.c`, `p1par.c` | Parte I: estadísticas, versión secuencial y paralela |
| `p2sec.c`, `p2mutex.c`, `p2mutexcat.c`, `p2priv.c` | Parte II: histograma secuencial, con mutex global, con un mutex por categoría y privado por thread |
| `p3sec.c`, `p3par.c` | Parte III: buffer circular secuencial y con productores y consumidores |
| `experimentos_p1.sh`, `experimentos_p2.sh`, `experimentos_p3.sh` | Compilan, registran el equipo (`entorno_pN.txt`), ejecutan todas las combinaciones y llaman al análisis |
| `analizar_p1.py`, `analizar_p2.py`, `analizar_p3.py` | Verifican los resultados, calculan speedup y eficiencia y dibujan los gráficos |
| `cambios_contexto_p3.py` | Cuenta cuántas veces se duermen los threads de la Parte III |
| `datos_p*.csv`, `repartos.txt`, `cambios_contexto_p3.csv` | Mediciones en bruto |
| `resultados_p*.csv` | Mediciones verificadas, con speedup y eficiencia |
| `figuras/*.svg` y `*.png` | Gráficos (SVG para este informe, PNG para verlos rápido) |
| `informe/` | Fuente de este informe; `informe/tablas.py` genera todas sus tablas desde los CSV |
| `Laboratorio_A_Explicado.md`, `explicacion_experimentos_p*.md` | Material de estudio con explicaciones paso a paso |
| `prueba_sin_calentamiento/` | Experimento comparativo sin vuelta de calentamiento (`r = 0..6` y 1.ª vuelta en frío vs. `r = -1`) |
| `version_anterior/` | Respaldo de la primera versión (mediciones de dos equipos y de una sola repetición) |

: Archivos entregados en el repositorio.
