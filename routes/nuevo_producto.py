from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

nuevo_producto_bp = Blueprint('nuevo_producto', __name__)

@nuevo_producto_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para subir productos.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    conexion = conectar_bd()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
        tipo_usuario = cursor.fetchone()
        if tipo_usuario and tipo_usuario[0] != "Proveedor":
            flash("Solo los proveedores pueden subir productos.", "error")
            return redirect(url_for('menu'))
        cursor.close()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria_id = request.form['categoria']
        imagen = request.files.get('imagen')  

        if not nombre or not precio or not categoria_id:
            flash("El nombre, precio y categoría son obligatorios.", "error")
            return redirect(url_for('nuevo'))

        try:

            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO productos (nombre, descripcion, precio, categoria_id, proveedor_id)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (nombre, descripcion, precio, categoria_id, usuario_id))
            producto_id = cursor.fetchone()[0]

            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(f"{producto_id}_{imagen.filename}")
                ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(ruta)

                cursor.execute("""
                    INSERT INTO imagenes_productos (producto_id, ruta_imagen)
                    VALUES (%s, %s)
                """, (producto_id, f"imagenes/{filename}"))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash("Producto subido correctamente.", "success")
            return redirect(url_for('menu'))
        except Exception as e:
            print("Error al subir el producto:", e)
            flash("Ocurrió un error al subir el producto. Intenta nuevamente.", "error")
            return redirect(url_for('nuevo'))

    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template('nuevo.html', categorias=categorias)