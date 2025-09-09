from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/notificaciones')
@login_required
def notificaciones():
    if session.get('tipo_usuario') != "Proveedor":
        flash("Solo los proveedores pueden acceder a las notificaciones.", "error")
        return redirect(url_for('menu'))

    proveedor_id = session.get('usuario_id')
    print("Proveedor ID en sesión:", proveedor_id)

    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('menu'))

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT n.id, n.mensaje, n.leido, n.fecha, p.nombre AS producto, 
                   COALESCE(ip.ruta_imagen, 'static/imagenes/default-product.jpg') AS imagen, 
                   n.estado, u.nombre AS cliente
            FROM notificaciones n
            JOIN productos p ON n.producto_id = p.id
            LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
            JOIN usuarios u ON n.cliente_id = u.id
            WHERE n.proveedor_id = %s
            ORDER BY n.fecha DESC;
        """, (proveedor_id,))

        notificaciones = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        notificaciones_lista = []
        for fila in notificaciones:
            if len(fila) == len(columnas):
                notificaciones_lista.append(dict(zip(columnas, fila)))
            else:
                print(f"Error: Tamaño de fila {len(fila)} no coincide con columnas {len(columnas)}")

        print("DEBUG: Notificaciones procesadas correctamente:", notificaciones_lista)

        cursor.close()
        conexion.close()

        if not notificaciones_lista:
            flash("No tienes notificaciones en este momento.", "info")
            return redirect(url_for('menu'))

        return render_template('notificaciones.html', notificaciones=notificaciones_lista)

    except Exception as e:
        print("Error al cargar las notificaciones:", e)
        flash("Error al cargar las notificaciones. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('menu'))