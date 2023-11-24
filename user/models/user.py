from main import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=True)
    apellido = db.Column(db.String(50), nullable=True)
    mail = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(10), nullable=True)
    oficina = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    nivel = db.Column(db.String(15), nullable=False)
    #calculadoras = db.relationship("Calculadora", backref="user_calc")
    #asientos = db.relationship("Ruta", backref="user_ruta")
    #asientos2 = db.relationship("Gasto", backref="user_gasto")

    def __init__(self, username, password, nombre, apellido, mail, telefono, oficina, nivel) -> None:
        self.username = username
        self.password = password
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self.telefono = telefono
        self.oficina = oficina
        self.nivel = nivel
        
    def __repr__(self) -> str:
        return f'User: {self.username}'