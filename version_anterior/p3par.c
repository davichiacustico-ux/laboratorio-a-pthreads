#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, calloc, atoi/atol
#include <pthread.h>   // pthread_create, pthread_join, mutex, cond
#include <time.h>      // clock_gettime, para medir el tiempo

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

// Devuelve el momento actual en segundos (con decimales)
double ahora(void)
{
    struct timespec t;
    clock_gettime(CLOCK_REALTIME, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
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

    // 3. Crear productores y consumidores, esperar a todos y medir el tiempo
    double t0 = ahora();

    for (int i = 0; i < P; i++)
        pthread_create(&hilos_p[i], NULL, productor, &args_p[i]);
    for (int i = 0; i < C; i++)
        pthread_create(&hilos_c[i], NULL, consumidor, &args_c[i]);

    for (int i = 0; i < P; i++)
        pthread_join(hilos_p[i], NULL);
    for (int i = 0; i < C; i++)
        pthread_join(hilos_c[i], NULL);

    double t1 = ahora();

    // 4. Combinar las libretas para verificar totales y sumas
    long producidos = 0, consumidos = 0;
    long long suma_prod = 0, suma_cons = 0;

    for (int i = 0; i < P; i++) {
        producidos += args_p[i].cantidad;
        suma_prod += args_p[i].suma;
    }
    for (int i = 0; i < C; i++) {
        consumidos += args_c[i].cantidad;
        suma_cons += args_c[i].suma;
    }

    // Verificar que cada elemento [0..TOTAL-1] fue consumido exactamente 1 vez
    long perdidos = 0, duplicados = 0;
    for (long i = 0; i < TOTAL; i++) {
        if (vistos[i] == 0) perdidos++;
        else if (vistos[i] > 1) duplicados++;
    }

    // 5. Mostrar resultados
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
    printf("Tiempo paralelo = %.6f s\n", t1 - t0);

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
