from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

frutas_bp = Blueprint('frutas', __name__)

@frutas_bp.route('/frutas')
@login_required
def frutas():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()


            cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
            tipo_usuario = cursor.fetchone()
            if not tipo_usuario or tipo_usuario[0] != "Cliente":
                flash("Solo los clientes pueden acceder a esta página.", "error")
                return redirect(url_for('menu'))


            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                       u.nombre AS proveedor, ip.ruta_imagen
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                JOIN usuarios u ON p.proveedor_id = u.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                WHERE c.nombre = 'Frutas'
                ORDER BY p.fecha_creacion DESC
            """)
            productos = cursor.fetchall()


            productos_procesados = []
            for producto in productos:
                productos_procesados.append({
                    'id': producto[0],
                    'nombre': producto[1],
                    'descripcion': producto[2],
                    'precio': producto[3],
                    'categoria': producto[4],
                    'proveedor': producto[5],
                    'imagen': f"/static/{producto[6]}" if producto[6] else '/static/imagenes/default-product.jpg'
                })

            cursor.close()
            conexion.close()


            return render_template('frutas.html', productos=productos_procesados)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio'))
    except Exception as e:
        print(f"Error al cargar los productos de la categoría 'Frutas': {e}")
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('menu_clientes.menu_principal'))