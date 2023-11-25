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
from forms import fempresas
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

@calendario.route('/comunidad/<id>')
@login_required
def comunidad(id):
    localidades = Localidad.query.filter(Localidad.comunidad_id == id)
    comunidad = Comunidad.query.get(id)
    return render_template('calendario/comunidad.html',localidades = localidades, comunidad = comunidad)

@calendario.route('/empresa_cal/<empresa_id>')
@login_required
def empresa_cal(empresa_id):
    empresa = Empresa.query.get(empresa_id)
    loc = empresa.localidad_id
    com = empresa.localidad.comunidad_id
    festivoscom = Festivocom.query.filter(Festivocom.comunidad_id == com)
    festivosloc = Festivoloc.query.filter(Festivoloc.localidad_id == loc)
    datos = [get_calendar(1,2024,loc,com),get_calendar(2,2024,loc,com),get_calendar(3,2024,loc,com),
             get_calendar(4,2024,loc,com),get_calendar(5,2024,loc,com),get_calendar(6,2024,loc,com),
             get_calendar(7,2024,loc,com),get_calendar(8,2024,loc,com),get_calendar(9,2024,loc,com),
             get_calendar(10,2024,loc,com),get_calendar(11,2024,loc,com),get_calendar(12,2024,loc,com)]
    return render_template('calendario/empresa_cal.html',empresa = empresa,datos=datos,festivoscom=festivoscom,festivosloc=festivosloc)

@calendario.route('/comunidad')
@login_required
def comunidades():
    localidades = Localidad.query.order_by(Localidad.id).all()
    return render_template('calendario/comunidades.html',localidades = localidades)


@calendario.route('/empresa/<id>')
@login_required
def empresa(id):
    empresas = Empresa.query.filter(Empresa.localidad.has(Localidad.comunidad_id == id))
    comunidad = Comunidad.query.get(id)
    return render_template('calendario/empresa.html',empresas = empresas, comunidad = comunidad)

@calendario.route('/empresas')
def empresas():
    #return "Enlace correcto"
    empresas = Empresa.query.all()

    return render_template('calendario/empresas.html',empresas=empresas)

@calendario.route('/festcom/')
@login_required
def festcom():
    festivoscomunitarios = Festivocom.query.all()
    if festivoscomunitarios:
        meses = ('enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre')
        cal = {'enero':get_calendar(1,2024,11,10),'febrero':get_calendar(2,2024,11,10),'marzo':get_calendar(3,2024,11,10),
            'abril':get_calendar(4,2024,11,10),'mayo':get_calendar(5,2024,11,10),'junio':get_calendar(6,2024,11,10),
            'julio':get_calendar(7,2024,11,10),'agosto':get_calendar(8,2024,11,10),'septiembre':get_calendar(9,2024,11,10),
            'octubre':get_calendar(10,2024,11,10),'noviembre':get_calendar(11,2024,11,10),'diciembre':get_calendar(12,2024,11,10)}
        #print(cal['febrero'])
    else:
        festivoscomunitarios, meses, cal = '','',''
    return render_template('calendario/festcom.html',festivoscomunitarios = festivoscomunitarios,meses=meses,cal = cal)

# Lista de días festivos por localidades
@calendario.route('/festloc')
@login_required
def festloc():
    festivoslocales = Festivoloc.query.all()
    if festivoslocales:
        meses = ('enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre')
        cal = {'enero':get_calendar(1,2024,11,10),'febrero':get_calendar(2,2024,11,10),'marzo':get_calendar(3,2024,11,10),
            'abril':get_calendar(4,2024,11,10),'mayo':get_calendar(5,2024,11,10),'junio':get_calendar(6,2024,11,10),
            'julio':get_calendar(7,2024,11,10),'agosto':get_calendar(8,2024,11,10),'septiembre':get_calendar(9,2024,11,10),
            'octubre':get_calendar(10,2024,11,10),'noviembre':get_calendar(11,2024,11,10),'diciembre':get_calendar(12,2024,11,10)}
    else:
        festivoslocales, meses, cal = '','',''
    return render_template('calendario/festloc.html',festivoslocales = festivoslocales,meses=meses,cal = cal)


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

