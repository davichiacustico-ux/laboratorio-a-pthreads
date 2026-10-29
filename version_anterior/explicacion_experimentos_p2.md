# Explicación de `experimentos_p2.sh` + `analizar_p2.py`

Dos archivos que trabajan en equipo para hacer los experimentos de la **Parte II (Construcción paralela de un histograma)**:

| Archivo | Lenguaje | Su trabajo |
|---|---|---|
| 🐚 `experimentos_p2.sh` | sh | **Ejecutar y anotar**: compila `p2sec`, `p2mutex` y `p2priv`, los corre y guarda lo que imprimen en `datos_p2.csv` |
| 🐍 `analizar_p2.py` | Python | **Pensar y dibujar**: comprueba que las 10 categorías coincidan y sumen N, calcula speedup y eficiencia de ambas estrategias y dibuja los gráficos |

### Leyenda de colores

| Color | Significado |
|---|---|
| 🔵 <span style="color:#1f6feb">**Azul**</span> | <span style="color:#1f6feb">Versión **secuencial** (`p2sec`)</span> |
| 🟠 <span style="color:#d97706">**Naranja**</span> | <span style="color:#d97706">Estrategia 1: **Mutex compartido** (`p2mutex`)</span> |
| 🟢 <span style="color:#2da44e">**Verde**</span> | <span style="color:#2da44e">Estrategia 2: **Histograma privado por thread** (`p2priv`)</span> |
| 🟣 <span style="color:#8250df">**Morado**</span> | <span style="color:#8250df">Comparación de las 10 categorías, suma == N, speedup y eficiencia</span> |

---

## Idea general (para dummies)

Imagina que tienes `N` exámenes con notas de `0` a `99` y quieres contar cuántos cayeron en cada decena (`0–9`, `10–19`, ..., `90–99`):

<pre>
🐚 experimentos_p2.sh
   Para cada N:
      <span style="color:#1f6feb">🔵 Ejecuta p2sec N          → 1 persona sola cuenta las 10 casillas (referencia Ts)</span>
      Para cada T (1, 2, 4, 8):
         <span style="color:#d97706">🟠 Ejecuta p2mutex N T    → T amigos comparten 1 sola hoja y hacen fila con candado</span>
         <span style="color:#2da44e">🟢 Ejecuta p2priv N T     → cada amigo cuenta en su propia hoja y al final suman las 10 casillas</span>
   Al final llama a Python ↓

🐍 analizar_p2.py
   Lee datos_p2.csv
   Para cada (N, T):
      <span style="color:#8250df">🟣 ¿Las 10 casillas de mutex y privado son idénticas al secuencial?</span>
      <span style="color:#8250df">🟣 ¿La suma de las 10 casillas es exactamente igual a N?</span>
      <span style="color:#8250df">🟣 Calcula Speedup y Eficiencia tanto de Mutex como de Privado</span>
   Guarda resultados_p2.csv y dibuja speedup_p2.png y eficiencia_p2.png
</pre>

---

## Archivos que genera

| Archivo | Lo genera | Contenido |
|---|---|---|
| `datos_p2.csv` | 🐚 sh | Datos en bruto: <span style="color:#1f6feb">5 filas secuenciales</span> + <span style="color:#d97706">20 filas mutex</span> + <span style="color:#2da44e">20 filas privado</span> |
| `resultados_p2.csv` | 🐍 Python | 20 filas comparando <span style="color:#1f6feb">Ts</span>, <span style="color:#d97706">Tp_mutex</span> y <span style="color:#2da44e">Tp_priv</span> con speedup, eficiencia y `OK` |
| `speedup_p2.png` | 🐍 Python | <span style="color:#8250df">Gráfico comparativo de Speedup: Histograma privado vs. Mutex compartido</span> |
| `eficiencia_p2.png` | 🐍 Python | <span style="color:#8250df">Gráfico comparativo de Eficiencia: Histograma privado vs. Mutex compartido</span> |

## Cómo ejecutarlo

```bash
sh experimentos_p2.sh
```
O la versión directa en puro `sh`:
```bash
sh run_p2.sh
```
