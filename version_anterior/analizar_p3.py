"""
Parte III - Paso 2 de 2: ANALIZAR los experimentos de Productores-Consumidores

Lee datos_p3.csv (lo genera experimentos_p3.sh) y:
  1. verifica que producidos == consumidos == total
  2. verifica que suma_prod == suma_cons y que perdidos == 0 y duplicados == 0
  3. guarda resultados_p3.csv y muestra la tabla
  4. dibuja tiempos_p3.png comparando configuraciones P:C y tamanos de buffer

Uso: python3 analizar_p3.py
"""
import csv

import matplotlib
matplotlib.use("Agg")  # no abre ventanas, solo guarda las imagenes
import matplotlib.pyplot as plt


# 1. Leer los datos en bruto
secuencial = {}  # buffer -> fila secuencial
paralelo = []    # filas paralelas

with open("datos_p3.csv") as f:
    for fila in csv.DictReader(f):
        if fila["version"] == "secuencial":
            secuencial[fila["buffer"]] = fila
        else:
            paralelo.append(fila)


# 2. Verificar que no se pierdan ni se dupliquen elementos
resultados = []
for par in paralelo:
    sec = secuencial[par["buffer"]]
    total = int(par["total"])
    prod = int(par["producidos"])
    cons = int(par["consumidos"])
    perd = int(par["perdidos"])
    dupl = int(par["duplicados"])

    correcto = (
        prod == total
        and cons == total
        and par["suma_prod"] == sec["suma_prod"]
        and par["suma_cons"] == sec["suma_cons"]
        and perd == 0
        and dupl == 0
    )

    resultados.append({
        "total": total,
        "P": int(par["P"]),
        "C": int(par["C"]),
        "buffer": int(par["buffer"]),
        "producidos": prod,
        "consumidos": cons,
        "suma_prod": par["suma_prod"],
        "suma_cons": par["suma_cons"],
        "perdidos": perd,
        "duplicados": dupl,
        "Ts": sec["tiempo"],
        "Tp": par["tiempo"],
        "correcto": "OK" if correcto else "ERROR",
    })


# 3. Guardar y mostrar la tabla
with open("resultados_p3.csv", "w", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=resultados[0].keys())
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"{'Total':>7} {'P':>2} {'C':>2} {'Buffer':>6} {'Prod':>7} {'Cons':>7} "
      f"{'Perd':>4} {'Dupl':>4} {'Tp (s)':>10}  Correcto")
for r in resultados:
    print(f"{r['total']:>7} {r['P']:>2} {r['C']:>2} {r['buffer']:>6} {r['producidos']:>7} {r['consumidos']:>7} "
          f"{r['perdidos']:>4} {r['duplicados']:>4} {r['Tp']:>10}  {r['correcto']}")

errores = sum(r["correcto"] == "ERROR" for r in resultados)
print()
print("Todo coincide (0 perdidos, 0 duplicados)" if errores == 0 else f"ATENCION: {errores} errores")
print("Tabla guardada en resultados_p3.csv")


# 4. Grafico de tiempos por configuracion (P:C) y tamano de buffer
COLORES = ["#2a78d6", "#eb6834", "#1baf7a"]
BUFFERS = sorted({r["buffer"] for r in resultados})
ETIQUETAS_PC = []
for r in resultados:
    etq = f"{r['P']}P-{r['C']}C"
    if etq not in ETIQUETAS_PC:
        ETIQUETAS_PC.append(etq)

fig, ax = plt.subplots(figsize=(7.5, 4.5))
x = list(range(len(ETIQUETAS_PC)))

for color, b in zip(COLORES, BUFFERS):
    tiempos = [
        float(r["Tp"])
        for etq in ETIQUETAS_PC
        for r in resultados
        if r["buffer"] == b and f"{r['P']}P-{r['C']}C" == etq
    ]
    ax.plot(x, tiempos, "-o", color=color, linewidth=2, markersize=6, label=f"Buffer = {b}")

ax.set_title("Tiempo de ejecucion Productor-Consumidor (N = 100.003)", loc="left", fontsize=12)
ax.set_xlabel("Configuracion (Productores - Consumidores)")
ax.set_ylabel("Tiempo (s)")
ax.set_xticks(x)
ax.set_xticklabels(ETIQUETAS_PC)
ax.grid(axis="y", color="#e5e5e5")
for borde in ["top", "right"]:
    ax.spines[borde].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1, 1))

fig.tight_layout()
fig.savefig("tiempos_p3.png", dpi=150)
plt.close(fig)
print("Grafico guardado en tiempos_p3.png")
