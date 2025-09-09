from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

confirmar_pedidos_bp = Blueprint('confirmar_pedidos', __name__)

@confirmar_pedidos_bp.route('/confirmar_pedidos', methods=['GET', 'POST'])
@login_required
def confirmar_pedido():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para confirmar tu pedido.", "error")
        return redirect(url_for('login.login'))

    if request.method == 'GET':
        return redirect(url_for('carrito.carrito'))

    cliente_id = session.get('usuario_id')
    carrito = session.get('carrito', [])

    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for('carrito.carrito'))

    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('carrito.carrito'))

        cursor = conexion.cursor()

        cursor.execute("SELECT correo FROM usuarios WHERE id = %s", (cliente_id,))
        resultado = cursor.fetchone()
        if not resultado:
            flash("Error: No se encontró el usuario en la base de datos.", "error")
            return redirect(url_for('carrito.carrito'))
        correo_cliente = resultado[0]


        total = 0
        productos_pedido = []
        for item in carrito:
            print("Producto en carrito:", item)
            producto_id = item.get('producto_id')

            if not producto_id:
                flash(f"Error: Falta el producto en el carrito.", "error")
                return redirect(url_for('carrito.carrito'))

            cursor.execute("SELECT nombre, precio, proveedor_id FROM productos WHERE id = %s", (producto_id,))
            resultado = cursor.fetchone()
            if resultado:
                nombre_producto = resultado[0]
                precio = resultado[1]
                proveedor_id = resultado[2]
                total += precio * item['cantidad']
                productos_pedido.append((nombre_producto, item['cantidad'], proveedor_id))
            else:
                flash(f"Error: Producto con ID {producto_id} no encontrado.", "error")
                return redirect(url_for('carrito.carrito'))

        cursor.execute("""
            INSERT INTO pedidos (cliente_id, total)
            VALUES (%s, %s) RETURNING id
        """, (cliente_id, total))
        pedido_id = cursor.fetchone()[0]
        print("Pedido ID generado:", pedido_id)

        conexion.commit()
        for item in productos_pedido:
            nombre_producto, cantidad, proveedor_id = item
            cursor.execute("""
                INSERT INTO detalles_pedidos (pedido_id, producto_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, producto_id, cantidad, precio))


            mensaje_notificacion = f"Nuevo pedido recibido: {cantidad} unidades de {nombre_producto}"
            cursor.execute("""
                INSERT INTO notificaciones (proveedor_id, cliente_id, producto_id, mensaje, estado, fecha)
                VALUES (%s, %s, %s, %s, 'Pendiente', NOW())
            """, (proveedor_id, cliente_id, producto_id, mensaje_notificacion))

        conexion.commit()
        cursor.close()
        conexion.close()


        enviar_correo_pedido(correo_cliente, pedido_id, total, productos_pedido)

        session.pop('carrito', None)

        flash("Pedido confirmado correctamente. Se ha enviado un correo de confirmación.", "success")

        return render_template('confirmacion_pedidos.html', pedido_id=pedido_id, total=total, productos_pedido=productos_pedido)

    except Exception as e:
        print("Error al confirmar el pedido:", e)
        flash("Ocurrió un error al confirmar el pedido. Intenta nuevamente.", "error")
        return redirect(url_for('carrito.carrito'))