from main import db
from datetime import datetime, date, timedelta
from flask import current_app


class Festivocom(db.Model):
    __tablename__ = "festivocoms"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(300), nullable=True)
    comunidad_id = db.Column(db.Integer, db.ForeignKey('comunidads.id'), nullable=False)
    calendario_id = db.Column(db.Integer, db.ForeignKey('calendarios.id'), nullable=False)
    

    def __init__(self, fecha, nombre, descripcion, comunidad_id) -> None:
            
            fecha_referencia = date.fromisoformat(current_app.config['YEAR_ONE'] + "-01-01")
            if isinstance(fecha, datetime):
                fecha = fecha.date()
            
            self.fecha = fecha
            self.nombre = nombre
            self.descripcion = descripcion
            self.comunidad_id = comunidad_id
            self.calendario_id = (fecha - fecha_referencia).days +1
            
    def __repr__(self) -> str:
        return f'Festivos Comunitarios: {self.nombre}'