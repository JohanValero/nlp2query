import os
import re
import json
import pandas as pd
import sqlite3

from collections import defaultdict

from langchain_google_genai import GoogleGenerativeAI
from langchain import PromptTemplate
from langchain_core.runnables.base import RunnableSequence

from flask import Flask, request, jsonify
from flask_cors import CORS

cSOURCE_JSON_FILE : str = "db_config_2.json"

app = Flask(__name__)
CORS(app)

def calculate_depth(p_sql_structure : dict) -> None:
    tables : list[dict] = p_sql_structure["tables"]
    table_depths : dict = {}

    def get_table_depth(table_name, visited : set | None = None):
        if visited is None:
            visited : set = set()

        if table_name in table_depths:
            return table_depths[table_name]

        if table_name in visited:
            return 0
        
        visited.add(table_name)

        table : dict = get_table_by_name(tables, table_name)
        if not table or "foreign_keys" not in table:
            return 0

        max_depth : int = 0
        for fk in table.get("foreign_keys", []):
            referenced_table : str = fk["references"]["table"]
            depth : int = 1 + get_table_depth(referenced_table, visited)
            max_depth : int = max(max_depth, depth)

        table_depths[table_name] = max_depth
        return max_depth

    for table in tables:
        if table["name"] not in table_depths:
            table_depths[table["name"]] = get_table_depth(table["name"])

    for table in tables:
        table["depth"] = table_depths[table["name"]]

def print_schema_info(p_sql_structure : dict) -> None:
    print("Tablas ordenadas por depth (ascendente) y nombre (alfabéticamente):")
    current_depth : int = -1
    for table in p_sql_structure["tables"]:
        if current_depth != table["depth"]:
            print("Depth:", table["depth"])
            current_depth : int = table["depth"]
        print(f"{table['id']:2} -- {table['name']}")
        if "foreign_keys" in table:
            print("   * Foreign Keys (Parents):")
            for fk in table["foreign_keys"]:
                fk_table : dict = get_table_by_name(p_sql_structure["tables"], fk["references"]["table"])
                print(f'\tDepth: {fk_table["depth"]:2} - {table["name"]}({table["id"]}).{fk["fields"][0]} == {fk_table["name"]}({fk_table["id"]}).{fk["references"]["fields"][0]}')
        else:
            print("   * No have Parents.")
            
        childs = table["childs"]
        if childs and len(childs) > 0:
            print("   * References (Childs):")
            for ch in childs:
                child_table : dict = get_table_by_name(p_sql_structure["tables"], ch["references"]["table"])
                print(f'\tDepth: {child_table["depth"]:2} - {table["name"]}({table["id"]}).{ch["fields"][0]} == {child_table["name"]}({child_table["id"]}).{ch["references"]["fields"][0]}')
        else:
            print("   * No have childs.")

def assign_table_ids(p_tables : list[dict]) -> None:
    for id, t in enumerate(p_tables):
        t["id"] = id
    
def get_childs(p_tables : list[dict], p_table_name : str) -> list[dict] | None:
    table = get_table_by_name(p_tables, p_table_name)
    if table is None:
        return []

    childs = []
    for t in p_tables:
        if "foreign_keys" in t:
            for fk in t["foreign_keys"]:
                if fk["references"]["table"] == p_table_name:
                    childs.append({
                        "fields": fk["references"]["fields"],
                        "references": {
                            "table": t["name"],
                            "fields": fk["fields"]
                        }
                    })
                    break
    return childs

def assign_childs(p_tables : list[dict]) -> None:
    for tb in p_tables:
        tb["childs"] = get_childs(p_tables, tb["name"])

def get_table_by_name(p_tables : list[dict], p_table_name : str) -> dict | None:
    return next((t for t in p_tables if t["name"] == p_table_name), None)

def load_database_structure(p_json_file) -> None:
    sql_structure : dict = dict()
    with open(p_json_file, "r", encoding="utf-8") as tFile:
        sql_structure = json.load(tFile)
    calculate_depth(sql_structure)
    sql_structure["tables"] = sorted(sql_structure["tables"], key=lambda x: (x["depth"], x["name"]))
    assign_table_ids(sql_structure["tables"])
    assign_childs(sql_structure["tables"])
    return sql_structure

