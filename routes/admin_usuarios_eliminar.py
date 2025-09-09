from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_usuarios_eliminar_bp = Blueprint('admin_usuarios_eliminar', __name__)

@admin_usuarios_eliminar_bp.route('/admin/eliminar_usuario/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for('admin_usuarios.admin_usuarios'))