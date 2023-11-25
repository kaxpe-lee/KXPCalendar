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
    db.session.query(Empresa).delete()
    db.session.query(Festivoloc).delete()
    db.session.query(Festivocom).delete()
    db.session.query(Localidad).delete()
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

@calendario.route('/calendario_anual/<ejercicio>/<localidad_id>/<empresa>')
def calendario_anual(ejercicio,localidad_id,empresa):
    localidad = Localidad.query.get(localidad_id)
    print(localidad.nombre)
    empresa = Empresa.query.get(empresa)
    
    com = Festivocom.query.filter(Festivocom.comunidad_id == localidad.comunidad_id).order_by(Festivocom.fecha).all()
    loc = Festivoloc.query.filter(Festivoloc.localidad_id == localidad.id).order_by(Festivoloc.fecha).all()
    # Crear un objeto PDF con FPDF2
    pdf = PDF()
    
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.add_page()

    pdf.cab(empresa,localidad)
    # Definir los meses el 1 cuatrimestre
    
    x = 8
    y = 55
    largo = 46.125
    espacio = 2.5
    
    #pdf.add_month(x, y,get_calendar(1,2024,localidad, comunidad))

    mes = 1
    for c in range(1,4):
        for m in range(1,5):
            pdf.add_month(x, y,get_calendar(mes,2024,localidad.id,localidad.comunidad_id))
            x = x + largo + espacio
            mes += 1
        x = 8
        y += 48
        



    pdf.pie(com,loc,localidad)
    # Guardar el PDF en un buffer
    buffer = BytesIO()
    pdf.output(buffer)

    # Crear una respuesta Flask y establecer el contenido del PDF
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=calendario_anual.pdf'

    return response


