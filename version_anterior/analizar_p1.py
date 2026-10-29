"""
Parte I - Paso 2 de 2: ANALIZAR los experimentos

Lee datos_p1.csv (lo genera experimentos_p1.sh) y:
  1. compara cada ejecucion paralela con la secuencial del mismo N
  2. calcula speedup y eficiencia
  3. guarda resultados_p1.csv y muestra la tabla
  4. dibuja speedup.png y eficiencia.png

Uso: python3 analizar_p1.py
"""
import csv

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
        "Ts": sec["tiempo"],  # se guarda tal cual lo imprimio el programa (0.000001, no 1e-06)
        "Tp": par["tiempo"],
        "speedup": round(speedup, 3),
        "eficiencia": round(eficiencia, 3),
        "correcto": "OK" if correcto else "ERROR",
    })


# 3. Guardar y mostrar la tabla
with open("resultados_p1.csv", "w", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=resultados[0].keys())
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"{'N':>11} {'T':>2} {'Ts (s)':>10} {'Tp (s)':>10} {'Speedup':>8} {'Eficiencia':>10}  Correcto")
for r in resultados:
    print(f"{r['N']:>11} {r['T']:>2} {r['Ts']:>10} {r['Tp']:>10} "
          f"{r['speedup']:>8.3f} {r['eficiencia']:>10.3f}  {r['correcto']}")

errores = sum(r["correcto"] == "ERROR" for r in resultados)
print()
print("Todo coincide" if errores == 0 else f"ATENCION: {errores} resultados no coinciden")
print("Tabla guardada en resultados_p1.csv")


# 4. Graficos: una linea por cada N
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
VALORES_T = sorted({r["T"] for r in resultados})
VALORES_N = sorted({r["N"] for r in resultados})


def graficar(columna, titulo, ideal, archivo):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Linea de referencia: lo que se lograria en un mundo perfecto
    ax.plot(VALORES_T, ideal, "--", color="#999999", linewidth=1.5, label="Ideal")

    for color, n in zip(COLORES, VALORES_N):
        valores = [r[columna] for r in resultados if r["N"] == n]
        ax.plot(VALORES_T, valores, "-o", color=color, linewidth=2, markersize=6,
                label=f"N = {n:,}".replace(",", "."))

    ax.set_title(titulo, loc="left", fontsize=13)
    ax.set_xlabel("Threads (T)")
    ax.set_xticks(VALORES_T)
    ax.grid(axis="y", color="#e5e5e5")
    for borde in ["top", "right"]:
        ax.spines[borde].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1, 1))

    fig.tight_layout()
    fig.savefig(archivo, dpi=150)
    plt.close(fig)
    print(f"Grafico guardado en {archivo}")


graficar("speedup", "Speedup (Ts / Tp)", VALORES_T, "speedup.png")
graficar("eficiencia", "Eficiencia (Speedup / T)", [1] * len(VALORES_T), "eficiencia.png")
