#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atoi/atol
#include <pthread.h>   // pthread_create, pthread_join, pthread_mutex_t
#include <time.h>      // clock_gettime, para medir el tiempo

#define CATEGORIAS 10   // 10 intervalos: 0-9, 10-19, ..., 90-99
#define REPETICIONES 1  // cuantas veces se repite la medicion para promediar

// Histograma global compartido y un mutex por categoria (o global)
// Usamos un mutex compartido para proteger el incremento del histograma
long hist_global[CATEGORIAS];
pthread_mutex_t candado = PTHREAD_MUTEX_INITIALIZER;

// "Libreta" de cada thread: que segmento del arreglo le toca
typedef struct {
    int id;
    long inicio, fin;     // segmento [inicio, fin)
    const int *datos;
} ArgsThread;

// Devuelve el momento actual en segundos (con decimales)
double ahora(void)
{
    struct timespec t;
    clock_gettime(CLOCK_REALTIME, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

// Estrategia 1 (Mutex compartido): cada thread bloquea el mutex al actualizar
// el histograma compartido para evitar condiciones de carrera
void *trabajar_mutex(void *arg)
{
    ArgsThread *a = (ArgsThread *) arg;

    for (long i = a->inicio; i < a->fin; i++) {
        int cat = a->datos[i] / 10;
        pthread_mutex_lock(&candado);
        hist_global[cat]++;
        pthread_mutex_unlock(&candado);
    }
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

    // 1. Crear el arreglo igual que en p2sec.c (misma semilla = mismos datos)
    int *datos = malloc(N * sizeof(int));
    pthread_t *hilos = malloc(T * sizeof(pthread_t));
    ArgsThread *args = malloc(T * sizeof(ArgsThread));
    if (datos == NULL || hilos == NULL || args == NULL) {
        printf("No hay memoria para N=%ld\n", N);
        return 1;
    }

    srand(42);
    for (long i = 0; i < N; i++)
        datos[i] = rand() % 100;

    // 2. Repartir el arreglo: los primeros 'resto' threads reciben uno extra
    long base = N / T;
    long resto = N % T;
    for (int id = 0; id < T; id++) {
        args[id].id = id;
        args[id].datos = datos;
        args[id].inicio = id * base + (id < resto ? id : resto);
        args[id].fin = args[id].inicio + base + (id < resto ? 1 : 0);
    }

    // 3. Crear threads y esperarlos (se mide todo esto)
    double tiempo_total = 0;

    for (int r = 0; r < REPETICIONES; r++) {
        double t0 = ahora();

        for (int c = 0; c < CATEGORIAS; c++)
            hist_global[c] = 0;

        for (int id = 0; id < T; id++)
            pthread_create(&hilos[id], NULL, trabajar_mutex, &args[id]);
        for (int id = 0; id < T; id++)
            pthread_join(hilos[id], NULL);

        double t1 = ahora();
        tiempo_total += t1 - t0;
    }

    // 4. Verificar que la suma de las 10 categorias sea igual a N
    long total = 0;
    for (int c = 0; c < CATEGORIAS; c++)
        total += hist_global[c];

    double tiempo_promedio = tiempo_total / REPETICIONES;

    // 5. Mostrar resultados (mismo formato que p2sec.c)
    printf("N = %ld\n", N);
    printf("Threads  = %d\n", T);
    for (int c = 0; c < CATEGORIAS; c++)
        printf("Cat %02d-%02d = %ld\n", c * 10, c * 10 + 9, hist_global[c]);
    printf("Total    = %ld\n", total);
    printf("Tiempo paralelo mutex (promedio de %d) = %.6f s\n", REPETICIONES, tiempo_promedio);

    pthread_mutex_destroy(&candado);
    free(datos);
    free(hilos);
    free(args);
    return 0;
}
