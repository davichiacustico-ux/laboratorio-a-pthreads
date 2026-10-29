#include <stdio.h>     // printf
#include <stdlib.h>    // malloc, free, rand, srand, atol, qsort
#include <time.h>      // clock_gettime, para medir el tiempo

#define CATEGORIAS 10   // 10 intervalos: 0-9, 10-19, ..., 90-99
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

int main(int argc, char *argv[])
{
    if (argc < 2) {
        printf("Uso: %s N [u|s]\n", argv[0]);
        return 1;
    }

    long N = atol(argv[1]);
    if (N <= 0) {
        printf("N debe ser mayor que 0\n");
        return 1;
    }

    char dist = (argc > 2) ? argv[2][0] : 'u';  // distribucion de los datos (por defecto uniforme)
    if (dist != 'u' && dist != 's') {
        printf("La distribucion debe ser u (uniforme) o s (sesgada)\n");
        return 1;
    }

    // 1. Crear el arreglo y llenarlo con numeros entre 0 y 99 (no se mide)
    int *datos = malloc(N * sizeof(int));
    if (datos == NULL) {
        printf("No hay memoria para N=%ld\n", N);
        return 1;
    }

    generar(datos, N, dist);

    // 2. Construir el histograma REPETICIONES veces y quedarse con la mediana del tiempo.
    //    La vuelta r = -1 es de calentamiento: no se guarda
    long hist[CATEGORIAS];
    double tiempos[REPETICIONES];

    for (int r = -1; r < REPETICIONES; r++) {
        double t0 = ahora();

        for (int c = 0; c < CATEGORIAS; c++)
            hist[c] = 0;

        for (long i = 0; i < N; i++) {
            int cat = datos[i] / 10;  // 0..9->0, 10..19->1, ..., 90..99->9
            hist[cat]++;
        }

        double t1 = ahora();
        if (r >= 0) tiempos[r] = t1 - t0;
    }

    // 3. Verificar que la suma de las 10 categorias sea igual a N
    long total = 0;
    for (int c = 0; c < CATEGORIAS; c++)
        total += hist[c];

    double t_mediana = mediana(tiempos, REPETICIONES);

    // 4. Mostrar resultados
    printf("N = %ld\n", N);
    printf("Distribucion = %s\n", dist == 'u' ? "uniforme" : "sesgada");
    for (int c = 0; c < CATEGORIAS; c++)
        printf("Cat %02d-%02d = %ld\n", c * 10, c * 10 + 9, hist[c]);
    printf("Total    = %ld\n", total);
    printf("Tiempo secuencial (mediana de %d) = %.9f s\n", REPETICIONES, t_mediana);
    printf("Tiempo minimo = %.9f s\n", tiempos[0]);
    printf("Tiempo maximo = %.9f s\n", tiempos[REPETICIONES - 1]);

    free(datos);
    return 0;
}
