#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, atoi/atol
#include <time.h>      // clock_gettime, para medir el tiempo

// Devuelve el momento actual en segundos (con decimales)
double ahora(void)
{
    struct timespec t;
    clock_gettime(CLOCK_REALTIME, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
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

    // 2. Producir y consumir en rafagas que llenan y vacian el buffer circular
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

    // 3. Verificar que cada elemento [0..TOTAL-1] fue consumido exactamente 1 vez
    long perdidos = 0;
    long duplicados = 0;
    for (long i = 0; i < TOTAL; i++) {
        if (vistos[i] == 0) perdidos++;
        else if (vistos[i] > 1) duplicados++;
    }

    // 4. Mostrar resultados
    printf("Total      = %ld\n", TOTAL);
    printf("Buffer     = %d\n", TAM_BUFFER);
    printf("Producidos = %ld\n", producidos);
    printf("Consumidos = %ld\n", consumidos);
    printf("SumaProd   = %lld\n", suma_prod);
    printf("SumaCons   = %lld\n", suma_cons);
    printf("Perdidos   = %ld\n", perdidos);
    printf("Duplicados = %ld\n", duplicados);
    printf("Tiempo secuencial = %.6f s\n", t1 - t0);

    free(buffer);
    free(vistos);
    return 0;
}
