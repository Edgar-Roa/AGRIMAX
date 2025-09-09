from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_editar_usuarios_bp = Blueprint('admin_editar_usuario', __name__)

@admin_editar_usuarios_bp.route('/admin/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('inicio.inicio'))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    if request.method == 'POST':
        correo = request.form['correo']
        tipo = request.form['tipo']
        cursor.execute(
            "UPDATE usuarios SET correo=%s, tipo=%s WHERE id=%s", (correo, tipo, id)
        )
        conexion.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for('admin_usuarios.admin_usuarios'))

    cursor.execute("SELECT id, nombre, correo, tipo FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('editar_usuario.html', usuario=usuario)