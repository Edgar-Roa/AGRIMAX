from functools import wraps
from flask import Flask, render_template, request,redirect, url_for, flash
from bd import conectar_bd 
import bcrypt
from flask import session
from flask import jsonify
import os
from werkzeug.utils import secure_filename
from flask import make_response
from flask_mail import Mail, Message
app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash' 
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_COOKIE_SECURE'] = True   
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
app.config['UPLOAD_FOLDER'] = 'static/imagenes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'agrimaaxx@gmail.com'
app.config['MAIL_PASSWORD'] = 'ktyn rgqi emxw swjr'  

mail = Mail(app)

def enviar_correo(destinatario, asunto, plantilla, datos):
    mensaje = Message(asunto, sender='agrimaaxx@gmail.com', recipients=[destinatario])
    mensaje.html = render_template(plantilla, datos=datos)
    mail.send(mensaje)

def enviar_correo_pedido(destinatario, pedido_id, total, productos):
    try:
        mensaje = Message("Confirmación de Pedido", sender=app.config['MAIL_USERNAME'], recipients=[destinatario])
        mensaje.html = render_template('correo_pedido.html', datos={"pedido_id": pedido_id, "total": total, "productos": productos})

        mail.send(mensaje)
        print(f"Correo de pedido enviado a {destinatario}")
    except Exception as e:
        print("Error al enviar correo de pedido:", e)

