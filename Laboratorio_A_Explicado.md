# Laboratorio A — Programación con Pthreads: Reducciones, Histograma y Sincronización

Explicación **para dummies** paso a paso del laboratorio, con analogías, ejemplos con números chiquitos y las respuestas fáciles a todas las preguntas del PDF.

> **Cómo leer este documento:**
> - Aquí está la **explicación para dummies** de todo el laboratorio: analogías cotidianas, ejemplos con números chiquitos, dibujos en texto de qué pasa en memoria y cómo funciona cada archivo `.c`.
> - El **informe formal** para entregar (tablas completas, gráficos, análisis y respuestas técnicas) está en [`Informe_Laboratorio_A.pdf`](Informe_Laboratorio_A.pdf); su fuente es la carpeta [`informe/`](informe/).
> - Los números de este documento salen de las mismas mediciones del informe: Intel Core i5-10400 con WSL2, mediana de 7 repeticiones.

---

## 0. Las 7 ideas que necesitas antes de empezar (para dummies)

| Concepto | En cristiano (para dummies) |
|---|---|
| **Thread (hilo)** | Un **trabajador** dentro de tu programa. Si creas 4 threads, tienes 4 trabajadores operando al mismo tiempo sobre la misma memoria. |
| **Variable compartida** | Una **pizarra en la pared** que todos los threads pueden mirar y modificar. |
| **Variable local / privada** | Una **libreta personal** de cada thread: solo él escribe ahí y nadie más la toca mientras trabaja. |
| **Condición de carrera** | Dos threads intentan actualizar la misma casilla de la pizarra **al mismo tiempo** y uno pisa el resultado del otro. El resultado sale mal y cambia en cada ejecución. |
| **Mutex (`pthread_mutex_t`)** | Un **candado** (o la única tiza del salón): solo el thread que tiene el candado puede tocar la pizarra; los demás hacen fila. |
| **Variable de condición (`pthread_cond_t`)** | Una **sala de espera con timbre**: si un thread ve que no puede avanzar (ej. el buffer está lleno o vacío), suelta el candado y se **duerme** hasta que otro thread toque el timbre (`signal`). |
| **Speedup y Eficiencia** | **Speedup** = `Ts / Tp` (cuántas veces más rápido fue el paralelo que el secuencial). **Eficiencia** = `Speedup / T` (qué tanto rindió cada thread: `1.0` = 100 % ideal). |

### Las 6 funciones de Pthreads que usamos en todo el laboratorio

```c
pthread_create(&hilo, NULL, funcion, &arg);  // Contrata un thread para que ejecute 'funcion(&arg)'
pthread_join(hilo, NULL);                    // Espera a que ese thread termine su trabajo
pthread_mutex_lock(&candado);                // Cierra el candado (si otro lo tiene, espera en la fila)
pthread_mutex_unlock(&candado);              // Abre el candado para que pase el siguiente
pthread_cond_wait(&condicion, &candado);     // Suelta el candado y se duerme hasta que le avisen; al despertar recupera el candado
pthread_cond_signal(&condicion);             // Despierta a un thread que esté dormido en 'condicion'
```

---

## Parte I (Para Dummies) — Estadísticas de un conjunto de datos (`p1sec.c` y `p1par.c`)

### ¿Qué piden en una frase?
Dado un arreglo gigante de `N` números enteros (entre `0` y `999`), calcular la **suma total**, el **mínimo**, el **máximo** y el **promedio**, repartiendo el arreglo entre `T` threads incluso cuando `N` no se pueda dividir exacto entre `T`.

### La idea general con colores
- 🔵 **Secuencial (`p1sec.c`):** Una sola persona recorre los `N` números de principio a fin y anota suma, mínimo, máximo y promedio.
- 🟢 **Paralelo (`p1par.c`):** Cortamos el arreglo en `T` pedazos seguidos. Cada thread recorre **su pedazo** usando **variables locales** y al terminar anota sus 3 resultados parciales (`suma`, `min`, `max`) en su propia estructura (`ArgsThread`, su "libreta").
- 🟣 **Combinación final:** Cuando todos los threads terminan (`pthread_join`), el `main` lee las `T` libretas, suma los subtotales, saca el menor de los mínimos, el mayor de los máximos y divide la suma global entre `N`. **Sin usar ningún mutex.**

