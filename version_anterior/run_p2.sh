#!/bin/sh
# Parte II: compara el histograma secuencial (p2sec) con las dos estrategias
# paralelas: mutex compartido (p2mutex) e histograma privado por thread (p2priv)
# Uso: sh run_p2.sh
# Genera: resultados_p2.csv

export LC_ALL=C   # punto decimal (no coma) para no romper el CSV

VALORES_N="1000 100000 1000000 1000003 10000000"   # 1000003 no es multiplo de 2, 4 ni 8
VALORES_T="1 2 4 8"

# Saca las 10 categorias y el Total de la salida de un programa
categorias() { echo "$1" | awk -F'= ' '/^(Cat|Total)/ {printf "%s ", $2}'; }
total_hist() { echo "$1" | awk -F'= ' '/^Total/ {print $2}'; }
tiempo()     { echo "$1" | awk -F'= ' '/^Tiempo/ {sub(/ s$/, "", $2); print $2}'; }

# 1. Compilar
gcc -O2 -pthread p2sec.c   -o p2sec   || exit 1
gcc -O2 -pthread p2mutex.c -o p2mutex || exit 1
gcc -O2 -pthread p2priv.c  -o p2priv  || exit 1

# 2. Ejecutar, comparar las 10 categorias + Total == N, y calcular speedup y eficiencia
echo "N,T,Ts,Tp_mutex,Speedup_mutex,Efic_mutex,Tp_priv,Speedup_priv,Efic_priv,SumaTotal,Correcto" > resultados_p2.csv

for N in $VALORES_N; do
    SEC=$(./p2sec "$N")
    CAT_SEC=$(categorias "$SEC")
    TS=$(tiempo "$SEC")

    for T in $VALORES_T; do
        MUT=$(./p2mutex "$N" "$T")
        PRV=$(./p2priv  "$N" "$T")

        TP_MUT=$(tiempo "$MUT")
        TP_PRV=$(tiempo "$PRV")
        TOT_PRV=$(total_hist "$PRV")

        if [ "$CAT_SEC" = "$(categorias "$MUT")" ] && [ "$CAT_SEC" = "$(categorias "$PRV")" ] && [ "$TOT_PRV" = "$N" ]; then
            CORRECTO=OK
        else
            CORRECTO=ERROR
        fi

        CALC_MUT=$(awk -v ts="$TS" -v tp="$TP_MUT" -v t="$T" 'BEGIN { s = ts / tp; printf "%.3f,%.3f", s, s / t }')
        CALC_PRV=$(awk -v ts="$TS" -v tp="$TP_PRV" -v t="$T" 'BEGIN { s = ts / tp; printf "%.3f,%.3f", s, s / t }')

        echo "$N,$T,$TS,$TP_MUT,$CALC_MUT,$TP_PRV,$CALC_PRV,$TOT_PRV,$CORRECTO" >> resultados_p2.csv
    done
done

# 3. Mostrar la tabla
column -t -s, resultados_p2.csv
grep -q ERROR resultados_p2.csv && echo "ATENCION: hay resultados que no coinciden" || echo "Todo coincide (10 categorias identicas y suma == N)"
