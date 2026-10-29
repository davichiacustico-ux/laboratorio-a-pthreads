#!/bin/sh
# Parte I: compara la version secuencial (p1sec) con la paralela (p1par)
# Uso: sh run_p1.sh
# Genera: entorno.txt, resultados_p1.csv y repartos.txt

export LC_ALL=C   # punto decimal (no coma) para no romper el CSV

VALORES_N="1000 100000 1000000 1000003 10000000 100000000"   # 1000003 no es multiplo de 2, 4 ni 8
VALORES_T="1 2 4 8"

# Saca "suma min max promedio" de la salida de un programa
resultados() { echo "$1" | awk -F'= ' '/^(Suma|Minimo|Maximo|Promedio)/ {printf "%s ", $2}'; }
# Saca el tiempo (sin la " s" final)
tiempo()     { echo "$1" | awk -F'= ' '/^Tiempo/ {sub(/ s$/, "", $2); print $2}'; }

# 1. Compilar
gcc -O2 -pthread p1sec.c -o p1sec || exit 1
gcc -O2 -pthread p1par.c -o p1par || exit 1

# 2. Datos del equipo
{ date; lscpu | grep -E "Model name|^CPU\(s\)|Thread|Core|Socket"; free -h; gcc --version | head -n 1; } > entorno.txt

# 3. Ejecutar, comparar y calcular speedup y eficiencia
echo "N,T,Suma,Minimo,Maximo,Promedio,Ts,Tp,Speedup,Eficiencia,Correcto" > resultados_p1.csv
: > repartos.txt

for N in $VALORES_N; do
    SEC=$(./p1sec "$N")
    RES_SEC=$(resultados "$SEC")
    TS=$(tiempo "$SEC")

    for T in $VALORES_T; do
        PAR=$(./p1par "$N" "$T")
        TP=$(tiempo "$PAR")

        if [ "$RES_SEC" = "$(resultados "$PAR")" ]; then CORRECTO=OK; else CORRECTO=ERROR; fi

        # Speedup = Ts / Tp   Eficiencia = Speedup / T
        CALC=$(awk -v ts="$TS" -v tp="$TP" -v t="$T" 'BEGIN { s = ts / tp; printf "%.3f,%.3f", s, s / t }')

        echo "$N,$T,$(echo $RES_SEC | tr ' ' ','),$TS,$TP,$CALC,$CORRECTO" >> resultados_p1.csv
        { echo "N = $N, T = $T"; echo "$PAR" | grep '^Thread [0-9]'; echo; } >> repartos.txt
    done
done

# 4. Mostrar la tabla
column -t -s, resultados_p1.csv
grep -q ERROR resultados_p1.csv && echo "ATENCION: hay resultados que no coinciden" || echo "Todo coincide"