### Forma 1 — Analogía: contar billetes en un banco
Imagina que llegan **1.000.003 billetes** al banco y hay **4 cajeros** (`T = 4`):
1. Partimos el fajo de billetes en 4 montones casi iguales (3 cajeros reciben `250.001` billetes y el último recibe `250.000`).
2. Cada cajero cuenta **en silencio en su propio escritorio** (variables locales en registros del CPU) cuánto suman sus billetes, cuál fue el billete más chico y cuál el más grande.
3. Cuando terminó, escribe esos 3 números en su hoja personal (`args[id].suma`, `args[id].min`, `args[id].max`).
4. Cuando los 4 terminaron (`pthread_join`), el gerente junta las 4 hojas y suma los 4 números. ¡Nadie se peleó por una pizarra!

### Forma 2 — ¿Cómo funciona la fórmula cuando `N` no es múltiplo de `T`?
En `p1par.c` (líneas 101–107) usamos esta división entera con resto:

```c
long base  = N / T;   // cuántos recibe cada thread como mínimo
long resto = N % T;   // cuántos elementos "sobran"

args[id].inicio = id * base + (id < resto ? id : resto);
args[id].fin    = args[id].inicio + base + (id < resto ? 1 : 0);
```

Hagámoslo con **números chiquitos**: imagina `N = 10` elementos (índices `0` al `9`) y `T = 4` threads:
- `base = 10 / 4 = 2` (todos reciben al menos 2 elementos).
- `resto = 10 % 4 = 2` (sobran 2 elementos, así que **los primeros 2 threads** —`id = 0` e `id = 1`— reciben **1 elemento extra**).

| Thread (`id`) | ¿`id < resto` (`id < 2`)? | `inicio` | `fin` | Segmento `[inicio, fin)` | Cantidad |
|---|---|---|---|---|---|
| **Thread 0** | Sí (`0 < 2`) | `0*2 + 0 = 0` | `0 + 2 + 1 = 3` | `[0, 3)` → índices `0, 1, 2` | **3 elementos** |
| **Thread 1** | Sí (`1 < 2`) | `1*2 + 1 = 3` | `3 + 2 + 1 = 6` | `[3, 6)` → índices `3, 4, 5` | **3 elementos** |
| **Thread 2** | No (`2 < 2` falso) | `2*2 + 2 = 6` | `6 + 2 + 0 = 8` | `[6, 8)` → índices `6, 7` | **2 elementos** |
| **Thread 3** | No (`3 < 2` falso) | `3*2 + 2 = 8` | `8 + 2 + 0 = 10` | `[8, 10)` → índices `8, 9` | **2 elementos** |

¡Fíjate que no queda ningún hueco ni ningún elemento repetido (`3 + 3 + 2 + 2 = 10`), y la diferencia máxima de carga entre cualquier par de threads es de **a lo sumo 1 elemento**!
En nuestras pruebas reales con `N = 1.000.003` y `T = 4` (guardado en `repartos.txt`):
- Threads `0, 1, 2`: reciben `250.001` elementos cada uno.
- Thread `3`: recibe `250.000` elementos.

### Forma 3 — El dibujo de la condición de carrera (si no usáramos variables locales)
¿Qué pasaría si todos los threads hicieran `suma_global += datos[i]` directamente sin sincronización?
Aunque en C se escribe en una línea, para el procesador `suma_global += x` son **3 pasos separados** (1: Leer de RAM a registro, 2: Sumar en el registro, 3: Escribir de vuelta en RAM):

```text
Instante   Thread 0 (quiere sumar 50)        Thread 1 (quiere sumar 30)        suma_global en RAM
   1       Lee suma_global (vale 100)                                          100
   2                                         Lee suma_global (vale 100)        100
   3       Calcula 100 + 50 = 150                                              100
   4                                         Calcula 100 + 30 = 130            100
   5       Escribe 150 en RAM                                                  150
   6                                         Escribe 130 en RAM                130  <-- ¡SE PERDIÓ EL +50!
```

### Preguntas de análisis de la Parte I (respondidas para dummies)

1. **¿Por qué conviene calcular resultados parciales en cada thread?**
   Porque así cada thread acumula `suma`, `min` y `max` en **variables locales privadas** (que el compilador guarda directamente en registros ultrarrápidos del procesador) sin tocar la memoria de los demás threads ni hacer fila en un mutex. Además, evita el *false sharing* (que dos núcleos se peleen por la misma línea de caché en cada iteración).