def enviar_correo_registro(destinatario, nombre, tipo_usuario):
    try:
        if tipo_usuario == "Cliente":
            asunto = "¡Bienvenido a AGRIMAX!"
            plantilla = "correo_cliente.html"
        elif tipo_usuario == "Proveedor":
            asunto = "¡Bienvenido a AGRIMAX, proveedor!"
            plantilla = "correo_proveedor.html"
        else:
            return  

        mensaje = Message(asunto, sender=app.config['MAIL_USERNAME'], recipients=[destinatario])
        mensaje.html = render_template(plantilla, datos={"nombre": nombre})
        mail.send(mensaje)
        print(f"Correo de registro enviado a {destinatario}")
    except Exception as e:
        print("Error al enviar correo:", e)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def no_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return decorated_function

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            
            nombre = request.form.get('nombre')
            edad = request.form.get('edad')
            correo = request.form.get('correo')
            contraseña = request.form.get('contraseña')
            tipo = request.form.get('tipo')
            fecha_nacimiento = request.form.get('fecha_nacimiento', None)
            telefono = request.form.get('telefono', None)

            
            if not nombre or not edad or not correo or not contraseña or not tipo:
                flash("Todos los campos son obligatorios.", "error")
                return render_template('registro.html')

           
            hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

            
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()

                
                cursor.execute("""
                    INSERT INTO usuarios (nombre, correo, contraseña, tipo, edad, fecha_nacimiento, telefono)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (nombre, correo, hashed_password.decode('utf-8'), tipo, edad, fecha_nacimiento, telefono))

                usuario_id = cursor.fetchone()[0]

                
                cursor.execute("""
                    INSERT INTO perfiles (usuario_id, foto, biografia)
                    VALUES (%s, %s, %s)
                """, (usuario_id, '/static/imagenes/default.jpg', 'Biografía no configurada'))

                conexion.commit()
                cursor.close()
                conexion.close()

                print("Usuario y perfil registrados correctamente.")

                
                enviar_correo_registro(correo, nombre, tipo)

                flash("Usuario registrado correctamente. Se ha enviado un correo de bienvenida.", "success")
                return redirect(url_for('login'))
            else:
                flash("No se pudo conectar a la base de datos.", "error")
        except Exception as e:
            print("Error al registrar el usuario:", e)
            flash("Ocurrió un error al registrar el usuario. Intenta nuevamente.", "error")

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        try:
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT id, nombre, tipo, contraseña FROM usuarios WHERE correo = %s
                """, (correo,))
                usuario = cursor.fetchone()
                cursor.close()
                conexion.close()

                if usuario and bcrypt.checkpw(contraseña.encode('utf-8'), usuario[3].encode('utf-8')):
                    session['usuario_id'] = usuario[0]
                    session['tipo_usuario'] = usuario[2]

                    flash(f"Bienvenido, {usuario[1]}!", "success")

                    
                    if usuario[2] == "Administrador":
                        return redirect(url_for('admin_dashboard'))
                    elif usuario[2] == "Cliente":
                        return redirect(url_for('menu_principal'))
                    elif usuario[2] == "Proveedor":
                        return redirect(url_for('menu'))
                else:
                    flash("Correo o contraseña incorrectos.", "error")
                    return render_template('login.html')
            else:
                flash("Error al conectar con la base de datos.", "error")
                return render_template('login.html')
        except Exception as e:
            print("Error al iniciar sesión:", e)
            flash("Ocurrió un error al iniciar sesión. Intenta nuevamente.", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/admin/dashboard')
@login_required
@no_cache
def admin_dashboard():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))
    
    return render_template('admin_dashboard.html')

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, correo, tipo, fecha_nacimiento FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/eliminar_usuario/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    if request.method == 'POST':
        correo = request.form['correo']
        tipo = request.form['tipo']
        cursor.execute(
            "UPDATE usuarios SET correo=%s, tipo=%s WHERE id=%s", (correo, tipo, id)
        )
        conexion.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for('admin_usuarios'))

    cursor.execute("SELECT id, nombre, correo, tipo FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/admin/reportes')
@login_required
def admin_reportes():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    
    cursor.execute("""
        SELECT tipo, COUNT(*) FROM usuarios GROUP BY tipo
    """)
    usuarios_por_tipo = cursor.fetchall()

    
    cursor.execute("""
        SELECT DATE(fecha_registro), COUNT(*) FROM usuarios GROUP BY DATE(fecha_registro)
    """)
    registros_por_fecha = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('admin_reportes.html', usuarios_por_tipo=usuarios_por_tipo, registros_por_fecha=registros_por_fecha)

@app.route('/admin/productos')
@login_required
@no_cache
def admin_productos():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()


    cursor.execute("""
    SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, p.fecha_creacion, u.nombre AS proveedor,
           (SELECT ip.ruta_imagen FROM imagenes_productos ip WHERE ip.producto_id = p.id LIMIT 1) AS ruta_imagen
    FROM productos p
    JOIN usuarios u ON p.proveedor_id = u.id
    JOIN categorias c ON p.categoria_id = c.id
""")

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('admin_productos.html', productos=productos)

@app.route('/admin/eliminar_producto/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_producto_admin(producto_id):  
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    flash("Producto eliminado correctamente.", "success")
    return redirect(url_for('admin_productos'))

@app.route('/admin/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria_id = request.form['categoria_id']

        cursor.execute("""
            UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, categoria_id=%s WHERE id=%s
        """, (nombre, descripcion, precio, categoria_id, id))
        conexion.commit()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for('admin_productos'))

    cursor.execute("SELECT id, nombre, descripcion, precio, categoria_id FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('editar_producto.html', producto=producto)

@app.route('/admin/crear_usuario', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        tipo = request.form['tipo']
        contraseña_plana = request.form['contraseña']


        salt = bcrypt.gensalt()
        contraseña_hash = bcrypt.hashpw(contraseña_plana.encode('utf-8'), salt).decode('utf-8')

        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contraseña, tipo)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, contraseña_hash, tipo))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for('admin_usuarios'))

    return render_template('crear_usuario.html')

@app.route('/admin/pedidos')
@login_required
@no_cache
def admin_pedidos():
    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('admin_dashboard'))  

        cursor = conexion.cursor()


        cursor.execute("""
            SELECT p.id, u.nombre AS cliente, u.correo AS email, p.total, p.estado, p.fecha
            FROM pedidos p
            JOIN usuarios u ON p.cliente_id = u.id
            ORDER BY p.fecha DESC
        """)
        pedidos_result = cursor.fetchall()

        pedidos = []
        for pedido in pedidos_result:
            pedido_id = pedido[0]


            cursor.execute("""
                SELECT pr.nombre, dp.cantidad, dp.precio_unitario
                FROM detalles_pedidos dp
                JOIN productos pr ON dp.producto_id = pr.id
                WHERE dp.pedido_id = %s
            """, (pedido_id,))
            productos_result = cursor.fetchall()

            productos = [{"nombre": p[0], "cantidad": p[1], "precio": p[2]} for p in productos_result]

            pedidos.append({
                "id": pedido[0],
                "cliente": pedido[1],
                "email": pedido[2],
                "total": pedido[3],
                "estado": pedido[4],
                "fecha": pedido[5],
                "productos": productos
            })

        cursor.close()
        conexion.close()

        return render_template('admin_pedidos.html', pedidos=pedidos)

    except Exception as e:
        print("Error al obtener los pedidos:", e)
        flash("Error al cargar los pedidos.", "error")
        return redirect(url_for('admin_dashboard'))

    except Exception as e:
        print("Error al obtener los pedidos:", e)
        flash("Error al cargar los pedidos.", "error")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/pedido/<int:pedido_id>')