def resumen_excel():
    data = 'calendario/static/excel/calendario.xlsx'
    ruta = 'calendario/static/excel'
    fichero = 'calendario.xlsx'

    ruta_archivo = os.path.join(app.root_path, ruta, fichero)

    if os.path.exists(ruta_archivo):

        empresas = pd.read_excel(data,sheet_name="Empresas", names=['Empresa','Domicilio','Actividad','Convenio','Centro','Localidad'])
        empresas[['localidad_id', 'localidad']] = empresas['Localidad'].str.split('-', expand=True)
        empresas = empresas.fillna('')
        emp = len(empresas)

        localidades = pd.read_excel(data,sheet_name="Localidades")
        localidades.columns = ['id','localidad','cod_localidad','cod_comunidad','descripcion']
        localidades[['comunidad_id', 'comunidad']] = localidades['cod_comunidad'].str.split('-', expand=True)
        localidades = localidades.fillna('')
        loc = len(localidades)
        
        fesloc = pd.read_excel(data,sheet_name="Festivos_Localidades")
        fesloc.columns = ['id','fecha','nombre','descripcion','id_localidad']
        fesloc[['localidad_id', 'localidad']] = fesloc['id_localidad'].str.split('-', expand=True)
        fesloc = fesloc.fillna('')
        floc = len(fesloc)

        fescom = pd.read_excel(data,sheet_name="Festivos_Comunidades")
        fescom.columns = ['id','fecha','nombre','descripcion','id_comunidad']
        fescom[['comunidad_id', 'comunidad']] = fescom['id_comunidad'].str.split('-', expand=True)
        fescom = fescom.fillna('')
        fcom = len(fescom)

        resumen = {'fcom':fcom,'floc':floc,'loc':loc,'emp':emp}
    else: 
        resumen = {'fcom':0,'floc':0,'loc':0,'emp':0}
    return resumen

@calendario.route('/datos/',methods = ['GET','POST'])
def datos():
    if request.method == 'POST':
        fichero = request.files['fichero']
        if fichero:
            form = fempresas()
            
            # Hacer algo con el archivo, por ejemplo, guardarlo en el servidor
            filepath = os.path.abspath('calendario/static/excel/calendario.xlsx')
            fichero.save(filepath)

            resumen = resumen_excel()
            return render_template('calendario/datosform.html',form=form, resumen = resumen)
            
        else:
            ticket = ''
            return "Metodo POST"
    elif request.method == 'GET':
        form = fempresas()

        resumen = resumen_excel()

        return render_template('calendario/datosform.html',form=form,resumen=resumen)

@calendario.route('/datos_import')
def datos_import():
    db.session.query(Empresa).delete()
    db.session.query(Festivoloc).delete()
    db.session.query(Festivocom).delete()
    db.session.query(Localidad).delete()
    db.session.query(Comunidad).delete()
    
    db.session.commit()

    data = 'calendario/static/excel/calendario.xlsx'

    comunidades = pd.read_excel(data,sheet_name="Comunidades")
    comunidades.columns = ['id','comunidad','descripcion','comunidad_id']
    comunidades = comunidades.fillna('')

    for index, row in comunidades.iterrows():
        comunidades = Comunidad(id=row['id'], nombre=row['comunidad'],descripcion=row['descripcion'])
        db.session.add(comunidades)
    db.session.commit()

    localidades = pd.read_excel(data,sheet_name="Localidades")
    localidades.columns = ['id','localidad','cod_localidad','cod_comunidad','descripcion']
    localidades[['comunidad_id', 'comunidad']] = localidades['cod_comunidad'].str.split('-', expand=True)
    localidades = localidades.fillna('')

    for index, row in localidades.iterrows():
        localidades = Localidad(id=row['id'], nombre=row['localidad'],comunidad_id=row['comunidad_id'], descripcion=row['descripcion'])
        db.session.add(localidades)
    db.session.commit()

    fescom = pd.read_excel(data,sheet_name="Festivos_Comunidades")
    fescom.columns = ['id','fecha','nombre','descripcion','id_comunidad']
    fescom[['comunidad_id', 'comunidad']] = fescom['id_comunidad'].str.split('-', expand=True)
    fescom = fescom.fillna('')

    for index, row in fescom.iterrows():
        fescom = Festivocom(fecha = row['fecha'],nombre = row['nombre'],descripcion=row['descripcion'],comunidad_id=row['comunidad_id'])
        db.session.add(fescom)
    db.session.commit()

    fesloc = pd.read_excel(data,sheet_name="Festivos_Localidades")
    fesloc.columns = ['id','fecha','nombre','descripcion','id_localidad']
    fesloc[['localidad_id', 'localidad']] = fesloc['id_localidad'].str.split('-', expand=True)
    fesloc = fesloc.fillna('')

    for index, row in fesloc.iterrows():
        fesloc = Festivoloc(fecha = row['fecha'],nombre = row['nombre'],descripcion=row['descripcion'],localidad_id=row['localidad_id'])
        db.session.add(fesloc)
    db.session.commit()

    empresas = pd.read_excel(data,sheet_name="Empresas", names=['id','Empresa','Domicilio','Actividad','Convenio','Centro','Localidad'])
    empresas[['localidad_id', 'localidad']] = empresas['Localidad'].str.split('-', expand=True)
    empresas = empresas.fillna('')
    
    for index, row in empresas.iterrows():
        empresa = Empresa(id=row['id'], nombre=row['Empresa'], domicilio=row['Domicilio'],actividad=row['Actividad'], convenio=row['Convenio'], centro=row['Centro'], localidad_id=row['localidad_id'])
        db.session.add(empresa)
    db.session.commit()
        
    return redirect(url_for('calendario.inicio'))

