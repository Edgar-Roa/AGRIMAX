from flask import Flask, render_template
from flask_mail import Mail
from flask_login import LoginManager, UserMixin
import bcrypt
from models import Usuario
from extensions import mail, login_manager

app = Flask(__name__)

app.secret_key = 'clave_secreta_para_flash'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['UPLOAD_FOLDER'] = 'static/imagenes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'agrimaaxx@gmail.com'
app.config['MAIL_PASSWORD'] = 'ojho ayqo kqzd mbaf'


mail.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login.login"

@login_manager.user_loader
def load_user(user_id):
    from bd import conectar_bd
    conexion = conectar_bd()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, tipo FROM usuarios WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()
        if usuario:
            return Usuario(usuario[0], usuario[1], usuario[2])
    return None


from routes.inicio import inicio_bp
from routes.registro import registro_bp
from routes.login import login_bp
from routes.logout import logout_bp
from routes.admin_dashboard import admin_dashboard_bp
from routes.admin_usuarios import admin_usuarios_bp
from routes.admin_usuarios_eliminar import admin_usuarios_eliminar_bp
from routes.admin_editar_usuarios import admin_editar_usuarios_bp
from routes.admin_reportes import admin_reportes_bp
from routes.admin_productos import admin_productos_bp
from routes.admin_eliminar_productos import admin_eliminar_productos_bp
from routes.admin_editar_productos import admin_editar_productos_bp
from routes.admin_crear_usuarios import admin_crear_usuarios_bp
from routes.admin_pedidos import admin_pedidos_bp
from routes.admin_detalles_pedidos import admin_detalles_pedidos_bp
from routes.admin_eliminar_pedidos import admin_eliminar_pedidos_bp
from routes.usuarios import usuarios_bp
from routes.procesos_productos import procesos_productos_bp
from routes.actualizar_estados import actualizar_estados_bp
from routes.menu_clientes import menu_clientes_bp
from routes.menu_provedor import menu_provedor_bp
from routes.nuevo_producto import nuevo_producto_bp
from routes.configuracion import configuracion_bp
from routes.redes import redes_bp
from routes.agregar_carrito import agregar_carrito_bp
from routes.eliminar_del_carrito import eliminar_del_carrito_bp
from routes.carrito import carrito_bp
from routes.confirmar_pedidos import confirmar_pedidos_bp
from routes.notificaciones import notificaciones_bp
from routes.marcar_notificaciones import marcar_notificaciones_bp
from routes.graficas import graficas_bp
from routes.modificar_productos import modificar_productos_bp
from routes.eliminar_productos import eliminar_productos_bp
from routes.verduras import verduras_bp
from routes.frutas import frutas_bp
from routes.legumbres import legumbres_bp
from routes.hortalizas import hortalizas_bp

app.register_blueprint(inicio_bp)
app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(admin_dashboard_bp)
app.register_blueprint(admin_usuarios_bp)
app.register_blueprint(admin_usuarios_eliminar_bp)
app.register_blueprint(admin_editar_usuarios_bp)
app.register_blueprint(admin_reportes_bp)
app.register_blueprint(admin_productos_bp)
app.register_blueprint(admin_eliminar_productos_bp)
app.register_blueprint(admin_editar_productos_bp)
app.register_blueprint(admin_crear_usuarios_bp)
app.register_blueprint(admin_pedidos_bp)
app.register_blueprint(admin_detalles_pedidos_bp)
app.register_blueprint(admin_eliminar_pedidos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(procesos_productos_bp)
app.register_blueprint(actualizar_estados_bp)
app.register_blueprint(menu_clientes_bp)
app.register_blueprint(menu_provedor_bp)
app.register_blueprint(nuevo_producto_bp)
app.register_blueprint(configuracion_bp)
app.register_blueprint(redes_bp)
app.register_blueprint(agregar_carrito_bp)
app.register_blueprint(eliminar_del_carrito_bp)
app.register_blueprint(carrito_bp)
app.register_blueprint(confirmar_pedidos_bp)
app.register_blueprint(notificaciones_bp)
app.register_blueprint(marcar_notificaciones_bp)
app.register_blueprint(graficas_bp)
app.register_blueprint(modificar_productos_bp)
app.register_blueprint(eliminar_productos_bp)
app.register_blueprint(verduras_bp)
app.register_blueprint(frutas_bp)
app.register_blueprint(legumbres_bp)
app.register_blueprint(hortalizas_bp)

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True)