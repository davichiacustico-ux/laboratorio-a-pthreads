#!/bin/sh
# Parte II - Paso 1 de 2: EJECUTAR los experimentos del histograma
#
# Corre p2sec, p2mutex y p2priv con varios N y T, y guarda lo que imprimen en
# datos_p2.csv (datos "en bruto"). Al final llama a analizar_p2.py (Paso 2),
# que compara las 10 categorias, calcula speedup/eficiencia y dibuja los graficos.
#
# Uso: sh experimentos_p2.sh

export LC_ALL=C   # punto decimal (no coma) para no romper el CSV

VALORES_N="1000 100000 1000000 1000003 10000000"   # 1000003 no es multiplo de 2, 4 ni 8
VALORES_T="1 2 4 8"

# Agrega una fila a datos_p2.csv a partir de lo que imprimio un programa
#   $1 = version (secuencial / mutex / privado)   $2 = N   $3 = T   $4 = salida
guardar_fila() {
    VALORES=$(echo "$4" | awk -F'= ' '/^(Cat|Total|Tiempo)/ {sub(/ s$/, "", $2); printf ",%s", $2}')
    echo "$1,$2,$3$VALORES" >> datos_p2.csv
}

# 1. Compilar
echo "Compilando Parte II..."
gcc -O2 -pthread p2sec.c   -o p2sec   || exit 1
gcc -O2 -pthread p2mutex.c -o p2mutex || exit 1
gcc -O2 -pthread p2priv.c  -o p2priv  || exit 1

# 2. Ejecutar los experimentos
echo "version,N,T,c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,total,tiempo" > datos_p2.csv

for N in $VALORES_N; do
    echo "Ejecutando N = $N"
    guardar_fila secuencial "$N" 1 "$(./p2sec "$N")"

    for T in $VALORES_T; do
        guardar_fila mutex   "$N" "$T" "$(./p2mutex "$N" "$T")"
        guardar_fila privado "$N" "$T" "$(./p2priv  "$N" "$T")"
    done
done

echo "Datos guardados en datos_p2.csv"
echo

# 3. Analizar con Python
python3 analizar_p2.py
