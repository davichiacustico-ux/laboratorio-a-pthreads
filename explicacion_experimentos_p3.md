# Explicación de `experimentos_p3.sh` + `analizar_p3.py`

Dos archivos que trabajan en equipo para hacer los experimentos de la **Parte III (Productores y consumidores con buffer acotado)**:

| Archivo | Lenguaje | Su trabajo |
|---|---|---|
| 🐚 `experimentos_p3.sh` | sh | **Ejecutar y anotar**: compila `p3sec` y `p3par`, prueba distintas combinaciones de productores (`P`), consumidores (`C`) y tamaños de buffer (`B`), y guarda todo en `datos_p3.csv` |
| 🐍 `analizar_p3.py` | Python | **Verificar y dibujar**: comprueba que no se haya perdido ni duplicado ningún elemento en ninguna de las 8 ejecuciones de cada prueba, guarda `resultados_p3.csv` y dibuja `tiempos_p3` |

---

## Idea general (para dummies)

Piensa en una **panadería con una vitrina circular de tamaño fijo (`Buffer`)**:
- Los **Productores (`P`)** son los panaderos: hornean panes numerados del `0` al `TOTAL - 1` y los ponen en la vitrina. Si la vitrina está **llena**, se duermen en la variable de condición `no_lleno` hasta que alguien saque un pan.
- Los **Consumidores (`C`)** son los clientes: sacan panes de la vitrina y anotan qué número de pan les tocó (`vistos[item]++`). Si la vitrina está **vacía**, se duermen en `no_vacio` hasta que un panadero meta un pan.
- El **Mutex (`candado`)** asegura que dos manos nunca metan o saquen pan de la vitrina al mismo instante.

<pre>
🐚 experimentos_p3.sh
   Para cada tamaño de Buffer (8, 64, 1024):
      🔵 Ejecuta p3sec 100003 Buffer          → referencia secuencial
      Para cada pareja P:C (1:1, 2:2, 4:4, 8:8, 2:4, 4:2):
         🟢 Ejecuta p3par 100003 P C Buffer   → P productores y C consumidores
   (cada programa trabaja 8 veces por dentro: 1 de calentamiento + 7 medidas, y verifica las 8)
   Al final llama a Python ↓

🐍 analizar_p3.py
   Lee datos_p3.csv
   Para cada prueba verifica:
      🟣 1. Producidos == 100003, Consumidos == 100003 y el buffer terminó vacío (EnBuffer == 0)
      🟣 2. SumaProd == SumaCons == 0 + 1 + ... + 100002 = 5 000 250 003
      🟣 3. Perdidos == 0 (ningún elemento quedó sin consumir)
      🟣 4. Duplicados == 0 (ningún elemento fue consumido dos veces)
      🟣 5. RepFallidas == 0 (ninguna de las 8 ejecuciones falló alguna de las anteriores)
   Guarda resultados_p3.csv y dibuja tiempos_p3
</pre>

### ¿Qué cambia al repetir 8 veces?
Antes de cada ejecución, `p3par` deja el buffer vacío (`in = out = cuenta = 0`) y pone `vistos[]` en cero (esto no se mide). Después de cada ejecución revisa `vistos[]`: si en **alguna** de las 8 hubo un perdido, un duplicado, un elemento olvidado en el buffer o sumas distintas, suma 1 a `RepFallidas`. Así cada configuración se comprueba 8 veces, no una.

### ¿Por qué un gráfico de puntos y en escala logarítmica?
- Las configuraciones `P:C` no tienen orden (`2P-4C` no va "después" de `8P-8C`): unirlas con líneas sugeriría una tendencia que no existe. Cada punto es la **mediana** de las 7 mediciones y la barrita vertical va de la **más rápida** a la **más lenta**.
- Los tiempos van de milisegundos (buffer 1024) a segundos (buffer 8): en escala lineal los puntos del buffer 1024 quedarían pegados al cero.
- La línea gris punteada es el **secuencial**, para ver de un vistazo que aquí el paralelo es más lento.

---

## Archivos que genera

| Archivo | Lo genera | Contenido |
|---|---|---|
| `entorno_p3.txt` | 🐚 sh | Datos del equipo |
| `datos_p3.csv` | 🐚 sh | Datos en bruto: 3 buffers × (1 secuencial + 6 configuraciones `P:C`) = 21 filas |
| `resultados_p3.csv` | 🐍 Python | 18 filas verificadas con `Producidos`, `Consumidos`, `EnBuffer`, `Perdidos`, `Duplicados`, `RepFallidas`, `Ts`, `Tp` (mediana, mínima y máxima) y `OK` |
| `tiempos_p3.png` y `figuras/tiempos_p3.svg` | 🐍 Python | Tiempo según `P:C` y el tamaño del buffer circular |
| `cambios_contexto_p3.csv` | 🐍 `cambios_contexto_p3.py` (paso 5 del sh) | Cuántas veces se durmieron los threads en cada configuración (cambios de contexto voluntarios, medidos con `getrusage`): explica por qué 2P–2C es la más lenta |

## Cómo ejecutarlo

Desde la carpeta del laboratorio en Linux o WSL:
```bash
sh experimentos_p3.sh
```
Solo el análisis y el gráfico (usa el `datos_p3.csv` que ya existe):
```bash
python3 analizar_p3.py
```
