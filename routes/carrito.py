from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

carrito_bp = Blueprint('carrito', __name__)

@carrito_bp.route('/carrito')
@login_required
def carrito():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para ver tu carrito.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    carrito = session.get('carrito', [])
    productos = []

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()

            for item in carrito:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, ip.ruta_imagen
                    FROM productos p
                    JOIN categorias c ON p.categoria_id = c.id
                    LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                    WHERE p.id = %s
                """, (item['producto_id'],))
                producto = cursor.fetchone()
                if producto:
                    productos.append({
                        'id': producto[0],
                        'nombre': producto[1],
                        'descripcion': producto[2],
                        'precio': producto[3],
                        'categoria': producto[4],
                        'imagen': producto[5],
                        'cantidad': item['cantidad'],
                        'subtotal': producto[3] * item['cantidad']
                    })

            cursor.close()
            conexion.close()

    except Exception as e:
        print("Error al cargar el carrito:", e)
        flash("Ocurrió un error al cargar el carrito.", "error")

    total = sum([p['subtotal'] for p in productos])
    return render_template('carrito.html', productos=productos, total=total, usuario_id=usuario_id)