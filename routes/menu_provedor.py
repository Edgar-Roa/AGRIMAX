from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

menu_provedor_bp = Blueprint('menu_provedor', __name__)

@menu_provedor_bp.route('/menu')
@login_required
def menu():
    usuario_id = session.get('usuario_id') 
    if not usuario_id:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login.login'))

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                       p.fecha_creacion, ip.ruta_imagen
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                WHERE p.proveedor_id = %s
                ORDER BY p.fecha_creacion DESC
            """, (usuario_id,))
            productos = cursor.fetchall()

            cursor.close()
            conexion.close()

            productos_procesados = []
            for producto in productos:
                productos_procesados.append({
                    'id': producto[0],
                    'nombre': producto[1],
                    'descripcion': producto[2],
                    'precio': producto[3],
                    'categoria': producto[4],
                    'fecha_creacion': producto[5],
                    'imagen': f"/static/{producto[6]}" if producto[6] else '/static/imagenes/default-product.jpg'
                })

            return render_template('menu_provedor.html', usuario_id=usuario_id, productos=productos_procesados)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('login.login'))
    except Exception as e:
        print("Error al cargar los productos del proveedor:", e)
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('login.login'))