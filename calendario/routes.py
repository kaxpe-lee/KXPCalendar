from flask import(render_template, Blueprint, flash, g, redirect, request, session,url_for,send_file,Response,make_response)
from werkzeug.utils import secure_filename
#from dateutil import parser
from user.models.user import User
from calendario.models.empresa import Empresa
from calendario.models.calendario import Calendario
from calendario.models.comunidad import Comunidad
from calendario.models.localidad import Localidad
from calendario.models.festivocom import Festivocom
from calendario.models.festivoloc import Festivoloc
from sqlalchemy.orm import aliased

from sqlalchemy import text, func, and_ , or_

#from reportlab.lib import colors
#from fpdf import FPDF
#from io import BytesIO

from user.routes import login_required
#from datetime import date, timedelta, datetime
#import calendar
from main import db, app
import os, json
#import locale
#import pandas as pd
#from forms import fempresas
#from forms import fcalendario

calendario = Blueprint('calendario', __name__, template_folder='templates', url_prefix='/calendario')

lang_code =  'es'

@calendario.route('/calendarios')
def calendarios():
    return redirect(url_for('index'))