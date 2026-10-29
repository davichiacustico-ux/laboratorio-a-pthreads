#!/bin/sh
# Parte III: prueba productores y consumidores con distintas cantidades de
# productores (P), consumidores (C) y tamanos de buffer circular
# Uso: sh run_p3.sh
# Genera: resultados_p3.csv

export LC_ALL=C   # punto decimal (no coma) para no romper el CSV

TOTAL=100003                            # no es multiplo de 2, 4 ni 8
PARES_PC="1:1 2:2 4:4 8:8 2:4 4:2"      # combinaciones P:C (simetricas y asimetricas)
BUFFERS="8 64 1024"                     # tamanos del buffer circular

valor()  { echo "$1" | awk -F'= ' -v k="$2" '$1 ~ "^"k {print $2}'; }
tiempo() { echo "$1" | awk -F'= ' '/^Tiempo/ {sub(/ s$/, "", $2); print $2}'; }

# 1. Compilar
gcc -O2 -pthread p3sec.c -o p3sec || exit 1
gcc -O2 -pthread p3par.c -o p3par || exit 1

# 2. Ejecutar pruebas
echo "Total,P,C,Buffer,Producidos,Consumidos,SumaProd,SumaCons,Perdidos,Duplicados,Ts,Tp,Correcto" > resultados_p3.csv

for B in $BUFFERS; do
    SEC=$(./p3sec "$TOTAL" "$B")
    TS=$(tiempo "$SEC")
    SUMA_REF=$(valor "$SEC" "SumaProd")

    for PC in $PARES_PC; do
        P=${PC%:*}
        C=${PC#*:}

        PAR=$(./p3par "$TOTAL" "$P" "$C" "$B")
        TP=$(tiempo "$PAR")
        PROD=$(valor "$PAR" "Producidos")
        CONS=$(valor "$PAR" "Consumidos")
        SPROD=$(valor "$PAR" "SumaProd")
        SCONS=$(valor "$PAR" "SumaCons")
        PERD=$(valor "$PAR" "Perdidos")
        DUPL=$(valor "$PAR" "Duplicados")
        ENBUF=$(valor "$PAR" "EnBuffer")

        if [ "$PROD" = "$TOTAL" ] && [ "$CONS" = "$TOTAL" ] && \
           [ "$SPROD" = "$SUMA_REF" ] && [ "$SCONS" = "$SUMA_REF" ] && \
           [ "$PERD" = "0" ] && [ "$DUPL" = "0" ] && [ "$ENBUF" = "0" ]; then
            CORRECTO=OK
        else
            CORRECTO=ERROR
        fi

        echo "$TOTAL,$P,$C,$B,$PROD,$CONS,$SPROD,$SCONS,$PERD,$DUPL,$TS,$TP,$CORRECTO" >> resultados_p3.csv
    done
done

# 3. Mostrar la tabla
column -t -s, resultados_p3.csv
grep -q ERROR resultados_p3.csv && echo "ATENCION: hay errores de sincronizacion" || echo "Todo coincide (0 perdidos, 0 duplicados)"
