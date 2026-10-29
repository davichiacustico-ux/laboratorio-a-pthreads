# Versión anterior (respaldo del 29/10/2026)

Copia de los archivos tal como estaban antes de corregir el laboratorio. Las
mediciones de esta versión **no son comparables entre sí**:

- **Parte I** (`datos_p1.csv`, `entorno.txt`): Intel Core Ultra 9 285 del laboratorio,
  22/10/2026.
- **Partes II y III** (`datos_p2.csv`, `datos_p3.csv`): Intel Core i5-10400 con WSL2,
  29/10/2026 a las 01:47, según las marcas de tiempo de los archivos. `entorno.txt`
  no describe este equipo.
- Cada tiempo es **una sola medición**, tomada con `CLOCK_REALTIME` e impresa con 6
  decimales (resolución de 1 µs).

`run_p1.sh`, `run_p2.sh`, `run_p3.sh` y `explicacion_run_p1.md` eran una segunda forma
de correr los experimentos que sobrescribía `resultados_p*.csv` con otras columnas. Se
reemplazaron por `experimentos_p*.sh` + `analizar_p*.py`.
