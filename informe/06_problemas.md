# 6. Problemas encontrados y soluciones

| Problema | Causa | Solución |
|:--|:--|:--|
| Desbordamiento de la suma | Con N = 10^8^ y valores hasta 999, la suma llega a unos 5 × 10^10^, más que el máximo de un `int` (2 147 483 647) | `long long` en los acumuladores locales y en el global |
| N no divisible entre T | Si cada thread recibe `N / T` elementos, los `N % T` últimos quedan sin procesar | Reparto por bloques con un elemento extra para los primeros `N % T` threads |
| Histograma con mutex global muy lento | Un `lock` y `unlock` por elemento serializa a los threads y hace viajar la línea de caché del mutex entre núcleos | Histograma privado por thread; se agregó un mutex por categoría para medir el efecto de la distribución |
| Elemento robado entre el `signal` y el despertar; despertares espurios | Con `if`, el thread despertado no vuelve a comprobar la condición | Esperar siempre dentro de `while (cuenta == 0)` y `while (cuenta == TAM_BUFFER)` |
| Comas decimales en los CSV | En Linux configurado en español, `awk` imprime `0,054` y rompe las columnas | `export LC_ALL=C` en los scripts |
| Mediciones ruidosas | Una sola medición por caso: el histograma privado con un thread parecía más rápido que el secuencial | Una ejecución de calentamiento y 7 medidas; se reporta la mediana, la mínima y la máxima |
| Reloj y resolución | `CLOCK_REALTIME` puede saltar si se ajusta la hora; guardado en un `double` (unos 1.8 × 10^9^ s) solo distingue unos 0.24 µs, y los tiempos se imprimían con 6 decimales | `CLOCK_MONOTONIC`, que cuenta desde el arranque y conserva resolución de nanosegundos, e impresión con `%.9f` |
| Datos de dos equipos mezclados | La primera versión tenía la Parte I medida en el Core Ultra 9 285 del laboratorio y las Partes II y III en otro equipo, con un único `entorno.txt` | Se volvió a medir todo en un mismo equipo y cada parte guarda su `entorno_pN.txt`; la versión anterior se conserva en `version_anterior/` |
| Dos juegos de scripts | `run_p*.sh` y `experimentos_p*.sh` escribían el mismo `resultados_p*.csv` con columnas distintas | Un solo flujo: `experimentos_p*.sh` más `analizar_p*.py` |
| Fallos silenciosos | No se revisaba el resultado de `pthread_create`, y con TOTAL mayor que `INT_MAX` los identificadores `int` de la Parte III se desbordaban | `crear_thread()` termina el programa si no se puede crear un thread, y se valida TOTAL |

: Problemas encontrados durante el laboratorio y cómo se resolvieron.
