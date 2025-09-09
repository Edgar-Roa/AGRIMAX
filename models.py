from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, nombre, tipo):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        