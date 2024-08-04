# routes.py
from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps
from app import app, db
from app.models import User, Teacher, Student
from app.forms import LoginForm, AddTeacherForm, AddStudentForm
import logging

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['user_type'] = user.user_type
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'manager':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
@manager_required
def add_teacher():
    form = AddTeacherForm()
    if form.validate_on_submit():
        new_teacher = Teacher(name=form.name.data, manager_id=form.manager_id.data)
        db.session.add(new_teacher)
        db.session.commit()
        flash('Teacher added successfully!')
        return redirect(url_for('home'))
    return render_template('add_teacher.html', form=form)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
@manager_required
def add_student():
    form = AddStudentForm()
    if form.validate_on_submit():
        new_student = Student(name=form.name.data, teacher_id=form.teacher_id.data)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('home'))
    return render_template('add_student.html', form=form)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/test_db')
def test_db():
    try:
        # Attempt to query the User table
        users = User.query.all()
        return f"Connected to the database. Number of users: {len(users)}"
    except Exception as e:
        return f"Failed to connect to the database. Error: {str(e)}"

from flask import jsonify
from sqlalchemy import text

from flask import jsonify
from sqlalchemy import text

@app.route('/create_test_user')
def create_test_user():
    user = User(username='TestAHH', user_type='manager')
    plain_password = '123'
    user.set_password(plain_password)
    db.session.add(user)
    db.session.commit()
    
    # Fetch the user directly from the database
    with db.engine.connect() as connection:
        result = connection.execute(text("SELECT password_hash FROM user WHERE username = 'TestAHH'"))
        db_hash = result.fetchone()[0]
    
    check_result = user.check_password(plain_password)
    
    # Fetch the user again and perform another password check
    fetched_user = User.query.filter_by(username='TestAHH').first()
    second_check = fetched_user.check_password(plain_password)
    
    return jsonify({
        "test_user_created": True,
        "first_password_check": check_result,
        "second_password_check": second_check,
        "hashes_match": db_hash == user.password_hash,
        "user_object_hash": user.password_hash,
        "database_hash": db_hash,
        "hash_length": len(db_hash)
    })