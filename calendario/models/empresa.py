from main import db

class Empresa(db.Model):
    __tablename__ = "empresas"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nombre = db.Column(db.String(150), nullable=False)
    domicilio = db.Column(db.String(150), nullable=False)
    actividad = db.Column(db.String(150), nullable=False)
    convenio = db.Column(db.String(150), nullable=False)
    centro = db.Column(db.String(150), nullable=False)
    localidad_id = db.Column(db.Integer, db.ForeignKey('localidads.id'), nullable=False)
    #id_localidad = db.Column(db.Integer, db.ForeignKey('localidad.id'), nullable=False)

    def __init__(self, id, nombre, domicilio,actividad,convenio, centro, localidad_id) -> None:
            
            self.id = id
            self.nombre = nombre
            self.domicilio = domicilio
            self.actividad = actividad
            self.convenio = convenio
            self.centro = centro
            self.localidad_id = localidad_id
            
    def __repr__(self) -> str:
        return f'Empresa: {self.nombre}'