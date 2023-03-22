### nlp2query

Transforma una pregunta en lenguaje natural a una consulta SQL en la base de datos.

# Instalación

Se debe tener instalado Python.
Opcionalmente se recomienda un editor de código como Visual Studio Code.

Se abre una consola de comandos o terminal en la carpeta del proyecto y se ejecuta los siguientes comandos:

* pip install -r requirements.txt
* python3 main.py (en caso de no funcionar se puede ejecutar: python main.py)

Esto abrirá una ventana que permitirá ingresar una pregunta en lenguaje natural que consultará en la siguiente base de datos en SQLLite:

```sql
TB_NETFLIX_DATA (
    show_id,
    type,
    title,
    director,
    cast,
    country,
    date_added,
    release_year,
    rating,
    duration,
    listed_in,
    description
)
```

Un ejemplo de uso es preguntar: Dime todos los filmes que hayan sido grabadas en Colombia
Esto PUEDE generar la siguiente consulta:
```sql
SELECT * FROM TB_NETFLIX_DATA WHERE country LIKE '%Colombia%'
```