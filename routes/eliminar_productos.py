from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

eliminar_productos_bp = Blueprint('eliminar_productos', __name__)

@eliminar_productos_bp.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_producto(producto_id):
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()


        cursor.execute("SELECT proveedor_id FROM productos WHERE id = %s", (producto_id,))
        resultado = cursor.fetchone()
        if not resultado or resultado[0] != usuario_id:
            flash("No tienes permiso para eliminar este producto.", "error")
            return redirect(url_for('menu'))


        cursor.execute("SELECT ruta_imagen FROM imagenes_productos WHERE producto_id = %s", (producto_id,))
        ruta_imagen = cursor.fetchone()
        if ruta_imagen:
            try:
                os.remove(os.path.join('static', ruta_imagen[0]))
            except Exception as e:
                print(f"Error al eliminar la imagen: {e}")


        cursor.execute("DELETE FROM imagenes_productos WHERE producto_id = %s", (producto_id,))
        cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Producto eliminado correctamente.", "success")
        return redirect(url_for('menu'))
    except Exception as e:
        print(f"Error al eliminar el producto: {e}")
        flash("Ocurrió un error al eliminar el producto.", "error")
        return redirect(url_for('menu'))