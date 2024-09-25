import re
import json
import sqlite3
from collections import defaultdict
import pandas as pd
import os
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

cGEMINI_API_KEY : str = ""

def calculate_table_depth(structure):
    # Initialize all tables with depth 0
    table_depths = {table['name']: 0 for table in structure['tables']}
    
    # Function to get the depth of a table
    def get_depth(table_name):
        if table_name not in table_depths:
            return 0
        return table_depths[table_name]
    
    # Iterate until no changes are made
    changed = True
    while changed:
        changed = False
        for table in structure['tables']:
            if 'foreign_keys' in table:
                new_depth = max(get_depth(fk['references']['table']) for fk in table['foreign_keys']) + 1
                if new_depth > table_depths[table['name']]:
                    table_depths[table['name']] = new_depth
                    changed = True
    
    # Update the structure with calculated depths
    for table in structure['tables']:
        table['deep'] = table_depths[table['name']]
    
    return structure

def update_database_structure(file_path):
    # Read the existing structure
    with open(file_path, 'r', encoding='utf-8') as file:
        structure = json.load(file)
    
    # Calculate and update depths
    updated_structure = calculate_table_depth(structure)
    
    # Write the updated structure back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(updated_structure, file, indent=2, ensure_ascii=False)
    
    print("Database structure updated with DEEP values.")

def print_table_depths(structure):
    for table in structure['tables']:
        print(f"Table: {table['name']}, DEEP: {table['deep']}")

def generate_optimal_join(structure, table_names):
    # Crear un diccionario de tablas para un acceso más fácil
    tables = {table['name']: table for table in structure['tables']}
    
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
    min_depth_table = min(table_names, key=lambda t: tables[t]['deep'])
    
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

def visualize_table_relations(structure):
    mermaid_code = ["graph TD"]
    
    for table in structure['tables']:
        table_name = table['name']
        mermaid_code.append(f"    {table_name}[{table_name}<br>DEEP: {table['deep']}]")
        
        if 'foreign_keys' in table:
            for fk in table['foreign_keys']:
                ref_table = fk['references']['table']
                fields = ', '.join(fk['fields'])
                ref_fields = ', '.join(fk['references']['fields'])
                mermaid_code.append(f"    {table_name} -->|{fields} -> {ref_fields}| {ref_table}")
    
    return "\n".join(mermaid_code)

def print_table_relations(structure):
    print("\nTable Relations:")
    # Agrupar tablas por DEEP
    tables_by_deep = defaultdict(list)
    for table in structure['tables']:
        tables_by_deep[table['deep']].append(table)
    
    # Imprimir tablas agrupadas por DEEP
    for deep, tables in sorted(tables_by_deep.items()):
        print(f"DEEP: {deep}")
        for table in tables:
            print(f"* {table['name']}:")
            if 'foreign_keys' in table:
                for fk in table['foreign_keys']:
                    ref_table = fk['references']['table']
                    for i in range(len(fk['fields'])):
                        print(f"   * {table['name']}.{fk['fields'][i]} -> {ref_table}.{fk['references']['fields'][i]}")
            else:
                print("   * No foreign keys")
        print()  # Línea en blanco entre grupos de DEEP

def print_join_structure(join_structure):
    print(f"Base Table: {join_structure['base_table']}")
    print("Joins:")
    for join in join_structure['joins']:
        print(f"  Join {join['table']} ON "
              f"{join['condition']['left_table']}.{join['condition']['left_field']} = "
              f"{join['condition']['right_table']}.{join['condition']['right_field']}")

def extract_tables_from_prompt(prompt, structure, llm):
    # Preparar la información de las tablas
    tables_info = []
    for table in structure['tables']:
        table_info = f"Table: {table['name']}\n"
        table_info += f"Functional Description: {table.get('functional_description', 'N/A')}\n"
        table_info += f"Technical Description: {table.get('technical_description', 'N/A')}\n"
        table_info += "Fields: " + ", ".join([field['name'] for field in table['fields']]) + "\n\n"
        tables_info.append(table_info)
    
    tables_info_str = "\n".join(tables_info)

    # Crear el template para el prompt
    prompt_template = PromptTemplate(
        input_variables=["tables_info", "user_query"],
        template="""
        Given the following database structure:

        {tables_info}

        And the user query: "{user_query}"

        Please list the names of the tables that are most relevant to answering this query. 
        Only return the table names, separated by commas, without any additional explanation.
        """
    )

    # Crear y ejecutar la cadena LLM
    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.run(tables_info=tables_info_str, user_query=prompt)

    # Procesar el resultado
    extracted_tables = [table.strip() for table in result.split(',')]
    return extracted_tables

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

