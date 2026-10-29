"""
Parte II - Paso 2 de 2: ANALIZAR los experimentos del histograma

Lee datos_p2.csv (lo genera experimentos_p2.sh) y:
  1. compara cada ejecucion paralela (privado, mutex global y mutex por categoria)
     con la secuencial del mismo N y la misma distribucion de datos
  2. verifica que las 10 categorias coincidan y que su suma sea igual a N
  3. con datos uniformes, calcula speedup y eficiencia de las tres estrategias
  4. compara datos uniformes vs. sesgados (contencion)
  5. guarda resultados_p2.csv y resultados_p2_dist.csv y muestra las tablas
  6. dibuja speedup_p2, eficiencia_p2 y distribucion_p2 (.png y figuras/*.svg)

Uso: python3 analizar_p2.py
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")  # no abre ventanas, solo guarda las imagenes
import matplotlib.pyplot as plt

CATEGORIAS = [f"c{i}" for i in range(10)] + ["total"]
ESTRATEGIAS = ["privado", "mutex", "mutexcat"]   # como se llaman en datos_p2.csv
NOMBRES = {"privado": "Histograma privado", "mutex": "Mutex global",
           "mutexcat": "Mutex por categoría"}


# 1. Leer los datos en bruto: (version, distribucion, N, T) -> fila
filas = {}
with open("datos_p2.csv") as f:
    for fila in csv.DictReader(f):
        filas[(fila["version"], fila["dist"], int(fila["N"]), int(fila["T"]))] = fila

VALORES_T = sorted({T for (v, d, N, T) in filas if v != "secuencial"})


def coincide(par, sec, N):
    """Las 10 categorias y el total son iguales a los del secuencial y suman N."""
    return all(par[c] == sec[c] for c in CATEGORIAS) and int(par["total"]) == N


def ms(texto):
    """Segundos (texto del CSV) -> milisegundos."""
    return float(texto) * 1e3


# 2. Datos uniformes: comparar y calcular speedup y eficiencia de las 3 estrategias
resultados = []
for N in sorted({N for (v, d, N, T) in filas if d == "u"}):
    sec = filas[("secuencial", "u", N, 1)]
    ts = float(sec["tiempo"])
    for T in VALORES_T:
        r = {"N": N, "T": T, "Ts": sec["tiempo"]}
        correcto = True
        for e in ESTRATEGIAS:
            par = filas[(e, "u", N, T)]
            speedup = ts / float(par["tiempo"])
            r[f"Tp_{e}"] = par["tiempo"]
            r[f"speedup_{e}"] = round(speedup, 3)
            r[f"efic_{e}"] = round(speedup / T, 3)
            correcto = correcto and coincide(par, sec, N)
        r["total"] = sec["total"]
        r["correcto"] = "OK" if correcto else "ERROR"
        resultados.append(r)


# 3. Uniforme vs. sesgada, con el N que tiene datos sesgados
N_DIST = max(N for (v, d, N, T) in filas if d == "s")
dist_res = []
for d, nombre in [("u", "uniforme"), ("s", "sesgada")]:
    sec = filas[("secuencial", d, N_DIST, 1)]
    for T in VALORES_T:
        r = {"dist": nombre, "N": N_DIST, "T": T, "cat0": sec["c0"], "Ts": sec["tiempo"]}
        correcto = True
        for e in ESTRATEGIAS:
            par = filas[(e, d, N_DIST, T)]
            r[f"Tp_{e}"] = par["tiempo"]
            correcto = correcto and coincide(par, sec, N_DIST)
        r["correcto"] = "OK" if correcto else "ERROR"
        dist_res.append(r)


# 4. Guardar y mostrar las tablas (tiempos en ms)
for archivo, filas_csv in [("resultados_p2.csv", resultados), ("resultados_p2_dist.csv", dist_res)]:
    with open(archivo, "w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=filas_csv[0].keys())
        escritor.writeheader()
        escritor.writerows(filas_csv)

print(f"{'N':>9} {'T':>2} {'Ts':>9} {'Tp_priv':>9} {'Sp_priv':>8} {'Tp_mutex':>9} {'Sp_mutex':>8} "
      f"{'Tp_mcat':>9} {'Sp_mcat':>8}  Correcto   (tiempos en ms)")
for r in resultados:
    print(f"{r['N']:>9} {r['T']:>2} {ms(r['Ts']):>9.3f} {ms(r['Tp_privado']):>9.3f} "
          f"{r['speedup_privado']:>8.3f} {ms(r['Tp_mutex']):>9.3f} {r['speedup_mutex']:>8.3f} "
          f"{ms(r['Tp_mutexcat']):>9.3f} {r['speedup_mutexcat']:>8.3f}  {r['correcto']}")

print()
print(f"Uniforme vs. sesgada (N = {N_DIST}, tiempos en ms)")
print(f"{'dist':>9} {'T':>2} {'cat0':>8} {'Ts':>9} {'Tp_priv':>9} {'Tp_mutex':>9} {'Tp_mcat':>9}  Correcto")
for r in dist_res:
    print(f"{r['dist']:>9} {r['T']:>2} {r['cat0']:>8} {ms(r['Ts']):>9.3f} {ms(r['Tp_privado']):>9.3f} "
          f"{ms(r['Tp_mutex']):>9.3f} {ms(r['Tp_mutexcat']):>9.3f}  {r['correcto']}")

errores = sum(r["correcto"] == "ERROR" for r in resultados + dist_res)
print()
print("Todo coincide (10 categorias + suma == N)" if errores == 0 else f"ATENCION: {errores} errores")
print("Tablas guardadas en resultados_p2.csv y resultados_p2_dist.csv")


# 5. Graficos. Cada N tiene el mismo color y marcador que en la Parte I
COLOR_N = {1000: "#2a78d6", 100000: "#eb6834", 1000000: "#1baf7a",
           1000003: "#eda100", 10000000: "#e87ba4", 100000000: "#008300"}
MARCADOR_N = {1000: "o", 100000: "s", 1000000: "^", 1000003: "D", 10000000: "v", 100000000: "P"}
VALORES_N = sorted({r["N"] for r in resultados})


def guardar(fig, nombre):
    """Guarda el grafico como PNG (para verlo rapido) y como SVG en figuras/ (para el informe)."""
    os.makedirs("figuras", exist_ok=True)
    fig.savefig(f"{nombre}.png", dpi=150, bbox_inches="tight")
    fig.savefig(f"figuras/{nombre}.svg", bbox_inches="tight")
    plt.close(fig)
    print(f"Grafico guardado en {nombre}.png y figuras/{nombre}.svg")


def limpiar(ax, titulo):
    ax.set_title(titulo, loc="left", fontsize=11)
    ax.set_xlabel("Threads (T)")
    ax.set_xticks(VALORES_T)
    ax.grid(axis="y", color="#e5e5e5")
    for borde in ["top", "right"]:
        ax.spines[borde].set_visible(False)


def cuadricula(compartir_y=False):
    """Tres paneles en una cuadricula de 2 x 2, para que el texto se lea al imprimir;
    el cuarto lugar queda para la leyenda."""
    fig, ejes = plt.subplots(2, 2, figsize=(9, 6.5), sharey=compartir_y)
    ejes[1][1].axis("off")
    return fig, [ejes[0][0], ejes[0][1], ejes[1][0]], ejes[1][1]


def graficar(prefijo, titulo, ideal, nombre):
    """Un panel por estrategia; cada panel tiene su propia escala vertical."""
    fig, ejes, hueco = cuadricula()
    for ax, e in zip(ejes, ESTRATEGIAS):
        if e == "privado":
            ax.plot(VALORES_T, ideal, "--", color="#999999", linewidth=1.5, label="Ideal")
        for n in VALORES_N:
            valores = [r[f"{prefijo}_{e}"] for r in resultados if r["N"] == n]
            ax.plot(VALORES_T, valores, "-", marker=MARCADOR_N[n], color=COLOR_N[n],
                    linewidth=2, markersize=7, label=f"N = {n:,}".replace(",", " "))
        limpiar(ax, f"{titulo} — {NOMBRES[e]}")
    # Una sola leyenda en el cuarto lugar (la del primer panel, que incluye "Ideal")
    manejadores, etiquetas = ejes[0].get_legend_handles_labels()
    hueco.legend(manejadores, etiquetas, frameon=False, fontsize=10, loc="center")
    fig.tight_layout()
    guardar(fig, nombre)


graficar("speedup", "Speedup (Ts / Tp)", VALORES_T, "speedup_p2")
graficar("efic", "Eficiencia (Speedup / T)", [1] * len(VALORES_T), "eficiencia_p2")


# Uniforme vs. sesgada: un panel por estrategia, con la misma escala logaritmica
# en los tres. La linea punteada es el secuencial con los mismos datos
COLOR_DIST = {"uniforme": "#2a78d6", "sesgada": "#eb6834"}
MARCADOR_DIST = {"uniforme": "o", "sesgada": "s"}

fig, ejes, hueco = cuadricula(compartir_y=True)
for ax, e in zip(ejes, ESTRATEGIAS):
    for nombre in ["uniforme", "sesgada"]:
        filas_d = [r for r in dist_res if r["dist"] == nombre]
        ax.plot(VALORES_T, [ms(r[f"Tp_{e}"]) for r in filas_d], "-", marker=MARCADOR_DIST[nombre],
                color=COLOR_DIST[nombre], linewidth=2, markersize=7, label=f"Paralelo, {nombre}")
        ax.axhline(ms(filas_d[0]["Ts"]), color=COLOR_DIST[nombre], linestyle=":", linewidth=1.5,
                   label=f"Secuencial, {nombre}")
    ax.set_yscale("log")
    limpiar(ax, NOMBRES[e])
for ax in (ejes[0], ejes[2]):
    ax.set_ylabel("Tiempo (ms, escala logarítmica)")
manejadores, etiquetas = ejes[0].get_legend_handles_labels()
hueco.legend(manejadores, etiquetas, frameon=False, fontsize=10, loc="center")
fig.suptitle(f"Datos uniformes vs. sesgados (N = {N_DIST:,})".replace(",", " "),
             x=0.01, ha="left", fontsize=13)
fig.tight_layout()
guardar(fig, "distribucion_p2")
