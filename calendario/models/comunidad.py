from main import db

class Comunidad(db.Model):
    __tablename__ = "comunidads"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(300), nullable=True)
    localidades = db.relationship("Localidad", backref="comunidad", cascade="all, delete-orphan")
    festivocom = db.relationship('Festivocom', backref='comunidad', uselist=False)

    def __init__(self,id, nombre, descripcion) -> None:
            
            self.id = id
            self.nombre = nombre
            self.descripcion = descripcion
        
    def __repr__(self) -> str:
        return f'Localidad: {self.nombre}'