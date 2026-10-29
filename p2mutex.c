#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atoi/atol, qsort, exit
#include <pthread.h>   // pthread_create, pthread_join, pthread_mutex_t
#include <time.h>      // clock_gettime, para medir el tiempo

#define CATEGORIAS 10   // 10 intervalos: 0-9, 10-19, ..., 90-99
#define REPETICIONES 7  // mediciones que se guardan (impar: la mediana es el valor del medio)

// Histograma global compartido y UN solo mutex global que protege las 10 casillas
// (la version con un mutex por categoria esta en p2mutexcat.c)
long hist_global[CATEGORIAS];
pthread_mutex_t candado = PTHREAD_MUTEX_INITIALIZER;

// "Libreta" de cada thread: que segmento del arreglo le toca
typedef struct {
    int id;
    long inicio, fin;     // segmento [inicio, fin)
    const int *datos;
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

// Llena el arreglo con valores entre 0 y 99. Con la semilla fija, p2sec, p2mutex,
// p2mutexcat y p2priv reciben exactamente los mismos datos.
//   'u' = uniforme: los 100 valores tienen la misma probabilidad
//   's' = sesgada: 9 de cada 10 valores salen entre 0 y 9 (~91 % cae en la categoria 0)
void generar(int *datos, long N, char dist)
{
    srand(42);
    for (long i = 0; i < N; i++) {
        if (dist == 's' && rand() % 10 != 0)
            datos[i] = rand() % 10;
        else
            datos[i] = rand() % 100;
    }
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
        printf("Uso: %s N T [u|s]\n", argv[0]);
        return 1;
    }

    long N = atol(argv[1]);
    int T = atoi(argv[2]);
    if (N <= 0 || T <= 0) {
        printf("N y T deben ser mayores que 0\n");
        return 1;
    }

    char dist = (argc > 3) ? argv[3][0] : 'u';  // distribucion de los datos (por defecto uniforme)
    if (dist != 'u' && dist != 's') {
        printf("La distribucion debe ser u (uniforme) o s (sesgada)\n");
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

    generar(datos, N, dist);

    // 2. Repartir el arreglo: los primeros 'resto' threads reciben uno extra
    long base = N / T;
    long resto = N % T;
    for (int id = 0; id < T; id++) {
        args[id].id = id;
        args[id].datos = datos;
        args[id].inicio = id * base + (id < resto ? id : resto);
        args[id].fin = args[id].inicio + base + (id < resto ? 1 : 0);
    }

    // 3. Crear threads y esperarlos (se mide todo esto), REPETICIONES veces;
    //    se reporta la mediana. La vuelta r = -1 es de calentamiento
    double tiempos[REPETICIONES];

    for (int r = -1; r < REPETICIONES; r++) {
        double t0 = ahora();

        for (int c = 0; c < CATEGORIAS; c++)
            hist_global[c] = 0;

        for (int id = 0; id < T; id++)
            crear_thread(&hilos[id], trabajar_mutex, &args[id]);
        for (int id = 0; id < T; id++)
            pthread_join(hilos[id], NULL);

        double t1 = ahora();
        if (r >= 0) tiempos[r] = t1 - t0;
    }

    // 4. Verificar que la suma de las 10 categorias sea igual a N
    long total = 0;
    for (int c = 0; c < CATEGORIAS; c++)
        total += hist_global[c];

    double t_mediana = mediana(tiempos, REPETICIONES);

    // 5. Mostrar resultados (mismo formato que p2sec.c)
    printf("N = %ld\n", N);
    printf("Threads  = %d\n", T);
    printf("Distribucion = %s\n", dist == 'u' ? "uniforme" : "sesgada");
    for (int c = 0; c < CATEGORIAS; c++)
        printf("Cat %02d-%02d = %ld\n", c * 10, c * 10 + 9, hist_global[c]);
    printf("Total    = %ld\n", total);
    printf("Tiempo paralelo mutex (mediana de %d) = %.9f s\n", REPETICIONES, t_mediana);
    printf("Tiempo minimo = %.9f s\n", tiempos[0]);
    printf("Tiempo maximo = %.9f s\n", tiempos[REPETICIONES - 1]);

    pthread_mutex_destroy(&candado);
    free(datos);
    free(hilos);
    free(args);
    return 0;
}
