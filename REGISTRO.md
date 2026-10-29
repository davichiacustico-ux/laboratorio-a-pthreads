## 2026-10-29

- [x] Respaldo de la versión anterior en `version_anterior/` (35 archivos + README); retirados de la raíz `run_p1.sh`, `run_p2.sh`, `run_p3.sh`, `explicacion_run_p1.md` y `entorno.txt` (copias en el respaldo).
- [x] Código C (7 programas): `CLOCK_MONOTONIC`, 1 ejecución de calentamiento + 7 medidas con mediana, mínima y máxima (`%.9f`), `crear_thread()` que verifica `pthread_create`, validación de TOTAL <= INT_MAX (Parte III), argumento `u|s` de distribución (Parte II), `p1sec.c` sin `pthread.h`.
- [x] Nuevo `p2mutexcat.c`: un mutex por categoría, cada casilla alineada a 64 bytes.
- [x] `experimentos_p1.sh`..`experimentos_p3.sh`: columnas `t_min`/`t_max`, `entorno_pN.txt` por parte, `p2mutexcat` y datos sesgados (P2), `EnBuffer`/`RepFallidas` y conteo de cambios de contexto (P3).
- [x] `analizar_p1.py`..`analizar_p3.py`: tablas en ms, color y marcador fijos por N, PNG + `figuras/*.svg`, Parte II en cuadrícula 2x2 + `distribucion_p2`, Parte III como gráfico de puntos en escala logarítmica.
- [x] Nuevos `cambios_contexto_p3.py` y `cambios_contexto_p3.csv`.
- [x] Verificación: gcc `-Wall -Wextra` sin avisos; ThreadSanitizer sin avisos en p1par, p2mutex, p2mutexcat, p2priv y p3par; casos límite correctos.
- [x] Experimentos repetidos en un solo equipo (i5-10400, WSL2 Ubuntu-CUDA, 146 s): datos, resultados, repartos, entornos y figuras; todo OK.
- [x] Informe nuevo: `informe/00..08_*.md` + `informe/tablas.py` -> `Informe_Laboratorio_A.pdf` (17 páginas, pandoc + Typst).
- [x] Reparado: un heredoc dañó 16 números del informe (referencias de grupo convertidas en caracteres de control); restaurados con un script verificado.
- [x] Metadatos verificados: PDF sin /Author ni /Producer, /Creator "Typst 0.15.1", XMP sin dc:creator; PNG/SVG solo con "Matplotlib"; sin correo.
- [x] `Laboratorio_A_Explicado.md`: números nuevos, mutex por categoría, enlaces relativos; la mitad formal pasó al PDF (la anterior queda en `version_anterior/`).
- [x] `explicacion_experimentos_p1..p3.md` actualizados (repeticiones, líneas citadas, archivos nuevos).
- [x] Completado en `informe/00_portada.md` el encabezado UNSA con "Nombre: David Tamo Turpo", "Curso: Computación Paralela y Distribuida", "Profesor: Alvaro Henry Mamani Aliaga" y el enlace al repositorio público; quitada la introducción y ampliada la explicación de los scripts `.sh` en `informe/01_introduccion.md` y `README.md`; regenerado `Informe_Laboratorio_A.pdf`.
