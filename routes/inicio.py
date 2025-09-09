from flask import Blueprint, render_template, request
from bd import conectar_bd

inicio_bp= Blueprint("inicio",__name__)

@inicio_bp.route("/")
def inicio():
    return render_template("inicio.html")



