"""
Parte II - Paso 2 de 2: ANALIZAR los experimentos del histograma

Lee datos_p2.csv (lo genera experimentos_p2.sh) y:
  1. compara cada ejecucion paralela (mutex y privado) con la secuencial del mismo N
  2. verifica que las 10 categorias coincidan y que su suma sea igual a N
  3. calcula speedup y eficiencia para ambas estrategias
  4. guarda resultados_p2.csv y muestra la tabla
  5. dibuja speedup_p2.png y eficiencia_p2.png

Uso: python3 analizar_p2.py
"""
import csv

import matplotlib
matplotlib.use("Agg")  # no abre ventanas, solo guarda las imagenes
import matplotlib.pyplot as plt

CATEGORIAS = [f"c{i}" for i in range(10)] + ["total"]


# 1. Leer los datos en bruto
secuencial = {}  # N -> fila del secuencial
mutex = {}       # (N, T) -> fila de mutex compartido
privado = {}     # (N, T) -> fila de histograma privado

with open("datos_p2.csv") as f:
    for fila in csv.DictReader(f):
        v = fila["version"]
        if v == "secuencial":
            secuencial[fila["N"]] = fila
        elif v == "mutex":
            mutex[(fila["N"], fila["T"])] = fila
        elif v == "privado":
            privado[(fila["N"], fila["T"])] = fila


# 2. Comparar y calcular speedup y eficiencia de ambas estrategias
resultados = []
for (n_str, t_str), prv in privado.items():
    sec = secuencial[n_str]
    mut = mutex[(n_str, t_str)]

    N = int(n_str)
    T = int(t_str)
    ts = float(sec["tiempo"])
    tp_mut = float(mut["tiempo"])
    tp_prv = float(prv["tiempo"])

    sp_mut = ts / tp_mut
    ef_mut = sp_mut / T
    sp_prv = ts / tp_prv
    ef_prv = sp_prv / T

    ok_mut = all(sec[c] == mut[c] for c in CATEGORIAS) and int(mut["total"]) == N
    ok_prv = all(sec[c] == prv[c] for c in CATEGORIAS) and int(prv["total"]) == N

    resultados.append({
        "N": N,
        "T": T,
        "Ts": sec["tiempo"],
        "Tp_mutex": mut["tiempo"],
        "speedup_mutex": round(sp_mut, 3),
        "efic_mutex": round(ef_mut, 3),
        "Tp_priv": prv["tiempo"],
        "speedup_priv": round(sp_prv, 3),
        "efic_priv": round(ef_prv, 3),
        "total": prv["total"],
        "correcto": "OK" if (ok_mut and ok_prv) else "ERROR",
    })


# 3. Guardar y mostrar la tabla
with open("resultados_p2.csv", "w", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=resultados[0].keys())
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"{'N':>9} {'T':>2} {'Ts (s)':>10} {'Tp_mut (s)':>10} {'Sp_mut':>7} "
      f"{'Tp_priv (s)':>11} {'Sp_priv':>8} {'Ef_priv':>8}  Correcto")
for r in resultados:
    print(f"{r['N']:>9} {r['T']:>2} {r['Ts']:>10} {r['Tp_mutex']:>10} {r['speedup_mutex']:>7.3f} "
          f"{r['Tp_priv']:>11} {r['speedup_priv']:>8.3f} {r['efic_priv']:>8.3f}  {r['correcto']}")

errores = sum(r["correcto"] == "ERROR" for r in resultados)
print()
print("Todo coincide (10 categorias + suma == N)" if errores == 0 else f"ATENCION: {errores} errores")
print("Tabla guardada en resultados_p2.csv")


# 4. Graficos del histograma privado vs. mutex compartido
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#008300"]
VALORES_T = sorted({r["T"] for r in resultados})
VALORES_N = sorted({r["N"] for r in resultados})


def graficar(col_priv, col_mut, titulo, ideal, archivo):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Panel izquierdo: Histograma privado por thread
    ax1.plot(VALORES_T, ideal, "--", color="#999999", linewidth=1.5, label="Ideal")
    for color, n in zip(COLORES, VALORES_N):
        valores = [r[col_priv] for r in resultados if r["N"] == n]
        ax1.plot(VALORES_T, valores, "-o", color=color, linewidth=2, markersize=6,
                 label=f"N = {n:,}".replace(",", "."))
    ax1.set_title(f"{titulo} — Histograma privado", loc="left", fontsize=11)
    ax1.set_xlabel("Threads (T)")
    ax1.set_xticks(VALORES_T)
    ax1.grid(axis="y", color="#e5e5e5")
    for borde in ["top", "right"]:
        ax1.spines[borde].set_visible(False)

    # Panel derecho: Mutex compartido
    for color, n in zip(COLORES, VALORES_N):
        valores = [r[col_mut] for r in resultados if r["N"] == n]
        ax2.plot(VALORES_T, valores, "-s", color=color, linewidth=2, markersize=6,
                 label=f"N = {n:,}".replace(",", "."))
    ax2.set_title(f"{titulo} — Mutex compartido", loc="left", fontsize=11)
    ax2.set_xlabel("Threads (T)")
    ax2.set_xticks(VALORES_T)
    ax2.grid(axis="y", color="#e5e5e5")
    for borde in ["top", "right"]:
        ax2.spines[borde].set_visible(False)
    ax2.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1, 1))

    fig.tight_layout()
    fig.savefig(archivo, dpi=150)
    plt.close(fig)
    print(f"Grafico guardado en {archivo}")


graficar("speedup_priv", "speedup_mutex", "Speedup (Ts / Tp)", VALORES_T, "speedup_p2.png")
graficar("efic_priv", "efic_mutex", "Eficiencia (Speedup / T)", [1] * len(VALORES_T), "eficiencia_p2.png")
