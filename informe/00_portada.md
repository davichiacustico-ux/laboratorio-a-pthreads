---
lang: es
papersize: a4
fontsize: 10.5pt
margin:
  x: 2.2cm
  y: 2.4cm
page-numbering: "1"
table-caption-position: top
header-includes: |
  ```{=typst}
  #show table: set text(size: 8.5pt)
  #show raw.where(block: true): set text(size: 8.5pt)
  ```
---

```{=typst}
#align(center)[
  #v(0.3cm)
  #text(size: 16pt)[#smallcaps[Universidad Nacional de San Agustín]] \
  #v(0.2cm)
  #text(size: 12pt)[#smallcaps[Escuela Profesional de Ciencia de la Computación]]

  #v(0.9cm)
  #line(length: 100%, stroke: 1.2pt)
  #v(0.35cm)
  #text(size: 17pt, weight: "bold")[Laboratorio A: Programación con Pthreads] \
  #v(0.2cm)
  #text(size: 12pt)[Reducciones, histograma y sincronización]
  #v(0.35cm)
  #line(length: 100%, stroke: 1.2pt)
]

#v(0.6cm)
#grid(
  columns: (1fr, 1fr),
  align(left)[
    *Nombre:* \
    David Tamo Turpo \
    #v(0.2cm)
    *Repositorio GitHub:* \
    #link("https://github.com/davichiacustico-ux/laboratorio-a-pthreads")[github.com/davichiacustico-ux/laboratorio-a-pthreads]
  ],
  align(right)[
    *Curso:* \
    Computación Paralela y Distribuida \
    #v(0.2cm)
    *Profesor:* \
    Alvaro Henry Mamani Aliaga
  ]
)
#v(0.5cm)
```
