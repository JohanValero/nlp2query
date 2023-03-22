# nlp2query

Transforma una pregunta en lenguaje natural a una consulta SQL en la base de datos.

### Instalación

Se debe tener instalado Python.
Opcionalmente se recomienda un editor de código como Visual Studio Code.

Se abre una consola de comandos o terminal en la carpeta del proyecto y se ejecuta los siguientes comandos:

```
pip install -r requirements.txt
```

```
python main.py
```

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

Esta consulta se ejecutará por debajo y se mostrará en la consola de comandos.
```
   index show_id     type  ...   duration                                          listed_in                                        description
0    278    s279    Movie  ...     64 min                                    Stand-Up Comedy  Through songs and puns, comedian Lokillo Flore...
1    288    s289  TV Show  ...   1 Season  Crime TV Shows, International TV Shows, Spanis...  Based on the book "Las Fantásticas," this exci...
2    744    s745  TV Show  ...   1 Season  International TV Shows, Spanish-Language TV Sh...  Four of Colombia's funniest and bawdiest comed...
3    750    s751    Movie  ...     97 min   Dramas, Independent Movies, International Movies  To escape an arranged marriage, a woman flees ...
4    753    s754  TV Show  ...   1 Season  International TV Shows, Romantic TV Shows, Spa...  After learning they were switched at birth, we...
```