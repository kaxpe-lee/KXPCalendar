from flask_wtf import FlaskForm
from wtforms import DateField,StringField, SubmitField,SelectField, PasswordField, IntegerField, BooleanField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileRequired

#Formulario de registro
class login(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(max=45)])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Aceptar')
    
class fempresas(FlaskForm):
    fichero = FileField('Fichero Excel:')
    submit = SubmitField('Aceptar')

class fcalendario(FlaskForm):
    year = IntegerField('Año:', validators=[DataRequired(), NumberRange(min=2023, message="El año debe ser mayor de 2022")])
    submit = SubmitField('Aceptar')