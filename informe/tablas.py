"""
Rellena las tablas del informe con los datos de los experimentos.

Lee entorno_p*.txt, repartos.txt, datos_p2.csv y resultados_p*.csv (en la carpeta
del laboratorio) y reemplaza lo que hay entre las marcas
    <!-- tabla:NOMBRE -->  ...  <!-- /tabla:NOMBRE -->
de los archivos informe/*.md. Asi ninguna tabla se copia a mano: si se repiten los
experimentos, basta con volver a correr este script y exportar.

Uso (desde la carpeta del laboratorio):
    python informe/tablas.py
    pandoc informe/0*.md --columns=250 --pdf-engine=typst -o Informe_Laboratorio_A.pdf
"""
import csv
import math
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INFORME = RAIZ / "informe"
NBSP = " "   # espacio no separable: separador de miles que no se corta


def leer_csv(nombre):
    with open(RAIZ / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def miles(n):
    """1000003 -> '1 000 003'."""
    return f"{int(n):,}".replace(",", NBSP)


def ms(segundos):
    """Segundos (texto del CSV) -> milisegundos con 3 cifras significativas."""
    x = float(segundos) * 1e3
    decimales = max(0, 2 - math.floor(math.log10(abs(x)))) if x else 0
    return f"{x:.{decimales}f}"


def espacios_miles(texto):
    """'1 000 003' -> '1 000 003' con espacios no separables, para que no se corte."""
    patron = re.compile(r"(?<![\w.])(\d{1,3}) (\d{3})(?!\d)")
    anterior = None
    while anterior != texto:
        anterior, texto = texto, patron.sub(lambda m: m.group(1) + NBSP + m.group(2), texto)
    return texto


def tabla(encabezado, filas, alineacion, titulo):
    """Tabla Markdown con su titulo; alineacion: una letra (l, r, c) por columna."""
    sep = {"l": ":--", "r": "--:", "c": ":-:"}
    lineas = ["| " + " | ".join(encabezado) + " |",
              "|" + "|".join(sep[a] for a in alineacion) + "|"]
    lineas += ["| " + " | ".join(str(c) for c in fila) + " |" for fila in filas]
    return espacios_miles("\n".join(lineas) + f"\n\n: {titulo}")


def primera(texto, clave, anterior):
    """Muestra el texto solo en la primera fila de cada grupo (cuando cambia la clave)."""
    return texto if clave != anterior else ""


# ---------------------------------------------------------------- entorno
def leer_entorno(parte):
    lineas = (RAIZ / f"entorno_p{parte}.txt").read_text(encoding="utf-8").splitlines()
    datos = {"fecha": lineas[0].strip(), "sistema": lineas[1].strip()}
    for linea in lineas[2:]:
        if ":" in linea and not linea.startswith(" "):
            clave, valor = linea.split(":", 1)
            datos[clave.strip()] = valor.strip()
        if linea.startswith("Mem:"):
            datos["memoria"] = linea.split()[1]
        if linea.startswith("gcc"):
            datos["gcc"] = linea.strip()
    return datos


def tabla_entorno():
    partes = {p: leer_entorno(p) for p in (1, 2, 3)}
    e = partes[1]
    modelos = {d["Model name"] for d in partes.values()}
    filas = [
        ["Procesador", " / ".join(sorted(modelos))],
        ["Núcleos e hilos", f"{e['Core(s) per socket']} núcleos físicos × {e['Thread(s) per core']} "
                            f"hilos por núcleo = {e['CPU(s)']} CPU lógicas"],
        ["Memoria visible en Linux", e["memoria"].replace("Gi", " GiB")],
        ["Sistema (uname)", e["sistema"]],
        ["Compilador", f"{e['gcc']}, opciones `-O2 -pthread`"],
    ]
    for p, d in partes.items():
        filas.append([f"Mediciones de la Parte {'I' * p}", d["fecha"]])
    if len(modelos) > 1:
        filas.append(["Atención", "las partes se midieron en procesadores distintos"])
    return tabla(["Componente", "Valor"], filas, "ll",
                 "Equipo donde se ejecutaron las tres partes (de `entorno_p1.txt`, "
                 "`entorno_p2.txt` y `entorno_p3.txt`).")


# ---------------------------------------------------------------- Parte I
def tabla_reparto():
    texto = (RAIZ / "repartos.txt").read_text(encoding="utf-8")
    bloque = texto.split("N = 1000003, T = 8\n")[1].split("\n\n")[0]
    filas = []
    for linea in bloque.splitlines():
        m = re.match(r"Thread (\d+): \[(\d+), (\d+)\) -> (\d+) elementos", linea)
        filas.append([m[1], miles(m[2]), miles(m[3]), miles(m[4])])
    return tabla(["Thread", "Inicio", "Fin (excluido)", "Elementos"], filas, "rrrr",
                 "Reparto de N = 1 000 003 elementos entre T = 8 threads (de `repartos.txt`): "
                 "1 000 003 = 8 × 125 000 + 3, así que los threads 0, 1 y 2 reciben un elemento más.")


def tabla_p1_estadisticas():
    filas, vistos = [], set()
    datos = leer_csv("resultados_p1.csv")
    for r in datos:
        if r["N"] in vistos:
            continue
        vistos.add(r["N"])
        grupo = [x for x in datos if x["N"] == r["N"]]
        estado = "OK" if all(x["correcto"] == "OK" for x in grupo) else "ERROR"
        filas.append([miles(r["N"]), miles(r["suma"]), r["minimo"], r["maximo"],
                      r["promedio"], ", ".join(x["T"] for x in grupo), estado])
    return tabla(["N", "Suma", "Mínimo", "Máximo", "Promedio", "T probados", "¿Igual al secuencial?"],
                 filas, "rrrrrcc",
                 "Resultados de la Parte I. Para cada N, las cuatro ejecuciones paralelas dieron "
                 "exactamente la misma suma, mínimo, máximo y promedio que la versión secuencial.")


def tabla_p1():
    filas, anterior = [], None
    for r in leer_csv("resultados_p1.csv"):
        filas.append([primera(miles(r["N"]), r["N"], anterior), r["T"],
                      primera(ms(r["Ts"]), r["N"], anterior),
                      ms(r["Tp"]), f"{ms(r['Tp_min'])} – {ms(r['Tp_max'])}",
                      f"{float(r['speedup']):.2f}", f"{float(r['eficiencia']):.2f}"])
        anterior = r["N"]
    return tabla(["N", "T", "Ts (ms)", "Tp (ms)", "Tp mín – máx (ms)", "Speedup", "Eficiencia"],
                 filas, "rrrrrrr",
                 "Tiempos de la Parte I: mediana de 7 mediciones (Tp incluye crear, esperar y "
                 "combinar los threads) y rango de las 7 mediciones paralelas.")


# ---------------------------------------------------------------- Parte II
def tabla_p2():
    filas, anterior = [], None
    for r in leer_csv("resultados_p2.csv"):
        filas.append([primera(miles(r["N"]), r["N"], anterior), r["T"],
                      primera(ms(r["Ts"]), r["N"], anterior),
                      ms(r["Tp_privado"]), f"{float(r['speedup_privado']):.2f}",
                      f"{float(r['efic_privado']):.2f}",
                      ms(r["Tp_mutex"]), f"{float(r['speedup_mutex']):.3f}",
                      ms(r["Tp_mutexcat"]), f"{float(r['speedup_mutexcat']):.3f}"])
        anterior = r["N"]
    return tabla(["N", "T", "Ts", "Tp priv.", "S priv.", "E priv.",
                  "Tp global", "S global", "Tp categ.", "S categ."],
                 filas, "rrrrrrrrrr",
                 "Histograma con datos uniformes. Tiempos en ms (mediana de 7); S = speedup, "
                 "E = eficiencia; priv. = histograma privado, global = un mutex global, "
                 "categ. = un mutex por categoría. En todas las filas las 10 categorías "
                 "coinciden con el secuencial y suman N.")


def tabla_p2_categorias():
    sec = {(r["dist"], r["N"]): r for r in leer_csv("datos_p2.csv") if r["version"] == "secuencial"}
    n = max(int(N) for (d, N) in sec if d == "s")
    u, s = sec[("u", str(n))], sec[("s", str(n))]
    filas = [[f"c{i}", f"{10 * i:02d}–{10 * i + 9:02d}", miles(u[f"c{i}"]), miles(s[f"c{i}"])]
             for i in range(10)]
    filas.append(["**Total**", "", f"**{miles(u['total'])}**", f"**{miles(s['total'])}**"])
    return tabla(["Categoría", "Intervalo", "Uniforme", "Sesgada"], filas, "ccrr",
                 f"Histograma secuencial de N = {miles(n)} valores con las dos distribuciones. "
                 "Las tres versiones paralelas obtuvieron los mismos conteos con T = 1, 2, 4 y 8.")


def tabla_p2_dist():
    filas, anterior = [], None
    for r in leer_csv("resultados_p2_dist.csv"):
        relacion = float(r["Tp_mutexcat"]) / float(r["Tp_mutex"])
        filas.append([primera(r["dist"].capitalize(), r["dist"], anterior), r["T"],
                      primera(ms(r["Ts"]), r["dist"], anterior),
                      ms(r["Tp_privado"]), ms(r["Tp_mutex"]), ms(r["Tp_mutexcat"]),
                      f"{relacion:.2f}"])
        anterior = r["dist"]
    return tabla(["Datos", "T", "Ts", "Tp priv.", "Tp global", "Tp categ.", "categ. / global"],
                 filas, "lrrrrrr",
                 "Influencia de la distribución de los datos (N = 10 000 000, tiempos en ms, "
                 "mediana de 7). La última columna compara el mutex por categoría con el global: "
                 "menos de 1 significa que repartir los candados ayudó.")


# ---------------------------------------------------------------- Parte III
def tabla_p3():
    filas, anterior = [], None
    for r in leer_csv("resultados_p3.csv"):
        fallos = int(r["perdidos"]) + int(r["duplicados"]) + int(r["rep_fallidas"])
        filas.append([primera(r["buffer"], r["buffer"], anterior), f"{r['P']}P–{r['C']}C",
                      primera(ms(r["Ts"]), r["buffer"], anterior),
                      ms(r["Tp"]), f"{ms(r['Tp_min'])} – {ms(r['Tp_max'])}",
                      f"{float(r['Tp']) / float(r['Ts']):.0f}",
                      r["perdidos"], r["duplicados"], r["rep_fallidas"],
                      "OK" if r["correcto"] == "OK" and fallos == 0 else "ERROR"])
        anterior = r["buffer"]
    total = miles(leer_csv("resultados_p3.csv")[0]["total"])
    return tabla(["Buffer", "P–C", "Ts (ms)", "Tp (ms)", "Tp mín – máx (ms)", "Tp / Ts",
                  "Perdidos", "Duplicados", "Ejec. fallidas", "Estado"],
                 filas, "rcrrrrrrrc",
                 f"Productores y consumidores con TOTAL = {total} elementos. Tiempos: mediana de "
                 "7 mediciones. Perdidos, duplicados y ejecuciones fallidas suman las 8 ejecuciones "
                 "de cada configuración (1 de calentamiento + 7 medidas).")


def tabla_p3_contexto():
    datos = leer_csv("cambios_contexto_p3.csv")
    buffers = sorted({int(r["buffer"]) for r in datos})
    configuraciones = []
    for r in datos:
        if (r["P"], r["C"]) not in configuraciones:
            configuraciones.append((r["P"], r["C"]))
    encabezado = ["P–C"]
    for b in buffers:
        encabezado += [f"Esperas (B = {b})", f"ms (B = {b})"]
    filas = []
    for P, C in configuraciones:
        fila = [f"{P}P–{C}C"]
        for b in buffers:
            r = next(x for x in datos if int(x["buffer"]) == b and (x["P"], x["C"]) == (P, C))
            fila += [miles(r["voluntarios_por_ejec"]), ms(r["tiempo"])]
        filas.append(fila)
    return tabla(encabezado, filas, "c" + "rr" * len(buffers),
                 "Esperas por ejecución: cambios de contexto voluntarios, es decir, cuántas veces "
                 "se durmió algún thread en el mutex o en una variable de condición (sumando todos "
                 "los threads, medido con `getrusage` por `cambios_contexto_p3.py`), y tiempo de "
                 "esa misma corrida. B = tamaño del buffer.")


TABLAS = {
    "entorno": tabla_entorno,
    "reparto": tabla_reparto,
    "p1_estadisticas": tabla_p1_estadisticas,
    "p1": tabla_p1,
    "p2": tabla_p2,
    "p2_categorias": tabla_p2_categorias,
    "p2_dist": tabla_p2_dist,
    "p3": tabla_p3,
    "p3_contexto": tabla_p3_contexto,
}

pendientes = set(TABLAS)
for archivo in sorted(INFORME.glob("*.md")):
    texto = archivo.read_text(encoding="utf-8")
    nuevo = texto
    for nombre, generar in TABLAS.items():
        patron = re.compile(rf"<!-- tabla:{nombre} -->.*?<!-- /tabla:{nombre} -->", re.S)
        if patron.search(nuevo):
            contenido = generar()
            nuevo = patron.sub(lambda m: f"<!-- tabla:{nombre} -->\n\n{contenido}\n\n"
                                         f"<!-- /tabla:{nombre} -->", nuevo)
            pendientes.discard(nombre)
    if nuevo != texto:
        archivo.write_text(nuevo, encoding="utf-8")
        print(f"Tablas actualizadas en {archivo.name}")

if pendientes:
    print("Sin marca en el informe:", ", ".join(sorted(pendientes)))
