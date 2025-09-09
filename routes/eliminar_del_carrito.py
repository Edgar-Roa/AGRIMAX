from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

eliminar_del_carrito_bp = Blueprint('eliminar_del_carrito', __name__)

@eliminar_del_carrito_bp.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_del_carrito(producto_id):
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for('login'))

    carrito = session.get('carrito', [])

    carrito = [item for item in carrito if 'producto_id' in item and int(item['producto_id']) != producto_id]
    session['carrito'] = carrito

    flash("Producto eliminado del carrito.", "success")
    return redirect(url_for('carrito'))