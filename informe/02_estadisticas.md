# 2. Estadísticas del conjunto de datos (Parte I)

## 2.1 Estrategia de paralelización

El arreglo `datos[0..N-1]`, con valores entre 0 y 999, se divide en T bloques contiguos. Con $b = \lfloor N/T \rfloor$ y $r = N \bmod T$, el thread `id` recibe el intervalo [inicio, fin) con

$$\text{inicio} = \text{id} \cdot b + \min(\text{id}, r), \qquad \text{fin} = \text{inicio} + b + [\,\text{id} < r\,]$$

Es decir, los primeros $r$ threads procesan $b + 1$ elementos y los demás $b$: la carga difiere a lo sumo en un elemento y ningún índice queda sin procesar ni se procesa dos veces.

<!-- tabla:reparto -->

| Thread | Inicio | Fin (excluido) | Elementos |
|--:|--:|--:|--:|
| 0 | 0 | 125 001 | 125 001 |
| 1 | 125 001 | 250 002 | 125 001 |
| 2 | 250 002 | 375 003 | 125 001 |
| 3 | 375 003 | 500 003 | 125 000 |
| 4 | 500 003 | 625 003 | 125 000 |
| 5 | 625 003 | 750 003 | 125 000 |
| 6 | 750 003 | 875 003 | 125 000 |
| 7 | 875 003 | 1 000 003 | 125 000 |

: Reparto de N = 1 000 003 elementos entre T = 8 threads (de `repartos.txt`): 1 000 003 = 8 × 125 000 + 3, así que los threads 0, 1 y 2 reciben un elemento más.

<!-- /tabla:reparto -->

Cada thread recorre su bloque acumulando en **variables locales** la suma, el mínimo y el máximo. La suma es `long long` porque con N = 10^8^ llega a unos 5 × 10^10^ y no cabe en un `int`. Al terminar, cada thread escribe una sola vez sus tres resultados en su propia estructura `args[id]`. El hilo principal espera a todos con `pthread_join` y combina los T resultados parciales: suma de las sumas, mínimo de los mínimos y máximo de los máximos; el promedio es la suma global dividida entre N. No se usa ningún mutex.

## 2.2 Comprobación de resultados

<!-- tabla:p1_estadisticas -->

| N | Suma | Mínimo | Máximo | Promedio | T probados | ¿Igual al secuencial? |
|--:|--:|--:|--:|--:|:-:|:-:|
| 1 000 | 489 014 | 0 | 999 | 489.0140 | 1, 2, 4, 8 | OK |
| 100 000 | 50 026 152 | 0 | 999 | 500.2615 | 1, 2, 4, 8 | OK |
| 1 000 000 | 499 639 820 | 0 | 999 | 499.6398 | 1, 2, 4, 8 | OK |
| 1 000 003 | 499 641 123 | 0 | 999 | 499.6396 | 1, 2, 4, 8 | OK |
| 10 000 000 | 4 995 813 121 | 0 | 999 | 499.5813 | 1, 2, 4, 8 | OK |
| 100 000 000 | 49 954 148 838 | 0 | 999 | 499.5415 | 1, 2, 4, 8 | OK |

: Resultados de la Parte I. Para cada N, las cuatro ejecuciones paralelas dieron exactamente la misma suma, mínimo, máximo y promedio que la versión secuencial.

<!-- /tabla:p1_estadisticas -->

## 2.3 Tiempos, speedup y eficiencia

<!-- tabla:p1 -->

| N | T | Ts (ms) | Tp (ms) | Tp mín – máx (ms) | Speedup | Eficiencia |
|--:|--:|--:|--:|--:|--:|--:|
| 1 000 | 1 | 0.000606 | 0.0607 | 0.0516 – 0.0703 | 0.01 | 0.01 |
|  | 2 |  | 0.0920 | 0.0818 – 0.143 | 0.01 | 0.00 |
|  | 4 |  | 0.128 | 0.127 – 0.148 | 0.01 | 0.00 |
|  | 8 |  | 0.363 | 0.321 – 0.428 | 0.00 | 0.00 |
| 100 000 | 1 | 0.0567 | 0.123 | 0.111 – 0.133 | 0.46 | 0.46 |
|  | 2 |  | 0.146 | 0.0936 – 0.165 | 0.39 | 0.19 |
|  | 4 |  | 0.146 | 0.140 – 0.198 | 0.39 | 0.10 |
|  | 8 |  | 0.301 | 0.290 – 0.317 | 0.19 | 0.02 |
| 1 000 000 | 1 | 0.649 | 0.784 | 0.757 – 1.16 | 0.83 | 0.83 |
|  | 2 |  | 0.701 | 0.617 – 0.859 | 0.93 | 0.46 |
|  | 4 |  | 0.400 | 0.377 – 0.459 | 1.62 | 0.41 |
|  | 8 |  | 0.425 | 0.368 – 0.533 | 1.53 | 0.19 |
| 1 000 003 | 1 | 0.723 | 0.705 | 0.660 – 0.767 | 1.03 | 1.03 |
|  | 2 |  | 0.454 | 0.388 – 0.638 | 1.59 | 0.80 |
|  | 4 |  | 0.393 | 0.323 – 0.422 | 1.84 | 0.46 |
|  | 8 |  | 0.454 | 0.406 – 0.540 | 1.59 | 0.20 |
| 10 000 000 | 1 | 6.70 | 7.01 | 6.82 – 7.59 | 0.95 | 0.95 |
|  | 2 |  | 3.90 | 3.73 – 6.13 | 1.72 | 0.86 |
|  | 4 |  | 2.22 | 2.11 – 2.27 | 3.02 | 0.76 |
|  | 8 |  | 2.07 | 1.99 – 2.21 | 3.23 | 0.40 |
| 100 000 000 | 1 | 67.6 | 68.2 | 66.8 – 68.7 | 0.99 | 0.99 |
|  | 2 |  | 34.5 | 34.3 – 38.7 | 1.96 | 0.98 |
|  | 4 |  | 24.1 | 19.8 – 28.6 | 2.81 | 0.70 |
|  | 8 |  | 18.9 | 18.0 – 19.5 | 3.58 | 0.45 |

