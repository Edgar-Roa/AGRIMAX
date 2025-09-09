from flask import render_template, current_app
from flask_mail import Message
from extensions import mail


def enviar_correo(destinatario, asunto, plantilla, datos):
    try:
        mensaje = Message(
            asunto,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[destinatario]
        )
        mensaje.html = render_template(plantilla, datos=datos)
        mail.send(mensaje)
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print("Error al enviar correo:", e)


def enviar_correo_pedido(destinatario, pedido_id, total, productos):
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
