#!/bin/sh
# Parte III - Paso 1 de 2: EJECUTAR los experimentos de Productores-Consumidores
#
# Corre p3sec y p3par con distintas cantidades de productores (P), consumidores (C)
# y tamanos de buffer (B), y guarda lo que imprimen en datos_p3.csv. Cada programa
# se ejecuta 8 veces por dentro (1 de calentamiento + 7 medidas) y verifica cada una.
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
    VALORES=$(echo "$6" | awk -F'= ' '/^(Producidos|Consumidos|EnBuffer|SumaProd|SumaCons|Perdidos|Duplicados|RepFallidas|Tiempo)/ {sub(/ s$/, "", $2); printf ",%s", $2}')
    echo "$1,$2,$3,$4,$5$VALORES" >> datos_p3.csv
}

# 1. Compilar
echo "Compilando Parte III..."
gcc -O2 -pthread p3sec.c -o p3sec || exit 1
gcc -O2 -pthread p3par.c -o p3par || exit 1

# 2. Guardar los datos del equipo (uname dice si es Linux nativo o WSL)
{ date; uname -sr; lscpu | grep -E "Model name|^CPU\(s\)|Thread|Core|Socket"; free -h; gcc --version | head -n 1; } > entorno_p3.txt

# 3. Ejecutar los experimentos
echo "version,total,P,C,buffer,producidos,consumidos,en_buffer,suma_prod,suma_cons,perdidos,duplicados,rep_fallidas,tiempo,t_min,t_max" > datos_p3.csv

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

# 4. Analizar con Python
python3 analizar_p3.py

# 5. Contar los cambios de contexto (cuantas veces se duermen los threads)
echo
echo "Contando cambios de contexto..."
python3 cambios_contexto_p3.py > cambios_contexto_p3.csv && echo "Guardados en cambios_contexto_p3.csv"