@login_required
@no_cache
def admin_detalle_pedido(pedido_id):
    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('admin_pedidos'))

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT p.id, u.nombre AS cliente, u.correo AS email, p.total, p.estado, p.fecha
            FROM pedidos p
            JOIN usuarios u ON p.cliente_id = u.id
            WHERE p.id = %s
        """, (pedido_id,))
        pedido_result = cursor.fetchone()

        if not pedido_result:
            flash("Pedido no encontrado.", "error")
            return redirect(url_for('admin_pedidos'))


        cursor.execute("""
            SELECT pr.id, pr.nombre, pr.descripcion, pr.precio, c.nombre AS categoria, pr.fecha_creacion, u.nombre AS proveedor,
                   dp.cantidad,
                   COALESCE(
                       (SELECT ip.ruta_imagen FROM imagenes_productos ip WHERE ip.producto_id = pr.id LIMIT 1),
                       'default.png'
                   ) AS imagen
            FROM detalles_pedidos dp
            JOIN productos pr ON dp.producto_id = pr.id
            JOIN usuarios u ON pr.proveedor_id = u.id
            JOIN categorias c ON pr.categoria_id = c.id
            WHERE dp.pedido_id = %s
        """, (pedido_id,))
        productos_result = cursor.fetchall()

        productos = [{"id": p[0], "nombre": p[1], "descripcion": p[2], "precio": p[3], "categoria": p[4], "fecha_creacion": p[5], "proveedor": p[6], "cantidad": p[7], "imagen": f"/static/imagenes/{p[8]}"} for p in productos_result]

        pedido = {
            "id": pedido_result[0],
            "cliente": pedido_result[1],
            "email": pedido_result[2],
            "total": pedido_result[3],
            "estado": pedido_result[4],
            "fecha": pedido_result[5],
            "productos": productos
        }

        cursor.close()
        conexion.close()

        return render_template('admin_detalle_pedido.html', pedido=pedido)

    except Exception as e:
        print("Error al obtener detalles del pedido:", e)
        flash("Error al cargar los detalles del pedido.", "error")
        return redirect(url_for('admin_pedidos'))

@app.route('/admin/eliminar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def eliminar_pedido(pedido_id):
    if session.get('tipo_usuario') != 'Administrador':
        flash("Acceso denegado", "error")
        return redirect(url_for('menu_principal'))

    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()


        cursor.execute("SELECT id FROM pedidos WHERE id = %s", (pedido_id,))
        pedido_existente = cursor.fetchone()

        if not pedido_existente:
            flash("El pedido no existe.", "error")
            return redirect(url_for('admin_pedidos'))


        cursor.execute("SELECT producto_id FROM detalles_pedidos WHERE pedido_id = %s", (pedido_id,))
        productos_asociados = cursor.fetchall()
        productos_ids = [producto[0] for producto in productos_asociados]

        if productos_ids:
            cursor.execute("DELETE FROM notificaciones WHERE producto_id IN %s", (tuple(productos_ids),))
            print(f"DEBUG: Notificaciones eliminadas para productos del pedido ID {pedido_id}")


        cursor.execute("DELETE FROM detalles_pedidos WHERE pedido_id = %s", (pedido_id,))
        print(f"DEBUG: Detalles eliminados para pedido ID {pedido_id}")


        cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
        print(f"DEBUG: Pedido eliminado correctamente ID {pedido_id}")

        conexion.commit()

        flash("Pedido y sus notificaciones eliminados correctamente.", "success")

    except Exception as e:
        print(f"Error al eliminar el pedido y notificaciones: {e}")
        flash("Error al eliminar el pedido y sus notificaciones.", "error")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(url_for('admin_pedidos'))

@app.route('/perfil/<int:usuario_id>')
@login_required
@no_cache
def perfil(usuario_id):
    try:

        if session.get('usuario_id') != usuario_id:
            flash("No tienes permiso para acceder a este perfil.", "error")
            return redirect(url_for('inicio'))


        conexion = conectar_bd()
        if not conexion:  
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio'))

        cursor = conexion.cursor()


        cursor.execute("""
            SELECT u.nombre, u.correo, u.tipo, COALESCE(p.foto, 'static/imagenes/default-profile.jpg') AS foto, 
                   COALESCE(p.biografia, 'Sin biografía') AS biografia
            FROM usuarios u
            LEFT JOIN perfiles p ON u.id = p.usuario_id
            WHERE u.id = %s
        """, (usuario_id,))
        perfil_resultado = cursor.fetchone()

        if not perfil_resultado:
            flash("El perfil no existe.", "error")
            return redirect(url_for('inicio'))


        columnas_perfil = [desc[0] for desc in cursor.description]
        perfil = dict(zip(columnas_perfil, perfil_resultado))


        cursor.execute("""
            SELECT p.nombre AS producto, dp.cantidad, dp.precio_unitario, 
                   dp.cantidad * dp.precio_unitario AS subtotal, ped.fecha, 
                   COALESCE(ped.estado, 'Pendiente') AS estado, 
                   COALESCE(ip.ruta_imagen, 'static/imagenes/default-product.jpg') AS ruta_imagen, 
                   u.nombre AS proveedor, p.id AS producto_id
            FROM detalles_pedidos dp
            JOIN pedidos ped ON dp.pedido_id = ped.id
            JOIN productos p ON dp.producto_id = p.id
            LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
            JOIN usuarios u ON p.proveedor_id = u.id
            WHERE ped.cliente_id = %s
            ORDER BY ped.fecha DESC;
        """, (usuario_id,))
        compras_resultado = cursor.fetchall()

        columnas_compras = [desc[0] for desc in cursor.description]
        compras = [dict(zip(columnas_compras, compra)) for compra in compras_resultado]  
        for compra in compras:
            print(f"DEBUG: Producto {compra['producto']} → Estado en perfil: {compra['estado']}")

    except Exception as e:
        print("Error al cargar el perfil:", e)
        flash("Error al cargar el perfil. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('inicio'))

    finally:
        cursor.close()
        conexion.close()


    if perfil['tipo'] == "Proveedor":
        return render_template('perfil.html', perfil=perfil)
    elif perfil['tipo'] == "Cliente":
        return render_template('perfil_clientes.html', perfil=perfil, compras=compras)
    else:
        flash("Tipo de usuario desconocido.", "error")
        return redirect(url_for('inicio'))

@app.route('/proceso/<int:producto_id>')
@login_required
@no_cache
def ver_proceso(producto_id):
    try:
        
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('perfil', usuario_id=session['usuario_id']))

        cursor = conexion.cursor()


        cursor.execute("""
            SELECT p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                   u.nombre AS proveedor, ip.ruta_imagen, dp.estado
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            JOIN usuarios u ON p.proveedor_id = u.id
            LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
            JOIN detalles_pedidos dp ON p.id = dp.producto_id
            WHERE p.id = %s
            FOR UPDATE;
        """, (producto_id,))
        producto = cursor.fetchone()

        cursor.close()
        conexion.close()

        if producto:
            return render_template('proceso_producto.html', producto=producto)
        else:
            flash("No se encontró información sobre el proceso del producto.", "error")
            return redirect(url_for('perfil', usuario_id=session['usuario_id']))

    except Exception as e:
        print(f"Error al cargar el proceso del producto: {e}")
        flash("Error al cargar el proceso del producto. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('perfil', usuario_id=session['usuario_id']))

@app.route('/actualizar_estado/<string:tipo>/<int:item_id>', methods=['POST'])
@login_required
def actualizar_estado(tipo, item_id):
    nuevo_estado = request.form.get('estado')


    if not nuevo_estado:
        flash("No se proporcionó un estado válido.", "error")
        return redirect(url_for('notificaciones'))

    try:
        print(f"DEBUG: Recibido tipo={tipo}, item_id={item_id}, nuevo_estado='{nuevo_estado}'")


        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('notificaciones'))

        cursor = conexion.cursor()


        cursor.execute("SELECT id, estado FROM pedidos WHERE id = %s", (item_id,))
        pedido_actual = cursor.fetchone()

        if not pedido_actual:
            flash("El pedido no existe en la base de datos.", "error")
            return redirect(url_for('notificaciones'))

        if tipo == "pedido":
            if session.get('tipo_usuario') != "Proveedor":
                flash("Solo los proveedores pueden actualizar el estado del pedido.", "error")
                return redirect(url_for('menu'))

            cursor.execute("""
                UPDATE pedidos
                SET estado = %s
                WHERE id = %s
                RETURNING estado;
            """, (nuevo_estado, item_id))
            estado_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado actualizado en la BD: {estado_actualizado}")

        elif tipo == "notificacion":
            cursor.execute("""
                UPDATE notificaciones
                SET estado = %s
                WHERE id = %s
                RETURNING estado;
            """, (nuevo_estado, item_id))
            estado_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado de notificación actualizado en la BD: {estado_actualizado}")

        elif tipo == "producto":
            cursor.execute("""
                UPDATE productos
                SET estado = %s
                WHERE id = %s
                RETURNING estado;
            """, (nuevo_estado, item_id))
            estado_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado de producto actualizado en la BD: {estado_actualizado}")

            cursor.execute("""
                UPDATE detalles_pedidos
                SET estado_producto = %s
                WHERE producto_id = %s
                RETURNING estado_producto;
            """, (nuevo_estado, item_id))
            estado_producto_actualizado = cursor.fetchone()
            print(f"DEBUG: Estado de detalles_pedidos actualizado en la BD: {estado_producto_actualizado}")

        print("DEBUG: Ejecutando commit en la base de datos...")
        conexion.commit()

        cursor.close()
        conexion.close()

        flash(f"Estado de {tipo} actualizado correctamente.", "success")

    except Exception as e:
        print(f"Error al actualizar el estado de {tipo}: {e}")
        flash("Error al actualizar el estado. Por favor, inténtalo de nuevo.", "error")

    if tipo == "pedido":
        return redirect(url_for('ver_proceso', producto_id=item_id))
    elif tipo == "notificacion":
        return redirect(url_for('notificaciones'))
    elif tipo == "producto":
        return redirect(url_for('ver_producto', producto_id=item_id))

@app.route('/menu_principal')
@login_required
@no_cache
def menu_principal():
    usuario_id = session['usuario_id']
    print(f"Usuario autenticado: {usuario_id}")

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            print("Conexión a la base de datos exitosa.")

            cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
            tipo_usuario = cursor.fetchone()
            print(f"Tipo de usuario: {tipo_usuario}")

            if not tipo_usuario or tipo_usuario[0] != "Cliente":
                flash("Solo los clientes pueden acceder a esta página.", "error")
                return redirect(url_for('menu'))

            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                       u.nombre AS proveedor, ip.ruta_imagen, u.id AS proveedor_id
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                JOIN usuarios u ON p.proveedor_id = u.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                ORDER BY p.fecha_creacion DESC
            """)
            productos = cursor.fetchall()
            print(f"Productos obtenidos: {productos}")

            cursor.close()
            conexion.close()

            return render_template('menu_cliente.html', productos=productos, usuario_id=usuario_id)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio'))
    except Exception as e:
        print(f"Error al cargar los productos: {e}")
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('inicio'))

