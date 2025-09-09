from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_reportes_bp = Blueprint('admin_reportes', __name__)

@admin_reportes_bp.route('/admin/reportes')
@login_required
def admin_reportes():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    
    cursor.execute("""
        SELECT tipo, COUNT(*) FROM usuarios GROUP BY tipo
    """)
    usuarios_por_tipo = cursor.fetchall()

    
    cursor.execute("""
        SELECT DATE(fecha_registro), COUNT(*) FROM usuarios GROUP BY DATE(fecha_registro)
    """)
    registros_por_fecha = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('admin_reportes.html', usuarios_por_tipo=usuarios_por_tipo, registros_por_fecha=registros_por_fecha)