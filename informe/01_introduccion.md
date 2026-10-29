# 1. Entorno de ejecución, métricas y scripts de prueba

## 1.1 Entorno de ejecución

<!-- tabla:entorno -->

| Componente | Valor |
|:--|:--|
| Procesador | Intel(R) Core(TM) i5-10400 CPU @ 2.90GHz |
| Núcleos e hilos | 6 núcleos físicos × 2 hilos por núcleo = 12 CPU lógicas |
| Memoria visible en Linux | 11 GiB |
| Sistema (uname) | Linux 6.18.54.1-microsoft-standard-WSL2 |
| Compilador | gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0, opciones `-O2 -pthread` |
| Mediciones de la Parte I | Thu Oct 29 02:32:57 -05 2026 |
| Mediciones de la Parte II | Thu Oct 29 02:33:11 -05 2026 |
| Mediciones de la Parte III | Thu Oct 29 02:34:25 -05 2026 |

: Equipo donde se ejecutaron las tres partes (de `entorno_p1.txt`, `entorno_p2.txt` y `entorno_p3.txt`).

<!-- /tabla:entorno -->

Las tres partes se midieron en el mismo equipo y en la misma sesión. El procesador tiene 6 núcleos físicos con *hyper-threading* (12 CPU lógicas): con T = 8 hay más threads que núcleos físicos, así que algunos núcleos ejecutan dos threads que comparten sus unidades de cálculo y su caché. Las pruebas corren en Linux dentro de WSL2, una máquina virtual ligera sobre Windows 10 Pro; la memoria visible es la asignada a esa máquina virtual, y crear un thread o despertar a uno que duerme cuesta más que en Linux nativo (secciones 2.3 y 4.3).

## 1.2 Métricas y forma de medir

$$S_T = \frac{T_s}{T_p(T)} \qquad\qquad E_T = \frac{S_T}{T}$$

donde $T_s$ es el tiempo de la versión secuencial, $T_p(T)$ el de la versión paralela con $T$ threads, $S_T$ el *speedup* y $E_T$ la eficiencia.

- **Qué se mide.** En las versiones paralelas el cronómetro incluye crear los threads, esperarlos con `pthread_join` y combinar los resultados parciales, es decir, el costo completo de paralelizar. La generación de los datos no se mide; usa una semilla fija (`srand(42)`) para que todas las versiones reciban exactamente el mismo arreglo.
- **Reloj.** `clock_gettime(CLOCK_MONOTONIC)`, que no salta si se ajusta la hora del sistema. Los tiempos se imprimen con resolución de nanosegundos (`%.9f`).
- **Repeticiones.** Cada programa ejecuta el cálculo una vez de calentamiento (`r = -1`), que no se guarda, y luego 7 veces medidas; se reporta la **mediana** y, como medida de dispersión, la medición mínima y la máxima. La mediana no se deja arrastrar por una ejecución interrumpida por el sistema operativo: con N ≥ 10^7^ la diferencia entre la medición más lenta y la más rápida fue típicamente de 9 a 11 %, pero con N pequeños llegó a 77 %.
- **Threads.** T = 1, 2, 4 y 8, como pide el enunciado.

## 1.3 Compilación y explicación de los scripts (`.sh`)

El flujo de pruebas de cada parte está automatizado en un script de shell POSIX (`experimentos_p1.sh`, `experimentos_p2.sh` y `experimentos_p3.sh`) que se ejecuta con:

```bash
sh experimentos_p1.sh   # datos_p1.csv, resultados_p1.csv, repartos.txt, speedup, eficiencia
sh experimentos_p2.sh   # datos_p2.csv, resultados_p2*.csv, speedup_p2, eficiencia_p2, distribucion_p2
sh experimentos_p3.sh   # datos_p3.csv, resultados_p3.csv, tiempos_p3, cambios_contexto_p3.csv
```

Cada script `.sh` sigue cinco pasos internos:

