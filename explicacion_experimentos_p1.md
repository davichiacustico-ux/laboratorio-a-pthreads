# Explicación de `experimentos_p1.sh` + `analizar_p1.py`

Dos archivos que trabajan en equipo para hacer los experimentos de la **Parte I**:

| Archivo | Lenguaje | Su trabajo |
|---|---|---|
| 🐚 `experimentos_p1.sh` | sh | **Ejecutar y anotar**: compila, corre los programas y guarda lo que imprimen |
| 🐍 `analizar_p1.py` | Python | **Pensar y dibujar**: compara, calcula speedup y eficiencia, y hace los gráficos |

### Leyenda de colores

| Color | Significado |
|---|---|
| 🔵 <span style="color:#1f6feb">**Azul**</span> | <span style="color:#1f6feb">Todo lo de la versión **secuencial** (`p1sec`)</span> |
| 🟢 <span style="color:#2da44e">**Verde**</span> | <span style="color:#2da44e">Todo lo de la versión **paralela** (`p1par`)</span> |
| 🟣 <span style="color:#8250df">**Morado**</span> | <span style="color:#8250df">Donde se **juntan las dos**: comparación, speedup y eficiencia</span> |
| ⚪ Normal | Preparación general (no es de ninguna de las dos) |

> Para ver los colores en VS Code abre la vista previa con **Ctrl + Shift + V**.

---

## Idea general (para dummies)

Piensa en un **cocinero** y un **contador**:

- 🐚 El **sh** es el cocinero: prepara todo, cocina (ejecuta los programas) y **anota en una libreta** lo que salió, sin hacer cuentas.
- 🐍 **Python** es el contador: lee la libreta, **revisa que todo cuadre**, hace las cuentas y dibuja los gráficos.

<pre>
🐚 experimentos_p1.sh
   Para cada N:
      <span style="color:#1f6feb">🔵 Ejecuta p1sec N          → anota una fila "secuencial" en datos_p1.csv</span>
      Para cada T (1, 2, 4, 8):
         <span style="color:#2da44e">🟢 Ejecuta p1par N T      → anota una fila "paralelo" en datos_p1.csv</span>
         <span style="color:#2da44e">🟢 Copia el reparto       → repartos.txt</span>
   Al final llama a Python ↓

