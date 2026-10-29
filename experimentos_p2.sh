#!/bin/sh
# Parte II - Paso 1 de 2: EJECUTAR los experimentos del histograma
#
# Corre p2sec, p2mutex (un mutex global), p2mutexcat (un mutex por categoria) y
# p2priv (histograma privado) con varios N y T, y guarda lo que imprimen en
# datos_p2.csv (datos "en bruto"). Primero con datos uniformes y despues, con
# N = 10 000 000, con datos sesgados, para ver como influye la distribucion en la
# contencion. Cada programa repite su medicion 7 veces e imprime la mediana.
# Al final llama a analizar_p2.py (Paso 2), que compara las 10 categorias,
# calcula speedup/eficiencia y dibuja los graficos.
#
# Uso: sh experimentos_p2.sh

export LC_ALL=C   # punto decimal (no coma) para no romper el CSV

VALORES_N="1000 100000 1000000 1000003 10000000"   # 1000003 no es multiplo de 2, 4 ni 8
VALORES_T="1 2 4 8"
N_SESGADA=10000000                                 # N para comparar uniforme vs. sesgada

# Agrega una fila a datos_p2.csv a partir de lo que imprimio un programa
#   $1 = version (secuencial / mutex / mutexcat / privado)   $2 = distribucion (u / s)
#   $3 = N   $4 = T   $5 = salida
guardar_fila() {
    VALORES=$(echo "$5" | awk -F'= ' '/^(Cat|Total|Tiempo)/ {sub(/ s$/, "", $2); printf ",%s", $2}')
    echo "$1,$2,$3,$4$VALORES" >> datos_p2.csv
}

# Corre las 4 versiones con un N y una distribucion
#   $1 = distribucion (u / s)   $2 = N
experimento() {
    guardar_fila secuencial "$1" "$2" 1 "$(./p2sec "$2" "$1")"
    for T in $VALORES_T; do
        guardar_fila mutex    "$1" "$2" "$T" "$(./p2mutex    "$2" "$T" "$1")"
        guardar_fila mutexcat "$1" "$2" "$T" "$(./p2mutexcat "$2" "$T" "$1")"
        guardar_fila privado  "$1" "$2" "$T" "$(./p2priv     "$2" "$T" "$1")"
    done
}

# 1. Compilar
echo "Compilando Parte II..."
gcc -O2 -pthread p2sec.c      -o p2sec      || exit 1
gcc -O2 -pthread p2mutex.c    -o p2mutex    || exit 1
gcc -O2 -pthread p2mutexcat.c -o p2mutexcat || exit 1
gcc -O2 -pthread p2priv.c     -o p2priv     || exit 1

# 2. Guardar los datos del equipo (uname dice si es Linux nativo o WSL)
{ date; uname -sr; lscpu | grep -E "Model name|^CPU\(s\)|Thread|Core|Socket"; free -h; gcc --version | head -n 1; } > entorno_p2.txt

# 3. Ejecutar los experimentos
echo "version,dist,N,T,c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,total,tiempo,t_min,t_max" > datos_p2.csv

for N in $VALORES_N; do
    echo "Ejecutando N = $N (uniforme)"
    experimento u "$N"
done

echo "Ejecutando N = $N_SESGADA (sesgada)"
experimento s "$N_SESGADA"

echo "Datos guardados en datos_p2.csv"
echo

# 4. Analizar con Python
python3 analizar_p2.py