2. **¿Qué problema surgiría si todos los threads actualizaran una única variable de suma sin sincronización?**
   Ocurriría una **condición de carrera** (*race condition* / *lost update*): dos o más threads leerían el mismo valor viejo de `suma` antes de que el otro escriba su resultado, pisándose entre sí. La suma final saldría **menor que la real** y daría un número distinto cada vez que ejecutes el programa.
3. **¿Es necesario utilizar un mutex para combinar los resultados parciales? Justifique su estrategia.**
   **No es necesario en nuestra estrategia**, porque cada thread escribe su resultado parcial en su propia posición `args[id]` (ningún otro thread escribe en `args[id]`), y el hilo principal recién combina los `T` resultados **después** de que terminaron todos los `pthread_join`. Como `pthread_join` actúa como barrera de sincronización y después solo trabaja un hilo (el `main`), no hay concurrencia al combinar. *(Si en cambio cada thread sumara a una variable global dentro de su función antes de terminar, ahí sí haría falta un mutex).*
4. **¿Cómo se distribuye el trabajo cuando N no es múltiplo del número de threads?**
   Se calcula el cociente entero `base = N / T` y el residuo `resto = N % T`. Los primeros `resto` threads (`id < resto`) reciben `base + 1` elementos contiguos y los demás (`T - resto` threads) reciben `base` elementos contiguos. Así el trabajo queda perfectamente balanceado (máximo 1 elemento de diferencia).
5. **¿Por qué el speedup puede ser menor que el número de threads?**
   Por cuatro razones prácticas:
   - **Costo fijo (overhead) de Pthreads:** Crear (`pthread_create`) y esperar (`pthread_join`) threads toma entre `0.06 ms` (1 thread) y `0.36 ms` (8 threads) en el equipo de las pruebas. Si `N` es pequeño (`1.000` o `100.000`), se tarda más contratando a los trabajadores que sumando los números.
   - **Ancho de banda de memoria (Memory Wall):** Sumar enteros hace muy pocas cuentas por cada byte leído de la RAM. Con 4 u 8 threads leyendo a máxima velocidad, el bus de memoria RAM se llena y los núcleos tienen que esperar datos.
   - **Ley de Amdahl:** Siempre hay una parte secuencial (repartir, crear hilos, combinar los `T` resultados) que no se acelera.
   - **Frecuencia Turbo y planificación del SO:** Un solo núcleo activo suele correr a mayor frecuencia Turbo que 8 núcleos activos a la vez.

---

## Parte II (Para Dummies) — Construcción paralela de un histograma (`p2sec.c`, `p2mutex.c` y `p2priv.c`)

### ¿Qué piden en una frase?
Dado un arreglo de `N` números entre `0` y `99`, contar cuántos caen en cada una de las **10 decenas** (`0–9`, `10–19`, `20–29`, ..., `90–99`), comprobar que las 10 casillas sumen `N`, y comparar dos formas de hacerlo con threads: **con un mutex compartido** vs. **con un histograma privado por thread**.

### Truco matemático para saber en qué casilla cae un número
Como los números van de `0` a `99` y son enteros en C, dividir entre `10` quita los decimales:
- Si `datos[i] = 7` → `7 / 10 = 0` (cae en la casilla `0`, que es `00–09`).
- Si `datos[i] = 48` → `48 / 10 = 4` (cae en la casilla `4`, que es `40–49`).
- Si `datos[i] = 99` → `99 / 10 = 9` (cae en la casilla `9`, que es `90–99`).

### Las dos estrategias paralelas cara a cara

```text
🟠 ESTRATEGIA 1: Mutex compartido (p2mutex.c)
   Todos los threads escriben en el MISMO hist_global[10].
   Por cada número (N veces):
      1. Cerrar candado (pthread_mutex_lock)
      2. hist_global[cat]++
      3. Abrir candado (pthread_mutex_unlock)
   👉 Resultado: Correcto, pero LENTÍSIMO (hacen fila 10 millones de veces).

🔴 ESTRATEGIA 1b: Un mutex por categoría (p2mutexcat.c)
   Igual que la 1, pero cada casilla tiene SU PROPIO candado:
      lock(candado de la casilla cat) → cuenta++ → unlock(candado de la casilla cat)
   Dos threads solo hacen fila si cuentan números de la MISMA casilla.
   👉 Resultado: Correcto y algo menos lento que la 1, pero sigue haciendo un
      lock/unlock por número, así que sigue siendo mucho más lento que el secuencial.

🟢 ESTRATEGIA 2: Histograma privado por thread (p2priv.c)
   Cada thread tiene su propio arreglo local[10] = {0}.
   Durante todo su segmento (N/T números):
      local[cat]++   (¡en su libreta privada, SIN candado!)
   Al final (después de pthread_join), el main suma las 10 casillas de los T threads.
   👉 Resultado: Correcto y ULTRARRÁPIDO (0 filas durante el recorrido).
```

