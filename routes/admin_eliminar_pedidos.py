from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_eliminar_pedidos_bp = Blueprint('admin_eliminar_pedidos', __name__)

@admin_eliminar_pedidos_bp.route('/admin/eliminar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def eliminar_pedido(pedido_id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()


        cursor.execute("SELECT id FROM pedidos WHERE id = %s", (pedido_id,))
        pedido_existente = cursor.fetchone()

        if not pedido_existente:
            flash("El pedido no existe.", "error")
            return redirect(url_for('admin_pedidos'))


        cursor.execute("SELECT producto_id FROM detalles_pedidos WHERE pedido_id = %s", (pedido_id,))
        productos_asociados = cursor.fetchall()
        productos_ids = [producto[0] for producto in productos_asociados]

        if productos_ids:
            cursor.execute("DELETE FROM notificaciones WHERE producto_id IN %s", (tuple(productos_ids),))
            print(f"DEBUG: Notificaciones eliminadas para productos del pedido ID {pedido_id}")


        cursor.execute("DELETE FROM detalles_pedidos WHERE pedido_id = %s", (pedido_id,))
        print(f"DEBUG: Detalles eliminados para pedido ID {pedido_id}")


        cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
        print(f"DEBUG: Pedido eliminado correctamente ID {pedido_id}")

        conexion.commit()

        flash("Pedido y sus notificaciones eliminados correctamente.", "success")

    except Exception as e:
        print(f"Error al eliminar el pedido y notificaciones: {e}")
        flash("Error al eliminar el pedido y sus notificaciones.", "error")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(url_for('admin_pedidos.admin_pedidos'))