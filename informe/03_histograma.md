# 3. Construcción del histograma (Parte II)

## 3.1 Estrategias implementadas

Cada valor $v \in [0, 99]$ va a la categoría $c = \lfloor v/10 \rfloor \in \{0, \dots, 9\}$ (en C, `datos[i] / 10` con división entera). Se compararon cuatro programas que procesan el mismo arreglo con el mismo reparto en bloques de la Parte I:

| Programa | Histograma | Sincronización durante el conteo |
|:--|:--|:--|
| `p2sec` | Uno, local (`hist[c]++`) | Ninguna: un solo thread |
| `p2mutex` | Uno, compartido (`hist_global[10]`) | Un mutex global: `lock` y `unlock` por cada elemento |
| `p2mutexcat` | Uno, compartido; cada casilla con su contador y su mutex, en su propia línea de caché de 64 bytes | Un mutex por categoría: solo compiten threads que cuentan la misma categoría |
| `p2priv` | Uno privado por thread (`local[10]`) | Ninguna; el hilo principal suma los T histogramas tras `pthread_join` (10 × T sumas) |

: Las cuatro versiones del histograma.

`p2mutexcat` se agregó para estudiar con mediciones la pregunta sobre la distribución de los datos. Para eso, todos los programas aceptan un argumento opcional: `u` genera datos uniformes (por defecto) y `s` datos sesgados, donde 9 de cada 10 valores se generan entre 0 y 9, de modo que cerca del 91 % de los datos cae en la categoría 0.

## 3.2 Comprobación de resultados

En las 24 combinaciones medidas (20 con datos uniformes y 4 con datos sesgados), las 10 categorías de las tres versiones paralelas coincidieron exactamente con las de la versión secuencial con los mismos datos, y su suma fue exactamente N.

<!-- tabla:p2_categorias -->

| Categoría | Intervalo | Uniforme | Sesgada |
|:-:|:-:|--:|--:|
| c0 | 00–09 | 1 000 011 | 9 100 248 |
| c1 | 10–19 | 1 000 434 | 99 533 |
| c2 | 20–29 | 1 000 793 | 99 737 |
| c3 | 30–39 | 999 584 | 99 665 |
| c4 | 40–49 | 1 000 287 | 100 155 |
| c5 | 50–59 | 1 000 361 | 100 146 |
| c6 | 60–69 | 999 878 | 100 018 |
| c7 | 70–79 | 1 000 923 | 100 165 |
| c8 | 80–89 | 998 621 | 100 415 |
| c9 | 90–99 | 999 108 | 99 918 |
| **Total** |  | **10 000 000** | **10 000 000** |

: Histograma secuencial de N = 10 000 000 valores con las dos distribuciones. Las tres versiones paralelas obtuvieron los mismos conteos con T = 1, 2, 4 y 8.

<!-- /tabla:p2_categorias -->

## 3.3 Rendimiento con datos uniformes

<!-- tabla:p2 -->

