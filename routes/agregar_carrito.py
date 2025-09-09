from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

agregar_carrito_bp = Blueprint('agregar_carrito', __name__)


@agregar_carrito_bp.route('/agregar_al_carrito', methods=['POST'])
@login_required
def agregar_al_carrito():
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT precio FROM productos WHERE id = %s", (producto_id,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not resultado:
            flash("Error: Producto no encontrado.", "error")
            return redirect(url_for('menu_principal'))

        precio_unitario = resultado[0]

        if precio_unitario is None:
            flash(f"Error: El producto con ID {producto_id} no tiene un precio válido.", "error")
            return redirect(url_for('menu_principal'))

        carrito = session.get('carrito', [])

        nuevo_producto = {
            'producto_id': int(producto_id), 
            'cantidad': cantidad, 
            'precio_unitario': float(precio_unitario)  
        }

        for producto in carrito:
            if producto['producto_id'] == nuevo_producto['producto_id'] and 'precio_unitario' not in producto:
                producto['precio_unitario'] = nuevo_producto['precio_unitario']

        carrito.append(nuevo_producto)
        session['carrito'] = carrito

        print("Carrito corregido después de validación:", session['carrito'])

        flash("Producto agregado al carrito.", "success")
        return redirect(url_for('menu_principal'))

    except Exception as e:
        print("Error al agregar al carrito:", e)
        flash("Error al agregar producto al carrito.", "error")
        return redirect(url_for('menu_principal'))