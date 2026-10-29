#!/bin/sh
# Parte III - Paso 1 de 2: EJECUTAR los experimentos de Productores-Consumidores
#
# Corre p3sec y p3par con distintas cantidades de productores (P), consumidores (C)
# y tamanos de buffer (B), y guarda lo que imprimen en datos_p3.csv.
# Al final llama a analizar_p3.py (Paso 2), que verifica que no se pierdan ni
# dupliquen elementos y dibuja tiempos_p3.png.
#
# Uso: sh experimentos_p3.sh

export LC_ALL=C   # punto decimal (no coma) para no romper el CSV

TOTAL=100003                            # no es multiplo de 2, 4 ni 8
PARES_PC="1:1 2:2 4:4 8:8 2:4 4:2"      # combinaciones P:C
BUFFERS="8 64 1024"                     # tamanos del buffer circular

# Agrega una fila a datos_p3.csv
#   $1 = version   $2 = TOTAL   $3 = P   $4 = C   $5 = B   $6 = salida
guardar_fila() {
    VALORES=$(echo "$6" | awk -F'= ' '/^(Producidos|Consumidos|SumaProd|SumaCons|Perdidos|Duplicados|Tiempo)/ {sub(/ s$/, "", $2); printf ",%s", $2}')
    echo "$1,$2,$3,$4,$5$VALORES" >> datos_p3.csv
}

# 1. Compilar
echo "Compilando Parte III..."
gcc -O2 -pthread p3sec.c -o p3sec || exit 1
gcc -O2 -pthread p3par.c -o p3par || exit 1

# 2. Ejecutar los experimentos
echo "version,total,P,C,buffer,producidos,consumidos,suma_prod,suma_cons,perdidos,duplicados,tiempo" > datos_p3.csv

for B in $BUFFERS; do
    echo "Ejecutando Buffer = $B"
    guardar_fila secuencial "$TOTAL" 1 1 "$B" "$(./p3sec "$TOTAL" "$B")"

    for PC in $PARES_PC; do
        P=${PC%:*}
        C=${PC#*:}
        guardar_fila paralelo "$TOTAL" "$P" "$C" "$B" "$(./p3par "$TOTAL" "$P" "$C" "$B")"
    done
done

echo "Datos guardados en datos_p3.csv"
echo

# 3. Analizar con Python
python3 analizar_p3.py
