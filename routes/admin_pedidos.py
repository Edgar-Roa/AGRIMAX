from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_pedidos_bp = Blueprint('admin_pedidos', __name__)

@admin_pedidos_bp.route('/admin/pedidos')
@login_required
def admin_pedidos():
    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('admin_dashboard'))  

        cursor = conexion.cursor()


        cursor.execute("""
            SELECT p.id, u.nombre AS cliente, u.correo AS email, p.total, p.estado, p.fecha
            FROM pedidos p
            JOIN usuarios u ON p.cliente_id = u.id
            ORDER BY p.fecha DESC
        """)
        pedidos_result = cursor.fetchall()

        pedidos = []
        for pedido in pedidos_result:
            pedido_id = pedido[0]


            cursor.execute("""
                SELECT pr.nombre, dp.cantidad, dp.precio_unitario
                FROM detalles_pedidos dp
                JOIN productos pr ON dp.producto_id = pr.id
                WHERE dp.pedido_id = %s
            """, (pedido_id,))
            productos_result = cursor.fetchall()

            productos = [{"nombre": p[0], "cantidad": p[1], "precio": p[2]} for p in productos_result]

            pedidos.append({
                "id": pedido[0],
                "cliente": pedido[1],
                "email": pedido[2],
                "total": pedido[3],
                "estado": pedido[4],
                "fecha": pedido[5],
                "productos": productos
            })

        cursor.close()
        conexion.close()

        return render_template('admin_pedidos.html', pedidos=pedidos)

    except Exception as e:
        print("Error al obtener los pedidos:", e)
        flash("Error al cargar los pedidos.", "error")
        return redirect(url_for('admin_dashboard'))

    except Exception as e:
        print("Error al obtener los pedidos:", e)
        flash("Error al cargar los pedidos.", "error")
        return redirect(url_for('admin_dashboard'))