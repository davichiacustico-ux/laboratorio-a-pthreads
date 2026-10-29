"""
Parte III - Paso 2 de 2: ANALIZAR los experimentos de Productores-Consumidores

Lee datos_p3.csv (lo genera experimentos_p3.sh) y:
  1. verifica que producidos == consumidos == total y que el buffer quede vacio
  2. verifica que suma_prod == suma_cons == 0 + 1 + ... + (total - 1), que
     perdidos == 0, duplicados == 0 y que ninguna de las 8 ejecuciones fallo
  3. guarda resultados_p3.csv y muestra la tabla (tiempos en ms)
  4. dibuja tiempos_p3 (.png y figuras/tiempos_p3.svg) comparando configuraciones
     P:C y tamanos de buffer

Uso: python3 analizar_p3.py
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")  # no abre ventanas, solo guarda las imagenes
import matplotlib.pyplot as plt


def ms(texto):
    """Segundos (texto del CSV) -> milisegundos."""
    return float(texto) * 1e3


def verificar(fila):
    """True si en las 8 ejecuciones no se perdio ni duplico ningun elemento."""
    total = int(fila["total"])
    esperada = total * (total - 1) // 2   # 0 + 1 + ... + (total - 1)
    return (
        int(fila["producidos"]) == total
        and int(fila["consumidos"]) == total
        and int(fila["en_buffer"]) == 0
        and int(fila["suma_prod"]) == esperada
        and int(fila["suma_cons"]) == esperada
        and int(fila["perdidos"]) == 0
        and int(fila["duplicados"]) == 0
        and int(fila["rep_fallidas"]) == 0
    )


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
    resultados.append({
        "total": int(par["total"]),
        "P": int(par["P"]),
        "C": int(par["C"]),
        "buffer": int(par["buffer"]),
        "producidos": int(par["producidos"]),
        "consumidos": int(par["consumidos"]),
        "en_buffer": int(par["en_buffer"]),
        "suma_prod": par["suma_prod"],
        "suma_cons": par["suma_cons"],
        "perdidos": int(par["perdidos"]),
        "duplicados": int(par["duplicados"]),
        "rep_fallidas": int(par["rep_fallidas"]),
        "Ts": sec["tiempo"],
        "Tp": par["tiempo"],
        "Tp_min": par["t_min"],
        "Tp_max": par["t_max"],
        "correcto": "OK" if verificar(par) and verificar(sec) else "ERROR",
    })


# 3. Guardar y mostrar la tabla
with open("resultados_p3.csv", "w", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=resultados[0].keys())
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"{'Total':>7} {'P':>2} {'C':>2} {'Buffer':>6} {'Prod':>7} {'Cons':>7} {'Perd':>4} {'Dupl':>4} "
      f"{'Fall':>4} {'Ts (ms)':>9} {'Tp (ms)':>9}  Correcto")
for r in resultados:
    print(f"{r['total']:>7} {r['P']:>2} {r['C']:>2} {r['buffer']:>6} {r['producidos']:>7} "
          f"{r['consumidos']:>7} {r['perdidos']:>4} {r['duplicados']:>4} {r['rep_fallidas']:>4} "
          f"{ms(r['Ts']):>9.3f} {ms(r['Tp']):>9.3f}  {r['correcto']}")

errores = sum(r["correcto"] == "ERROR" for r in resultados)
print()
print("Todo coincide (0 perdidos, 0 duplicados)" if errores == 0 else f"ATENCION: {errores} errores")
print("Tabla guardada en resultados_p3.csv")


# 4. Grafico: un punto por configuracion P:C y tamano de buffer (la mediana) y una
#    barra vertical de la minima a la maxima de las 7 mediciones. Puntos y no lineas,
#    porque las configuraciones no tienen orden; escala logaritmica porque los tiempos
#    van de milisegundos a segundos
COLORES = {8: "#2a78d6", 64: "#eb6834", 1024: "#1baf7a"}
MARCADORES = {8: "o", 64: "s", 1024: "^"}
BUFFERS = sorted({r["buffer"] for r in resultados})
ETIQUETAS_PC = []
for r in resultados:
    etq = f"{r['P']}P-{r['C']}C"
    if etq not in ETIQUETAS_PC:
        ETIQUETAS_PC.append(etq)

fig, ax = plt.subplots(figsize=(8, 4.5))
for k, b in enumerate(BUFFERS):
    desplazamiento = (k - (len(BUFFERS) - 1) / 2) * 0.22   # separa los puntos de cada buffer
    for i, etq in enumerate(ETIQUETAS_PC):
        r = next(r for r in resultados if r["buffer"] == b and f"{r['P']}P-{r['C']}C" == etq)
        x = i + desplazamiento
        ax.plot([x, x], [ms(r["Tp_min"]), ms(r["Tp_max"])], color=COLORES[b], linewidth=1.5)
        ax.plot(x, ms(r["Tp"]), marker=MARCADORES[b], color=COLORES[b], markersize=7,
                linestyle="none", label=f"Buffer = {b}" if i == 0 else None)

# Referencia: el secuencial (el mas lento de los tres tamanos de buffer)
ts = max(ms(s["tiempo"]) for s in secuencial.values())
ax.axhline(ts, color="#999999", linestyle="--", linewidth=1.5, label=f"Secuencial (≤ {ts:.1f} ms)")

total = f"{resultados[0]['total']:,}".replace(",", " ")
ax.set_yscale("log")
ax.set_title(f"Tiempo de Productor-Consumidor (TOTAL = {total})", loc="left", fontsize=12)
ax.set_xlabel("Configuración (productores – consumidores)")
ax.set_ylabel("Tiempo (ms, escala logarítmica)")
ax.set_xticks(range(len(ETIQUETAS_PC)))
ax.set_xticklabels(ETIQUETAS_PC)
ax.grid(axis="y", color="#e5e5e5")
for borde in ["top", "right"]:
    ax.spines[borde].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1, 1))

fig.tight_layout()
os.makedirs("figuras", exist_ok=True)
fig.savefig("tiempos_p3.png", dpi=150, bbox_inches="tight")
fig.savefig("figuras/tiempos_p3.svg", bbox_inches="tight")
plt.close(fig)
print("Grafico guardado en tiempos_p3.png y figuras/tiempos_p3.svg")
