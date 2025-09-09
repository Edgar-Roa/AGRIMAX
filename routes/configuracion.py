from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

configuracion_bp = Blueprint('configuracion', __name__)

@configuracion_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required

def configuracion():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
        tipo_usuario = cursor.fetchone()[0]

        if request.method == 'GET':
            cursor.execute("""
                SELECT u.id, u.nombre, u.correo, p.foto, p.biografia, p.notificaciones_email, p.notificaciones_sms
                FROM usuarios u
                LEFT JOIN perfiles p ON u.id = p.usuario_id
                WHERE u.id = %s
            """, (usuario_id,))
            usuario_data = cursor.fetchone()

            usuario = {
                'id': usuario_data[0],
                'nombre': usuario_data[1],
                'correo': usuario_data[2],
                'foto': usuario_data[3] if usuario_data[3] else 'imagenes/default-profile.jpg',
                'biografia': usuario_data[4] if usuario_data[4] else '',
                'notificaciones_email': usuario_data[5],
                'notificaciones_sms': usuario_data[6]
            }

            cursor.close()
            conexion.close()

            if tipo_usuario == "Cliente":
                return render_template('configuracion_clientes.html', usuario=usuario)
            elif tipo_usuario == "Proveedor":
                return render_template('configuracion.html', usuario=usuario)
            else:
                flash("Tipo de usuario desconocido.", "error")
                return redirect(url_for('inicio.inicio'))

        elif request.method == 'POST':
            seccion = request.form.get('seccion')

            if seccion == 'perfil':
                nombre = request.form.get('nombre')
                apellido = request.form.get('apellido', '')
                biografia = request.form.get('biografia', '')
                foto = request.files.get('foto')

                if foto and allowed_file(foto.filename):
                    filename = secure_filename(f"{usuario_id}_{foto.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    foto.save(filepath)

                    ruta_foto = f"imagenes/{filename}"
                    cursor.execute("""
                        UPDATE perfiles 
                        SET foto = %s, biografia = %s 
                        WHERE usuario_id = %s
                    """, (ruta_foto, biografia, usuario_id))
                else:
                    cursor.execute("""
                        UPDATE perfiles 
                        SET biografia = %s 
                        WHERE usuario_id = %s
                    """, (biografia, usuario_id))

                cursor.execute("""
                    UPDATE usuarios 
                    SET nombre = %s, apellido = %s 
                    WHERE id = %s
                """, (nombre, apellido, usuario_id))

            elif seccion == 'notificaciones':
                notificaciones_email = 'notificaciones_email' in request.form
                notificaciones_sms = 'notificaciones_sms' in request.form

                cursor.execute("""
                    UPDATE perfiles 
                    SET notificaciones_email = %s, notificaciones_sms = %s 
                    WHERE usuario_id = %s
                """, (notificaciones_email, notificaciones_sms, usuario_id))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash("Configuración actualizada correctamente.", "success")
            return redirect(url_for('configuracion'))

    except Exception as e:
        print(f"Error al manejar la configuración: {e}")
        flash("Ocurrió un error al manejar la configuración.", "error")
        return redirect(url_for('inicio.inicio'))