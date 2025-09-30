from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

actualizar_cantidad_bp = Blueprint('actualizar_cantidad', __name__)


@actualizar_cantidad_bp.route('/actualizar_cantidad', methods=['POST'])
@login_required
def actualizar_cantidad():
    if request.is_json:
        data = request.get_json()
        producto_id = int(data['producto_id'])
        nueva_cantidad = int(data['nueva_cantidad'])

        carrito = session.get('carrito', [])
        nuevo_carrito = []

        for item in carrito:
            if item['producto_id'] == producto_id:
                if nueva_cantidad > 0:
                    item['cantidad'] = nueva_cantidad
                    nuevo_carrito.append(item)
                else:
                    flash("Producto eliminado del carrito.", "success")
            else:
                nuevo_carrito.append(item)

        session['carrito'] = nuevo_carrito
        session.modified = True

        return {'success': True}
    return {'success': False, 'message': 'Petición inválida'}, 400