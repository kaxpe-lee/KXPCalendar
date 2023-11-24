from flask import (Flask, redirect, session, render_template, request, send_from_directory, url_for)
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://kaxper:miloja@localhost/agenda2py"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'miloja1502'
app.config['DEBUG'] = True

db = SQLAlchemy(app)

from user.models.user import User
from user.routes import login_required
from werkzeug.security import check_password_hash, generate_password_hash

from user.routes import user
app.register_blueprint(user)

from calendario.routes import calendario
app.register_blueprint(calendario)

@app.route('/')
def index():
    if 'user_id' in session:
        return "Usuario logueado"  
    else:
	    return redirect(url_for('user.login'))
    

def testeando():
    if db.session.query(User).count() == 0:
        user = User("admin", generate_password_hash("password"), 'Admin', "", "admin@admin.com", "000000000", "Oficina", "0")
        db.session.add(user)
        db.session.commit()

            
with app.app_context():
    db.create_all()
    testeando()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
