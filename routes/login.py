from flask import Blueprint, render_template, request, redirect, url_for, flash, session, request
from bd import conectar_bd
from flask_login import login_user
from models import Usuario  # Importa la clase Usuario desde app.py
import bcrypt

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        try:
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT id, nombre, tipo, contraseña FROM usuarios WHERE correo = %s
                """, (correo,))
                usuario = cursor.fetchone()
                cursor.close()
                conexion.close()

                if usuario and bcrypt.checkpw(contraseña.encode('utf-8'), usuario[3].encode('utf-8')):
                    usuario_obj = Usuario(usuario[0],usuario[1],usuario[2])
                    login_user(usuario_obj)
                    session['usuario_id'] = usuario[0]
                    session['tipo_usuario'] = usuario[2]

                    flash(f"Bienvenido, {usuario[1]}!", "success")

                    
                    if usuario[2] == "Administrador":
                        return redirect(url_for('admin_dashboard.admin_dashboard'))
                    elif usuario[2] == "Cliente":
                        return redirect(url_for('menu_clientes.menu_principal'))
                    elif usuario[2] == "Proveedor":
                        return redirect(url_for('menu_provedor.menu'))
                else:
                    flash("Correo o contraseña incorrectos.", "error")
                    return render_template('login.html')
            else:
                flash("Error al conectar con la base de datos.", "error")
                return render_template('login.html')
        except Exception as e:
            print("Error al iniciar sesión:", e)
            flash("Ocurrió un error al iniciar sesión. Intenta nuevamente.", "error")
            return render_template('login.html')

    return render_template('login.html')    