: Tiempos de la Parte I: mediana de 7 mediciones (Tp incluye crear, esperar y combinar los threads) y rango de las 7 mediciones paralelas.

<!-- /tabla:p1 -->

![Speedup de la Parte I. La línea gris punteada es el speedup ideal (igual a T).](figuras/speedup.svg){width=80%}

![Eficiencia de la Parte I. La línea gris punteada es la eficiencia ideal (1).](figuras/eficiencia.svg){width=80%}

- **Con N pequeños (10^3^ y 10^5^) el paralelo pierde.** Recorrer 1 000 elementos toma 0.6 µs, mientras que crear y esperar un solo thread cuesta unos 60 µs en este equipo, y 8 threads unos 360 µs (diferencia $T_p - T_s$ con N = 1 000). Con N = 10^5^ el cálculo secuencial dura 57 µs, todavía menos que ese costo fijo, y el speedup no pasa de 0.46.
- **Con N = 10^6^ la ganancia es moderada.** Con unos 0.7 ms de trabajo, el costo fijo ya es una fracción menor y se llega a un speedup de 1.6 a 1.8 con 4 threads, pero pasar a 8 no ayuda: cada thread tiene tan poco trabajo que el costo de crearlo vuelve a pesar.
- **Con N grandes (10^7^ y 10^8^) el paralelo gana, pero lejos del ideal.** Con N = 10^8^, dos threads logran $S_2 = 1.96$ (eficiencia 0.98, casi perfecta), cuatro $S_4 = 2.81$ y ocho $S_8 = 3.58$. Hay dos frenos. Primero, el cálculo está **limitado por la memoria**: por cada entero de 4 bytes leído solo se hace una suma y dos comparaciones. Un thread lee los 400 MB del arreglo en 67.6 ms (unos 5.9 GB/s); con 8 threads la lectura sube a unos 21 GB/s y la memoria pasa a ser el recurso compartido que limita a todos los núcleos. Segundo, con T = 8 hay más threads que núcleos físicos.
- **N = 1 000 003**, que no es múltiplo de 2, 4 ni 8, se comporta igual que N = 10^6^: el elemento extra de algunos threads no desbalancea la carga.
- **Con T = 1** y N ≥ 10^6^, el speedup queda entre 0.83 y 1.03: la versión paralela hace el mismo trabajo más la creación de un thread, y por debajo de 1 ms la medición varía hasta un 68 %.

## 2.4 Respuestas a las preguntas de análisis

**¿Por qué conviene calcular resultados parciales en cada thread?**
Porque así cada thread trabaja sin compartir nada durante el recorrido: sus acumuladores locales viven en registros del procesador, no hay que sincronizar en cada elemento y ningún núcleo invalida la caché de otro. La única comunicación es una escritura por thread al final y una combinación de T valores en el hilo principal, un costo O(T) despreciable frente al O(N/T) del recorrido.

**¿Qué problema surgiría si todos los threads actualizaran una única variable de suma sin sincronización?**
Una condición de carrera. `suma += datos[i]` no es atómica: el procesador lee `suma`, le suma el valor y la escribe. Si dos threads leen el mismo valor antes de que el otro escriba, una de las dos actualizaciones se pierde (*lost update*): la suma final saldría menor que la real y distinta en cada ejecución. Y protegerla con un mutex daría un resultado correcto pero lento: es lo que mide el histograma con mutex global de la Parte II, 21 veces más lento que el secuencial incluso con un solo thread (sección 3.3).

**¿Es necesario utilizar un mutex para combinar los resultados parciales? Justifique su estrategia.**
No, con esta estrategia. Cada thread escribe solo en su propia estructura `args[id]`, y el hilo principal lee esas estructuras después de `pthread_join`. `pthread_join` es un punto de sincronización: garantiza que el thread terminó y que todo lo que escribió es visible para quien lo esperó. Durante la combinación hay un solo thread trabajando, así que no hay nada que proteger. Haría falta un mutex si cada thread sumara su resultado a una variable global compartida antes de terminar.

**¿Cómo se distribuye el trabajo cuando N no es múltiplo del número de threads?**
Con el reparto por bloques de la sección 2.1: los primeros $N \bmod T$ threads reciben $\lfloor N/T \rfloor + 1$ elementos y el resto $\lfloor N/T \rfloor$. Para N = 1 000 003 y T = 8, tres threads procesan 125 001 elementos y cinco procesan 125 000. Los resultados coincidieron con el secuencial en todos los casos.

**¿Por qué el speedup puede ser menor que el número de threads?**
Por varias razones que se suman. (1) El costo fijo de crear y esperar threads, de 60 µs con 1 thread a 360 µs con 8 en este equipo, que domina con N pequeños. (2) El ancho de banda de memoria: el cálculo es tan simple que, con varios threads, la memoria no alcanza a entregar los datos al ritmo al que los núcleos los procesan. (3) Los recursos compartidos: con T = 8 hay más threads que núcleos físicos, y con todos los núcleos ocupados el procesador no puede mantener la frecuencia turbo de un solo núcleo. (4) La parte secuencial (repartir el arreglo, combinar los resultados) no se acelera (ley de Amdahl).
