import sqlite3
import os

def create_sqlite_database(schema_file, db_name):
    # Eliminar la base de datos si ya existe
    if os.path.exists(db_name):
        os.remove(db_name)

    # Conectar a la base de datos (esto la creará si no existe)
    conn = sqlite3.connect(db_name)
    
    # Configurar la conexión para usar UTF-8
    conn.text_factory = str

    # Crear un cursor
    cursor = conn.cursor()

    # Leer el archivo del esquema
    with open(schema_file, 'r', encoding='utf-8') as file:
        schema = file.read()

    # Dividir el esquema en comandos individuales
    commands = schema.split(';')

    # Primero, crear todas las tablas
    for command in commands:
        try:
            cursor.execute(command)
        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            print("command:", command)

    # Commit los cambios y cerrar la conexión
    conn.commit()
    conn.close()

    print(f"Base de datos SQLite '{db_name}' creada exitosamente.")

if __name__ == "__main__":
    schema_file = 'schema.sql'
    db_name = 'facturacion.db'
    create_sqlite_database(schema_file, db_name)