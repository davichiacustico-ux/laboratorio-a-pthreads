# Explicación de `run_p1.sh`

Script de la **Parte I**: ejecuta la versión secuencial y la paralela, compara sus resultados y calcula speedup y eficiencia.

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

<pre>
Para cada N (tamaño del arreglo):
   <span style="color:#1f6feb">🔵 Una persona sola suma los números         → anoto resultado y tiempo Ts</span>
   Para cada T (1, 2, 4, 8 amigos):
      <span style="color:#2da44e">🟢 T amigos se reparten los números          → anoto resultado y tiempo Tp</span>
      <span style="color:#8250df">🟣 ¿Dieron lo mismo?                          → OK / ERROR</span>
      <span style="color:#8250df">🟣 ¿Cuánto más rápido fueron los amigos?     → Speedup = Ts / Tp</span>
      <span style="color:#8250df">🟣 ¿Qué tan bien se aprovechó cada amigo?    → Eficiencia = Speedup / T</span>
</pre>

El secuencial se ejecuta **una vez por N** (no depende de T); el paralelo, **cuatro veces por N** (una por cada T).

---

## Paso 0 — Preparación ⚪ (líneas 1–14)

```sh
#!/bin/sh
export LC_ALL=C
```
- `#!/bin/sh` indica que el archivo se ejecuta con `sh`.
- `LC_ALL=C` hace que los números usen **punto decimal** (`0.054`) en vez de coma (`0,054`). Como tu Linux está en español, sin esto `awk` escribiría comas y **rompería el CSV**, que separa columnas con comas.

```sh
VALORES_N="1000 100000 1000000 1000003 10000000 100000000"
VALORES_T="1 2 4 8"
```
- Los **tamaños del arreglo** que se prueban. `1000003` está a propósito: **no es múltiplo de 2, 4 ni 8**, para probar el reparto no exacto.
- Las **cantidades de threads** que pide el PDF.

```sh
resultados() { ... }
tiempo()     { ... }
```
Dos funciones "lectoras". Los programas imprimen algo así:
```
Suma     = 489014
Minimo   = 0
Maximo   = 999
Promedio = 489.0140
Tiempo ... = 0.000041 s
```
- `resultados` toma el texto después del `= ` en las líneas Suma, Minimo, Maximo y Promedio → `"489014 0 999 489.0140 "`.
- `tiempo` toma el número de la línea Tiempo y le quita la `" s"` → `0.000041`.

Sirven **para los dos programas** (<span style="color:#1f6feb">p1sec</span> y <span style="color:#2da44e">p1par</span>), porque ambos imprimen con el mismo formato.

---

## Paso 1 — Compilar (líneas 16–18)

<span style="color:#1f6feb">🔵 `gcc -O2 -pthread p1sec.c -o p1sec || exit 1` → compila la versión **secuencial**.</span>

<span style="color:#2da44e">🟢 `gcc -O2 -pthread p1par.c -o p1par || exit 1` → compila la versión **paralela**.</span>

- Las **dos con las mismas opciones** (`-O2 -pthread`), para que la comparación sea justa.
- `|| exit 1` significa: *"si falla la compilación, detén el script"*.

---

## Paso 2 — Datos del equipo ⚪ (líneas 20–21)

```sh
{ date; lscpu | grep ...; free -h; gcc --version | head -n 1; } > entorno.txt
```
Guarda en `entorno.txt` la fecha, el procesador y sus núcleos, la memoria RAM y la versión de gcc. Es para la sección **"Introducción y entorno de ejecución"** del informe.

---

## Paso 3 — Preparar los archivos de salida ⚪ (líneas 24–25)

```sh
echo "N,T,Suma,Minimo,Maximo,Promedio,Ts,Tp,Speedup,Eficiencia,Correcto" > resultados_p1.csv
: > repartos.txt
```
- Crea `resultados_p1.csv` con la **fila de títulos** (`>` borra lo que hubiera antes).
- Crea `repartos.txt` **vacío**.

---

## Paso 4 — El bucle principal (líneas 27–44)

### 4a. Bucle de N y versión secuencial (líneas 27–30)

<pre>
for N in $VALORES_N; do
<span style="color:#1f6feb">    SEC=$(./p1sec "$N")            # 🔵 ejecuta el secuencial y guarda TODO lo que imprime
    RES_SEC=$(resultados "$SEC")   # 🔵 se queda con "suma min max promedio"
    TS=$(tiempo "$SEC")            # 🔵 se queda con el tiempo secuencial → Ts</span>
</pre>

<span style="color:#1f6feb">🔵 Por cada tamaño N, el **secuencial se ejecuta una sola vez**. Su resultado (`RES_SEC`) es la **referencia correcta** y su tiempo (`TS`) es el **Ts** de la fórmula del speedup.</span>

### 4b. Bucle de T y versión paralela (líneas 32–34)

<pre>
    for T in $VALORES_T; do
<span style="color:#2da44e">        PAR=$(./p1par "$N" "$T")   # 🟢 ejecuta el paralelo con T threads
        TP=$(tiempo "$PAR")        # 🟢 se queda con el tiempo paralelo → Tp</span>
