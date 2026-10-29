#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atol
#include <time.h>      // clock_gettime, para medir el tiempo

#define CATEGORIAS 10   // 10 intervalos: 0-9, 10-19, ..., 90-99
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

    // 1. Crear el arreglo y llenarlo con numeros entre 0 y 99 (no se mide)
    int *datos = malloc(N * sizeof(int));
    if (datos == NULL) {
        printf("No hay memoria para N=%ld\n", N);
        return 1;
    }

    srand(42);  // semilla fija: siempre los mismos numeros
    for (long i = 0; i < N; i++)
        datos[i] = rand() % 100;  // valores entre 0 y 99

    // 2. Construir el histograma secuencialmente y medir el tiempo
    long hist[CATEGORIAS];
    double tiempo_total = 0;

    for (int r = 0; r < REPETICIONES; r++) {
        double t0 = ahora();

        for (int c = 0; c < CATEGORIAS; c++)
            hist[c] = 0;

        for (long i = 0; i < N; i++) {
            int cat = datos[i] / 10;  // 0..9->0, 10..19->1, ..., 90..99->9
            hist[cat]++;
        }

        double t1 = ahora();
        tiempo_total += t1 - t0;
    }

    // 3. Verificar que la suma de las 10 categorias sea igual a N
    long total = 0;
    for (int c = 0; c < CATEGORIAS; c++)
        total += hist[c];

    double tiempo_promedio = tiempo_total / REPETICIONES;

    // 4. Mostrar resultados
    printf("N = %ld\n", N);
    for (int c = 0; c < CATEGORIAS; c++)
        printf("Cat %02d-%02d = %ld\n", c * 10, c * 10 + 9, hist[c]);
    printf("Total    = %ld\n", total);
    printf("Tiempo secuencial (promedio de %d) = %.6f s\n", REPETICIONES, tiempo_promedio);

    free(datos);
    return 0;
}
