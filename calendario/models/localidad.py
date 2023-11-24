from main import db

class Localidad(db.Model):
    __tablename__ = "localidads"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nombre = db.Column(db.String(100), nullable=False)
    comunidad_id = db.Column(db.Integer, db.ForeignKey('comunidads.id'), nullable=False)
    descripcion = db.Column(db.String(300), nullable=True)
    festivoloc = db.relationship('Festivoloc', backref='localidad', uselist=True)
    empresa = db.relationship('Empresa', backref='localidad', uselist=True)

    def __init__(self,id, nombre,comunidad_id, descripcion) -> None:
            
            self.id = id
            self.nombre = nombre
            self.comunidad_id = comunidad_id
            self.descripcion = descripcion
            
    def __repr__(self) -> str:
        return f'Localidad: {self.nombre}'