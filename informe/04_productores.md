# 4. Productores y consumidores (Parte III)

## 4.1 Diseño del buffer y de la sincronización

El estado compartido es `buffer[TAM_BUFFER]` (arreglo circular), `in` (próxima posición donde insertar), `out` (próxima posición de donde extraer) y `cuenta` (elementos almacenados, entre 0 y `TAM_BUFFER`). Los índices avanzan con `(i + 1) % TAM_BUFFER`, así que el arreglo se recorre en círculo y se conserva el orden de llegada. Un mutex, `candado`, protege todo ese estado, y dos variables de condición coordinan las esperas:

- `no_lleno`: los productores esperan en ella mientras `cuenta == TAM_BUFFER`;
- `no_vacio`: los consumidores esperan en ella mientras `cuenta == 0`.

```c
pthread_mutex_lock(&candado);
while (cuenta == TAM_BUFFER)                 // buffer lleno: dormir
    pthread_cond_wait(&no_lleno, &candado);  // suelta el candado mientras duerme
buffer[in] = (int) item;                     // insertar
in = (in + 1) % TAM_BUFFER;
cuenta++;
pthread_cond_signal(&no_vacio);              // despierta a un consumidor
pthread_mutex_unlock(&candado);
```

El consumidor es simétrico: espera en `no_vacio` mientras `cuenta == 0`, extrae de `buffer[out]` y avisa en `no_lleno`. La condición se vuelve a evaluar con `while` y no con `if` porque, entre el `signal` y el momento en que el thread despertado recupera el candado, otro thread del mismo tipo puede haberse llevado el elemento (o el hueco); además, POSIX admite despertares espurios. Como hay una variable de condición para cada tipo de thread, un `signal` nunca despierta a un thread del tipo equivocado.

Los TOTAL elementos son los enteros 0, 1, …, TOTAL − 1, repartidos en bloques entre los P productores (el mismo reparto de la Parte I). Cada consumidor extrae una cuota fija, también repartida en bloques; como las cuotas suman exactamente TOTAL, ningún consumidor espera un elemento que nunca llegará.

## 4.2 Verificación

Como cada elemento es un entero distinto, la verificación es exacta. En cada ejecución se comprueba que:

1. Producidos = Consumidos = TOTAL y el buffer termina vacío (`cuenta == 0`).
2. La suma de lo producido y la de lo consumido valen $0 + 1 + \dots + (\text{TOTAL} - 1) = \text{TOTAL}(\text{TOTAL} - 1)/2 = 5\,000\,250\,003$.
3. Cada consumidor hace `vistos[item]++` dentro de la sección crítica; al final todas las casillas de `vistos[0..TOTAL-1]` deben valer exactamente 1. Una casilla en 0 es un elemento perdido y una mayor que 1, un duplicado.

Cada configuración se ejecuta 8 veces (1 de calentamiento y 7 medidas) y cada ejecución se verifica por separado. En las 18 configuraciones (144 ejecuciones) hubo 0 elementos perdidos, 0 duplicados y 0 ejecuciones fallidas. También se probaron casos extremos con buffer de una sola posición (8 productores y 1 consumidor, 1 productor y 8 consumidores) y con menos elementos que threads (5 elementos, 8 productores y 8 consumidores), sin errores.

## 4.3 Resultados

<!-- tabla:p3 -->