### Ejemplo con números reales medidos (`N = 10.000.000`, `T = 4` threads)

| Versión | Tiempo medido (mediana de 7) | Speedup vs. Secuencial | ¿10 categorías iguales y suman `10.000.000`? |
|---|---|---|---|
| 🔵 **Secuencial (`p2sec`)** | `8.60 ms` | `1.00x` | ✅ Sí (`10.000.000`) |
| 🟠 **Mutex compartido (`p2mutex`)** | `476 ms` | **`0.018x`** *(55 veces más lento)* | ✅ Sí (`10.000.000`) |
| 🔴 **Mutex por categoría (`p2mutexcat`)** | `340 ms` | **`0.025x`** *(40 veces más lento)* | ✅ Sí (`10.000.000`) |
| 🟢 **Histograma privado (`p2priv`)** | `2.83 ms` | **`3.04x`** *(3 veces más rápido)* | ✅ Sí (`10.000.000`) |

¡Mira esa diferencia! Con 4 threads y `N = 10.000.000`, el **histograma privado** tarda `2.83 ms`, mientras que el **mutex compartido** tarda `476 ms` (**168 veces más lento** que el privado).

### Preguntas de análisis de la Parte II (respondidas para dummies)

1. **¿En qué situación se produce una condición de carrera al actualizar el histograma?**
   Se produce cuando **dos o más threads leen al mismo tiempo números que pertenecen a la misma categoría `cat`** (por ejemplo, el Thread 0 lee un `23` y el Thread 1 lee un `28`, ambos van a la categoría `2`, que es `20–29`) e intentan ejecutar `hist[2]++` simultáneamente sobre un mismo arreglo compartido sin protección. Como `hist[2]++` es leer-sumar-escribir, uno pisa el incremento del otro y la suma de las 10 categorías termina dando **menos que `N`**.
2. **¿Qué diferencias hay entre usar un mutex compartido y un histograma privado por thread?**
   - **Mutex compartido (`p2mutex.c`):** Usa **1 solo histograma global** y protege cada incremento con `pthread_mutex_lock/unlock`. Ejecuta `N` bloqueos de candado, serializa a los threads (solo uno puede contar a la vez) y provoca altísima contención de caché.
   - **Histograma privado (`p2priv.c`):** Usa **un arreglo de 10 enteros por cada thread** (`local[10]`). Cada thread trabaja 100 % en paralelo en su propia caché L1 sin bloquearse nunca, y al final el hilo principal hace apenas `10 × T` sumas simples. Consume apenas `80 bytes` extra de memoria por thread (`10 × 8 bytes`), que no es nada.
3. **¿Qué estrategia esperarías que escale mejor y por qué?**
   Escala muchísimo mejor el **histograma privado por thread (`p2priv`)**, porque elimina por completo la contención y la serialización durante el bucle de `N` elementos: el trabajo por thread baja como $O(N/T)$ y la combinación final cuesta solo $O(10 \cdot T)$, que para 10 categorías y 8 threads son apenas 80 sumas. En cambio, el mutex compartido no escala: al subir de 1 a 2 threads el tiempo empeora drásticamente porque los núcleos empiezan a pelearse por el candado.
