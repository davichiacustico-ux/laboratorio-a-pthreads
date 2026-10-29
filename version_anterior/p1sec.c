#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atoi/atol
#include <pthread.h>   // pthread_create, pthread_join, pthread_t
#include <time.h>      // clock_gettime, para medir el tiempo
#include <limits.h>    // INT_MAX, INT_MIN

#define REPETICIONES 1  // cuantas veces se repite la medicion para promediar

// Devuelve el momento actual en segundos (con decimales)
double ahora(void)
{
    struct timespec t;
    clock_gettime(CLOCK_REALTIME, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        printf("Uso: %s N\n", argv[0]);
        return 1;
    }

    long N = atol(argv[1]);
    if (N <= 0) {
        printf("N debe ser mayor que 0\n");
        return 1;
    }

    // 1. Crear el arreglo y llenarlo con numeros al azar (no se mide)
    int *datos = malloc(N * sizeof(int));
    if (datos == NULL) {
        printf("No hay memoria para N=%ld\n", N);
        return 1;
    }

    srand(42);  // semilla fija: siempre los mismos numeros
    for (long i = 0; i < N; i++)
        datos[i] = rand() % 1000;  // valores entre 0 y 999

    // 2. Calcular suma, minimo y maximo varias veces y promediar el tiempo
    long long suma = 0;  // long long: con N grande la suma no cabe en int
    int min = INT_MAX;
    int max = INT_MIN;
    double tiempo_total = 0;

    for (int r = 0; r < REPETICIONES; r++) {
        double t0 = ahora();

        suma = 0;
        min = INT_MAX;
        max = INT_MIN;
        for (long i = 0; i < N; i++) {
            suma += datos[i];
            if (datos[i] < min) min = datos[i];
            if (datos[i] > max) max = datos[i];
        }

        double t1 = ahora();
        tiempo_total += t1 - t0;
    }

    double promedio = (double) suma / N;
    double tiempo_promedio = tiempo_total / REPETICIONES;

    // 3. Mostrar resultados
    printf("N = %ld\n", N);
    printf("Suma     = %lld\n", suma);
    printf("Minimo   = %d\n", min);
    printf("Maximo   = %d\n", max);
    printf("Promedio = %.4f\n", promedio);
    printf("Tiempo secuencial (promedio de %d) = %.6f s\n", REPETICIONES, tiempo_promedio);

    free(datos);
    return 0;
}
