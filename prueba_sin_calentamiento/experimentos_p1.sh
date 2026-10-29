#!/bin/sh
# Parte I - Paso 1 de 2: EJECUTAR los experimentos
#
# Corre p1sec y p1par con varios N y T, y guarda lo que imprimen en datos_p1.csv
# (datos "en bruto", sin hacer cuentas). Cada programa repite su medicion 7 veces
# e imprime la mediana, la minima y la maxima. Al final llama a analizar_p1.py
# (Paso 2), que compara, calcula speedup y eficiencia y dibuja los graficos.
#
# Uso: sh experimentos_p1.sh

export LC_ALL=C   # punto decimal (no coma) para no romper el CSV

VALORES_N="1000 100000 1000000 1000003 10000000 100000000"   # 1000003 no es multiplo de 2, 4 ni 8
VALORES_T="1 2 4 8"

# Agrega una fila a datos_p1.csv a partir de lo que imprimio un programa
#   $1 = version (secuencial / paralelo)   $2 = N   $3 = T   $4 = salida del programa
guardar_fila() {
    VALORES=$(echo "$4" | awk -F'= ' '/^(Suma|Minimo|Maximo|Promedio|Tiempo|Primera)/ {sub(/ s$/, "", $2); printf ",%s", $2}')
    echo "$1,$2,$3$VALORES" >> datos_p1.csv
}

# 1. Compilar
echo "Compilando..."
gcc -O2 -pthread p1sec.c -o p1sec || exit 1
gcc -O2 -pthread p1par.c -o p1par || exit 1

# 2. Guardar los datos del equipo (uname dice si es Linux nativo o WSL)
{ date; uname -sr; lscpu | grep -E "Model name|^CPU\(s\)|Thread|Core|Socket"; free -h; gcc --version | head -n 1; } > entorno_p1.txt

# 3. Ejecutar los experimentos
echo "version,N,T,suma,minimo,maximo,promedio,tiempo,t_min,t_max,t_primera" > datos_p1.csv
: > repartos.txt

for N in $VALORES_N; do
    echo "Ejecutando N = $N"
    guardar_fila secuencial "$N" 1 "$(./p1sec "$N")"

    for T in $VALORES_T; do
        SALIDA=$(./p1par "$N" "$T")
        guardar_fila paralelo "$N" "$T" "$SALIDA"
        { echo "N = $N, T = $T"; echo "$SALIDA" | grep '^Thread [0-9]'; echo; } >> repartos.txt
    done
done

echo "Datos guardados en datos_p1.csv"
echo

# 4. Analizar con Python
python3 analizar_p1.py
