from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

procesos_productos_bp = Blueprint('procesos_productos', __name__)

@procesos_productos_bp.route('/proceso/<int:producto_id>')
@login_required
def ver_proceso(producto_id):
    try:
        
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('perfil', usuario_id=session['usuario_id']))

        cursor = conexion.cursor()


        cursor.execute("""
            SELECT p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                   u.nombre AS proveedor, ip.ruta_imagen, dp.estado
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            JOIN usuarios u ON p.proveedor_id = u.id
            LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
            JOIN detalles_pedidos dp ON p.id = dp.producto_id
            WHERE p.id = %s
            FOR UPDATE;
        """, (producto_id,))
        producto = cursor.fetchone()

        cursor.close()
        conexion.close()

        if producto:
            return render_template('proceso_producto.html', producto=producto)
        else:
            flash("No se encontró información sobre el proceso del producto.", "error")
            return redirect(url_for('perfil', usuario_id=session['usuario_id']))

    except Exception as e:
        print(f"Error al cargar el proceso del producto: {e}")
        flash("Error al cargar el proceso del producto. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('perfil', usuario_id=session['usuario_id']))