#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atoi/atol
#include <pthread.h>   // pthread_create, pthread_join, pthread_t
#include <time.h>      // clock_gettime, para medir el tiempo
#include <limits.h>    // INT_MAX, INT_MIN

#define REPETICIONES 1  // cuantas veces se repite la medicion para promediar

// "Libreta" de cada thread: lo que recibe y lo que devuelve
typedef struct {
    int id;
    long inicio, fin;     // segmento [inicio, fin)
    const int *datos;
    long long suma;       // resultados parciales
    int min, max;
} ArgsThread;

// Devuelve el momento actual en segundos (con decimales)
double ahora(void)
{
    struct timespec t;
    clock_gettime(CLOCK_REALTIME, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

// Trabajo de cada thread: recorre su segmento usando variables locales
// y escribe en su libreta una sola vez al final
void *trabajar(void *arg)
{
    ArgsThread *a = (ArgsThread *) arg;

    long long suma = 0;
    int min = INT_MAX;
    int max = INT_MIN;
    for (long i = a->inicio; i < a->fin; i++) {
        suma += a->datos[i];
        if (a->datos[i] < min) min = a->datos[i];
        if (a->datos[i] > max) max = a->datos[i];
    }

    a->suma = suma;
    a->min = min;
    a->max = max;
    return NULL;
}

int main(int argc, char *argv[])
{
    if (argc < 3) {
        printf("Uso: %s N T\n", argv[0]);
        return 1;
    }

    long N = atol(argv[1]);
    int T = atoi(argv[2]);
    if (N <= 0 || T <= 0) {
        printf("N y T deben ser mayores que 0\n");
        return 1;
    }

    // 1. Crear el arreglo igual que en p1sec.c (misma semilla = mismos datos)
    int *datos = malloc(N * sizeof(int));
    pthread_t *hilos = malloc(T * sizeof(pthread_t));
    ArgsThread *args = malloc(T * sizeof(ArgsThread));
    if (datos == NULL || hilos == NULL || args == NULL) {
        printf("No hay memoria para N=%ld\n", N);
        return 1;
    }

    srand(42);
    for (long i = 0; i < N; i++)
        datos[i] = rand() % 1000;

    // 2. Repartir el arreglo: los primeros 'resto' threads reciben uno extra
    long base = N / T;
    long resto = N % T;
    for (int id = 0; id < T; id++) {
        args[id].id = id;
        args[id].datos = datos;
        args[id].inicio = id * base + (id < resto ? id : resto);
        args[id].fin = args[id].inicio + base + (id < resto ? 1 : 0);
        printf("Thread %d: [%ld, %ld) -> %ld elementos\n",
               id, args[id].inicio, args[id].fin, args[id].fin - args[id].inicio);
    }

    // 3. Crear threads, esperarlos y combinar (se mide todo esto)
    long long suma = 0;
    int min = INT_MAX;
    int max = INT_MIN;
    double tiempo_total = 0;

    for (int r = 0; r < REPETICIONES; r++) {
        double t0 = ahora();

        for (int id = 0; id < T; id++)
            pthread_create(&hilos[id], NULL, trabajar, &args[id]);
        for (int id = 0; id < T; id++)
            pthread_join(hilos[id], NULL);

        // Sin mutex: cada thread escribio en su propia libreta
        // y pthread_join garantiza que ya terminaron
        suma = 0;
        min = INT_MAX;
        max = INT_MIN;
        for (int id = 0; id < T; id++) {
            suma += args[id].suma;
            if (args[id].min < min) min = args[id].min;
            if (args[id].max > max) max = args[id].max;
        }

        double t1 = ahora();
        tiempo_total += t1 - t0;
    }

    double promedio = (double) suma / N;  // suma global / N
    double tiempo_promedio = tiempo_total / REPETICIONES;

    // 4. Mostrar resultados (mismo formato que p1sec.c)
    printf("N = %ld\n", N);
    printf("Threads  = %d\n", T);
    printf("Suma     = %lld\n", suma);
    printf("Minimo   = %d\n", min);
    printf("Maximo   = %d\n", max);
    printf("Promedio = %.4f\n", promedio);
    printf("Tiempo paralelo (promedio de %d) = %.6f s\n", REPETICIONES, tiempo_promedio);

    free(datos);
    free(hilos);
    free(args);
    return 0;
}
