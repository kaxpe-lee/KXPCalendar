from flask import(render_template, Blueprint, flash, g, redirect, request, session,url_for)
import os, json
from werkzeug.security import check_password_hash, generate_password_hash
from user.models.user import User

from main import db

import functools

user = Blueprint('user', __name__, template_folder='templates', url_prefix='/user')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))
        return view(**kwargs)
    return wrapped_view


#Registrar un usuario
@user.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if g.user.nivel == '0':
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            mail = request.form.get('mail')
            telefono = request.form.get('telefono')
            oficina = request.form.get('oficina')
            nivel = request.form.get('nivel')
            user = User(username, generate_password_hash(password), nombre, apellido, mail, telefono, oficina, nivel)
            error = None
            if not username:
                error = 'Se requiere nombre de usuario'
            elif not password:
                error = 'Se requiere  contraseña'

            user_name = User.query.filter_by(username = username).first()
            if user_name == None:
                db.session.add(user)
                db.session.commit()
                error = 'El usuario no existe, se ha ha creado nuevo'
            else:
                error = f'El usuario {username} ya esta registrado'
            flash(error)
            return render_template('user/register.html')
        else:
            return render_template('user/register.html')        
        #return render_template('user/register.html')
    else:
        return redirect(url_for('asiento.index'))
#Iniciar sesión
@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
       
        error = None

        user = User.query.filter_by(username = username).first()

        if user == None:
            error = 'Nombre de usuario incorrecto'
        elif not check_password_hash(user.password, password):
            error = 'Contraseña incorrecta'
        
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))
       
        flash(error)
        return render_template('user/login.html')
    else:
        return render_template('user/login.html')        
    #return render_template('user/register.html')

@user.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

@user.route('logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



def is_user_empty():
    return db.session.query(User).count() == 0




@user.route('/check')
def check():
    if is_user_empty() == True:
        user = User("admin", generate_password_hash("password"), 'Admin', "", "admin@admin.com", "000000000", "Oficina", "0")
        db.session.add(user)
        db.session.commit()
         
    return redirect(url_for('user.login'))

def textos():
    texto = {}
    texto['modulo'] = 'user'
    texto['modulo']['user'] = 'login','logout','register'


def load_language(lang_code):
    lang_file = {lang_code}+".json"
    if os.path.exists("static/"+lang_file):
        with open(lang_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None