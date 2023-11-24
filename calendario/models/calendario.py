
from main import db
from datetime import datetime, date, timedelta
from flask import current_app

class Calendario(db.Model):
    __tablename__ = "calendarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    fecha = db.Column(db.Date, nullable=False)
    ejercicio = db.Column(db.String(4), nullable=False)
    mes = db.Column(db.String(2), nullable=False)
    mes2 = db.Column(db.String(2), nullable=False)
    nombre_mes = db.Column(db.String(12), nullable=False)
    dia = db.Column(db.String(2), nullable=False)
    dia2 = db.Column(db.String(2), nullable=False)
    trimestre = db.Column(db.String(1), nullable=False)
    semana = db.Column(db.Integer, nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    festivocom = db.relationship('Festivocom', backref='calendariocom', lazy=False)
    festivoloc = db.relationship('Festivoloc', backref='calendarioloc', lazy=False)
    #asientos2 = db.relationship("Gasto", backref="user_gasto")

    def __init__(self, fecha, ejercicio,mes,mes2, nombre_mes,dia,dia2,trimestre,semana, weekday) -> None:
            
            fecha_referencia = date.fromisoformat(current_app.config['YEAR_ONE'] + "-01-01")
            
            self.id = (fecha - fecha_referencia).days +1
            self.fecha = fecha
            self.ejercicio = ejercicio
            self.mes = mes
            self.mes2 = mes2
            self.dia = dia
            self.dia2 = dia2
            self.trimestre = trimestre
            self.nombre_mes = nombre_mes
            self.semana = semana
            self.weekday = weekday
        
    def __repr__(self) -> str:
        return f'Calendarios: {self.fecha}'