@app.route('/menu')
@login_required
@no_cache
def menu():
    usuario_id = session.get('usuario_id') 
    if not usuario_id:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login'))

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, 
                       p.fecha_creacion, ip.ruta_imagen
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                WHERE p.proveedor_id = %s
                ORDER BY p.fecha_creacion DESC
            """, (usuario_id,))
            productos = cursor.fetchall()

            cursor.close()
            conexion.close()

            productos_procesados = []
            for producto in productos:
                productos_procesados.append({
                    'id': producto[0],
                    'nombre': producto[1],
                    'descripcion': producto[2],
                    'precio': producto[3],
                    'categoria': producto[4],
                    'fecha_creacion': producto[5],
                    'imagen': f"/static/{producto[6]}" if producto[6] else '/static/imagenes/default-product.jpg'
                })

            return render_template('menu_provedor.html', usuario_id=usuario_id, productos=productos_procesados)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('login'))
    except Exception as e:
        print("Error al cargar los productos del proveedor:", e)
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('login'))

@app.route('/nuevo', methods=['GET', 'POST'])
@login_required
@no_cache
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

@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
@no_cache
def configuracion():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
        tipo_usuario = cursor.fetchone()[0]

        if request.method == 'GET':
            cursor.execute("""
                SELECT u.id, u.nombre, u.correo, p.foto, p.biografia, p.notificaciones_email, p.notificaciones_sms
                FROM usuarios u
                LEFT JOIN perfiles p ON u.id = p.usuario_id
                WHERE u.id = %s
            """, (usuario_id,))
            usuario_data = cursor.fetchone()

            usuario = {
                'id': usuario_data[0],
                'nombre': usuario_data[1],
                'correo': usuario_data[2],
                'foto': usuario_data[3] if usuario_data[3] else 'imagenes/default-profile.jpg',
                'biografia': usuario_data[4] if usuario_data[4] else '',
                'notificaciones_email': usuario_data[5],
                'notificaciones_sms': usuario_data[6]
            }

            cursor.close()
            conexion.close()

            if tipo_usuario == "Cliente":
                return render_template('configuracion_clientes.html', usuario=usuario)
            elif tipo_usuario == "Proveedor":
                return render_template('configuracion.html', usuario=usuario)
            else:
                flash("Tipo de usuario desconocido.", "error")
                return redirect(url_for('inicio'))

        elif request.method == 'POST':
            seccion = request.form.get('seccion')

            if seccion == 'perfil':
                nombre = request.form.get('nombre')
                apellido = request.form.get('apellido', '')
                biografia = request.form.get('biografia', '')
                foto = request.files.get('foto')

                if foto and allowed_file(foto.filename):
                    filename = secure_filename(f"{usuario_id}_{foto.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    foto.save(filepath)

                    ruta_foto = f"imagenes/{filename}"
                    cursor.execute("""
                        UPDATE perfiles 
                        SET foto = %s, biografia = %s 
                        WHERE usuario_id = %s
                    """, (ruta_foto, biografia, usuario_id))
                else:
                    cursor.execute("""
                        UPDATE perfiles 
                        SET biografia = %s 
                        WHERE usuario_id = %s
                    """, (biografia, usuario_id))

                cursor.execute("""
                    UPDATE usuarios 
                    SET nombre = %s, apellido = %s 
                    WHERE id = %s
                """, (nombre, apellido, usuario_id))

            elif seccion == 'notificaciones':
                notificaciones_email = 'notificaciones_email' in request.form
                notificaciones_sms = 'notificaciones_sms' in request.form

                cursor.execute("""
                    UPDATE perfiles 
                    SET notificaciones_email = %s, notificaciones_sms = %s 
                    WHERE usuario_id = %s
                """, (notificaciones_email, notificaciones_sms, usuario_id))

            conexion.commit()
            cursor.close()
            conexion.close()

            flash("Configuración actualizada correctamente.", "success")
            return redirect(url_for('configuracion'))

    except Exception as e:
        print(f"Error al manejar la configuración: {e}")
        flash("Ocurrió un error al manejar la configuración.", "error")
        return redirect(url_for('inicio'))

@app.route('/redes')
def redes():
    return render_template('redes.html')

@app.route('/agregar_al_carrito', methods=['POST'])
@login_required
@no_cache
def agregar_al_carrito():
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT precio FROM productos WHERE id = %s", (producto_id,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not resultado:
            flash("Error: Producto no encontrado.", "error")
            return redirect(url_for('menu_principal'))

        precio_unitario = resultado[0]

        if precio_unitario is None:
            flash(f"Error: El producto con ID {producto_id} no tiene un precio válido.", "error")
            return redirect(url_for('menu_principal'))

        carrito = session.get('carrito', [])

        nuevo_producto = {
            'producto_id': int(producto_id), 
            'cantidad': cantidad, 
            'precio_unitario': float(precio_unitario)  
        }

        for producto in carrito:
            if producto['producto_id'] == nuevo_producto['producto_id'] and 'precio_unitario' not in producto:
                producto['precio_unitario'] = nuevo_producto['precio_unitario']

        carrito.append(nuevo_producto)
        session['carrito'] = carrito

        print("Carrito corregido después de validación:", session['carrito'])

        flash("Producto agregado al carrito.", "success")
        return redirect(url_for('menu_principal'))

    except Exception as e:
        print("Error al agregar al carrito:", e)
        flash("Error al agregar producto al carrito.", "error")
        return redirect(url_for('menu_principal'))

@app.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
@login_required
@no_cache
def eliminar_del_carrito(producto_id):
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for('login'))

    carrito = session.get('carrito', [])

    carrito = [item for item in carrito if 'producto_id' in item and int(item['producto_id']) != producto_id]
    session['carrito'] = carrito

    flash("Producto eliminado del carrito.", "success")
    return redirect(url_for('carrito'))

@app.route('/carrito')
@login_required
@no_cache
def carrito():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para ver tu carrito.", "error")
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    carrito = session.get('carrito', [])
    productos = []

    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()

            for item in carrito:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria, ip.ruta_imagen
                    FROM productos p
                    JOIN categorias c ON p.categoria_id = c.id
                    LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                    WHERE p.id = %s
                """, (item['producto_id'],))
                producto = cursor.fetchone()
                if producto:
                    productos.append({
                        'id': producto[0],
                        'nombre': producto[1],
                        'descripcion': producto[2],
                        'precio': producto[3],
                        'categoria': producto[4],
                        'imagen': producto[5],
                        'cantidad': item['cantidad'],
                        'subtotal': producto[3] * item['cantidad']
                    })

            cursor.close()
            conexion.close()

    except Exception as e:
        print("Error al cargar el carrito:", e)
        flash("Ocurrió un error al cargar el carrito.", "error")

    total = sum([p['subtotal'] for p in productos])
    return render_template('carrito.html', productos=productos, total=total, usuario_id=usuario_id)

