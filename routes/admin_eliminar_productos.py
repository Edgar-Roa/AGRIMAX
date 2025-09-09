from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_eliminar_productos_bp = Blueprint('admin_eliminar_productos', __name__)

@admin_eliminar_productos_bp.route('/admin/eliminar_producto/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_producto_admin(producto_id):  
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    flash("Producto eliminado correctamente.", "success")
    return redirect(url_for('admin_productos.admin_productos'))