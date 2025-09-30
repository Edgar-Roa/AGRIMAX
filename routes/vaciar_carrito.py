# routes/vaciar_carrito.py

from flask import Blueprint, session, redirect, url_for, flash
from flask_login import login_required

vaciar_carrito_bp = Blueprint('vaciar_carrito', __name__)

@vaciar_carrito_bp.route('/vaciar_carrito', methods=['POST'])
@login_required
def vaciar_carrito():
    session['carrito'] = []
    session.modified = True
    flash("Carrito vaciado correctamente.", "success")
    return redirect(url_for('carrito.carrito'))