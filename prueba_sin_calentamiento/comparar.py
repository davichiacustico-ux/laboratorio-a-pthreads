"""
Compara los resultados CON calentamiento (carpeta raiz) vs. SIN calentamiento
(esta subcarpeta: tanto la mediana de 7 sin r=-1 como la 1.a vuelta en frio).
Genera COMPARACION.md.
"""
import csv
from pathlib import Path

ACTUAL = Path(__file__).resolve().parent
RAIZ = ACTUAL.parent


def leer_p1(ruta):
    with open(ruta, encoding="utf-8") as f:
        return {(r["version"], int(r["N"]), int(r["T"])): r for r in csv.DictReader(f)}


def leer_p2(ruta):
    with open(ruta, encoding="utf-8") as f:
        return {(r["version"], r["dist"], int(r["N"]), int(r["T"])): r for r in csv.DictReader(f)}


def leer_p3(ruta):
    with open(ruta, encoding="utf-8") as f:
        return {(r["version"], int(r["buffer"]), int(r["P"]), int(r["C"])): r for r in csv.DictReader(f)}


p1_con = leer_p1(RAIZ / "datos_p1.csv")
p1_sin = leer_p1(ACTUAL / "datos_p1.csv")

p2_con = leer_p2(RAIZ / "datos_p2.csv")
p2_sin = leer_p2(ACTUAL / "datos_p2.csv")

p3_con = leer_p3(RAIZ / "datos_p3.csv")
p3_sin = leer_p3(ACTUAL / "datos_p3.csv")

pesos = {
    1000: "4 KB (cabe en L1)",
    100000: "400 KB (cabe en L2/L3)",
    1000000: "4 MB (cabe en L3)",
    1000003: "4 MB (cabe en L3)",
    10000000: "40 MB (> L3 de 12 MB)",
    100000000: "400 MB (>> L3 de 12 MB)",
}

lineas = [
    "# Comparación experimental: CON calentamiento vs. SIN calentamiento",
    "",
    "Se comparan **tres formas de medir** sobre el mismo equipo (`Intel Core i5-10400`, WSL2 `Ubuntu-CUDA`):",
    "1. **CON calentamiento (`r = -1` + mediana de 7):** Los datos originales de la carpeta raíz.",
    "2. **SIN calentamiento (mediana de 7, `r = 0..6`):** Quitando la vuelta `r = -1`, pero manteniendo 7 mediciones y tomando la mediana.",
    "3. **1.ª vuelta en frío (`r = 0` sola):** Qué pasa si mides **una sola vez sin calentamiento**.",
    "",
    "---",
    "",
    "## 1. Parte I — Estadísticas (`p1sec` y `p1par`)",
    "",
    "### 1.1 Tiempos secuenciales (`p1sec`)",
    "",
    "| N | Peso en RAM | CON calent. (mediana, ms) | SIN calent. (mediana, ms) | 1.ª vuelta en frío (ms) | Ratio 1.ª vuelta / Mediana |",
    "|---:|---:|---:|---:|---:|---:|",
]

for N in sorted({k[1] for k in p1_con if k[0] == "secuencial"}):
    c = p1_con[("secuencial", N, 1)]
    s = p1_sin[("secuencial", N, 1)]
    tc = float(c["tiempo"]) * 1e3
    ts = float(s["tiempo"]) * 1e3
    tf = float(s["t_primera"]) * 1e3
    ratio = tf / ts if ts > 0 else 0
    lineas.append(f"| {N:,} | {pesos[N]} | {tc:.4f} | {ts:.4f} | {tf:.4f} | **{ratio:.2f}x** |")

lineas += [
    "",
    "### 1.2 Tiempos paralelos (`p1par`) y Speedup en los tres modos",
    "",
    "| N | T | Tp CON calent. (ms) | Tp SIN calent. (ms) | Tp 1.ª vuelta en frío (ms) | Ratio Tp Frío / Mediana | Speedup CON | Speedup SIN | Speedup 1.ª vuelta |",
    "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
]

for N in sorted({k[1] for k in p1_con if k[0] == "paralelo"}):
    ts_con = float(p1_con[("secuencial", N, 1)]["tiempo"])
    ts_sin = float(p1_sin[("secuencial", N, 1)]["tiempo"])
    ts_frio = float(p1_sin[("secuencial", N, 1)]["t_primera"])
    for T in (1, 2, 4, 8):
        tp_con = float(p1_con[("paralelo", N, T)]["tiempo"])
        tp_sin = float(p1_sin[("paralelo", N, T)]["tiempo"])
        tp_frio = float(p1_sin[("paralelo", N, T)]["t_primera"])
        sp_con = ts_con / tp_con
        sp_sin = ts_sin / tp_sin
        sp_frio = ts_frio / tp_frio
        ratio_tp = tp_frio / tp_sin
        lineas.append(
            f"| {N:,} | {T} | {tp_con*1e3:.4f} | {tp_sin*1e3:.4f} | {tp_frio*1e3:.4f} | "
            f"**{ratio_tp:.2f}x** | {sp_con:.3f} | {sp_sin:.3f} | {sp_frio:.3f} |"
        )

lineas += [
    "",
    "---",
    "",
    "## 2. Parte II — Histograma privado (`p2priv`, uniforme)",
    "",
    "| N | T | Tp CON calent. (ms) | Tp SIN calent. (ms) | Tp 1.ª vuelta en frío (ms) | Ratio Tp Frío / Mediana | Speedup CON | Speedup SIN | Speedup 1.ª vuelta |",
    "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
]

for N in sorted({k[2] for k in p2_con if k[0] == "privado" and k[1] == "u"}):
    ts_con = float(p2_con[("secuencial", "u", N, 1)]["tiempo"])
    ts_sin = float(p2_sin[("secuencial", "u", N, 1)]["tiempo"])
    ts_frio = float(p2_sin[("secuencial", "u", N, 1)]["t_primera"])
    for T in (1, 2, 4, 8):
        tp_con = float(p2_con[("privado", "u", N, T)]["tiempo"])
        tp_sin = float(p2_sin[("privado", "u", N, T)]["tiempo"])
        tp_frio = float(p2_sin[("privado", "u", N, T)]["t_primera"])
        ratio_tp = tp_frio / tp_sin
        lineas.append(
            f"| {N:,} | {T} | {tp_con*1e3:.4f} | {tp_sin*1e3:.4f} | {tp_frio*1e3:.4f} | "
            f"**{ratio_tp:.2f}x** | {ts_con/tp_con:.3f} | {ts_sin/tp_sin:.3f} | {ts_frio/tp_frio:.3f} |"
        )

lineas += [
    "",
    "---",
    "",
    "## 3. Parte III — Productores y Consumidores (`p3par`)",
    "",
    "| Buffer | P–C | Tp CON calent. (mediana, ms) | Tp SIN calent. (mediana, ms) | Tp 1.ª vuelta en frío (ms) | Ratio Frío / Mediana |",
    "|---:|:---:|---:|---:|---:|---:|",
]

for (ver, B, P, C), c in p3_con.items():
    if ver == "secuencial":
        continue
    s = p3_sin[(ver, B, P, C)]
    tc = float(c["tiempo"]) * 1e3
    ts = float(s["tiempo"]) * 1e3
    tf = float(s["t_primera"]) * 1e3
    lineas.append(f"| {B} | {P}P–{C}C | {tc:.2f} | {ts:.2f} | {tf:.2f} | **{tf/ts:.2f}x** |")

(ACTUAL / "COMPARACION.md").write_text("\n".join(lineas), encoding="utf-8")
print("Actualizado COMPARACION.md")
