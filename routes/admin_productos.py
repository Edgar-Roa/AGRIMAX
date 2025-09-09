from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_productos_bp = Blueprint('admin_productos', __name__)

@admin_productos_bp.route('/admin/productos')
@login_required
def admin_productos():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()


    cursor.execute("""
    SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, p.fecha_creacion, u.nombre AS proveedor,
           (SELECT ip.ruta_imagen FROM imagenes_productos ip WHERE ip.producto_id = p.id LIMIT 1) AS ruta_imagen
    FROM productos p
    JOIN usuarios u ON p.proveedor_id = u.id
    JOIN categorias c ON p.categoria_id = c.id
""")

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('admin_productos.html', productos=productos)