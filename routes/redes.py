from flask import Blueprint, render_template,flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

redes_bp = Blueprint('redes', __name__)

@redes_bp.route('/redes')
def redes():
    return render_template('redes.html')