| N | T | Ts | Tp priv. | S priv. | E priv. | Tp global | S global | Tp categ. | S categ. |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 000 | 1 | 0.000801 | 0.0594 | 0.01 | 0.01 | 0.0823 | 0.010 | 0.0771 | 0.010 |
|  | 2 |  | 0.0863 | 0.01 | 0.01 | 0.0857 | 0.009 | 0.0944 | 0.008 |
|  | 4 |  | 0.138 | 0.01 | 0.00 | 0.135 | 0.006 | 0.138 | 0.006 |
|  | 8 |  | 0.278 | 0.00 | 0.00 | 0.279 | 0.003 | 0.282 | 0.003 |
| 100 000 | 1 | 0.0804 | 0.152 | 0.53 | 0.53 | 1.90 | 0.042 | 1.73 | 0.046 |
|  | 2 |  | 0.130 | 0.62 | 0.31 | 8.53 | 0.009 | 3.70 | 0.022 |
|  | 4 |  | 0.154 | 0.52 | 0.13 | 5.31 | 0.015 | 3.38 | 0.024 |
|  | 8 |  | 0.305 | 0.26 | 0.03 | 7.19 | 0.011 | 3.27 | 0.025 |
| 1 000 000 | 1 | 0.895 | 0.986 | 0.91 | 0.91 | 18.6 | 0.048 | 16.9 | 0.053 |
|  | 2 |  | 0.543 | 1.65 | 0.82 | 87.5 | 0.010 | 32.2 | 0.028 |
|  | 4 |  | 0.387 | 2.31 | 0.58 | 46.2 | 0.019 | 34.7 | 0.026 |
|  | 8 |  | 0.434 | 2.06 | 0.26 | 66.6 | 0.013 | 32.7 | 0.027 |
| 1 000 003 | 1 | 0.840 | 1.03 | 0.81 | 0.81 | 18.5 | 0.046 | 16.8 | 0.050 |
|  | 2 |  | 0.582 | 1.44 | 0.72 | 87.3 | 0.010 | 31.4 | 0.027 |
|  | 4 |  | 0.374 | 2.25 | 0.56 | 47.4 | 0.018 | 33.8 | 0.025 |
|  | 8 |  | 0.392 | 2.14 | 0.27 | 62.0 | 0.014 | 29.9 | 0.028 |
| 10 000 000 | 1 | 8.60 | 9.54 | 0.90 | 0.90 | 182 | 0.047 | 166 | 0.052 |
|  | 2 |  | 5.19 | 1.66 | 0.83 | 805 | 0.011 | 337 | 0.026 |
|  | 4 |  | 2.83 | 3.04 | 0.76 | 476 | 0.018 | 340 | 0.025 |
|  | 8 |  | 2.58 | 3.33 | 0.42 | 666 | 0.013 | 325 | 0.026 |

: Histograma con datos uniformes. Tiempos en ms (mediana de 7); S = speedup, E = eficiencia; priv. = histograma privado, global = un mutex global, categ. = un mutex por categoría. En todas las filas las 10 categorías coinciden con el secuencial y suman N.

<!-- /tabla:p2 -->

- **El histograma privado escala como la Parte I.** Con N = 10^7^ llega a $S_4 = 3.04$ y $S_8 = 3.33$. Con N pequeños, igual que en la Parte I, domina el costo de crear los threads.
- **El mutex global es siempre más lento que el secuencial.** Con un solo thread ya tarda 181.8 ms frente a los 8.6 ms del secuencial (21 veces más): bloquear y desbloquear un mutex libre cuesta unos 17 ns por elemento, unas 20 veces lo que cuesta contarlo. Con 2 threads el tiempo sube a 805 ms (94 veces el secuencial): los threads se turnan el candado en cada elemento y la línea de caché del mutex y del histograma viaja de un núcleo a otro millones de veces. Con 4 y 8 threads (476 y 666 ms) no mejora, porque el conteo queda completamente serializado: el speedup no pasa de 0.05 en ninguna configuración.
- **El mutex por categoría alivia, pero no resuelve.** Con datos uniformes, repartir los candados baja el tiempo de 805 a 337 ms con T = 2 (2.4 veces menos que el mutex global) y de 666 a 325 ms con T = 8, pero sigue siendo entre 38 y 40 veces más lento que el secuencial: el `lock` y `unlock` por elemento y el viaje de las líneas de caché entre núcleos se mantienen.
- Con N = 10^7^ y T = 8, el histograma privado (2.58 ms) es **258 veces más rápido** que el mutex global y 126 veces más rápido que el mutex por categoría.

![Speedup de las tres estrategias con datos uniformes. Cada panel tiene su propia escala vertical: las dos versiones con mutex no llegan a 0.06.](figuras/speedup_p2.svg){width=100%}

![Eficiencia de las tres estrategias con datos uniformes.](figuras/eficiencia_p2.svg){width=100%}

## 3.4 Influencia de la distribución de los datos

<!-- tabla:p2_dist -->

| Datos | T | Ts | Tp priv. | Tp global | Tp categ. | categ. / global |
|:--|--:|--:|--:|--:|--:|--:|
| Uniforme | 1 | 8.60 | 9.54 | 182 | 166 | 0.91 |
|  | 2 |  | 5.19 | 805 | 337 | 0.42 |
|  | 4 |  | 2.83 | 476 | 340 | 0.71 |
|  | 8 |  | 2.58 | 666 | 325 | 0.49 |
| Sesgada | 1 | 13.2 | 13.4 | 184 | 166 | 0.90 |
|  | 2 |  | 6.85 | 812 | 603 | 0.74 |
|  | 4 |  | 3.56 | 473 | 522 | 1.10 |
|  | 8 |  | 2.74 | 664 | 637 | 0.96 |

