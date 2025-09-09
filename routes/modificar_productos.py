from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

modificar_productos_bp = Blueprint('modificar_productos', __name__)

@modificar_productos_bp.route('/modificar_productos/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def modificar_producto_individual(producto_id):
    if 'usuario_id' not in session: 
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    conexion = conectar_bd()

    if request.method == 'GET':
        try:
            cursor = conexion.cursor()


            cursor.execute("SELECT proveedor_id FROM productos WHERE id = %s", (producto_id,))
            resultado = cursor.fetchone()

            if not resultado or resultado[0] != usuario_id:
                flash("No tienes permiso para modificar este producto.", "error")
                return redirect(url_for('menu_provedor.menu'))


            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, p.categoria_id, ip.ruta_imagen
                FROM productos p
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                WHERE p.id = %s
            """, (producto_id,))
            producto = cursor.fetchone()

            cursor.execute("SELECT id, nombre FROM categorias")
            categorias = cursor.fetchall()

            cursor.close()
            conexion.close()

            if producto:
                producto = {
                    'id': producto[0],
                    'nombre': producto[1],
                    'descripcion': producto[2],
                    'precio': producto[3],
                    'categoria_id': producto[4],
                    'foto': producto[5] if producto[5] else 'imagenes/default-product.jpg'
                }

                return render_template('modificar_productos.html', producto=producto, categorias=categorias)
            else:
                flash("Producto no encontrado.", "error")
                return redirect(url_for('menu_provedor.menu'))
        except Exception as e:
            print(f"Error al cargar el producto: {e}")
            flash("Ocurrió un error al cargar el producto.", "error")
            return redirect(url_for('menu_provedor.menu'))

    elif request.method == 'POST':
        try:
            cursor = conexion.cursor()


            nombre = request.form['nombre']
            descripcion = request.form.get('descripcion', '')
            precio = request.form['precio']
            categoria_id = request.form['categoria_id']
            imagen = request.files.get('imagen')


            cursor.execute("""
                UPDATE productos
                SET nombre = %s, descripcion = %s, precio = %s, categoria_id = %s
                WHERE id = %s
            """, (nombre, descripcion, precio, categoria_id, producto_id))


            if imagen and allowed_file(imagen.filename):

                filename = secure_filename(f"{producto_id}_{imagen.filename}")
                ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(ruta)


                cursor.execute("""
                    INSERT INTO imagenes_productos (producto_id, ruta_imagen)
                    VALUES (%s, %s)
                    ON CONFLICT (producto_id) DO UPDATE
                    SET ruta_imagen = EXCLUDED.ruta_imagen
                """, (producto_id, f"imagenes/{filename}"))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash("Producto modificado correctamente.", "success")
            return redirect(url_for('menu_provedor.menu'))
        except Exception as e:
            print(f"Error al modificar el producto: {e}")
            flash("Ocurrió un error al modificar el producto.", "error")
            return redirect(url_for('modificar_producto_individual', producto_id=producto_id))