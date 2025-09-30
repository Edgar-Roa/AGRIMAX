from flask import Blueprint, render_template, request
from bd import conectar_bd

inicio_bp= Blueprint("inicio",__name__)

@inicio_bp.route("/")
def inicio():
    try: 
        conexion = conectar_bd()
        if conexion:
            cursor= conexion.cursor()
            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                       u.nombre AS proveedor, ip.ruta_imagen, u.id AS proveedor_id
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                JOIN usuarios u ON p.proveedor_id = u.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                ORDER BY p.fecha_creacion DESC
            """)
            productos= cursor.fetchall()
            cursor.close()
            conexion.close()
            return render_template("inicio.html", productos=productos)  
    except Exception as e:
        print(f"Error al cargar los productos: {e}")
        return render_template("inicio.html", error="Error al cargar los productos")

    return render_template("inicio.html")



