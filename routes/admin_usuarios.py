from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import  conectar_bd

admin_usuarios_bp = Blueprint('admin_usuarios', __name__)

@admin_usuarios_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('inicio.inicio'))
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, correo, tipo, fecha_nacimiento FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('admin_usuarios.html', usuarios=usuarios)