4. **¿Cómo influye la distribución de los valores de entrada en la contención?**
   - Si se usa **un único mutex global** para todo el histograma, la contención es máxima sin importar qué valores salgan, porque cualquier categoría bloquea el mismo candado.
   - Con **un mutex por categoría** (10 mutex, uno para cada casilla `0..9`, programa `p2mutexcat.c`), la distribución de entrada influye directamente:
     - Si los datos son **uniformes** (todos los números entre 0 y 99 salen con igual probabilidad), los threads se reparten entre las 10 casillas y chocan con probabilidad $1/10$.
     - Si los datos están **sesgados o concentrados** (por ejemplo, casi todos los valores caen entre `0` y `9`), todos los threads pedirán siempre el mutex de la casilla `0`, generando un cuello de botella idéntico a tener un solo mutex global.
   - En cambio, con el **histograma privado por thread**, la distribución de entrada **no genera contención jamás**, porque cada thread toca únicamente su propio arreglo privado.
   - **Lo medimos** (`N = 10.000.000`, sección 3.4 del informe): con datos sesgados (~91 % en la casilla 0), el mutex por categoría pasa de `337 ms` a `603 ms` con 2 threads y queda casi igual que el mutex global, que no cambia (`805` frente a `812 ms`). Curiosidad: los datos sesgados también hacen **más lento al secuencial** (`8.6` → `13.2 ms`), porque cada `hist[0]++` tiene que esperar a que termine el anterior.

---

## Parte III (Para Dummies) — Productores y consumidores con buffer acotado (`p3sec.c` y `p3par.c`)

### ¿Qué piden en una frase?
Implementar una cola circular de tamaño fijo (`TAM_BUFFER`) donde `P` threads **productores** meten números y `C` threads **consumidores** los sacan, durmiendo cuando el buffer está lleno o vacío, y demostrando que **ni un solo número se pierde ni se consume dos veces**.

### Forma 1 — Analogía: La panadería con vitrina redonda
Imagina una panadería donde:
- Hay `P` **panaderos (productores)** que hornean panes numerados con un sello único (`0, 1, 2, ..., TOTAL-1`).
- Hay `C` **clientes (consumidores)** que compran panes.
- En el medio hay una **vitrina redonda giratoria (`buffer`)** donde solo caben `TAM_BUFFER` panes (digamos 8 panes).
- **Regla 1 (El candado / `mutex`):** Solo una persona (panadero o cliente) puede meter la mano en la vitrina a la vez. Si no, dos panaderos pondrían su pan en la misma bandeja o dos clientes agarrarían el mismo pan.
- **Regla 2 (Vitrina llena / `no_lleno`):** Si un panadero abre la vitrina y ve que ya hay 8 panes (`cuenta == TAM_BUFFER`), **cierra la vitrina y se sienta a dormir** en el sillón `no_lleno`. Cuando un cliente se lleve un pan, tocará la campanita `pthread_cond_signal(&no_lleno)` para despertarlo.
- **Regla 3 (Vitrina vacía / `no_vacio`):** Si un cliente abre la vitrina y ve que hay 0 panes (`cuenta == 0`), **cierra la vitrina y se sienta a dormir** en el sillón `no_vacio`. Cuando un panadero ponga un pan nuevo, tocará la campanita `pthread_cond_signal(&no_vacio)` para despertarlo.

### Forma 2 — ¿Cómo da la vuelta el buffer circular? (`in`, `out` y `cuenta`)
Un arreglo normal en C empieza en `0` y termina en `TAM_BUFFER - 1`. Para que sea **circular** (que después de la última casilla vuelva a la casilla `0`), usamos el operador módulo `% TAM_BUFFER`:

```c
// Cuando un PRODUCTOR mete un elemento:
buffer[in] = item;
in = (in + 1) % TAM_BUFFER;   // si TAM_BUFFER=4: 0 -> 1 -> 2 -> 3 -> 0 -> 1...
cuenta++;

// Cuando un CONSUMIDOR saca un elemento:
int item = buffer[out];
out = (out + 1) % TAM_BUFFER; // avanza en el mismo orden FIFO (primero en entrar, primero en salir)
cuenta--;
```

Mira un ejemplo chiquito con un buffer de capacidad `TAM_BUFFER = 3`:

| Paso | Acción | `buffer[0]` | `buffer[1]` | `buffer[2]` | `in` (próximo a meter) | `out` (próximo a sacar) | `cuenta` | Estado |
|---|---|---|---|---|---|---|---|---|
| Inicial | — | `.` | `.` | `.` | `0` | `0` | `0` | **Vacío** (`cuenta == 0`) |
| 1 | Productor mete `10` | **`10`** | `.` | `.` | `1` | `0` | `1` | Normal |
| 2 | Productor mete `20` | `10` | **`20`** | `.` | `2` | `0` | `2` | Normal |
| 3 | Productor mete `30` | `10` | `20` | **`30`** | `(2+1)%3 = 0` | `0` | `3` | **Lleno** (`cuenta == 3`) |
| 4 | Consumidor saca (`10`) | `.` | `20` | `30` | `0` | `1` | `2` | Quedó libre la casilla `0` |
| 5 | Productor mete `40` | **`40`** | `20` | `30` | `1` | `1` | `3` | **Dio la vuelta** a la casilla `0` |

