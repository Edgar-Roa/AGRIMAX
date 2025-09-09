from flask import Blueprint, render_template, request, redirect, url_for, flash, session, request
from bd import conectar_bd

logout_bp = Blueprint("logout",__name__)

@logout_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for('login.login'))