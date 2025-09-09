from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

actualizar_estados_bp = Blueprint('actualizar_estados', __name__)

@actualizar_estados_bp.route('/actualizar_estado/<string:tipo>/<int:item_id>', methods=['POST'])
@login_required
def actualizar_estado(tipo, item_id):
    nuevo_estado = request.form.get('estado')


    if not nuevo_estado:
        flash("No se proporcionó un estado válido.", "error")
        return redirect(url_for('notificaciones'))

    try:
        print(f"DEBUG: Recibido tipo={tipo}, item_id={item_id}, nuevo_estado='{nuevo_estado}'")


        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('notificaciones'))

        cursor = conexion.cursor()


        cursor.execute("SELECT id, estado FROM pedidos WHERE id = %s", (item_id,))
        pedido_actual = cursor.fetchone()

        if not pedido_actual:
            flash("El pedido no existe en la base de datos.", "error")
            return redirect(url_for('notificaciones'))

        if tipo == "pedido":
            if session.get('tipo_usuario') != "Proveedor":
                flash("Solo los proveedores pueden actualizar el estado del pedido.", "error")
                return redirect(url_for('menu'))

            cursor.execute("""
                UPDATE pedidos
                SET estado = %s
                WHERE id = %s
                RETURNING estado;
            """, (nuevo_estado, item_id))
            estado_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado actualizado en la BD: {estado_actualizado}")

        elif tipo == "notificacion":
            cursor.execute("""
                UPDATE notificaciones
                SET estado = %s
                WHERE id = %s
                RETURNING estado;
            """, (nuevo_estado, item_id))
            estado_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado de notificación actualizado en la BD: {estado_actualizado}")

        elif tipo == "producto":
            cursor.execute("""
                UPDATE productos
                SET estado = %s
                WHERE id = %s
                RETURNING estado;
            """, (nuevo_estado, item_id))
            estado_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado de producto actualizado en la BD: {estado_actualizado}")

            cursor.execute("""
                UPDATE detalles_pedidos
                SET estado_producto = %s
                WHERE producto_id = %s
                RETURNING estado_producto;
            """, (nuevo_estado, item_id))
            estado_producto_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado de detalles_pedidos actualizado en la BD: {estado_producto_actualizado}")

        print("DEBUG: Ejecutando commit en la base de datos...")
        conexion.commit()

        cursor.close()
        conexion.close()

        flash(f"Estado de {tipo} actualizado correctamente.", "success")

    except Exception as e:
        print(f"Error al actualizar el estado de {tipo}: {e}")
        flash("Error al actualizar el estado. Por favor, inténtalo de nuevo.", "error")

    if tipo == "pedido":
        return redirect(url_for('ver_proceso', producto_id=item_id))
    elif tipo == "notificacion":
        return redirect(url_for('notificaciones'))
    elif tipo == "producto":
        return redirect(url_for('ver_producto', producto_id=item_id))