def find_every_path(p_tables: list[dict], p_table_a: str, p_table_b: str) -> list[list[str]]:
    def dfs(current_table: str, target_table: str, path: list[str], visited: set[str]) -> list[list[str]]:
        if current_table == target_table:
            return [path]
        
        paths = []
        current_table_obj = get_table_by_name(p_tables, current_table)
        
        # Check foreign keys (parents)
        if "foreign_keys" in current_table_obj:
            for fk in current_table_obj["foreign_keys"]:
                next_table = fk["references"]["table"]
                if next_table not in visited:
                    new_path = path + [next_table]
                    new_visited = visited.union({next_table})
                    paths.extend(dfs(next_table, target_table, new_path, new_visited))
        
        # Check childs
        for child in current_table_obj.get("childs", []):
            next_table = child["references"]["table"]
            if next_table not in visited:
                new_path = path + [next_table]
                new_visited = visited.union({next_table})
                paths.extend(dfs(next_table, target_table, new_path, new_visited))
        
        return paths

    all_paths = dfs(p_table_a, p_table_b, [p_table_a], {p_table_a})
    return all_paths

def get_optimal_path(p_tables: list[dict], paths: list[list[str]]) -> list[str]:
    if not paths:
        return []

    def path_score(path):
        depths = [get_table_by_name(p_tables, table)["depth"] for table in path]
        descents = sum(1 for i in range(1, len(depths)) if depths[i] > depths[i-1])
        ascents = sum(1 for i in range(1, len(depths)) if depths[i] < depths[i-1])
        return (ascents, len(path), -descents)  # We use -descents to prefer more descents

    # First, filter only descending paths
    descending_paths = [path for path in paths if all(get_table_by_name(p_tables, path[i])["depth"] >= get_table_by_name(p_tables, path[i-1])["depth"] for i in range(1, len(path)))]

    if descending_paths:
        # If there are descending paths, choose the shortest one
        return min(descending_paths, key=len)
    else:
        # If no descending paths, choose the path with the least ascents and shortest length
        return min(paths, key=path_score)

