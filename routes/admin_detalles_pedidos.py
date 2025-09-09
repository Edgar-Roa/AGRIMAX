from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_detalles_pedidos_bp = Blueprint('admin_detalles_pedidos', __name__)

@admin_detalles_pedidos_bp.route('/admin/pedido/<int:pedido_id>')
@login_required
def admin_detalle_pedido(pedido_id):
    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('admin_pedidos'))

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT p.id, u.nombre AS cliente, u.correo AS email, p.total, p.estado, p.fecha
            FROM pedidos p
            JOIN usuarios u ON p.cliente_id = u.id
            WHERE p.id = %s
        """, (pedido_id,))
        pedido_result = cursor.fetchone()

        if not pedido_result:
            flash("Pedido no encontrado.", "error")
            return redirect(url_for('admin_pedidos'))


        cursor.execute("""
            SELECT pr.id, pr.nombre, pr.descripcion, pr.precio, c.nombre AS categoria, pr.fecha_creacion, u.nombre AS proveedor,
                   dp.cantidad,
                   COALESCE(
                       (SELECT ip.ruta_imagen FROM imagenes_productos ip WHERE ip.producto_id = pr.id LIMIT 1),
                       'default.png'
                   ) AS imagen
            FROM detalles_pedidos dp
            JOIN productos pr ON dp.producto_id = pr.id
            JOIN usuarios u ON pr.proveedor_id = u.id
            JOIN categorias c ON pr.categoria_id = c.id
            WHERE dp.pedido_id = %s
        """, (pedido_id,))
        productos_result = cursor.fetchall()

        productos = [{"id": p[0], "nombre": p[1], "descripcion": p[2], "precio": p[3], "categoria": p[4], "fecha_creacion": p[5], "proveedor": p[6], "cantidad": p[7], "imagen": f"/static/imagenes/{p[8]}"} for p in productos_result]

        pedido = {
            "id": pedido_result[0],
            "cliente": pedido_result[1],
            "email": pedido_result[2],
            "total": pedido_result[3],
            "estado": pedido_result[4],
            "fecha": pedido_result[5],
            "productos": productos
        }

        cursor.close()
        conexion.close()

        return render_template('admin_detalle_pedido.html', pedido=pedido)

    except Exception as e:
        print("Error al obtener detalles del pedido:", e)
        flash("Error al cargar los detalles del pedido.", "error")
        return redirect(url_for('admin_pedidos'))