| Buffer | P–C | Ts (ms) | Tp (ms) | Tp mín – máx (ms) | Tp / Ts | Perdidos | Duplicados | Ejec. fallidas | Estado |
|--:|:-:|--:|--:|--:|--:|--:|--:|--:|:-:|
| 8 | 1P–1C | 0.753 | 445 | 443 – 448 | 590 | 0 | 0 | 0 | OK |
|  | 2P–2C |  | 1901 | 1868 – 1910 | 2523 | 0 | 0 | 0 | OK |
|  | 4P–4C |  | 684 | 678 – 695 | 907 | 0 | 0 | 0 | OK |
|  | 8P–8C |  | 718 | 710 – 724 | 953 | 0 | 0 | 0 | OK |
|  | 2P–4C |  | 746 | 728 – 774 | 990 | 0 | 0 | 0 | OK |
|  | 4P–2C |  | 771 | 737 – 803 | 1023 | 0 | 0 | 0 | OK |
| 64 | 1P–1C | 1.35 | 55.1 | 53.1 – 56.0 | 41 | 0 | 0 | 0 | OK |
|  | 2P–2C |  | 760 | 661 – 865 | 561 | 0 | 0 | 0 | OK |
|  | 4P–4C |  | 122 | 117 – 133 | 90 | 0 | 0 | 0 | OK |
|  | 8P–8C |  | 128 | 121 – 137 | 94 | 0 | 0 | 0 | OK |
|  | 2P–4C |  | 188 | 140 – 209 | 139 | 0 | 0 | 0 | OK |
|  | 4P–2C |  | 171 | 163 – 211 | 126 | 0 | 0 | 0 | OK |
| 1024 | 1P–1C | 1.43 | 17.5 | 15.3 – 18.8 | 12 | 0 | 0 | 0 | OK |
|  | 2P–2C |  | 58.5 | 36.6 – 66.6 | 41 | 0 | 0 | 0 | OK |
|  | 4P–4C |  | 19.6 | 18.7 – 26.6 | 14 | 0 | 0 | 0 | OK |
|  | 8P–8C |  | 25.2 | 24.4 – 28.9 | 18 | 0 | 0 | 0 | OK |
|  | 2P–4C |  | 58.5 | 38.6 – 76.7 | 41 | 0 | 0 | 0 | OK |
|  | 4P–2C |  | 58.7 | 47.9 – 77.4 | 41 | 0 | 0 | 0 | OK |

: Productores y consumidores con TOTAL = 100 003 elementos. Tiempos: mediana de 7 mediciones. Perdidos, duplicados y ejecuciones fallidas suman las 8 ejecuciones de cada configuración (1 de calentamiento + 7 medidas).

<!-- /tabla:p3 -->

![Tiempo de cada configuración: mediana de 7 mediciones; la barra vertical va de la medición más rápida a la más lenta. Escala logarítmica.](figuras/tiempos_p3.svg){width=88%}

<!-- tabla:p3_contexto -->

| P–C | Esperas (B = 8) | ms (B = 8) | Esperas (B = 64) | ms (B = 64) | Esperas (B = 1024) | ms (B = 1024) |
|:-:|--:|--:|--:|--:|--:|--:|
| 1P–1C | 25 050 | 444 | 3 021 | 53.5 | 78 | 18.7 |
| 2P–2C | 172 441 | 1892 | 80 336 | 894 | 5 437 | 54.9 |
| 4P–4C | 90 599 | 688 | 16 617 | 122 | 4 964 | 21.9 |
| 8P–8C | 95 657 | 721 | 19 999 | 126 | 8 955 | 24.8 |
| 2P–4C | 84 436 | 778 | 19 311 | 165 | 7 612 | 58.2 |
| 4P–2C | 84 716 | 773 | 19 209 | 170 | 7 498 | 68.9 |

: Esperas por ejecución: cambios de contexto voluntarios, es decir, cuántas veces se durmió algún thread en el mutex o en una variable de condición (sumando todos los threads, medido con `getrusage` por `cambios_contexto_p3.py`), y tiempo de esa misma corrida. B = tamaño del buffer.

<!-- /tabla:p3_contexto -->

