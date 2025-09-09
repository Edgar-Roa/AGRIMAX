import psycopg2

# Diccionario con los datos de conexión
configuracion_bd = {
    'host': 'localhost',
    'database': 'agrimax',
    'user': 'postgres',
    'password': '12345'
}

# Función que retorna la conexión
def conectar_bd():
    try:
        conexion = psycopg2.connect(**configuracion_bd)
        print("Conexión exitosa a la base de datos")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Prueba local del módulo
if __name__ == "__main__":
    conectar_bd()