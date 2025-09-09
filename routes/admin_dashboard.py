from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/admin/dashboard')
@login_required

def admin_dashboard():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('inicio.inicio'))
    
    return render_template('admin_dashboard.html')