#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atol, qsort
#include <time.h>      // clock_gettime, para medir el tiempo
#include <limits.h>    // INT_MAX, INT_MIN

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

    // 2. Calcular suma, minimo y maximo REPETICIONES veces y quedarse con la mediana.
    //    La vuelta r = -1 es de calentamiento (cache y frecuencia de la CPU): no se guarda
    long long suma = 0;  // long long: con N grande la suma no cabe en int
    int min = INT_MAX;
    int max = INT_MIN;
    double tiempos[REPETICIONES];

    for (int r = -1; r < REPETICIONES; r++) {
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
        if (r >= 0) tiempos[r] = t1 - t0;
    }

    double promedio = (double) suma / N;
    double t_mediana = mediana(tiempos, REPETICIONES);

    // 3. Mostrar resultados
    printf("N = %ld\n", N);
    printf("Suma     = %lld\n", suma);
    printf("Minimo   = %d\n", min);
    printf("Maximo   = %d\n", max);
    printf("Promedio = %.4f\n", promedio);
    printf("Tiempo secuencial (mediana de %d) = %.9f s\n", REPETICIONES, t_mediana);
    printf("Tiempo minimo = %.9f s\n", tiempos[0]);
    printf("Tiempo maximo = %.9f s\n", tiempos[REPETICIONES - 1]);

    free(datos);
    return 0;
}
