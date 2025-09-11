from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_editar_productos_bp = Blueprint('admin_editar_productos', __name__)

@admin_editar_productos_bp.route('/admin/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria_id = request.form['categoria_id']

        cursor.execute("""
            UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, categoria_id=%s WHERE id=%s
        """, (nombre, descripcion, precio, categoria_id, id))
        conexion.commit()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for('admin_productos.admin_productos'))

    cursor.execute("SELECT id, nombre, descripcion, precio, categoria_id FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('editar_producto.html', producto=producto)