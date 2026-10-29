#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, calloc, atoi/atol, qsort, exit
#include <pthread.h>   // pthread_create, pthread_join, mutex, cond
#include <time.h>      // clock_gettime, para medir el tiempo
#include <limits.h>    // INT_MAX

#define REPETICIONES 7  // mediciones que se guardan (impar: la mediana es el valor del medio)

// Buffer circular compartido y sus indices
int *buffer;
int TAM_BUFFER;
int in = 0;            // indice donde inserta el siguiente productor
int out = 0;           // indice de donde extrae el siguiente consumidor
int cuenta = 0;        // cuantos elementos hay ahora mismo en el buffer

// Sincronizacion: un mutex y dos variables de condicion
pthread_mutex_t candado = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t no_lleno = PTHREAD_COND_INITIALIZER;   // productores esperan aqui si cuenta == TAM_BUFFER
pthread_cond_t no_vacio = PTHREAD_COND_INITIALIZER;   // consumidores esperan aqui si cuenta == 0

// Registro de verificacion (para comprobar que cada elemento se consume 1 sola vez)
int *vistos;

// "Libreta" de cada thread (productor o consumidor)
typedef struct {
    int id;
    long inicio, fin;       // rango de elementos [inicio, fin) que le toca producir o consumir
    long cantidad;          // cuantos elementos produjo o consumio este thread
    long long suma;         // suma de los elementos producidos o consumidos por este thread
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

// Trabajo de cada PRODUCTOR: genera los enteros de su segmento [inicio, fin)
// y los mete en el buffer circular esperando si esta lleno
void *productor(void *arg)
{
    ArgsThread *a = (ArgsThread *) arg;
    long cant = 0;
    long long suma = 0;

    for (long item = a->inicio; item < a->fin; item++) {
        pthread_mutex_lock(&candado);

        // Si el buffer esta lleno, dormir hasta que un consumidor saque algo
        while (cuenta == TAM_BUFFER)
            pthread_cond_wait(&no_lleno, &candado);

        // Insertar en el buffer circular
        buffer[in] = (int) item;
        in = (in + 1) % TAM_BUFFER;
        cuenta++;

        // Avisar a los consumidores que ya hay al menos un elemento disponible
        pthread_cond_signal(&no_vacio);
        pthread_mutex_unlock(&candado);

        cant++;
        suma += item;
    }

    a->cantidad = cant;
    a->suma = suma;
    return NULL;
}

// Trabajo de cada CONSUMIDOR: extrae la cantidad de elementos que le toca
// esperando si el buffer circular esta vacio
void *consumidor(void *arg)
{
    ArgsThread *a = (ArgsThread *) arg;
    long por_consumir = a->fin - a->inicio;
    long cant = 0;
    long long suma = 0;

    for (long k = 0; k < por_consumir; k++) {
        pthread_mutex_lock(&candado);

        // Si el buffer esta vacio, dormir hasta que un productor meta algo
        while (cuenta == 0)
            pthread_cond_wait(&no_vacio, &candado);

        // Extraer del buffer circular
        int item = buffer[out];
        out = (out + 1) % TAM_BUFFER;
        cuenta--;
        vistos[item]++;   // anotamos que este elemento fue consumido

        // Avisar a los productores que ya quedo al menos un hueco libre
        pthread_cond_signal(&no_lleno);
        pthread_mutex_unlock(&candado);

        cant++;
        suma += item;
    }

    a->cantidad = cant;
    a->suma = suma;
    return NULL;
}

int main(int argc, char *argv[])
{
    if (argc < 5) {
        printf("Uso: %s TOTAL P C TAM_BUFFER\n", argv[0]);
        return 1;
    }

    long TOTAL = atol(argv[1]);
    int P = atoi(argv[2]);
    int C = atoi(argv[3]);
    TAM_BUFFER = atoi(argv[4]);

    if (TOTAL <= 0 || P <= 0 || C <= 0 || TAM_BUFFER <= 0) {
        printf("Todos los parametros deben ser mayores que 0\n");
        return 1;
    }
    if (TOTAL > INT_MAX) {
        printf("TOTAL debe ser como maximo %d (cada elemento se guarda como int)\n", INT_MAX);
        return 1;
    }

    // 1. Reservar memoria para el buffer, el arreglo de verificacion y los threads
    buffer = malloc(TAM_BUFFER * sizeof(int));
    vistos = calloc(TOTAL, sizeof(int));
    pthread_t *hilos_p = malloc(P * sizeof(pthread_t));
    pthread_t *hilos_c = malloc(C * sizeof(pthread_t));
    ArgsThread *args_p = malloc(P * sizeof(ArgsThread));
    ArgsThread *args_c = malloc(C * sizeof(ArgsThread));

    if (!buffer || !vistos || !hilos_p || !hilos_c || !args_p || !args_c) {
        printf("No hay memoria\n");
        return 1;
    }

    // 2. Repartir los TOTAL elementos entre los P productores y entre los C consumidores
    long base_p = TOTAL / P, resto_p = TOTAL % P;
    for (int i = 0; i < P; i++) {
        args_p[i].id = i;
        args_p[i].inicio = i * base_p + (i < resto_p ? i : resto_p);
        args_p[i].fin = args_p[i].inicio + base_p + (i < resto_p ? 1 : 0);
    }

    long base_c = TOTAL / C, resto_c = TOTAL % C;
    for (int i = 0; i < C; i++) {
        args_c[i].id = i;
        args_c[i].inicio = i * base_c + (i < resto_c ? i : resto_c);
        args_c[i].fin = args_c[i].inicio + base_c + (i < resto_c ? 1 : 0);
    }

    // 3. Crear productores y consumidores, esperar a todos y medir el tiempo.
    //    Se repite REPETICIONES veces (mas una de calentamiento, r = -1, que no
    //    se mide) y cada ejecucion se verifica por separado
    long producidos = 0, consumidos = 0;
    long long suma_prod = 0, suma_cons = 0;
    long perdidos = 0, duplicados = 0;  // sumados en todas las ejecuciones
    int rep_fallidas = 0;               // ejecuciones en las que algo no cuadro
    double tiempos[REPETICIONES];

    for (int r = 0; r < REPETICIONES; r++) {
        // Buffer vacio y registro de verificacion en cero (no se mide)
        in = out = cuenta = 0;
        for (long i = 0; i < TOTAL; i++)
            vistos[i] = 0;

        double t0 = ahora();

        for (int i = 0; i < P; i++)
            crear_thread(&hilos_p[i], productor, &args_p[i]);
        for (int i = 0; i < C; i++)
            crear_thread(&hilos_c[i], consumidor, &args_c[i]);

        for (int i = 0; i < P; i++)
            pthread_join(hilos_p[i], NULL);
        for (int i = 0; i < C; i++)
            pthread_join(hilos_c[i], NULL);

        double t1 = ahora();
        if (r >= 0) tiempos[r] = t1 - t0;

        // 4. Combinar las libretas para verificar totales y sumas
        producidos = consumidos = 0;
        suma_prod = suma_cons = 0;
        for (int i = 0; i < P; i++) {
            producidos += args_p[i].cantidad;
            suma_prod += args_p[i].suma;
        }
        for (int i = 0; i < C; i++) {
            consumidos += args_c[i].cantidad;
            suma_cons += args_c[i].suma;
        }

        // Verificar que cada elemento [0..TOTAL-1] fue consumido exactamente 1 vez
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

    // 5. Mostrar resultados (los conteos y sumas son de la ultima ejecucion;
    //    Perdidos, Duplicados y RepFallidas suman todas las ejecuciones)
    printf("Total        = %ld\n", TOTAL);
    printf("Productores  = %d\n", P);
    printf("Consumidores = %d\n", C);
    printf("Buffer       = %d\n", TAM_BUFFER);
    printf("Producidos   = %ld\n", producidos);
    printf("Consumidos   = %ld\n", consumidos);
    printf("EnBuffer     = %d\n", cuenta);
    printf("SumaProd     = %lld\n", suma_prod);
    printf("SumaCons     = %lld\n", suma_cons);
    printf("Perdidos     = %ld\n", perdidos);
    printf("Duplicados   = %ld\n", duplicados);
    printf("RepFallidas  = %d\n", rep_fallidas);
    printf("Tiempo paralelo (mediana de %d) = %.9f s\n", REPETICIONES, t_mediana);
    printf("Tiempo minimo = %.9f s\n", tiempos[0]);
    printf("Tiempo maximo = %.9f s\n", tiempos[REPETICIONES - 1]);
    printf("Primera vuelta = %.9f s\n", t_primera);

    pthread_mutex_destroy(&candado);
    pthread_cond_destroy(&no_lleno);
    pthread_cond_destroy(&no_vacio);
    free(buffer);
    free(vistos);
    free(hilos_p);
    free(hilos_c);
    free(args_p);
    free(args_c);
    return 0;
}