### Detalle clave: ¿Por qué usamos `while (cuenta == TAM_BUFFER)` y NO `if`?
En `p3par.c` escribimos:
```c
while (cuenta == TAM_BUFFER)
    pthread_cond_wait(&no_lleno, &candado);
```
Si usáramos `if` en lugar de `while`, habría un error clásico cuando hay varios productores o varios consumidores:
1. El Consumidor A ve el buffer vacío y se duerme.
2. Un Productor mete 1 elemento y despierta al Consumidor A (`signal`).
3. **Antes** de que el Consumidor A logre tomar el mutex, entra el Consumidor B (que recién llegaba), toma el mutex y **se lleva ese único elemento**.
4. Ahora el Consumidor A recupera el mutex: si tenía un `if`, sigue adelante creyendo que hay un elemento ¡y lee de un buffer vacío! En cambio, con `while`, vuelve a revisar `cuenta == 0`, ve que sigue vacío y se vuelve a dormir seguro.

### Preguntas de análisis de la Parte III (respondidas para dummies)

1. **¿Por qué no basta con proteger únicamente el contador de elementos (`cuenta`)?**
   Porque al insertar o extraer no solo se modifica `cuenta`, sino también el arreglo `buffer[]` y los índices `in` y `out`. Si solo protegiéramos `cuenta`:
   - Dos productores podrían leer el **mismo índice `in`** al mismo tiempo, escribir dos elementos distintos en la misma casilla `buffer[in]` (perdiendo el primero) y dejar otra casilla con basura.
   - Dos consumidores podrían leer el **mismo índice `out`** al mismo tiempo y llevarse **el mismo elemento duplicado**, dejando el siguiente sin leer.
   Por eso toda la secuencia (`leer/escribir buffer` + `avanzar in/out` + `actualizar cuenta`) debe ser **una única sección crítica** protegida por el mismo mutex.
2. **¿Qué puede ocurrir si un consumidor intenta extraer un elemento de un buffer vacío?**
   - Extraerá **basura** o un **elemento viejo ya consumido antes** (duplicación de datos).
   - El contador `cuenta` pasará a ser **negativo** (`-1`), corrompiendo la lógica del buffer.
   - El índice `out` se adelantará al índice `in`, desfasando toda la cola circular.
3. **¿Qué puede ocurrir si un productor inserta en un buffer lleno?**
   - **Sobrescribirá (pisará) un elemento válido** que todavía no había sido leído por ningún consumidor (**pérdida de datos**).
   - El contador `cuenta` superará `TAM_BUFFER`, y como `in` dio la vuelta completa y alcanzó a `out`, se rompe el orden FIFO del buffer circular.
4. **¿Qué función cumplen el mutex y las variables de condición o semáforos elegidos?**
   - **`candado` (`pthread_mutex_t`):** Garantiza **exclusión mutua**: solo un thread (productor o consumidor) puede tocar `buffer`, `in`, `out` y `cuenta` a la vez.
   - **`no_lleno` (`pthread_cond_t`):** Bloquea (duerme sin gastar CPU) a los productores cuando `cuenta == TAM_BUFFER` y permite que un consumidor los despierte (`pthread_cond_signal(&no_lleno)`) apenas libera un espacio.
   - **`no_vacio` (`pthread_cond_t`):** Bloquea (duerme sin gastar CPU) a los consumidores cuando `cuenta == 0` y permite que un productor los despierte (`pthread_cond_signal(&no_vacio)`) apenas inserta un elemento.