@app.route('/confirmar_pedidos', methods=['GET', 'POST'])
@login_required
@no_cache
def confirmar_pedido():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para confirmar tu pedido.", "error")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return redirect(url_for('carrito'))

    cliente_id = session.get('usuario_id')
    carrito = session.get('carrito', [])

    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for('carrito'))

    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('carrito'))

        cursor = conexion.cursor()

        cursor.execute("SELECT correo FROM usuarios WHERE id = %s", (cliente_id,))
        resultado = cursor.fetchone()
        if not resultado:
            flash("Error: No se encontró el usuario en la base de datos.", "error")
            return redirect(url_for('carrito'))
        correo_cliente = resultado[0]


        total = 0
        productos_pedido = []
        for item in carrito:
            print("Producto en carrito:", item)
            producto_id = item.get('producto_id')

            if not producto_id:
                flash(f"Error: Falta el producto en el carrito.", "error")
                return redirect(url_for('carrito'))

            cursor.execute("SELECT nombre, precio, proveedor_id FROM productos WHERE id = %s", (producto_id,))
            resultado = cursor.fetchone()
            if resultado:
                nombre_producto = resultado[0]
                precio = resultado[1]
                proveedor_id = resultado[2]
                total += precio * item['cantidad']
                productos_pedido.append((nombre_producto, item['cantidad'], proveedor_id))
            else:
                flash(f"Error: Producto con ID {producto_id} no encontrado.", "error")
                return redirect(url_for('carrito'))

        cursor.execute("""
            INSERT INTO pedidos (cliente_id, total)
            VALUES (%s, %s) RETURNING id
        """, (cliente_id, total))
        pedido_id = cursor.fetchone()[0]
        print("Pedido ID generado:", pedido_id)

        conexion.commit()
        for item in productos_pedido:
            nombre_producto, cantidad, proveedor_id = item
            cursor.execute("""
                INSERT INTO detalles_pedidos (pedido_id, producto_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, producto_id, cantidad, precio))


            mensaje_notificacion = f"Nuevo pedido recibido: {cantidad} unidades de {nombre_producto}"
            cursor.execute("""
                INSERT INTO notificaciones (proveedor_id, cliente_id, producto_id, mensaje, estado, fecha)
                VALUES (%s, %s, %s, %s, 'Pendiente', NOW())
            """, (proveedor_id, cliente_id, producto_id, mensaje_notificacion))

        conexion.commit()
        cursor.close()
        conexion.close()


        enviar_correo_pedido(correo_cliente, pedido_id, total, productos_pedido)

        session.pop('carrito', None)

        flash("Pedido confirmado correctamente. Se ha enviado un correo de confirmación.", "success")

        return render_template('confirmacion_pedidos.html', pedido_id=pedido_id, total=total, productos_pedido=productos_pedido)

    except Exception as e:
        print("Error al confirmar el pedido:", e)
        flash("Ocurrió un error al confirmar el pedido. Intenta nuevamente.", "error")
        return redirect(url_for('carrito'))

@app.route('/notificaciones')
@login_required
@no_cache
def notificaciones():
    if session.get('tipo_usuario') != "Proveedor":
        flash("Solo los proveedores pueden acceder a las notificaciones.", "error")
        return redirect(url_for('menu'))

    proveedor_id = session.get('usuario_id')
    print("Proveedor ID en sesión:", proveedor_id)

    try:
        conexion = conectar_bd()
        if not conexion:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('menu'))

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT n.id, n.mensaje, n.leido, n.fecha, p.nombre AS producto, 
                   COALESCE(ip.ruta_imagen, 'static/imagenes/default-product.jpg') AS imagen, 
                   n.estado, u.nombre AS cliente
            FROM notificaciones n
            JOIN productos p ON n.producto_id = p.id
            LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
            JOIN usuarios u ON n.cliente_id = u.id
            WHERE n.proveedor_id = %s
            ORDER BY n.fecha DESC;
        """, (proveedor_id,))

        notificaciones = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        notificaciones_lista = []
        for fila in notificaciones:
            if len(fila) == len(columnas):
                notificaciones_lista.append(dict(zip(columnas, fila)))
            else:
                print(f"Error: Tamaño de fila {len(fila)} no coincide con columnas {len(columnas)}")

        print("DEBUG: Notificaciones procesadas correctamente:", notificaciones_lista)

        cursor.close()
        conexion.close()

        if not notificaciones_lista:
            flash("No tienes notificaciones en este momento.", "info")
            return redirect(url_for('menu'))

        return render_template('notificaciones.html', notificaciones=notificaciones_lista)

    except Exception as e:
        print("Error al cargar las notificaciones:", e)
        flash("Error al cargar las notificaciones. Por favor, inténtalo de nuevo.", "error")
        return redirect(url_for('menu'))

