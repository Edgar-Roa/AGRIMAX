from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

graficas_bp = Blueprint('graficas', __name__)

@graficas_bp.route('/graficas_agri')
@login_required
def graficas_agri():
    if 'usuario_id' not in session:
        flash("No autenticado", "error")
        return redirect(url_for('inicio.inicio'))

    try:
        proveedor_id = session['usuario_id']


        conexion = conectar_bd()
        cursor = conexion.cursor()


        cursor.execute('''
            SELECT productos_vendidos, total_ingresos, pedidos_recibidos, ventas_esperadas
            FROM estadisticas_ventas
            WHERE proveedor_id = %s
        ''', (proveedor_id,))
        resultado = cursor.fetchone()

        if resultado:
            productos_vendidos, total_ingresos, pedidos_recibidos, ventas_esperadas = resultado
            try:
                porcentaje_ventas = int((productos_vendidos / ventas_esperadas) * 100) if ventas_esperadas else 0
            except ZeroDivisionError:
                porcentaje_ventas = 0
        else:
            productos_vendidos = total_ingresos = pedidos_recibidos = ventas_esperadas = 0
            porcentaje_ventas = 0

        cursor.close()
        conexion.close()


        return render_template(
            'graficas agri.html',
            porcentaje_ventas=porcentaje_ventas,
            alcance=pedidos_recibidos,
            ventas_esperadas=ventas_esperadas
        )

    except Exception as e:
        print("Error al cargar las estadísticas:", e)
        flash("Error al cargar las estadísticas. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('inicio.inicio'))