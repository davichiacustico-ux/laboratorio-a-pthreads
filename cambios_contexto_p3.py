"""
Parte III - medicion extra: cambios de contexto de p3par

Corre p3par con cada tamano de buffer y configuracion P:C y cuenta cuantas veces
sus threads se durmieron (cambios de contexto voluntarios: esperar en una variable
de condicion o en el mutex) o fueron desalojados por el sistema (involuntarios).
getrusage(RUSAGE_CHILDREN) suma los de todos los threads del proceso hijo.
Solo funciona en Linux / WSL (modulo resource).

Uso: python3 cambios_contexto_p3.py > cambios_contexto_p3.csv
"""
import resource
import subprocess

TOTAL = "100003"
EJECUCIONES = 8  # p3par trabaja 8 veces por dentro: 1 de calentamiento + 7 medidas

print("buffer,P,C,voluntarios_por_ejec,involuntarios_por_ejec,tiempo")
for B in (8, 64, 1024):
    for P, C in ((1, 1), (2, 2), (4, 4), (8, 8), (2, 4), (4, 2)):
        antes = resource.getrusage(resource.RUSAGE_CHILDREN)
        salida = subprocess.run(["./p3par", TOTAL, str(P), str(C), str(B)],
                                capture_output=True, text=True).stdout
        despues = resource.getrusage(resource.RUSAGE_CHILDREN)
        vol = (despues.ru_nvcsw - antes.ru_nvcsw) / EJECUCIONES
        invol = (despues.ru_nivcsw - antes.ru_nivcsw) / EJECUCIONES
        mediana = [l for l in salida.splitlines() if l.startswith("Tiempo paralelo")][0]
        print(f"{B},{P},{C},{vol:.0f},{invol:.0f},{mediana.split('= ')[1].split()[0]}")