5. **¿Cómo comprobarías que todos los elementos producidos fueron consumidos exactamente una vez?**
   En `p3par.c` implementamos **triple verificación**:
   1. **Conteo global:** La suma de elementos producidos por todos los productores es `TOTAL`, la suma de consumidos por todos los consumidores es `TOTAL`, y al final `cuenta == 0` (el buffer queda vacío).
   2. **Suma aritmética (`SumaProd == SumaCons`):** Sumamos el valor numérico de todos los enteros generados (`0 + 1 + ... + (TOTAL-1)`) y comprobamos que sea idéntica a la suma de todos los enteros extraídos por los consumidores.
   3. **Arreglo de frecuencia exacta (`vistos[TOTAL]`):** Cada uno de los `TOTAL` elementos producidos es un entero único `item` en `[0, TOTAL-1]`. Cuando un consumidor extrae `item`, incrementa `vistos[item]++` dentro del mutex. Al terminar el programa, recorremos `vistos[0 .. TOTAL-1]` y verificamos que **todas las casillas valgan exactamente `1`**:
      - Si alguna casilla vale `0` → ese elemento **se perdió** (`Perdidos++`).
      - Si alguna casilla vale `> 1` → ese elemento **se consumió más de una vez** (`Duplicados++`).
      En nuestras 18 configuraciones de prueba, cada una ejecutada 8 veces (144 ejecuciones), `Perdidos = 0` y `Duplicados = 0`.

---

## Mapa de todos los archivos del proyecto

| Archivo | Parte | Qué hace |
|---|---|---|
| [`p1sec.c`](p1sec.c) | Parte I | Versión secuencial de estadísticas (`suma`, `min`, `max`, `promedio`) |
| [`p1par.c`](p1par.c) | Parte I | Versión paralela con Pthreads y reducción local sin mutex |
| [`experimentos_p1.sh`](experimentos_p1.sh) + [`analizar_p1.py`](analizar_p1.py) | Parte I | Ejecutan, comparan y generan [`resultados_p1.csv`](resultados_p1.csv), [`repartos.txt`](repartos.txt), `speedup.png` y `eficiencia.png` ([explicación](explicacion_experimentos_p1.md)) |
| [`p2sec.c`](p2sec.c) | Parte II | Histograma secuencial de 10 categorías (`0–9` a `90–99`) |
| [`p2mutex.c`](p2mutex.c) | Parte II | Estrategia 1: un mutex global |
| [`p2mutexcat.c`](p2mutexcat.c) | Parte II | Estrategia 1b: un mutex por categoría |
| [`p2priv.c`](p2priv.c) | Parte II | Estrategia 2: histograma privado por thread |
| [`experimentos_p2.sh`](experimentos_p2.sh) + [`analizar_p2.py`](analizar_p2.py) | Parte II | Verifican las 10 categorías con datos uniformes y sesgados y generan [`resultados_p2.csv`](resultados_p2.csv), [`resultados_p2_dist.csv`](resultados_p2_dist.csv) y los gráficos ([explicación](explicacion_experimentos_p2.md)) |
| [`p3sec.c`](p3sec.c) | Parte III | Referencia secuencial del buffer circular acotado |
| [`p3par.c`](p3par.c) | Parte III | Productores y consumidores con buffer circular, mutex y variables de condición |
| [`experimentos_p3.sh`](experimentos_p3.sh) + [`analizar_p3.py`](analizar_p3.py) | Parte III | Prueban distintas combinaciones `P:C` y tamaños de buffer y generan [`resultados_p3.csv`](resultados_p3.csv) y `tiempos_p3.png` ([explicación](explicacion_experimentos_p3.md)) |
| [`cambios_contexto_p3.py`](cambios_contexto_p3.py) | Parte III | Cuenta cuántas veces se duermen los threads ([`cambios_contexto_p3.csv`](cambios_contexto_p3.csv)) |
| [`Informe_Laboratorio_A.pdf`](Informe_Laboratorio_A.pdf) | Todas | Informe formal para entregar; su fuente está en [`informe/`](informe/) |
| [`version_anterior/`](version_anterior/) | Todas | Respaldo de la primera versión (ver su [`README.md`](version_anterior/README.md)) |

---

## El informe formal

La redacción formal (las secciones 1 a 7 que pide el PDF, con todas las tablas y gráficos) ya no está en este archivo: está en [`Informe_Laboratorio_A.pdf`](Informe_Laboratorio_A.pdf). Sus tablas se generan solas desde los CSV; para regenerarlo después de repetir los experimentos:

```bash
python informe/tablas.py
pandoc informe/0*.md --columns=250 --pdf-engine=typst -o Informe_Laboratorio_A.pdf
```

La versión anterior de esa redacción, con las mediciones de dos equipos distintos, quedó en [`version_anterior/Laboratorio_A_Explicado.md`](version_anterior/Laboratorio_A_Explicado.md).
