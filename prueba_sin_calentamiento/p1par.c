#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atoi/atol, qsort, exit
#include <pthread.h>   // pthread_create, pthread_join, pthread_t
#include <time.h>      // clock_gettime, para medir el tiempo
#include <limits.h>    // INT_MAX, INT_MIN

#define REPETICIONES 7  // mediciones que se guardan (impar: la mediana es el valor del medio)

// "Libreta" de cada thread: lo que recibe y lo que devuelve
typedef struct {
    int id;
    long inicio, fin;     // segmento [inicio, fin)
    const int *datos;
    long long suma;       // resultados parciales
    int min, max;
} ArgsThread;

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

// Crea un thread; si el sistema no puede crearlo, termina en vez de seguir
// con un pthread_t sin inicializar (el pthread_join fallaria)
void crear_thread(pthread_t *hilo, void *(*funcion)(void *), void *arg)
{
    if (pthread_create(hilo, NULL, funcion, arg) != 0) {
        printf("No se pudo crear un thread\n");
        exit(1);
    }
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

    // 3. Crear threads, esperarlos y combinar (se mide todo esto), REPETICIONES
    //    veces; se reporta la mediana. La vuelta r = -1 es de calentamiento
    long long suma = 0;
    int min = INT_MAX;
    int max = INT_MIN;
    double tiempos[REPETICIONES];

    for (int r = 0; r < REPETICIONES; r++) {
        double t0 = ahora();

        for (int id = 0; id < T; id++)
            crear_thread(&hilos[id], trabajar, &args[id]);
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
        if (r >= 0) tiempos[r] = t1 - t0;
    }

    double promedio = (double) suma / N;  // suma global / N
    double t_primera = tiempos[0];
    double t_mediana = mediana(tiempos, REPETICIONES);

    // 4. Mostrar resultados (mismo formato que p1sec.c)
    printf("N = %ld\n", N);
    printf("Threads  = %d\n", T);
    printf("Suma     = %lld\n", suma);
    printf("Minimo   = %d\n", min);
    printf("Maximo   = %d\n", max);
    printf("Promedio = %.4f\n", promedio);
    printf("Tiempo paralelo (mediana de %d) = %.9f s\n", REPETICIONES, t_mediana);
    printf("Tiempo minimo = %.9f s\n", tiempos[0]);
    printf("Tiempo maximo = %.9f s\n", tiempos[REPETICIONES - 1]);
    printf("Primera vuelta = %.9f s\n", t_primera);

    free(datos);
    free(hilos);
    free(args);
    return 0;
}