@app.route('/marcar_leido/<int:notificacion_id>', methods=['POST'])
@login_required
def marcar_leido(notificacion_id):
    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE notificaciones 
                SET leido = TRUE 
                WHERE id = %s
            """, (notificacion_id,))
            conexion.commit()
            cursor.close()
            conexion.close()
            flash("Notificación marcada como leída.", "success")
        else:
            flash("Error al conectar con la base de datos.", "error")
    except Exception as e:
        print("Error al marcar como leído:", e)
        flash("Ocurrió un error. Inténtalo de nuevo.", "error")

    return redirect(url_for('notificaciones'))

@app.route('/graficas_agri')
@login_required
@no_cache
def graficas_agri():
    if 'usuario_id' not in session:
        flash("No autenticado", "error")
        return redirect(url_for('inicio'))

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
        return redirect(url_for('inicio'))

@app.route('/modificar_productos/<int:producto_id>', methods=['GET', 'POST'])
@login_required
@no_cache
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
                return redirect(url_for('menu'))


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
                return redirect(url_for('menu'))
        except Exception as e:
            print(f"Error al cargar el producto: {e}")
            flash("Ocurrió un error al cargar el producto.", "error")
            return redirect(url_for('menu'))

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
            return redirect(url_for('menu'))
        except Exception as e:
            print(f"Error al modificar el producto: {e}")
            flash("Ocurrió un error al modificar el producto.", "error")
            return redirect(url_for('modificar_producto_individual', producto_id=producto_id))

@app.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
@login_required
@no_cache
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

@app.route('/verduras')
@login_required
@no_cache
def verduras():
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
                WHERE c.nombre = 'Verduras'
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


            return render_template('verduras.html', productos=productos_procesados)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio'))
    except Exception as e:
        print(f"Error al cargar los productos de la categoría 'Verduras': {e}")
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('inicio'))

@app.route('/frutas')
@login_required
@no_cache
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
        return redirect(url_for('inicio'))

@app.route('/legumbres')
@login_required
@no_cache
def legumbres():

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
                WHERE c.nombre = 'legumbres'
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


            return render_template('legumbres.html', productos=productos_procesados)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio'))
    except Exception as e:
        print(f"Error al cargar los productos de la categoría 'legumbres': {e}")
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('inicio'))

@app.route('/hortalizas')
@login_required
@no_cache
def hortalizas():
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


            cursor.execute
            ("""
                SELECT p.id, p.nombre, p.descripcion, p.precio, c.nombre AS categoria,
                    u.nombre AS proveedor, ip.ruta_imagen
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                JOIN usuarios u ON p.proveedor_id = u.id
                LEFT JOIN imagenes_productos ip ON p.id = ip.producto_id
                WHERE c.nombre = 'Hortalizas'
                ORDER BY p.fecha_creacion DESC""")
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

            return render_template('hortalizas.html', productos=productos_procesados)
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('inicio'))
    except Exception as e:
        print(f"Error al cargar los productos de la categoría 'Hortalizas': {e}")
        flash("Ocurrió un error al cargar los productos. Intenta nuevamente.", "error")
        return redirect(url_for('inicio'))

if __name__ == '__main__':
            app.run(debug=True)