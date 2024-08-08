# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField , SelectField,TextAreaField,HiddenField
from wtforms.validators import Email,DataRequired, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long.')])
    submit = SubmitField('Login')

class AddManagerForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add Manager')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class AddSupportStaffForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', [DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add Support Staff')

class AddTeacherForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add Teacher')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class AddStudentForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    teacher_id = SelectField('Teacher', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Student')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        


class SupportTicketForm(FlaskForm):
    issue_category = SelectField('Issue Category', choices=[
        ('login', 'Login Issues'),
        ('course_content', 'Course Content'),
        ('performance', 'Performance'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description of the Problem', validators=[DataRequired()])
    submit = SubmitField('Submit Ticket')


class CloseTicketForm(FlaskForm):
    id = HiddenField('Ticket ID', validators=[DataRequired()])
    submit = SubmitField('Close Ticket')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    organization = StringField('School/Organization Name')
    role = SelectField('Role', choices=[
        ('school_admin', 'School Administrator'),
        ('teacher', 'Teacher'),
        ('other', 'Other')
    ])
    message = TextAreaField('Message', validators=[DataRequired()])
    preferred_contact = SelectField('Preferred Contact Method', choices=[
        ('email', 'Email'),
        ('phone', 'Phone')
    ])
    best_time = StringField('Best Time to Contact (if phone is preferred)')
    submit = SubmitField('Submit')        