@calendario.route('/reset/')
@login_required
def reset():
    db.session.query(Localidad).delete()
    db.session.query(Festivocom).delete()
    db.session.query(Festivoloc).delete()
    db.session.query(Empresa).delete()
    db.session.query(Comunidad).delete()
    db.session.commit()

    return redirect(url_for('calendario.inicio'))
    

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


def get_calendar(mes, ano,localidad, comunidad):
    day_one = Calendario.query.filter(Calendario.mes2 == mes).filter(Calendario.ejercicio == ano).filter(Calendario.dia2 == '1').first()
    days = Calendario.query.filter(Calendario.mes2 == mes).filter(Calendario.ejercicio == ano).order_by(Calendario.fecha).all()
   
   # Otra opcion de consulta para revisar,left join
    resultado2 = db.session.query(Calendario, Festivocom).join(
    Festivocom, and_(Festivocom.calendario_id == Calendario.id, Festivocom.comunidad_id == comunidad), 
    isouter=True).join(
    Festivoloc, and_(Festivoloc.calendario_id == Calendario.id, Festivoloc.localidad_id == localidad),
    isouter=True).filter(Calendario.mes2 == str(mes)).all()

    # Otra opcion de consulta para revisar,left join
    resultado = db.session.query(
        Calendario.id,
        Calendario.fecha,
        Calendario.dia,
        Calendario.weekday,
        Calendario.nombre_mes,
        Festivocom.nombre.label('festivocom_nombre'),
        Festivocom.comunidad_id,
        Festivocom.descripcion,
        Festivoloc.nombre.label('festivoloc_nombre')
    ).outerjoin(Festivocom, (Calendario.id == Festivocom.calendario_id) & (Festivocom.comunidad_id == comunidad)).outerjoin(Festivoloc, (Calendario.id == Festivoloc.calendario_id) & (Festivoloc.localidad_id == localidad)).filter(Calendario.mes2.like(str(mes))).all()


    day_one_weekday = day_one.weekday
    # CUIDADO, si añadimos filas y faltan valores que despues imprimimos dara error
    #for d in range(day_one_weekday):
        
    # Supongamos que 'resultado' es una fila que proviene de una consulta
    fechita=date.fromisoformat(str(day_one.fecha))
    for d in range(day_one_weekday):
        dia_cero = Calendario(fecha=fechita - timedelta(days=d+1), ejercicio='2024', mes='2',mes2='02',nombre_mes='',dia='',dia2='',trimestre='',semana=1,weekday=1)
        days = [dia_cero] + days
        #days.add(comunidad)
        #resultado = {'fecha':'1900-01-01','id':'0','dia':'','dia2':'','festivocom': {'nombre': '','descripcion': ''},'festivoloc': {'nombre': '','descripcion': '' } }

        # Añadir la fila completa al principio de la lista
        #days.insert(0, resultado)
    fila_manual = (0,None,None,None,None,None)

    for d in range(day_one_weekday):
        resultado.insert(0, fila_manual)  

    year = ano
    month = mes
    #month_name = calendar.month_name[month]
    #days = calendar.monthcalendar(year, month)
    #lencal = len(days)

    #print(day_one.dia)
    #print(days)
    
    datos = {
        'year' : year,
        'month' : month,
        'day_one_weekday' : day_one_weekday,
        'days' : days,
        'days_name' : ['L','M','X','J','V','S','D'],
        'day_one' : day_one,
        'localidad' : localidad,
        'comunidad' : comunidad,
        'resultado' : resultado
    }
    #print("localidad: ")
    #print(localidad)
    #print("comunidad: ")
    #print(comunidad)
    return datos