- **El paralelo es mucho más lento que el secuencial, y es lo esperable.** El secuencial produce y consume los 100 003 enteros en 0.75 a 1.43 ms; la mejor configuración paralela tarda 17.5 ms (12 veces más) y la peor 1.9 s (unas 2 500 veces más). Cada elemento cuesta un `lock` y un `unlock`, y cada vez que el buffer se llena o se vacía un thread se duerme y otro debe despertarlo, lo que en este equipo cuesta del orden de 10 µs. Producir un entero no cuesta casi nada, así que no hay cálculo que repartir: el objetivo de esta parte es la correctitud de la sincronización. Con productores y consumidores que hicieran trabajo real (leer un archivo, procesar cada dato), el buffer permitiría solapar ambas etapas.
- **El tamaño del buffer es lo que más influye.** Con 8 posiciones el buffer se llena y se vacía constantemente y las configuraciones tardan de 445 a 1 901 ms; con 64, de 55 a 760 ms, y con 1024, de 17.5 a 58.7 ms, entre 13 y 35 veces menos que con 8. Un buffer grande absorbe las ráfagas de productores y consumidores, y los threads se duermen muchas menos veces: con 1P–1C, de unas 25 000 veces por ejecución con buffer 8 a menos de 100 con buffer 1024.
- **2P–2C es la configuración más lenta con buffer 8 y 64.** No es ruido: se repite en las 7 mediciones (dispersión menor al 10 % con buffer 8) y en una segunda corrida independiente. Con 2P–2C los threads se duermen unas 172 000 veces por ejecución con buffer 8, casi el doble que con 4P–4C y 7 veces más que con 1P–1C; con buffer 8 y 64, el tiempo sigue de cerca a ese número. Una explicación compatible con los datos son los despertares inútiles: el thread despertado por `signal` encuentra que otro de su mismo tipo ya tomó el elemento (o el hueco) y vuelve a dormirse, justamente el caso que obliga a usar `while`.
- Con 8P–8C hay 16 threads para 12 CPU lógicas, y es la única configuración en la que el sistema desaloja threads involuntariamente (de 117 a 1 010 veces por ejecución).

## 4.4 Respuestas a las preguntas de análisis

**¿Por qué no basta con proteger únicamente el contador de elementos?**
Porque insertar y extraer modifican tres datos acoplados: la casilla del buffer, el índice (`in` u `out`) y `cuenta`. Si solo `cuenta` estuviera protegido, dos productores podrían leer el mismo `in` y escribir en la misma casilla, y se perdería un elemento; dos consumidores podrían leer el mismo `out` y llevarse el mismo elemento, que quedaría duplicado. Un consumidor podría incluso ver `cuenta` incrementado antes de que el productor terminara de escribir la casilla. Toda la operación (comprobar la condición, leer o escribir la casilla, avanzar el índice y actualizar `cuenta`) debe ser una única sección crítica.

**¿Qué puede ocurrir si un consumidor intenta extraer un elemento de un buffer vacío?**
Leería una casilla que no contiene un elemento nuevo: basura o un elemento ya consumido, que quedaría duplicado. Además `cuenta` quedaría negativo y `out` adelantaría a `in`, desordenando el buffer para todas las operaciones siguientes. Por eso el consumidor duerme en `no_vacio` mientras `cuenta == 0`.

**¿Qué puede ocurrir si un productor inserta en un buffer lleno?**
Sobrescribiría un elemento que todavía no se consumió, que se perdería; `cuenta` superaría `TAM_BUFFER` e `in` pasaría por encima de `out`, rompiendo el orden de llegada. Por eso el productor duerme en `no_lleno` mientras `cuenta == TAM_BUFFER`.

**¿Qué función cumplen el mutex y las variables de condición o semáforos elegidos?**
El mutex da exclusión mutua sobre `buffer`, `in`, `out` y `cuenta`. Las variables de condición permiten esperar sin consumir CPU: `pthread_cond_wait` suelta el mutex y duerme al thread en un solo paso atómico, de modo que no se pierde un aviso entre comprobar la condición y dormirse, y al despertar vuelve a tomar el mutex antes de continuar. `no_lleno` es la sala de espera de los productores y la avisa un consumidor al liberar un hueco; `no_vacio` es la de los consumidores y la avisa un productor al insertar. Con semáforos se lograría lo mismo con dos semáforos contadores (huecos libres y elementos disponibles) más un mutex.

**¿Cómo comprobarías que todos los elementos producidos fueron consumidos exactamente una vez?**
Dando a cada elemento un identificador único (0 … TOTAL − 1) y registrando cada consumo con `vistos[item]++`, como en la sección 4.2: al final todas las casillas deben valer 1. Los conteos y las sumas son una comprobación adicional, pero por sí solos no bastan: perder el 2 y el 4 y consumir dos veces el 3 deja iguales el conteo y la suma (2 + 4 = 3 + 3), mientras que `vistos` detecta cualquier pérdida o duplicado.
