from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

marcar_notificaciones_bp = Blueprint('marcar_notificaciones', __name__)

@marcar_notificaciones_bp.route('/marcar_leido/<int:notificacion_id>', methods=['POST'])
@login_required
def marcar_leido(notificacion_id):
    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE notificaciones 
                SET leido = TRUE 
                WHERE id = %s
            """, (notificacion_id,))
            conexion.commit()
            cursor.close()
            conexion.close()
            flash("Notificación marcada como leída.", "success")
        else:
            flash("Error al conectar con la base de datos.", "error")
    except Exception as e:
        print("Error al marcar como leído:", e)
        flash("Ocurrió un error. Inténtalo de nuevo.", "error")

    return redirect(url_for('notificaciones'))