</pre>

<span style="color:#2da44e">🟢 Para el mismo N, el **paralelo se ejecuta 4 veces** (T = 1, 2, 4, 8). Cada vez se guarda su tiempo **Tp**.</span>

### 4c. Comparación (línea 36)

<pre>
<span style="color:#8250df">        if [ "$RES_SEC" = "$(resultados "$PAR")" ]; then CORRECTO=OK; else CORRECTO=ERROR; fi</span>
</pre>

<span style="color:#8250df">🟣 Compara el texto de los resultados:</span>

| | Texto comparado |
|---|---|
| <span style="color:#1f6feb">🔵 Secuencial</span> | <span style="color:#1f6feb">`489014 0 999 489.0140`</span> |
| <span style="color:#2da44e">🟢 Paralelo</span> | <span style="color:#2da44e">`489014 0 999 489.0140`</span> |
| <span style="color:#8250df">🟣 Resultado</span> | <span style="color:#8250df">Idénticos → **OK**</span> |

<span style="color:#8250df">Si suma, mínimo, máximo **y** promedio son exactamente iguales → `OK`; si cualquiera difiere → `ERROR`. Esto cumple el punto del PDF: *"Comprobar que la versión paralela produce resultados correctos"*.</span>

### 4d. Speedup y eficiencia (línea 39)

<pre>
<span style="color:#8250df">        CALC=$(awk ... 'BEGIN { s = ts / tp; printf "%.3f,%.3f", s, s / t }')</span>
</pre>

`sh` no sabe hacer cuentas con decimales, por eso se usa `awk` como calculadora:

- <span style="color:#8250df">🟣 **Speedup** = <span style="color:#1f6feb">Ts</span> / <span style="color:#2da44e">Tp</span> → cuántas veces más rápido fue el paralelo.</span>
- <span style="color:#8250df">🟣 **Eficiencia** = Speedup / T → qué fracción del ideal se logró (1.000 = perfecto).</span>

Ejemplo real (N = 100.000.000, T = 8):
<span style="color:#1f6feb">Ts = 0,055</span> y <span style="color:#2da44e">Tp = 0,012</span> → <span style="color:#8250df">Speedup = 4,56 y Eficiencia = 4,56 / 8 = 0,57</span>.

### 4e. Guardar la fila (líneas 41–42)

```sh
echo "$N,$T,...,$TS,$TP,$CALC,$CORRECTO" >> resultados_p1.csv
{ echo "N = $N, T = $T"; echo "$PAR" | grep '^Thread [0-9]'; echo; } >> repartos.txt
```
- Agrega **una fila** al CSV (`>>` agrega al final sin borrar).
- <span style="color:#2da44e">🟢 De la salida del **paralelo** saca solo las líneas `Thread 0: [...]`, `Thread 1: [...]`… y las agrega a `repartos.txt`. Así queda registrado **qué parte del arreglo le tocó a cada thread**.</span>

---

## Paso 5 — Mostrar el resumen ⚪ (líneas 47–48)

```sh
column -t -s, resultados_p1.csv
grep -q ERROR resultados_p1.csv && echo "ATENCION: ..." || echo "Todo coincide"
```
- `column` muestra el CSV como tabla alineada en la terminal.
- Si aparece alguna vez la palabra `ERROR` en el CSV, avisa; si no, dice **"Todo coincide"**.

---

## Archivos que genera

| Archivo | Contenido | Viene de |
|---|---|---|
| `entorno.txt` | Datos del equipo | ⚪ Paso 2 |
| `resultados_p1.csv` | Una fila por cada combinación de N y T (6 × 4 = 24) | <span style="color:#1f6feb">🔵 Ts y resultados</span> + <span style="color:#2da44e">🟢 Tp</span> + <span style="color:#8250df">🟣 speedup, eficiencia y OK</span> |
| `repartos.txt` | Rango del arreglo de cada thread | <span style="color:#2da44e">🟢 Salida de `p1par`</span> |

### Columnas del CSV

| Columna | Qué es | Origen |
|---|---|---|
| N | Tamaño del arreglo | ⚪ |
| T | Número de threads | <span style="color:#2da44e">🟢</span> |
| Suma, Minimo, Maximo, Promedio | Estadísticas del arreglo | <span style="color:#1f6feb">🔵 secuencial (el paralelo dio lo mismo si dice OK)</span> |
| Ts | Tiempo secuencial | <span style="color:#1f6feb">🔵</span> |
| Tp | Tiempo paralelo | <span style="color:#2da44e">🟢</span> |
| Speedup | Ts / Tp | <span style="color:#8250df">🟣</span> |
| Eficiencia | Speedup / T | <span style="color:#8250df">🟣</span> |
| Correcto | OK / ERROR | <span style="color:#8250df">🟣</span> |

---

## Cómo ejecutarlo

```bash
cd /home/alumno16/Documentos/Davichi/lab05Alvaro
sh run_p1.sh
```
