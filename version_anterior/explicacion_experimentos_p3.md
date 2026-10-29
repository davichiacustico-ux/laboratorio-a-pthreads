# Explicación de `experimentos_p3.sh` + `analizar_p3.py`

Dos archivos que trabajan en equipo para hacer los experimentos de la **Parte III (Productores y consumidores con buffer acotado)**:

| Archivo | Lenguaje | Su trabajo |
|---|---|---|
| 🐚 `experimentos_p3.sh` | sh | **Ejecutar y anotar**: compila `p3sec` y `p3par`, prueba distintas combinaciones de productores (`P`), consumidores (`C`) y tamaños de buffer (`B`), y guarda todo en `datos_p3.csv` |
| 🐍 `analizar_p3.py` | Python | **Verificar y dibujar**: comprueba que no se haya perdido ni duplicado ningún elemento (`perdidos == 0`, `duplicados == 0`, `suma_prod == suma_cons`), guarda `resultados_p3.csv` y dibuja `tiempos_p3.png` |

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
   Al final llama a Python ↓

🐍 analizar_p3.py
   Lee datos_p3.csv
   Para cada prueba verifica 4 cosas:
      🟣 1. Producidos == 100003 y Consumidos == 100003
      🟣 2. SumaProd == SumaCons (la suma de todos los números coincide)
      🟣 3. Perdidos == 0 (ningún elemento quedó sin consumir)
      🟣 4. Duplicados == 0 (ningún elemento fue consumido dos veces)
   Guarda resultados_p3.csv y dibuja tiempos_p3.png
</pre>

---

## Archivos que genera

| Archivo | Lo genera | Contenido |
|---|---|---|
| `datos_p3.csv` | 🐚 sh | Datos en bruto de las 3 capacidades de buffer × 6 configuraciones `P:C` |
| `resultados_p3.csv` | 🐍 Python | Tabla verificada con `Producidos`, `Consumidos`, `Perdidos`, `Duplicados`, `Ts`, `Tp` y `OK` |
| `tiempos_p3.png` | 🐍 Python | Gráfico del tiempo de ejecución según `P:C` y el tamaño del buffer circular |

## Cómo ejecutarlo

```bash
sh experimentos_p3.sh
```
O la versión directa en puro `sh`:
```bash
sh run_p3.sh
```
