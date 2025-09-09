from flask import Blueprint, render_template, request, redirect, url_for, flash, session, request
from bd import conectar_bd
import bcrypt
from correo_utils import enviar_correo_registro

registro_bp = Blueprint("registro",__name__)

@registro_bp.route("/registro", methods=['GET','POST'])
def registro():
    if request.method == 'POST':
        try:
            
            nombre = request.form.get('nombre')
            edad = request.form.get('edad')
            correo = request.form.get('correo')
            contraseña = request.form.get('contraseña')
            tipo = request.form.get('tipo')
            fecha_nacimiento = request.form.get('fecha_nacimiento', None)
            telefono = request.form.get('telefono', None)

            
            if not nombre or not edad or not correo or not contraseña or not tipo:
                flash("Todos los campos son obligatorios.", "error")
                return render_template('registro.html')

           
            hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

            
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()

                
                cursor.execute("""
                    INSERT INTO usuarios (nombre, correo, contraseña, tipo, edad, fecha_nacimiento, telefono)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (nombre, correo, hashed_password.decode('utf-8'), tipo, edad, fecha_nacimiento, telefono))

                usuario_id = cursor.fetchone()[0]

                
                cursor.execute("""
                    INSERT INTO perfiles (usuario_id, foto, biografia)
                    VALUES (%s, %s, %s)
                """, (usuario_id, '/static/imagenes/default.jpg', 'Biografía no configurada'))

                conexion.commit()
                cursor.close()
                conexion.close()

                print("Usuario y perfil registrados correctamente.")

                
                enviar_correo_registro(correo, nombre, tipo)

                flash("Usuario registrado correctamente. Se ha enviado un correo de bienvenida.", "success")
                return redirect(url_for('login.login'))
            else:
                flash("No se pudo conectar a la base de datos.", "error")
        except Exception as e:
            print("Error al registrar el usuario:", e)
            flash("Ocurrió un error al registrar el usuario. Intenta nuevamente.", "error")

    return render_template('registro.html')
