from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd
from flask import request
import bcrypt

admin_crear_usuarios_bp = Blueprint('admin_crear_usuarios', __name__)

@admin_crear_usuarios_bp.route('/admin/crear_usuario', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        tipo = request.form['tipo']
        contraseña_plana = request.form['contraseña']


        salt = bcrypt.gensalt()
        contraseña_hash = bcrypt.hashpw(contraseña_plana.encode('utf-8'), salt).decode('utf-8')

        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contraseña, tipo)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, contraseña_hash, tipo))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for('admin_usuarios'))

    return render_template('crear_usuario.html')