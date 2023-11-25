from main import db
from datetime import datetime, date, timedelta
from flask import current_app

class Festivoloc(db.Model):
    __tablename__ = "festivolocs"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    nombre = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.String(300), nullable=True)
    localidad_id = db.Column(db.Integer, db.ForeignKey('localidads.id'), nullable=False)
    calendario_id = db.Column(db.Integer, db.ForeignKey('calendarios.id'), nullable=False)

    def __init__(self, fecha, nombre, descripcion, localidad_id) -> None:
            
            fecha_referencia = date.fromisoformat("2024-01-01")

            if isinstance(fecha, datetime):
                fecha = fecha.date()

            self.fecha = fecha
            self.nombre = nombre
            self.descripcion = descripcion
            self.localidad_id = localidad_id
            self.calendario_id = (fecha - fecha_referencia).days +1
            
    def __repr__(self) -> str:
        return f'Festivos locales: {self.nombre}'