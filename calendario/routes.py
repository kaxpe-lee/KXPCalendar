from flask import(render_template, Blueprint, flash, g, redirect, request, session,url_for,send_file,Response,make_response)
from werkzeug.utils import secure_filename
from dateutil import parser
from user.models.user import User
from calendario.models.empresa import Empresa
from calendario.models.calendario import Calendario
from calendario.models.comunidad import Comunidad
from calendario.models.localidad import Localidad
from calendario.models.festivocom import Festivocom
from calendario.models.festivoloc import Festivoloc
from sqlalchemy.orm import aliased

from sqlalchemy import text, func, and_ , or_

from reportlab.lib import colors
from fpdf import FPDF
from io import BytesIO

from user.routes import login_required
from datetime import date, timedelta, datetime
import calendar
from main import db, app
import os, json
import locale
import pandas as pd
#from forms import fempresas
from forms import fcalendario

calendario = Blueprint('calendario', __name__, template_folder='templates', url_prefix='/calendario')

lang_code =  'es'

@calendario.route('/calendarios')
def calendarios():
    return redirect(url_for('index'))

@calendario.route('/')
@login_required
def inicio():
    
    # Comprobamos si hay calendario
    calendario = Calendario.query.count()
    empresas = Empresa.query.count()
    comunidades = Comunidad.query.count()
    localidades = Localidad.query.count()
    festivocom = Festivocom.query.count()
    festivoloc = Festivoloc.query.count()

    form = fcalendario()

    if calendario > 0:
        datos = {'calendario' : calendario,'empresas':empresas,'comunidades':comunidades,'localidades':localidades,'festivocom':festivocom,'festivoloc':festivoloc}
    else:
        datos = {'calendario' : calendario,'empresas':empresas,'comunidades':comunidades,'localidades':localidades,'festivocom':festivocom,'festivoloc':festivoloc}

    return render_template('calendario/inicio.html',datos = datos,form=form)

@calendario.route('/dias/',methods = ['POST'])
@login_required
def dias():
    form = fcalendario()
    year = request.form['year']
    
    #locale.setlocale(locale.LC_TIME, 'es_ES')
    fecha_inicial = year + "-01-01"
    fecha_final = year + "-12-31"
    fecha_inicial_obj = date.fromisoformat(fecha_inicial)
    fecha_final_obj = date.fromisoformat(fecha_final)

    # Verifica que la fecha inicial sea anterior a la fecha final
    if fecha_inicial_obj > fecha_final_obj:
        return "Error: La fecha inicial debe ser anterior a la fecha final."

    # Genera una lista de todas las fechas correlativas dentro del rango especificado
    all_dates = []
    current_date = fecha_inicial_obj
    while current_date <= fecha_final_obj:
        fecha = str(current_date)
        fecha2 = parser.parse(fecha)  # Convierte la cadena de fecha a un objeto datetime
        weekday = fecha2.weekday()
        semana = fecha2.isocalendar()[1]
        ejercicio = fecha[0:4]
        mes = fecha[5:7]
        mes2 = str(current_date.month)
        nombre_mes = str(calendar.month_name[current_date.month])
        dia = fecha[8:]
        dia2 = str(current_date.day)
        if mes in ['01','02','03']:
            trimestre = "1"
        elif mes in ['04','05','06']:
            trimestre = '2'
        elif mes in ['07','08','09']:
            trimestre = '3'
        else:
            trimestre = '4'
        all_dates.append(Calendario(fecha=current_date, ejercicio=ejercicio, mes=mes,mes2=mes2,nombre_mes= nombre_mes, dia=dia, dia2=dia2, trimestre=trimestre, semana = semana, weekday = weekday))
        current_date += timedelta(days=1)

    # Inserta las fechas en la tabla de la base de datos
    db.session.bulk_save_objects(all_dates)
    db.session.commit()

    return f"Se generaron y almacenaron {len(all_dates)} días correlativos en la base de datos."


def leftside_queries():
    # Realiza tus consultas a la base de datos aquí
    lscomunidades = Comunidad.query.filter(Comunidad.localidades.any()).all()
    leftside = {
        'comuni': lscomunidades,
        'locali': ''
    }
    return leftside

@app.context_processor
def inject_leftside_queries():
    return dict(leftside_queries=leftside_queries())