def generate_sql_query(prompt, join_structure, structure, llm):
    # Preparar la información de las tablas y sus campos
    tables_info = []
    for table in structure['tables']:
        if table['name'] in [join_structure['base_table']] + [j['table'] for j in join_structure['joins']]:
            table_info = f"Table: {table['name']}\n"
            table_info += "Fields: " + ", ".join([f"{field['name']} ({field['type']})" for field in table['fields']]) + "\n\n"
            tables_info.append(table_info)
    
    tables_info_str = "\n".join(tables_info)

    # Preparar la información de la estructura de JOIN
    join_info = f"Base Table: {join_structure['base_table']}\n"
    for join in join_structure['joins']:
        join_info += f"JOIN {join['table']} ON {join['condition']['left_table']}.{join['condition']['left_field']} = {join['condition']['right_table']}.{join['condition']['right_field']}\n"

    # Crear el template para el prompt
    prompt_template = PromptTemplate(
        input_variables=["tables_info", "join_info", "user_query"],
        template="""
        Given the following database structure:

        {tables_info}

        And the optimal JOIN structure:

        {join_info}

        Please generate a complete SQL query to answer the following user query:
        "{user_query}"

        The SQL query should:
        1. Use the provided JOIN structure.
        2. Select only the necessary fields to answer the query.
        3. Include appropriate WHERE clauses if needed.
        4. Use appropriate aggregate functions and GROUP BY clauses if needed.
        5. Order the results in a meaningful way if applicable.

        Return only the SQL query, without any additional explanation.
        """
    )

    # Crear y ejecutar la cadena LLM
    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.run(tables_info=tables_info_str, join_info=join_info, user_query=prompt)

    return post_process_sql_query(result.strip())

def execute_sql_query(query, db_path):
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"---   Error ejecutando la consulta: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    file_path = 'db_config.json'
    db_path = "facturacion.db"
    update_database_structure(file_path)
    
    # Read and print the updated structure
    with open(file_path, 'r', encoding='utf-8') as file:
        updated_structure = json.load(file)
    
    print_table_depths(updated_structure)
    print_table_relations(updated_structure)
    
    """
    # Ejemplo de uso de generate_optimal_join
    tables_to_join = ['movies', 'genres', 'directors']
    join_structure = generate_optimal_join(updated_structure, tables_to_join)
    print("\nOptimal JOIN structure for tables:", tables_to_join)
    print_join_structure(join_structure)

    # Ejemplo adicional con más tablas
    tables_to_join = ['movies', 'genres', 'directors', 'movie_genres', 'movie_directors']
    join_structure = generate_optimal_join(updated_structure, tables_to_join)
    print("\nOptimal JOIN structure for all tables:", tables_to_join)
    print_join_structure(join_structure)
    """
    
    # Configurar el modelo Gemini
    os.environ["GOOGLE_API_KEY"] = cGEMINI_API_KEY  # Reemplaza con tu API key real
    llm = GoogleGenerativeAI(model="gemini-pro", temperature=0)

    # Ejemplos de prompts
    prompts = [
        "Muestra los 10 clientes que han realizado más compras en el último año, incluyendo el total gastado por cada uno.",
        "¿Cuál es el producto más vendido en cada categoría y cuántos ingresos ha generado?",
        "Lista todas las facturas pendientes de pago que tienen más de 30 días de vencimiento, incluyendo los detalles del cliente y el monto adeudado.",
        "Calcula el total de devoluciones por mes en el último trimestre, desglosado por motivo de devolución.",
        "Muestra un informe de los 5 proveedores principales, incluyendo el total de compras realizadas, el producto más comprado a cada uno y el último pedido."
    ]
    
    print("\n--- Extracción de tablas con Langchain y Gemini ---")
    for prompt in prompts:
        print("## ########################################################################################################################################################################")
        extracted_tables = extract_tables_from_prompt(prompt, updated_structure, llm)
        print(f"--  Prompt: {prompt}")
        print(f"--  Tablas extraídas: {extracted_tables}")

        # Generar estructura de JOIN óptima
        if extracted_tables:
            join_structure = generate_optimal_join(updated_structure, extracted_tables)
            print("--  Optimal JOIN structure:")
            print_join_structure(join_structure)
            
            sql_query : str = generate_sql_query(prompt, join_structure, updated_structure, llm)
            print("--  Consulta SQL generada:")
            print(sql_query)
            
            # Ejecutar la consulta y mostrar resultados
            df = execute_sql_query(sql_query, db_path)
            if df is not None:
                print("--  Resultados:")
                print(df.to_string(index=False))
            else:
                print("--  No se pudieron obtener resultados para esta consulta.")
        else:
            print("--   No se pudieron extraer tablas relevantes para esta consulta.")