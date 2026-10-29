# Explicación de `experimentos_p2.sh` + `analizar_p2.py`

Dos archivos que trabajan en equipo para hacer los experimentos de la **Parte II (Construcción paralela de un histograma)**:

| Archivo | Lenguaje | Su trabajo |
|---|---|---|
| 🐚 `experimentos_p2.sh` | sh | **Ejecutar y anotar**: compila `p2sec`, `p2mutex`, `p2mutexcat` y `p2priv`, los corre con datos uniformes y sesgados y guarda lo que imprimen en `datos_p2.csv` |
| 🐍 `analizar_p2.py` | Python | **Pensar y dibujar**: comprueba que las 10 categorías coincidan y sumen N, calcula speedup y eficiencia de las tres estrategias, compara datos uniformes con sesgados y dibuja los gráficos |

### Leyenda de colores

| Color | Significado |
|---|---|
| 🔵 <span style="color:#1f6feb">**Azul**</span> | <span style="color:#1f6feb">Versión **secuencial** (`p2sec`)</span> |
| 🟠 <span style="color:#d97706">**Naranja**</span> | <span style="color:#d97706">Estrategia 1: **Mutex global** (`p2mutex`): un solo candado para las 10 casillas</span> |
| 🔴 <span style="color:#cf222e">**Rojo**</span> | <span style="color:#cf222e">Estrategia 1b: **Mutex por categoría** (`p2mutexcat`): un candado por casilla</span> |
| 🟢 <span style="color:#2da44e">**Verde**</span> | <span style="color:#2da44e">Estrategia 2: **Histograma privado por thread** (`p2priv`)</span> |
| 🟣 <span style="color:#8250df">**Morado**</span> | <span style="color:#8250df">Comparación de las 10 categorías, suma == N, speedup y eficiencia</span> |

---

## Idea general (para dummies)

Imagina que tienes `N` exámenes con notas de `0` a `99` y quieres contar cuántos cayeron en cada decena (`0–9`, `10–19`, ..., `90–99`):

<pre>
🐚 experimentos_p2.sh
   Para cada N, con datos uniformes (u):
      <span style="color:#1f6feb">🔵 Ejecuta p2sec N u            → 1 persona sola cuenta las 10 casillas (referencia Ts)</span>
      Para cada T (1, 2, 4, 8):
         <span style="color:#d97706">🟠 Ejecuta p2mutex N T u     → T amigos comparten 1 hoja y hacen fila con 1 solo candado</span>
         <span style="color:#cf222e">🔴 Ejecuta p2mutexcat N T u  → T amigos comparten 1 hoja, pero cada casilla tiene su candado</span>
         <span style="color:#2da44e">🟢 Ejecuta p2priv N T u      → cada amigo cuenta en su propia hoja y al final suman las 10 casillas</span>
   Para N = 10 000 000 repite todo con datos sesgados (s): ~91 % de las notas caen en 0–9
   Al final llama a Python ↓

🐍 analizar_p2.py
   Lee datos_p2.csv
   Para cada (distribución, N, T):
      <span style="color:#8250df">🟣 ¿Las 10 casillas de las 3 estrategias son idénticas a las del secuencial con los mismos datos?</span>
      <span style="color:#8250df">🟣 ¿La suma de las 10 casillas es exactamente igual a N?</span>
      <span style="color:#8250df">🟣 Con datos uniformes: Speedup y Eficiencia de las 3 estrategias</span>
      <span style="color:#8250df">🟣 Con N = 10 000 000: tiempos con datos uniformes vs. sesgados</span>
   Guarda resultados_p2.csv y resultados_p2_dist.csv y dibuja speedup_p2, eficiencia_p2 y distribucion_p2
</pre>

Cada programa repite su medición **7 veces** (más una de calentamiento que no se anota) e imprime la **mediana**, la mínima y la máxima, igual que en la Parte I.

### ¿Para qué sirve el mutex por categoría?
Con **un solo candado** (`p2mutex`), dos amigos chocan **siempre**, aunque uno anote en la casilla 2 y el otro en la 7. Con **un candado por casilla** (`p2mutexcat`) solo chocan si los dos anotan **en la misma casilla**. Cada casilla (su contador y su candado) ocupa su propia línea de caché de 64 bytes (`_Alignas(64)`), para que dos casillas distintas no se estorben por compartir línea (*false sharing*).

### ¿Y los datos sesgados?
La función `generar()` recibe la distribución:
- `u` (uniforme): las 100 notas tienen la misma probabilidad → cada casilla recibe ~10 % de los datos.
- `s` (sesgada): 9 de cada 10 notas salen entre 0 y 9 → **~91 % de los datos van a la casilla 0**.

Con datos sesgados, casi todos los amigos quieren el **mismo** candado (el de la casilla 0), así que el mutex por categoría se comporta casi como el mutex global. Así se responde con mediciones la pregunta *"¿Cómo influye la distribución de los valores de entrada en la contención?"*.

---

## Archivos que genera

| Archivo | Lo genera | Contenido |
|---|---|---|
| `entorno_p2.txt` | 🐚 sh | Datos del equipo |
| `datos_p2.csv` | 🐚 sh | Datos en bruto: 5 N uniformes × (<span style="color:#1f6feb">1 secuencial</span> + 4 T × 3 estrategias) = 65 filas, más 13 filas sesgadas (N = 10 000 000) |
| `resultados_p2.csv` | 🐍 Python | 20 filas (datos uniformes) con <span style="color:#1f6feb">Ts</span>, los Tp de <span style="color:#d97706">mutex</span>, <span style="color:#cf222e">mutexcat</span> y <span style="color:#2da44e">privado</span>, su speedup, su eficiencia y `OK` |
| `resultados_p2_dist.csv` | 🐍 Python | 8 filas (N = 10 000 000): tiempos con datos uniformes y sesgados y cuántos valores cayeron en la casilla 0 |
| `speedup_p2.png` y `figuras/speedup_p2.svg` | 🐍 Python | <span style="color:#8250df">Speedup, un panel por estrategia</span> |
| `eficiencia_p2.png` y `figuras/eficiencia_p2.svg` | 🐍 Python | <span style="color:#8250df">Eficiencia, un panel por estrategia</span> |
| `distribucion_p2.png` y `figuras/distribucion_p2.svg` | 🐍 Python | <span style="color:#8250df">Uniforme vs. sesgada, en escala logarítmica, con el secuencial como referencia</span> |

### Columnas de `datos_p2.csv` (sh)

| Columna | Qué es |
|---|---|
| version | `secuencial`, `mutex`, `mutexcat` o `privado` |
| dist | `u` (uniforme) o `s` (sesgada) |
| N, T | Tamaño del arreglo y threads (T = 1 en el secuencial) |
| c0 … c9 | Conteo de cada casilla (`0–9` … `90–99`) |
| total | Suma de las 10 casillas (debe ser N) |
| tiempo, t_min, t_max | Mediana, mínima y máxima de las 7 mediciones, en segundos |

## Cómo ejecutarlo

Desde la carpeta del laboratorio en Linux o WSL:
```bash
sh experimentos_p2.sh
```
Solo el análisis y los gráficos (usa el `datos_p2.csv` que ya existe):
```bash
python3 analizar_p2.py
```
Un programa suelto, por ejemplo el mutex por categoría con 4 threads y datos sesgados:
```bash
./p2mutexcat 10000000 4 s
```