1. **Formato numérico uniforme (`export LC_ALL=C`):** Fuerza el uso de punto decimal (`.`) en `awk` y en la salida estándar aunque el sistema esté configurado en español, evitando que una coma decimal (`0,054`) rompa las columnas de los archivos CSV.
2. **Compilación verificada (`gcc -O2 -pthread ... || exit 1`):** Compila los programas secuenciales y paralelos con el mismo nivel de optimización (`-O2`). El operador `|| exit 1` detiene inmediatamente el script si `gcc` devuelve algún error.
3. **Captura automática del hardware (`entorno_pN.txt`):** Un bloque agrupado `{ date; uname -sr; lscpu | grep -E ...; free -h; gcc --version | head -n 1; } > entorno_pN.txt` registra la fecha de inicio, kernel/WSL2, modelo de CPU, núcleos físicos e hilos lógicos, memoria RAM y versión de `gcc`.
4. **Extracción de métricas a CSV (`guardar_fila` con `awk`):** Los programas en C imprimen cada resultado en una línea con formato `Clave = Valor` (por ejemplo, `Suma = 489014` o `Tiempo paralelo (mediana de 7) = 0.000060700 s`). En el script, la función `guardar_fila()` captura la salida del programa y la procesa con `awk`:
   ```sh
   guardar_fila() {
       VALORES=$(echo "$4" | awk -F'= ' '/^(Suma|Minimo|Maximo|Promedio|Tiempo)/ {sub(/ s$/, "", $2); printf ",%s", $2}')
       echo "$1,$2,$3$VALORES" >> datos_p1.csv
   }
   ```
   `awk -F'= '` divide cada línea por el separador `= `, filtra únicamente las líneas de interés mediante una expresión regular, elimina la unidad `" s"` al final de los tiempos con `sub(/ s$/, "", $2)` y concatena los valores separados por comas para escribir una fila completa en `datos_pN.csv`.
5. **Barrido de combinaciones y llamada a Python:**
   - En **`experimentos_p1.sh`**: recorre `VALORES_N="1000 100000 1000000 1000003 10000000 100000000"`. Por cada `N`, ejecuta una vez `./p1sec "$N"` y luego barre `VALORES_T="1 2 4 8"` ejecutando `./p1par "$N" "$T"`. De la misma salida de `p1par` filtra con `grep '^Thread [0-9]'` los rangos `[inicio, fin)` asignados a cada hilo y los guarda en `repartos.txt`. Finalmente ejecuta `python3 analizar_p1.py`.
   - En **`experimentos_p2.sh`**: define la función auxiliar `experimento()`, que para una distribución (`u` o `s`) y un tamaño `N` corre primero `./p2sec "$N" "$dist"` y después, dentro de un bucle `for T in 1 2 4 8`, ejecuta las tres variantes paralelas (`./p2mutex`, `./p2mutexcat` y `./p2priv`). El script llama a `experimento u "$N"` para los cinco tamaños (`1000` a `10000000`) y luego a `experimento s 10000000` para evaluar los datos sesgados. Al terminar invoca `python3 analizar_p2.py`.
   - En **`experimentos_p3.sh`**: recorre `BUFFERS="8 64 1024"` con `TOTAL=100003`. Para cada tamaño de buffer ejecuta `./p3sec "$TOTAL" "$B"` y luego recorre `PARES_PC="1:1 2:2 4:4 8:8 2:4 4:2"`, separando productores y consumidores mediante expansión de parámetros POSIX (`P=${PC%:*}` extrae lo que está antes de `:` y `C=${PC#*:}` lo que está después) para invocar `./p3par "$TOTAL" "$P" "$C" "$B"`. Al final ejecuta `python3 analizar_p3.py` y `python3 cambios_contexto_p3.py > cambios_contexto_p3.csv`.

Cada programa también se puede compilar y ejecutar manualmente por separado:

```bash
gcc -O2 -pthread p1sec.c -o p1sec            # ./p1sec N
gcc -O2 -pthread p1par.c -o p1par            # ./p1par N T
gcc -O2 -pthread p2sec.c -o p2sec            # ./p2sec N [u|s]
gcc -O2 -pthread p2mutex.c -o p2mutex        # ./p2mutex N T [u|s]
gcc -O2 -pthread p2mutexcat.c -o p2mutexcat  # ./p2mutexcat N T [u|s]
gcc -O2 -pthread p2priv.c -o p2priv          # ./p2priv N T [u|s]
gcc -O2 -pthread p3sec.c -o p3sec            # ./p3sec TOTAL TAM_BUFFER
gcc -O2 -pthread p3par.c -o p3par            # ./p3par TOTAL P C TAM_BUFFER
```

El argumento opcional `u|s` de la Parte II elige datos uniformes (por defecto) o sesgados (sección 3.4).
