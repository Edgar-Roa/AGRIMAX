from bd import conectar_bd

# Probar la conexión
conexion = conectar_bd()
if conexion:
    cursor = conexion.cursor()
    cursor.execute("SELECT version();")  # Consulta simple para verificar la conexión
    version = cursor.fetchone()
    print("Versión de PostgreSQL:", version[0])
    cursor.close()
    conexion.close()
else:
    print("No se pudo conectar a la base de datos.")