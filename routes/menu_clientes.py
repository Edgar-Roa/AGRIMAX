from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

menu_clientes_bp = Blueprint('menu_clientes', __name__)

@menu_clientes_bp.route('/menu_principal')
@login_required
def menu_principal():
    usuario_id = session['usuario_id']
    print(f"Usuario autenticado: {usuario_id}")

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            print("Conexión a la base de datos exitosa.")

            cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
            tipo_usuario = cursor.fetchone()
            print(f"Tipo de usuario: {tipo_usuario}")

            if not tipo_usuario or tipo_usuario[0] != "Cliente":
                flash("Solo los clientes pueden acceder a esta página.", "error")
                return redirect(url_for('menu'))

            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                       u.nombre AS proveedor, ip.ruta_imagen, u.id AS proveedor_id
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                JOIN usuarios u ON p.proveedor_id = u.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                ORDER BY p.fecha_creacion DESC
            """)
            productos = cursor.fetchall()

            productos_procesados = []
            for producto in productos:
                productos_procesados.append({
                    'id': producto[0],
                    'nombre': producto[1],
                    'descripcion': producto[2],
                    'precio': producto[3],
                    'categoria': producto[4],
                    'proveedor': producto[5],
                    'imagen': f"/static/{producto[6]}" if producto[6] else '/static/imagenes/default-product.jpg',
                    'proveedor_id': producto[7]
                })

            carrito = session.get('carrito', [])
            cantidad_total = sum(item['cantidad'] for item in carrito)

            print(f"Productos obtenidos: {productos}")

            cursor.close()
            conexion.close()

            return render_template('menu_cliente.html',
                                   productos=productos_procesados,
                                   cantidad_total=cantidad_total,
                                   usuario_id=usuario_id)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio.inicio'))
    except Exception as e:
        print(f"Error al cargar los productos: {e}")
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('inicio.inicio'))