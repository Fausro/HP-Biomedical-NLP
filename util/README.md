## _traductor.py_

```
usage: traductor.py [-h] [-f filename] [-df dest_filename] [-ns] [-sf summary_file] [-np] [-nt] [-nplot]

Traducir bear.jsonl a bear.json

optional arguments:
  -h, --help         show this help message and exit
  -f filename        nombre del fichero origen, default bear.jsonl
  -df dest_filename  nombre para el fichero final, default bear.json
  -ns                crear fichero summary, default true
  -sf summary_file   nombre para el fichero summary, default summary.json
  -np                crear particiones, default true
  -nt                crear types, default true
  -nplot             crear plot del corpus, default true
```

## _register.py_

```
usage: register.py [-h] [-rf models_file] [-t] model

Realiza la evaluacion del rendimiento del modelo.

positional arguments:
  model            nombre del modelo

optional arguments:
  -h, --help       show this help message and exit
  -rf models_file  nombre para el registro de rendimiento, default models.json
  -t               crear las tablas de comparacion, default false
```

## _eval.py_

```
usage: eval.py [-h] [-ne] [-nr] model pred_file y_file

Crea las matrices de confusion de entidades y relaciones.

positional arguments:
  model       nombre del modelo
  pred_file   fichero con las predicciones
  y_file      fichero con las respuestas

optional arguments:
  -h, --help  show this help message and exit
  -ne         no crear la matriz de confusion de entidades
  -nr         no crear la matriz de confusion de relaciones
```
