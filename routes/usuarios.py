from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/perfil/<int:usuario_id>')
@login_required
def perfil(usuario_id):
    try:

        if session.get('usuario_id') != usuario_id:
            flash("No tienes permiso para acceder a este perfil.", "error")
            return redirect(url_for('inicio'))


        conexion = conectar_bd()
        if not conexion:  
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio'))

        cursor = conexion.cursor()


        cursor.execute("""
            SELECT u.nombre, u.correo, u.tipo, COALESCE(p.foto, 'static/imagenes/default-profile.jpg') AS foto, 
                   COALESCE(p.biografia, 'Sin biografía') AS biografia
            FROM usuarios u
            LEFT JOIN perfiles p ON u.id = p.usuario_id
            WHERE u.id = %s
        """, (usuario_id,))
        perfil_resultado = cursor.fetchone()

        if not perfil_resultado:
            flash("El perfil no existe.", "error")
            return redirect(url_for('inicio'))


        columnas_perfil = [desc[0] for desc in cursor.description]
        perfil = dict(zip(columnas_perfil, perfil_resultado))


        cursor.execute("""
            SELECT p.nombre AS producto, dp.cantidad, dp.precio_unitario, 
                   dp.cantidad * dp.precio_unitario AS subtotal, ped.fecha, 
                   COALESCE(ped.estado, 'Pendiente') AS estado, 
                   COALESCE(ip.ruta_imagen, 'static/imagenes/default-product.jpg') AS ruta_imagen, 
                   u.nombre AS proveedor, p.id AS producto_id
            FROM detalles_pedidos dp
            JOIN pedidos ped ON dp.pedido_id = ped.id
            JOIN productos p ON dp.producto_id = p.id
            LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
            JOIN usuarios u ON p.proveedor_id = u.id
            WHERE ped.cliente_id = %s
            ORDER BY ped.fecha DESC;
        """, (usuario_id,))
        compras_resultado = cursor.fetchall()

        columnas_compras = [desc[0] for desc in cursor.description]
        compras = [dict(zip(columnas_compras, compra)) for compra in compras_resultado]  
        for compra in compras:
            print(f"DEBUG: Producto {compra['producto']} → Estado en perfil: {compra['estado']}")

    except Exception as e:
        print("Error al cargar el perfil:", e)
        flash("Error al cargar el perfil. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('inicio'))

    finally:
        cursor.close()
        conexion.close()


    if perfil['tipo'] == "Proveedor":
        return render_template('perfil.html', perfil=perfil)
    elif perfil['tipo'] == "Cliente":
        return render_template('perfil_clientes.html', perfil=perfil, compras=compras)
    else:
        flash("Tipo de usuario desconocido.", "error")
        return redirect(url_for('inicio'))