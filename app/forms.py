# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddTeacherForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    manager_id = IntegerField('Manager ID', validators=[DataRequired()])
    submit = SubmitField('Add Teacher')

class AddStudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    teacher_id = IntegerField('Teacher ID', validators=[DataRequired()])
    submit = SubmitField('Add Student')
