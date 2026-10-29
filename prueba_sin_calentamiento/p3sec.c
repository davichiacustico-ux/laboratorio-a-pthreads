#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, calloc, atoi/atol, qsort
#include <time.h>      // clock_gettime, para medir el tiempo
#include <limits.h>    // INT_MAX

#define REPETICIONES 7  // mediciones que se guardan (impar: la mediana es el valor del medio)

// Devuelve el momento actual en segundos (con decimales).
// CLOCK_MONOTONIC no salta si alguien cambia la hora del sistema
double ahora(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

// Compara dos tiempos para qsort (de menor a mayor)
int comparar(const void *a, const void *b)
{
    double x = *(const double *) a;
    double y = *(const double *) b;
    return (x > y) - (x < y);
}

// Ordena los tiempos y devuelve la mediana; despues t[0] es el minimo y t[n-1] el maximo
double mediana(double *t, int n)
{
    qsort(t, n, sizeof(double), comparar);
    return t[n / 2];
}

int main(int argc, char *argv[])
{
    if (argc < 3) {
        printf("Uso: %s TOTAL TAM_BUFFER\n", argv[0]);
        return 1;
    }

    long TOTAL = atol(argv[1]);
    int TAM_BUFFER = atoi(argv[2]);
    if (TOTAL <= 0 || TAM_BUFFER <= 0) {
        printf("TOTAL y TAM_BUFFER deben ser mayores que 0\n");
        return 1;
    }
    if (TOTAL > INT_MAX) {
        printf("TOTAL debe ser como maximo %d (cada elemento se guarda como int)\n", INT_MAX);
        return 1;
    }

    // 1. Crear el buffer circular y el registro de verificacion
    int *buffer = malloc(TAM_BUFFER * sizeof(int));
    int *vistos = calloc(TOTAL, sizeof(int));
    if (buffer == NULL || vistos == NULL) {
        printf("No hay memoria\n");
        return 1;
    }

    int in = 0;       // indice de insercion
    int out = 0;      // indice de extraccion
    int cuenta = 0;   // elementos actuales en el buffer

    long producidos = 0;
    long consumidos = 0;
    long long suma_prod = 0;
    long long suma_cons = 0;

    long perdidos = 0;     // sumados en todas las ejecuciones
    long duplicados = 0;
    int rep_fallidas = 0;  // ejecuciones en las que algo no cuadro
    double tiempos[REPETICIONES];

    // 2. Producir y consumir en rafagas que llenan y vacian el buffer circular.
    //    Se repite REPETICIONES veces (mas una de calentamiento, r = -1, que no
    //    se mide) y cada ejecucion se verifica por separado
    for (int r = 0; r < REPETICIONES; r++) {
        in = out = cuenta = 0;
        producidos = consumidos = 0;
        suma_prod = suma_cons = 0;
        for (long i = 0; i < TOTAL; i++)
            vistos[i] = 0;

        double t0 = ahora();

        while (consumidos < TOTAL) {
            // Llenar el buffer hasta su capacidad o hasta terminar de producir
            while (cuenta < TAM_BUFFER && producidos < TOTAL) {
                int item = (int) producidos;   // cada elemento tiene su ID unico 0..TOTAL-1
                buffer[in] = item;
                in = (in + 1) % TAM_BUFFER;
                cuenta++;
                producidos++;
                suma_prod += item;
            }

            // Vaciar el buffer consumiendo los elementos insertados
            while (cuenta > 0) {
                int item = buffer[out];
                out = (out + 1) % TAM_BUFFER;
                cuenta--;
                consumidos++;
                suma_cons += item;
                vistos[item]++;
            }
        }

        double t1 = ahora();
        if (r >= 0) tiempos[r] = t1 - t0;

        // 3. Verificar que cada elemento [0..TOTAL-1] fue consumido exactamente 1 vez
        long perd = 0, dupl = 0;
        for (long i = 0; i < TOTAL; i++) {
            if (vistos[i] == 0) perd++;
            else if (vistos[i] > 1) dupl++;
        }
        perdidos += perd;
        duplicados += dupl;
        if (perd > 0 || dupl > 0 || cuenta != 0 || producidos != TOTAL ||
            consumidos != TOTAL || suma_prod != suma_cons)
            rep_fallidas++;
    }

    double t_primera = tiempos[0];
    double t_mediana = mediana(tiempos, REPETICIONES);

    // 4. Mostrar resultados (los conteos y sumas son de la ultima ejecucion;
    //    Perdidos, Duplicados y RepFallidas suman todas las ejecuciones)
    printf("Total       = %ld\n", TOTAL);
    printf("Buffer      = %d\n", TAM_BUFFER);
    printf("Producidos  = %ld\n", producidos);
    printf("Consumidos  = %ld\n", consumidos);
    printf("EnBuffer    = %d\n", cuenta);
    printf("SumaProd    = %lld\n", suma_prod);
    printf("SumaCons    = %lld\n", suma_cons);
    printf("Perdidos    = %ld\n", perdidos);
    printf("Duplicados  = %ld\n", duplicados);
    printf("RepFallidas = %d\n", rep_fallidas);
    printf("Tiempo secuencial (mediana de %d) = %.9f s\n", REPETICIONES, t_mediana);
    printf("Tiempo minimo = %.9f s\n", tiempos[0]);
    printf("Tiempo maximo = %.9f s\n", tiempos[REPETICIONES - 1]);
    printf("Primera vuelta = %.9f s\n", t_primera);

    free(buffer);
    free(vistos);
    return 0;
}