class PDF(FPDF):
    def header(self):
        pass
        
    def cab(self,empresa,localidad):
        localidad = localidad
        empresa = empresa
        self.image('./static/img/logo.png', 8, 8, 65)

        # Título a la derecha y pegado al margen superior
        self.set_xy(0, 11)
        self.set_font('Times', 'B', 17)
        self.set_text_color(58, 94, 67)
        #title_width = self.get_string_width('Calendario Anual')  # Ancho del título
        self.cell(0, 0, 'CALENDARIO LABORAL 2024', 0, 0, 'R')  # 'R' indica alineación a la derecha

        self.set_xy(0, 18)
        self.set_font('Times', 'B', 15)
        self.set_text_color(0, 0, 0)
        self.cell(0, 0, localidad.nombre.upper(), 0, 0, 'R')  # 'R' indica alineación a la derecha
        self.set_xy(8, 28)
        self.set_font('Times', '', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 0, 'Empresa: ', 0, 0, 'L')  # 'R' indica alineación a la derecha
        self.set_font('Times', 'B', 12)
        self.set_xy(25, 28)
        self.cell(0, 0, empresa.nombre, 0, 0, 'L')  # 'R' indica alineación a la derecha
        self.set_xy(25, 28)
        self.set_font('Times', '', 12)
        self.set_text_color(204, 204, 204)
        self.cell(0, 0, '__________________________________________________________________________________', 0, 0, 'L')  # 'R' indica alineación a la derecha
        self.set_xy(8, 34)
        self.set_text_color(0, 0, 0)
        self.set_font('Times', '', 12)
        self.cell(8, 0, 'Domicilio: ' + empresa.domicilio, 0, 0, 'L')  # 'R' indica alineación a la derecha
        self.set_text_color(204, 204, 204)
        self.set_xy(27, 34)
        self.cell(0, 0, '_________________________________________________________________________________', 0, 0, 'L')  # 'R' indica alineación a la derecha
        self.set_xy(8, 34)
        self.set_text_color(0, 0, 0)
        self.set_xy(25, 28)
        self.set_font('Times', '', 12)
        self.set_text_color(204, 204, 204)
        self.cell(0, 0, '__________________________________________________________________________________', 0, 0, 'L')
        self.set_xy(8, 40)
        self.set_text_color(0, 0, 0)
        self.cell(8, 0, 'Actividad: ' + empresa.actividad, 0, 0, 'L')
        self.set_text_color(204, 204, 204)
        self.set_xy(27, 40)
        self.cell(0, 0, '_________________________________________________________________________________', 0, 0, 'L')
        self.set_xy(8, 46)
        self.set_text_color(0, 0, 0)
        self.cell(8, 0, 'Convenio: ' + empresa.convenio, 0, 0, 'L')
        self.set_text_color(204, 204, 204)
        self.set_xy(27, 46)
        self.cell(0, 0, '_________________________________________________________________________________', 0, 0, 'L')
        self.set_xy(8, 52)


        # Configurar el espacio entre las cabeceras
        espacio_entre_cabeceras = 2.5

        # Configurar el margen izquierdo y derecho
        margen_izquierdo = 9
        margen_derecho = 9
    def pie(self,com,loc,localidad):
        x = 8
        y = 204
        espacio = 6

        self.set_xy(x,y)
        self.set_fill_color(58, 94, 67)
        self.set_text_color(255, 255, 255)
        self.cell(192, 6, 'FIESTAS ' + localidad.comunidad.nombre.upper(), 0, 0, 'C', 1)
        
        x = 8
        z = 105
        y = 206 + 6
        k = 206 + 6
        r = 105
        t = 264
        self.set_font('Times', '', 11)
        filas = len(com)/2 + 1
        i = 1
        for c in com:
            if i < filas:
                if c.descripcion == '':
                    self.set_fill_color(178, 0, 0)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(x,y)
                    self.cell(4, 4, '',0,0,'C',1)
                    x2 = x + 4
                    self.set_xy(x2,y)
                    self.set_fill_color(255, 255, 255)
                    self.set_text_color(178, 0, 0)
                    ancho1 = self.get_string_width(str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.cell(ancho1+1, 4, str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.set_text_color(0, 0, 0)
                    ancho2 = self.get_string_width(c.nombre)
                    self.cell(ancho2, 4, c.nombre)
                    y = y + espacio
                else:
                    self.set_fill_color(20, 180, 0)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(x,y)
                    self.cell(4, 4, '',0,0,'C',1)
                    x2 = x + 4
                    self.set_xy(x2,y)
                    self.set_fill_color(255, 255, 255)
                    self.set_text_color(20, 180, 0)
                    ancho1 = self.get_string_width(str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.cell(ancho1+1, 4, str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.set_text_color(0, 0, 0)
                    ancho2 = self.get_string_width(c.nombre)
                    self.cell(ancho2, 4, c.nombre)
                    y = y + espacio

                    self.set_fill_color(20, 180, 0)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(r,t)
                    self.cell(4, 4, '',0,0,'C',1)
                    r2 = r + 4
                    self.set_xy(r2,t)
                    self.set_fill_color(255, 255, 255)
                    self.set_text_color(0, 0, 0)
                    ancho1 = self.get_string_width(c.descripcion)
                    self.cell(ancho1+1, 4, c.descripcion)
                    t = t + espacio
            else:
                if c.descripcion == '':
                    self.set_fill_color(178, 0, 0)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(z,k)
                    self.cell(4, 4, '',0,0,'C',1)
                    z2 = z + 4
                    self.set_xy(z2,k)
                    self.set_fill_color(255, 255, 255)
                    self.set_text_color(178, 0, 0)
                    ancho1 = self.get_string_width(str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.cell(ancho1+1, 4, str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.set_text_color(0, 0, 0)
                    ancho2 = self.get_string_width(c.nombre)
                    self.cell(ancho2, 4, c.nombre)
                    k = k + espacio
                else:
                    self.set_fill_color(20, 180, 0)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(z,k)
                    self.cell(4, 4, '',0,0,'C',1)
                    z2 = z + 4
                    self.set_xy(z2,k)
                    self.set_fill_color(255, 255, 255)
                    self.set_text_color(20, 180, 0)
                    ancho1 = self.get_string_width(str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.cell(ancho1+1, 4, str(c.fecha)[-2:] + ' ' + str(c.calendariocom.nombre_mes[:3]))
                    self.set_text_color(0, 0, 0)
                    ancho2 = self.get_string_width(c.nombre)
                    self.cell(ancho2, 4, c.nombre)
                    k = k + espacio

                    self.set_fill_color(20, 180, 0)
                    self.set_text_color(255, 255, 255)
                    self.set_xy(r,t)
                    self.cell(4, 4, '',0,0,'C',1)
                    r2 = r + 4
                    self.set_xy(r2,t)
                    self.set_fill_color(255, 255, 255)
                    self.set_text_color(0, 0, 0)
                    ancho1 = self.get_string_width(c.descripcion)
                    self.cell(ancho1+1, 4, c.descripcion)
                    t = t + espacio
            i += 1

        y = 256
        x = 8
        self.set_xy(x,y)
        self.set_fill_color(58, 94, 67)
        self.set_text_color(255, 255, 255)
        self.cell(95, 6, 'FIESTAS LOCALES', 0, 0, 'C', 1)

        self.set_xy(x+95+2,y)
        self.set_fill_color(58, 94, 67)
        self.set_text_color(255, 255, 255)
        self.cell(95, 6, 'OBSERVACIONES', 0, 0, 'C', 1)

        x = 8
        y = y + 8
        for l in loc:
            self.set_text_color(255, 255, 255)
            self.set_fill_color(255, 128, 0)
            self.set_xy(x,y)
            self.cell(4, 4, '',0,0,'C',1)
            x2 = x + 4
            self.set_xy(x2,y)
            self.set_text_color(255, 128, 0)
            self.set_fill_color(255, 255, 255)
            ancho1 = self.get_string_width(str(l.fecha)[-2:] + ' ' + str(l.calendarioloc.nombre_mes[:3]))
            self.cell(ancho1+1, 4, str(l.fecha)[-2:] + ' ' + str(l.calendarioloc.nombre_mes[:3]),0,0,'L',1)
            self.set_text_color(0, 0, 0)
            ancho2 = self.get_string_width(l.nombre)
            self.cell(ancho2, 4, l.nombre)
            y = y + espacio
        
        

        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_xy(8 + 93 + 4,256+22)
        self.cell(0, 4, localidad.nombre + ', a 1 de enero de 2024',0,0,'R',1)

    def add_month(self,x,y,mes2):
        self.set_xy(x,y)
        self.set_fill_color(58, 94, 67)
        self.set_text_color(255, 255, 255)

        largo = 46.125
        espacio = 2.5

        self.cell(46.125, 6, mes2['day_one'].nombre_mes.capitalize(), 0, 0, 'C', 1)

        # NOMBRE DIAS DE LA SEMANA
        self.set_fill_color(255, 255, 255)
        self.set_text_color(58, 94, 67)
        self.set_font('Times', 'B', 11)

        xcell = x
        ycell = y + 6
        lcell = 6.589
        
        dias_semana = mes2['days_name']
        for i in dias_semana:

            self.set_xy(xcell, ycell)
            self.cell(lcell, 6, i, 0, 0, 'C', 1)
            xcell = xcell + lcell

        #dias = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
        dias = mes2['days']
        xxcell = x
        yycell = ycell + 6
        self.set_text_color(0, 0, 0)
        self.set_font('Times', '', 12)
        dayweek = 0
        #print(len(mes2['days']))
        for d in mes2['days']:
            
            dayweek += 1
            self.set_xy(xxcell,yycell)

            self.set_fill_color(255, 255, 255)
            self.set_text_color(0, 0, 0)

            if d.weekday == 6:
                self.set_fill_color(58, 94, 67)
                self.set_text_color(255, 255, 255)
            
            if d.festivocom:
                for day in d.festivocom:
                    if day.comunidad_id == int(mes2['comunidad']):
                        if day.descripcion != '':
                            self.set_fill_color(20, 180, 0)
                            self.set_text_color(255, 255, 255)
                        else:
                            self.set_fill_color(178, 0, 0)
                            self.set_text_color(255, 255, 255)
            if d.festivoloc:
                #print("Localidad: ")
                #print(mes2['localidad'])
                for day in d.festivoloc:
                    if day.localidad_id == int(mes2['localidad']):
                        self.set_fill_color(255, 128, 0)
                        self.set_text_color(255, 255, 255)                

            self.set_draw_color(255,255,255)
            self.cell(lcell,6,d.dia,1,0,'C',1)
            if dayweek == 7:
                xxcell = x
                yycell = yycell + 6
                dayweek = 0
            else:
                xxcell = xxcell + lcell