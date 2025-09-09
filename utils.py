from functools import wraps
from flask import session, redirect, url_for, flash, make_response, render_template, current_app
from flask_mail import Message

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for('login.login'))  # Cambia si tu endpoint es diferente
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

def enviar_correo(destinatario, asunto, plantilla, datos, mail):
    mensaje = Message(asunto, sender=current_app.config['MAIL_USERNAME'], recipients=[destinatario])
    mensaje.html = render_template(plantilla, datos=datos)
    mail.send(mensaje)

def enviar_correo_pedido(destinatario, pedido_id, total, productos, mail):
    try:
        mensaje = Message(
            "Confirmación de Pedido",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[destinatario]
        )
        mensaje.html = render_template(
            'correo_pedido.html',
            datos={"pedido_id": pedido_id, "total": total, "productos": productos}
        )
        mail.send(mensaje)
        print(f"Correo de pedido enviado a {destinatario}")
    except Exception as e:
        print("Error al enviar correo de pedido:", e)

def enviar_correo_registro(destinatario, nombre, tipo_usuario, mail):
    try:
        if tipo_usuario == "Cliente":
            asunto = "¡Bienvenido a AGRIMAX!"
            plantilla = "correo_cliente.html"
        elif tipo_usuario == "Proveedor":
            asunto = "¡Bienvenido a AGRIMAX, proveedor!"
            plantilla = "correo_proveedor.html"
        else:
            return

        mensaje = Message(
            asunto,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[destinatario]
        )
        mensaje.html = render_template(plantilla, datos={"nombre": nombre})
        mail.send(mensaje)
        print(f"Correo de registro enviado a {destinatario}")
    except Exception as e:
        print("Error al enviar correo:", e)