: Influencia de la distribución de los datos (N = 10 000 000, tiempos en ms, mediana de 7). La última columna compara el mutex por categoría con el global: menos de 1 significa que repartir los candados ayudó.

<!-- /tabla:p2_dist -->

![Tiempos con datos uniformes y sesgados (N = 10^7^, escala logarítmica). Las líneas punteadas son el secuencial con los mismos datos.](figuras/distribucion_p2.svg){width=100%}

- **Con un mutex global, la distribución no importa.** Los tiempos con datos uniformes y sesgados difieren menos de un 2 %: todos los threads compiten por el mismo candado, caigan sus valores donde caigan.
- **Con un mutex por categoría, la distribución decide.** Con datos sesgados, cerca del 91 % de los incrementos piden el candado de la categoría 0 y el mutex por categoría se comporta como un mutex global: con T = 2, 4 y 8 tarda 603, 522 y 637 ms, entre 1.5 y 2 veces más que con datos uniformes, y su tiempo queda entre 0.74 y 1.10 veces el del mutex global, frente a 0.42 a 0.71 veces con datos uniformes.
- **Con histograma privado no hay contención, pero los datos sesgados encarecen cada incremento.** El secuencial y el privado con un thread son entre 1.4 y 1.5 veces más lentos con datos sesgados (el secuencial, 13.2 frente a 8.6 ms): cuando casi todos los valores caen en la misma casilla, cada `hist[0]++` debe esperar a que termine el anterior (lectura, suma y escritura sobre la misma dirección de memoria), y esa cadena de dependencias impide que el procesador solape incrementos consecutivos. Ese costo sí se reparte entre los threads, porque cada uno tiene su propio contador: con 8 threads el privado baja a 2.74 ms, un speedup de 4.84 respecto del secuencial con los mismos datos.

## 3.5 Respuestas a las preguntas de análisis

**¿En qué situación se produce una condición de carrera al actualizar el histograma?**
Cuando dos o más threads incrementan a la vez la misma casilla de un histograma compartido sin exclusión mutua. `hist[c]++` es leer, sumar y escribir: si dos threads leen el mismo valor de `hist[c]` antes de que alguno escriba, ambos escriben el valor más uno y se pierde un conteo, de modo que la suma de las categorías queda por debajo de N. Con datos uniformes ocurre cuando dos threads procesan al mismo tiempo valores del mismo intervalo; con datos sesgados, casi siempre.

**¿Qué diferencias hay entre usar un mutex compartido y un histograma privado por thread?**
Ambos dan el resultado correcto, pero el mutex compartido sincroniza en cada uno de los N elementos: cada `lock` y `unlock` cuesta tiempo aunque nadie compita, solo un thread puede contar a la vez y el mutex y el histograma viajan constantemente entre las cachés de los núcleos. El histograma privado no sincroniza durante el conteo: cada thread cuenta en su propio arreglo de 10 contadores (80 bytes, un costo de memoria despreciable) dentro de su caché, y la combinación final son solo 10 × T sumas después de `pthread_join`. Medido con N = 10^7^ y T = 8: 666 ms frente a 2.58 ms.

**¿Qué estrategia esperarías que escale mejor y por qué?**
El histograma privado: su costo es O(N/T) sin esperas más O(10 T) para combinar. Con un mutex compartido cada elemento es una sección crítica, así que el conteo se ejecuta de uno en uno y agregar threads solo agrega contención. Los datos lo confirman: el privado llega a $S_8 = 3.33$, mientras que el mutex global no pasa de 0.05 y empeora al pasar de 1 a 2 threads.

**¿Cómo influye la distribución de los valores de entrada en la contención?**
Depende de la estrategia (sección 3.4). Con un mutex global, nada: la contención es máxima siempre. Con un mutex por categoría, mucho: con datos uniformes los threads se reparten entre 10 candados y chocan poco, y con datos sesgados casi todos piden el mismo candado y el tiempo se acerca al del mutex global. Con histogramas privados la distribución no genera contención, aunque los datos sesgados vuelven más lento cada incremento, también en el secuencial, por la dependencia entre incrementos a la misma casilla.