def generate_optimal_join(structure, table_names):
    # Crear un diccionario de tablas para un acceso más fácil
    tables : list[dict] = {table['name']: table for table in structure['tables']}
    
    # Crear un grafo de relaciones entre tablas
    graph = defaultdict(dict)
    for table in structure['tables']:
        if 'foreign_keys' in table:
            for fk in table['foreign_keys']:
                ref_table = fk['references']['table']
                graph[table['name']][ref_table] = (fk['fields'], fk['references']['fields'])
                graph[ref_table][table['name']] = (fk['references']['fields'], fk['fields'])

    def find_shortest_path(start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in graph:
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = find_shortest_path(node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest
    
    # Encontrar la tabla de menor profundidad
    min_depth_table = min(table_names, key=lambda t: tables[t]['depth'])
    
    join_structure = {
        "base_table": min_depth_table,
        "joins": []
    }
    
    joined_tables = set([min_depth_table])
    
    for table in table_names:
        if table not in joined_tables:
            path = find_shortest_path(min_depth_table, table)
            if path:
                for i in range(len(path) - 1):
                    t1, t2 = path[i], path[i+1]
                    fields1, fields2 = graph[t1][t2]
                    join = {
                        "table": t2,
                        "condition": {
                            "left_table": t1,
                            "left_field": fields1[0],
                            "right_table": t2,
                            "right_field": fields2[0]
                        }
                    }
                    if join not in join_structure["joins"]:
                        join_structure["joins"].append(join)
                joined_tables.update(path)

    return join_structure

def print_join_structure(join_structure : dict) -> None:
    print(f"Base Table: {join_structure['base_table']}")
    print("Joins:")
    for join in join_structure['joins']:
        print(f"  Join {join['table']} ON "
              f"{join['condition']['left_table']}.{join['condition']['left_field']} = "
              f"{join['condition']['right_table']}.{join['condition']['right_field']}")


def post_process_sql_query(sql_query):
    # Eliminar marcadores de código Markdown si están presentes
    sql_query = re.sub(r'^```sql\s*|```$', '', sql_query, flags=re.MULTILINE)
    
    # Eliminar espacios en blanco al inicio y al final
    sql_query = sql_query.strip()
    
    # Eliminar comentarios de una sola línea
    sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    
    # Eliminar comentarios multilinea
    sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
    
    # Reemplazar múltiples espacios en blanco con uno solo
    sql_query = re.sub(r'\s+', ' ', sql_query)
    
    return sql_query


def execute_sql_query(query, db_path) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"---   Error ejecutando la consulta: {e}")
        return None
    finally:
        conn.close()

def nlp2sql(p_prompt : str, p_structure : list[dict]) -> str:
    tables_info = []
    for table in p_structure['tables']:
        table_info = f"Table: {table['name']}\n"
        table_info += "Fields: " + ", ".join([field['name'] for field in table['fields']]) + "\n\n"
        tables_info.append(table_info)
    
    tables_info_str : str = "\n".join(tables_info)

    # 1. Detectar que campos se solicitan en el prompt
    fields_prompt = PromptTemplate(
        input_variables=["schema", "prompt"],
        template="""Contexto:
Estás analizando un prompt de usuario para identificar qué campos de una base de datos se necesitan para responder a su solicitud.

Esquema de base de datos:
{schema}

Prompt del usuario:
{prompt}

Instrucciones:
- Identifica los campos inferidos mencionados NO explícitamente en el prompt del usuario.
- Proporciona los nombres de los campos en una lista numerada.
- Cada campo debe estar en una nueva línea comenzando con un número seguido de un punto.

Respuesta:"""
    )
    fields_chain = fields_prompt|llm
    requested_fields : str = fields_chain.invoke({"schema": tables_info_str, "prompt": p_prompt}).strip()
    
    # 2. Detectar los campos que complementen y/o enriquezcan los campos detectados
    enrich_prompt = PromptTemplate(
        input_variables=["schema", "prompt", "requested_fields"],
        template="""Contexto:
Estás analizando un prompt de usuario para identificar campos adicionales que podrían enriquecer o complementar los campos ya solicitados para responder a la solicitud del usuario.

Esquema de base de datos:
{schema}

Prompt del usuario:
{prompt}

Campos solicitados:
{requested_fields}

Instrucciones:
- Identifica campos adicionales que no fueron mencionados explícitamente por el usuario pero que podrían ser útiles para enriquecer la respuesta.
- Considera campos como identificadores únicos, fechas, u otros detalles relevantes.
- No inventes campos que no estén en el esquema de la base de datos.
- Proporciona los nombres de los campos en una lista numerada.
- Cada campo debe estar en una nueva línea comenzando con un número seguido de un punto.
- Si no hay campos adicionales relevantes, responde "No se identificaron campos adicionales relevantes".

Ejemplos de campos adicionales relevantes:
- Si el usuario solicita nombres de clientes, un campo adicional relevante podría ser "id_cliente" para identificar de manera única a cada cliente.
- Si pide la información de un producto, entonces sería util el nombre del producto.
- Si el usuario solicita detalles de una compra, campos adicionales relevantes podrían ser "fecha_compra" y "total_compra".

Respuesta: """
    )
    enrich_chain : RunnableSequence = enrich_prompt|llm
    enriched_fields : str = enrich_chain.invoke({"schema": tables_info_str, "prompt": p_prompt, "requested_fields": ", ".join(requested_fields)}).strip()
    all_fields = requested_fields + enriched_fields

    # 3. Detectar los filtros necesarios según el prompt
    filters_prompt = PromptTemplate(
        input_variables=["schema", "prompt"],
        template="""Contexto:
Estás analizando un prompt de usuario para identificar los filtros o condiciones que deben aplicarse a una consulta de base de datos para responder a la solicitud del usuario.

Esquema de base de datos:
{schema}

Prompt del usuario:
{prompt}

Instrucciones:
- Identifica todas las condiciones o filtros mencionados explícitamente o implícitamente en el prompt del usuario.
- Considera filtros basados en fechas, cantidades, texto y cualquier otro criterio relevante.
- Para cada filtro, proporciona el nombre del campo, el operador de comparación y el valor.
- Expresa cada filtro en una nueva línea usando el formato: "[Nombre del campo] [Operador] [Valor]".
- Si se menciona un rango, usa "entre" como el operador y especifica los valores mínimo y máximo.
- Si no se mencionan filtros, responde "No se mencionan filtros".

Ejemplos de filtros:
- Si el usuario menciona "en los últimos 3 meses", un filtro podría ser: "fecha_compra entre '2023-03-01' y '2023-05-31'"
- Si el usuario menciona "compras superiores a $1000", un filtro podría ser: "total_compra > 1000"
- Si el usuario menciona "clientes con nombre 'John'", un filtro podría ser: "nombre_cliente = 'John'"

Respuesta: """
    )
    filters_chain = filters_prompt|llm
    filters = filters_chain.invoke({"schema": tables_info_str, "prompt": p_prompt}).strip()
    
    # 4. Identificar las tablas de donde obtener cada campo y filtro
    tables_prompt = PromptTemplate(
        input_variables=["schema", "prompt", "all_fields", "filters"],
        template="""Contexto:
Estás analizando un prompt de usuario para identificar las tablas de la base de datos que son más relevantes para obtener los campos solicitados y aplicar los filtros necesarios.

Estructura de la base de datos:
{schema}

Prompt del usuario:
{prompt}

Campos solicitados:
{all_fields}

Filtros a aplicar:
{filters}

Instrucciones:
- Identifica las tablas que contienen los campos solicitados por el usuario.
- Identifica las tablas necesarias para aplicar los filtros mencionados por el usuario.
- Proporciona solo los nombres de las tablas, separados por comas, sin ninguna explicación adicional.
- Si la consulta puede ser respondida usando una sola tabla, menciona solo esa tabla.
- Si la consulta requiere la unión de múltiples tablas, menciona todas las tablas necesarias.

Ejemplo de respuesta: tabla1, tabla2, tabla3

Respuesta: """
    )
    tables_chain = tables_prompt|llm
    table_mappings = tables_chain.invoke({"schema": tables_info_str, "prompt": p_prompt, "all_fields": ", ".join(all_fields), "filters": ", ".join(filters)}).strip()
    
    tables : list[str] = list(set(table_mappings.split(",")))
    tables : list[str] = [x.strip() for x in tables]

    join_structure : list[dict] = generate_optimal_join(p_structure, tables)

    join_info = f"Base Table: {join_structure['base_table']}\n"
    for join in join_structure['joins']:
        join_info += f"JOIN {join['table']} ON {join['condition']['left_table']}.{join['condition']['left_field']} = {join['condition']['right_table']}.{join['condition']['right_field']}\n"

    # 5. Identificar las funciones agrupadoras necesarias
    agg_prompt = PromptTemplate(
        input_variables=["schema", "prompt", "all_fields", "filters", "tables"],
        template="""Contexto:
Estás analizando un prompt de usuario para determinar qué funciones de agregación o analíticas de SQL (como SUM, MAX, MIN, AVG, COUNT, ROW_NUMBER, RANK, etc.) pueden ser necesarias para responder adecuadamente a la consulta, basándote en los campos solicitados, los filtros a aplicar y las tablas involucradas.

Esquema de la base de datos:
{schema}

Prompt del usuario:
{prompt}

Campos solicitados:
{all_fields}

Filtros a aplicar:
{filters}

Tablas a usar:
{tables}

Instrucciones:
- Analiza el prompt del usuario, los campos solicitados y los filtros para determinar si se requieren cálculos agregados o análisis de datos.
- Si se solicitan valores totales, promedios, conteos o valores extremos (máximo o mínimo), sugiere el uso de las funciones de agregación apropiadas (SUM, AVG, COUNT, MAX, MIN).
- Si se requiere numerar, ordenar o clasificar resultados, sugiere el uso de funciones analíticas relevantes (ROW_NUMBER, RANK, DENSE_RANK).
- Para cada función sugerida, explica por qué crees que es necesaria o útil basándote en el prompt del usuario.
- Si no crees que se necesiten funciones de agregación o analíticas para esta consulta, di "No se requieren funciones de agregación o analíticas para esta consulta".

Formato de respuesta:
- Función 1: Nombre de la función (razón por la que es necesaria)
- Función 2: Nombre de la función (razón por la que es necesaria)
...

Respuesta:"""
    )
    agg_chain = agg_prompt|llm
    agg_functions = agg_chain.invoke({"schema": tables_info_str, "tables": table_mappings, "prompt": p_prompt, "all_fields": ", ".join(all_fields), "filters": ", ".join(filters)}).strip()
    
    # 6. Generar consulta
    agg_prompt = PromptTemplate(
        input_variables=["schema", "prompt", "all_fields", "filters", "tables", "aggregations", "join"],
        template="""Contexto:
Como un experto en SQL, tu tarea es escribir una consulta SQL que responda a la pregunta del usuario, utilizando la información proporcionada sobre los campos solicitados, los filtros a aplicar, las tablas necesarias y las funciones de agregación y analíticas sugeridas.

Esquema de la base de datos:
{schema}

Prompt del usuario:
{prompt}

Campos solicitados:
{all_fields}

Filtros a aplicar:
{filters}

Tablas a usar:
{tables}

Join optimo:
{join}

Funciones de agregación y analíticas sugeridas:
{aggregations}

Instrucciones:
- Escribe una consulta SQL que recupere los campos solicitados de las tablas necesarias.
- Aplica los filtros especificados para restringir los resultados.
- Utiliza las funciones de agregación y analíticas sugeridas cuando sea apropiado para calcular totales, promedios, etc., o para numerar y clasificar resultados.
- Si se necesitan múltiples tablas, asegúrate de usar las cláusulas JOIN adecuadas para combinar las tablas basándote en las relaciones especificadas en el esquema de la base de datos.
- Formatea la consulta SQL para facilitar su lectura, con cada cláusula principal (SELECT, FROM, WHERE, GROUP BY, ORDER BY) en su propia línea.
- Asegúrate de que la consulta se ejecute sin errores y devuelva los resultados esperados basándote en el prompt del usuario.

Respuesta:"""
    )
    sql_chain = agg_prompt|llm
    sql_result = sql_chain.invoke({
        "schema": tables_info_str,
        "tables": table_mappings,
        "prompt": p_prompt,
        "all_fields": ", ".join(all_fields),
        "filters": ", ".join(filters),
        "aggregations": agg_functions,
        "join": join_structure
    }).strip()
    
    return post_process_sql_query(sql_result), {
        "requested_fields": requested_fields,
        "enriched_fields": enriched_fields,
        "filters": filters,
        "table_mappings": table_mappings,
        "join_info": join_info,
        "agg_functions": agg_functions,
        "sql_result": sql_result
    }

def nlp2data(p_prompt : str, p_structure : list[dict]) -> tuple[str, pd.DataFrame, dict]:
    sql_query, steps_info = nlp2sql(p_prompt, p_structure)
    print("sql_query:", sql_query)
    
    df : pd.DataFrame = execute_sql_query(sql_query, p_structure["database_name"])

    return sql_query, df, steps_info

llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.1)

cSQL_STRUCTURE : dict = load_database_structure(cSOURCE_JSON_FILE)

@app.route('/api/v0/generate_sql', methods=['GET'])
def query():
    prompt : str | None = request.args.get('prompt')
    
    if not prompt:
        return jsonify({"error": "No se proporcionó un prompt"}), 400
    
    try:
        sql_query, df, steps_info = nlp2data(prompt, cSQL_STRUCTURE)
        return jsonify({
            "promt": prompt,
            "sql": sql_query,
            "steps_info": steps_info,
            "records": df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

cPORT : int = os.getenv("PORT", 88)

if not cPORT:
    raise ValueError

if __name__ == "__main__":
    print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
    app.run(host="0.0.0.0", port=cPORT)