🐍 analizar_p1.py
   Lee datos_p1.csv
   Para cada fila <span style="color:#2da44e">paralela</span>, busca la <span style="color:#1f6feb">secuencial</span> con el mismo N:
      <span style="color:#8250df">🟣 ¿Dieron lo mismo?        → OK / ERROR</span>
      <span style="color:#8250df">🟣 Speedup    = Ts / Tp</span>
      <span style="color:#8250df">🟣 Eficiencia = Speedup / T</span>
   Guarda resultados_p1.csv, muestra la tabla y dibuja speedup y eficiencia (.png y figuras/*.svg)
</pre>

### ¿Por qué 7 repeticiones y la mediana?
Un tiempo medido una sola vez es una foto movida: en ese instante el sistema operativo pudo
estar haciendo otra cosa, la CPU pudo estar subiendo su frecuencia o la caché estaba fría.
Por eso cada programa:
1. Hace **una vuelta de calentamiento** (`r = -1`) que no se anota.
2. Mide **7 vueltas** y las ordena.
3. Imprime la **mediana** (la del medio, la 4.ª de 7), la **mínima** y la **máxima**.

La mediana no se deja arrastrar por una vuelta rara (por ejemplo, una que tardó el doble
porque Windows despertó algo), mientras que el promedio sí. La mínima y la máxima muestran
cuánto varió la medición.

### ¿Por qué separarlo así?
- `sh` es muy bueno **ejecutando programas**, pero malo para cuentas con decimales.
- Python es muy bueno **haciendo cuentas y gráficos**, pero más verboso para ejecutar programas.
- Además, si solo quieres **rehacer los gráficos**, no tienes que volver a correr todos los experimentos: basta con `python3 analizar_p1.py`.

---

# 🐚 Parte 1: `experimentos_p1.sh`

## Paso 0 — Preparación ⚪ (líneas 1–21)

```sh
export LC_ALL=C
VALORES_N="1000 100000 1000000 1000003 10000000 100000000"
VALORES_T="1 2 4 8"
```
- `LC_ALL=C` → usa **punto decimal** (`0.054`) y no coma. Tu Linux está en español, y sin esto la coma rompería el CSV.
- `VALORES_N` → tamaños del arreglo. `1000003` está a propósito: **no es múltiplo de 2, 4 ni 8**.
- `VALORES_T` → cantidades de threads que pide el PDF.

### La función `guardar_fila` (líneas 18–21)
```sh
guardar_fila() {
    VALORES=$(echo "$4" | awk -F'= ' '/^(Suma|Minimo|Maximo|Promedio|Tiempo)/ {sub(/ s$/, "", $2); printf ",%s", $2}')
    echo "$1,$2,$3$VALORES" >> datos_p1.csv
}
```
Recibe 4 datos: **versión**, **N**, **T** y **todo lo que imprimió el programa**. Con eso arma una fila del CSV.

Ejemplo: si `p1sec 1000` imprime
```
Suma     = 489014
Minimo   = 0
Maximo   = 999
Promedio = 489.0140
Tiempo secuencial (mediana de 7) = 0.000000606 s
Tiempo minimo = 0.000000505 s
Tiempo maximo = 0.000000607 s
```
- `awk` toma lo que está después de cada `= ` (y le quita la `" s"` final) → `,489014,0,999,489.0140,0.000000606,0.000000505,0.000000607`
- y la función escribe → `secuencial,1000,1,489014,0,999,489.0140,0.000000606,0.000000505,0.000000607`

Ojo: la línea `Minimo   = 0` es el **menor dato** del arreglo, mientras que `Tiempo minimo` es la **medición más rápida**; no se confunden porque `awk` toma las líneas en el orden en que salen.

La misma función sirve para <span style="color:#1f6feb">🔵 el secuencial</span> y para <span style="color:#2da44e">🟢 el paralelo</span>, porque los dos imprimen con el mismo formato.

## Paso 1 — Compilar (líneas 23–26)

<span style="color:#1f6feb">🔵 `gcc -O2 -pthread p1sec.c -o p1sec || exit 1` → compila la versión **secuencial**.</span>

<span style="color:#2da44e">🟢 `gcc -O2 -pthread p1par.c -o p1par || exit 1` → compila la versión **paralela**.</span>

Las dos con **las mismas opciones**, para que la comparación sea justa. `|| exit 1` significa *"si falla, detente"*.

## Paso 2 — Datos del equipo ⚪ (líneas 28–29)

Guarda en `entorno_p1.txt` la fecha, el sistema (`uname`: dice si es Linux nativo o WSL), el procesador, la memoria y la versión de gcc, para la sección **"Entorno de ejecución"** del informe. Cada parte guarda su propio archivo (`entorno_p1.txt`, `entorno_p2.txt`, `entorno_p3.txt`), así se nota si alguna se corrió en otro equipo.

## Paso 3 — Ejecutar los experimentos (líneas 31–44)

```sh
echo "version,N,T,suma,minimo,maximo,promedio,tiempo,t_min,t_max" > datos_p1.csv
: > repartos.txt
```
Crea `datos_p1.csv` con su fila de títulos y deja `repartos.txt` vacío.

<pre>
for N in $VALORES_N; do
    echo "Ejecutando N = $N"
<span style="color:#1f6feb">    guardar_fila secuencial "$N" 1 "$(./p1sec "$N")"          # 🔵 una vez por N</span>

    for T in $VALORES_T; do
<span style="color:#2da44e">        SALIDA=$(./p1par "$N" "$T")                            # 🟢 cuatro veces por N
        guardar_fila paralelo "$N" "$T" "$SALIDA"
        { echo "N = $N, T = $T"; echo "$SALIDA" | grep '^Thread [0-9]'; echo; } >> repartos.txt</span>
    done
done
</pre>

- <span style="color:#1f6feb">🔵 El **secuencial se ejecuta 1 vez por N**, porque no depende de los threads. En su fila se anota `T = 1` (una sola persona trabajando).</span>
- <span style="color:#2da44e">🟢 El **paralelo se ejecuta 4 veces por N** (T = 1, 2, 4, 8).</span>
- <span style="color:#2da44e">🟢 De la salida del paralelo se copian a `repartos.txt` las líneas `Thread 0: [...]`, `Thread 1: [...]`…, que muestran qué parte del arreglo le tocó a cada thread.</span>

En total: 6 filas <span style="color:#1f6feb">secuenciales</span> + 24 filas <span style="color:#2da44e">paralelas</span> = **30 filas** en `datos_p1.csv`.

## Paso 4 — Llamar a Python (línea 50)

```sh
python3 analizar_p1.py
```
El sh termina su trabajo y le pasa la posta a Python.

---

# 🐍 Parte 2: `analizar_p1.py`

Usa solo dos librerías:
- `csv` → leer y escribir archivos CSV (viene con Python).
- `matplotlib` → dibujar los gráficos (ya instalada en tu equipo).

`matplotlib.use("Agg")` hace que los gráficos **se guarden como imagen** sin abrir ventanas.

## Paso 1 — Leer los datos (líneas 22–30)

```python
secuencial = {}  # N -> fila del secuencial
paralelo = []    # filas del paralelo
```
Lee `datos_p1.csv` fila por fila y las separa en dos cajas:

- <span style="color:#1f6feb">🔵 `secuencial` es un **diccionario**: dado un N, te devuelve su fila secuencial. Ejemplo: `secuencial["1000"]` → la fila del secuencial con N = 1000.</span>
- <span style="color:#2da44e">🟢 `paralelo` es una **lista** con todas las filas paralelas.</span>

`csv.DictReader` convierte cada fila en un diccionario, por eso se puede escribir `fila["tiempo"]` en vez de `fila[7]`.

## Paso 2 — Comparar y calcular (líneas 33–59)

Para cada fila <span style="color:#2da44e">paralela</span>, busca su pareja <span style="color:#1f6feb">secuencial</span> con el mismo N:

<pre>
for par in paralelo:
    sec = secuencial[par["N"]]          # busca la pareja
<span style="color:#1f6feb">    ts = float(sec["tiempo"])           # 🔵 Ts</span>
<span style="color:#2da44e">    tp = float(par["tiempo"])           # 🟢 Tp</span>

<span style="color:#8250df">    speedup = ts / tp                   # 🟣
    eficiencia = speedup / T            # 🟣
    correcto = all(sec[e] == par[e] for e in ESTADISTICAS)   # 🟣</span>
</pre>

- `float(...)` convierte el texto `"0.053409"` en un número con el que se puede hacer cuentas.
- <span style="color:#8250df">🟣 **Speedup = <span style="color:#1f6feb">Ts</span> / <span style="color:#2da44e">Tp</span>** → cuántas veces más rápido fue el paralelo.</span>
- <span style="color:#8250df">🟣 **Eficiencia = Speedup / T** → qué tan bien se aprovechó cada thread (1,0 = perfecto).</span>
- <span style="color:#8250df">🟣 **`correcto`** → `all(...)` es verdadero solo si **suma, mínimo, máximo y promedio** son iguales en las dos versiones.</span>

| Estadística | <span style="color:#1f6feb">🔵 Secuencial</span> | <span style="color:#2da44e">🟢 Paralelo</span> | <span style="color:#8250df">🟣 ¿Igual?</span> |
|---|---|---|---|
| suma | <span style="color:#1f6feb">489014</span> | <span style="color:#2da44e">489014</span> | <span style="color:#8250df">✅</span> |
| minimo | <span style="color:#1f6feb">0</span> | <span style="color:#2da44e">0</span> | <span style="color:#8250df">✅</span> |
| maximo | <span style="color:#1f6feb">999</span> | <span style="color:#2da44e">999</span> | <span style="color:#8250df">✅</span> |
| promedio | <span style="color:#1f6feb">489.0140</span> | <span style="color:#2da44e">489.0140</span> | <span style="color:#8250df">✅ → **OK**</span> |

Ejemplo real (N = 100.000.000, T = 8):
<span style="color:#1f6feb">Ts = 67.6 ms</span> y <span style="color:#2da44e">Tp = 18.9 ms</span> → <span style="color:#8250df">Speedup = 3.58 y Eficiencia = 3.58 / 8 = 0.45</span>.

## Paso 3 — Guardar y mostrar la tabla (líneas 62–76)

- `csv.DictWriter` escribe todos los resultados en **`resultados_p1.csv`**.
- Los `print(f"...")` muestran la tabla alineada en la terminal, con los tiempos pasados a milisegundos (`float(r['Ts']) * 1e3`; `:>10.4f` significa *"alineado a la derecha, 10 espacios, 4 decimales"*).
- Al final cuenta los `ERROR`: si no hay ninguno, imprime **"Todo coincide"**.

## Paso 4 — Gráficos (líneas 79–121)

La función `graficar(...)` dibuja **una línea por cada N** y se usa dos veces:

| Gráfico | Eje Y | Línea "Ideal" (gris punteada) |
|---|---|---|
| `speedup.png` | <span style="color:#8250df">Speedup</span> | Diagonal: con T threads, speedup T |
| `eficiencia.png` | <span style="color:#8250df">Eficiencia</span> | Horizontal en 1,0: cada thread rinde al 100 % |

Detalles de la función:
- `ax.plot(..., "--", ...)` → dibuja la línea ideal punteada.
- `ax.plot(..., marker=MARCADOR_N[n], color=COLOR_N[n], ...)` → dibuja cada N con línea, color y marcador propios. Cada N tiene **el mismo color y el mismo marcador en las Partes I y II** (por ejemplo, N = 10 000 000 es siempre rosado con triángulo hacia abajo), y el marcador permite distinguir las líneas aunque se imprima en blanco y negro.
- `ax.spines[...]` → quita los bordes de arriba y de la derecha para que se vea más limpio.
- `guardar(fig, nombre)` → guarda `nombre.png` (150 dpi, para verlo rápido) y `figuras/nombre.svg` (vectorial, el que usa el informe en PDF).

### Cómo leer los gráficos
- Cuanto **más cerca de la línea gris** esté una línea de color, mejor se aprovechan los threads.
- Con **N chico** (1.000 y 100.000) las líneas quedan pegadas abajo: crear threads cuesta más que el cálculo.
- Con **N grande** el speedup sube, pero **nunca alcanza el ideal**, y la eficiencia **baja** al agregar threads.

---

## Archivos que genera

| Archivo | Lo genera | Contenido |
|---|---|---|
| `entorno_p1.txt` | 🐚 sh | Datos del equipo |
| `datos_p1.csv` | 🐚 sh | Datos en bruto: <span style="color:#1f6feb">6 filas secuenciales</span> + <span style="color:#2da44e">24 filas paralelas</span> |
| `repartos.txt` | 🐚 sh | <span style="color:#2da44e">Rango del arreglo de cada thread</span> |
| `resultados_p1.csv` | 🐍 Python | 24 filas con <span style="color:#1f6feb">Ts</span>, <span style="color:#2da44e">Tp</span>, <span style="color:#8250df">speedup, eficiencia y OK/ERROR</span> |
| `speedup.png` y `figuras/speedup.svg` | 🐍 Python | <span style="color:#8250df">Gráfico de speedup vs. threads</span> |
| `eficiencia.png` y `figuras/eficiencia.svg` | 🐍 Python | <span style="color:#8250df">Gráfico de eficiencia vs. threads</span> |

### Columnas de `datos_p1.csv` (sh)

| Columna | Qué es |
|---|---|
| version | <span style="color:#1f6feb">`secuencial`</span> o <span style="color:#2da44e">`paralelo`</span> |
| N | Tamaño del arreglo |
| T | Número de threads (<span style="color:#1f6feb">1 en el secuencial</span>) |
| suma, minimo, maximo, promedio | Lo que calculó el programa |
| tiempo | Mediana de las 7 mediciones, en segundos |
| t_min, t_max | La medición más rápida y la más lenta de las 7 |

### Columnas de `resultados_p1.csv` (Python)

| Columna | Qué es |
|---|---|
| N, T | Tamaño y threads |
| suma, minimo, maximo, promedio | <span style="color:#1f6feb">Del secuencial</span> (el paralelo dio lo mismo si dice OK) |
| Ts | <span style="color:#1f6feb">🔵 Tiempo secuencial</span> |
| Tp | <span style="color:#2da44e">🟢 Tiempo paralelo (mediana)</span> |
| Tp_min, Tp_max | <span style="color:#2da44e">🟢 Medición paralela más rápida y más lenta</span> |
| speedup | <span style="color:#8250df">🟣 Ts / Tp</span> |
| eficiencia | <span style="color:#8250df">🟣 Speedup / T</span> |
| correcto | <span style="color:#8250df">🟣 OK / ERROR</span> |

---

## Cómo ejecutarlo

Todo de una vez (experimentos + análisis + gráficos), desde la carpeta del laboratorio en Linux o WSL:
```bash
sh experimentos_p1.sh
```

Solo el análisis y los gráficos (usa el `datos_p1.csv` que ya existe):
```bash
python3 analizar_p1.py
```
