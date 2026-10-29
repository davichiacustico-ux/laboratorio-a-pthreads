"""
Parte I - Paso 2 de 2: ANALIZAR los experimentos

Lee datos_p1.csv (lo genera experimentos_p1.sh) y:
  1. compara cada ejecucion paralela con la secuencial del mismo N
  2. calcula speedup y eficiencia con las medianas de los tiempos
  3. guarda resultados_p1.csv y muestra la tabla (tiempos en ms)
  4. dibuja speedup y eficiencia (.png y figuras/*.svg para el informe)

Uso: python3 analizar_p1.py
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")  # no abre ventanas, solo guarda las imagenes
import matplotlib.pyplot as plt

ESTADISTICAS = ["suma", "minimo", "maximo", "promedio"]


# 1. Leer los datos en bruto
secuencial = {}  # N -> fila del secuencial
paralelo = []    # filas del paralelo
with open("datos_p1.csv") as f:
    for fila in csv.DictReader(f):
        if fila["version"] == "secuencial":
            secuencial[fila["N"]] = fila
        else:
            paralelo.append(fila)


# 2. Comparar y calcular speedup y eficiencia
resultados = []
for par in paralelo:
    sec = secuencial[par["N"]]  # el secuencial con el mismo N
    T = int(par["T"])
    ts = float(sec["tiempo"])
    tp = float(par["tiempo"])

    speedup = ts / tp
    eficiencia = speedup / T
    correcto = all(sec[e] == par[e] for e in ESTADISTICAS)

    resultados.append({
        "N": int(par["N"]),
        "T": T,
        "suma": sec["suma"],
        "minimo": sec["minimo"],
        "maximo": sec["maximo"],
        "promedio": sec["promedio"],
        "Ts": sec["tiempo"],  # medianas, tal cual las imprimio el programa (0.000001234, no 1.234e-06)
        "Tp": par["tiempo"],
        "Tp_min": par["t_min"],
        "Tp_max": par["t_max"],
        "speedup": round(speedup, 3),
        "eficiencia": round(eficiencia, 3),
        "correcto": "OK" if correcto else "ERROR",
    })


# 3. Guardar y mostrar la tabla
with open("resultados_p1.csv", "w", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=resultados[0].keys())
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"{'N':>11} {'T':>2} {'Ts (ms)':>10} {'Tp (ms)':>10} {'Speedup':>8} {'Eficiencia':>10}  Correcto")
for r in resultados:
    print(f"{r['N']:>11} {r['T']:>2} {float(r['Ts']) * 1e3:>10.4f} {float(r['Tp']) * 1e3:>10.4f} "
          f"{r['speedup']:>8.3f} {r['eficiencia']:>10.3f}  {r['correcto']}")

errores = sum(r["correcto"] == "ERROR" for r in resultados)
print()
print("Todo coincide" if errores == 0 else f"ATENCION: {errores} resultados no coinciden")
print("Tabla guardada en resultados_p1.csv")


# 4. Graficos: una linea por cada N. Cada N tiene el mismo color y marcador en las
#    Partes I y II (paleta categorica validada para daltonismo, en orden fijo)
COLOR_N = {1000: "#2a78d6", 100000: "#eb6834", 1000000: "#1baf7a",
           1000003: "#eda100", 10000000: "#e87ba4", 100000000: "#008300"}
MARCADOR_N = {1000: "o", 100000: "s", 1000000: "^", 1000003: "D", 10000000: "v", 100000000: "P"}
VALORES_T = sorted({r["T"] for r in resultados})
VALORES_N = sorted({r["N"] for r in resultados})


def guardar(fig, nombre):
    """Guarda el grafico como PNG (para verlo rapido) y como SVG en figuras/ (para el informe)."""
    os.makedirs("figuras", exist_ok=True)
    fig.savefig(f"{nombre}.png", dpi=150, bbox_inches="tight")
    fig.savefig(f"figuras/{nombre}.svg", bbox_inches="tight")
    plt.close(fig)
    print(f"Grafico guardado en {nombre}.png y figuras/{nombre}.svg")


def graficar(columna, titulo, ideal, nombre):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Linea de referencia: lo que se lograria en un mundo perfecto
    ax.plot(VALORES_T, ideal, "--", color="#999999", linewidth=1.5, label="Ideal")

    for n in VALORES_N:
        valores = [r[columna] for r in resultados if r["N"] == n]
        ax.plot(VALORES_T, valores, "-", marker=MARCADOR_N[n], color=COLOR_N[n],
                linewidth=2, markersize=7, label=f"N = {n:,}".replace(",", " "))

    ax.set_title(titulo, loc="left", fontsize=13)
    ax.set_xlabel("Threads (T)")
    ax.set_xticks(VALORES_T)
    ax.grid(axis="y", color="#e5e5e5")
    for borde in ["top", "right"]:
        ax.spines[borde].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1, 1))

    fig.tight_layout()
    guardar(fig, nombre)


graficar("speedup", "Speedup (Ts / Tp)", VALORES_T, "speedup")
graficar("eficiencia", "Eficiencia (Speedup / T)", [1] * len(VALORES_T), "eficiencia")
