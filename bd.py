import psycopg2
from psycopg2 import sql

def conectar_bd():
    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="agrimax",
            user="postgres",
            password="12345"
        )
        print("Conexión exitosa a la base de datos.")
        return conexion
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None