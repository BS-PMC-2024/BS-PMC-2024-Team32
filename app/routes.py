# routes.py
from flask import render_template, request, redirect, url_for, flash, session, abort,jsonify
from functools import wraps
from app import app, db
from app.models import User, Teacher, Student, Manager 
from app.forms import LoginForm, AddTeacherForm, AddStudentForm, AddManagerForm
import logging
from sqlalchemy import text

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
            return redirect(url_for('dashboard'))
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
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'teacher':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@app.route('/add_manager', methods=['GET', 'POST'])
@login_required
@manager_required
def add_manager():
    form = AddManagerForm()
    if form.validate_on_submit():
        manager = Manager(username=form.username.data, user_type='manager')
        manager.set_password(form.password.data)
        db.session.add(manager)
        db.session.commit()
        flash('New manager added successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_manager.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    user_type = session.get('user_type')
    if user_type == 'manager':
        return render_template('dashboard.html', user_type='manager')
    elif user_type == 'teacher':
        return render_template('dashboard.html', user_type='teacher')
    elif user_type == 'student':
        return render_template('dashboard.html', user_type='student')
    else:
        flash('Invalid user type', 'danger')
        return redirect(url_for('home'))
    

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
@manager_required
def add_teacher():
    form = AddTeacherForm()
    if form.validate_on_submit():
        teacher = Teacher(
            username=form.username.data, 
            name=form.name.data, 
            user_type='teacher', 
            manager_id=session['user_id']  # Automatically assign to the current manager
        )
        teacher.set_password(form.password.data)
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_teacher.html', form=form)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
@manager_required
def add_student():
    form = AddStudentForm()
    # Populate the teacher choices
    form.teacher_id.choices = [(t.id, f"{t.name} ({t.username})") for t in Teacher.query.filter_by(manager_id=session['user_id']).all()]
    
    if form.validate_on_submit():
        student = Student(
            username=form.username.data, 
            name=form.name.data, 
            user_type='student', 
            teacher_id=form.teacher_id.data
        )
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_student.html', form=form)


@app.route('/my_students')
@login_required
@teacher_required
def my_students():
    teacher = Teacher.query.get(session['user_id'])
    if teacher:
        students = Student.query.filter_by(teacher_id=teacher.id).all()
        return render_template('my_students.html', students=students)
    else:
        flash('Teacher not found', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

from app.models import User, Manager, Teacher, Student

@app.route('/test_db')
def test_db():
    try:
        # Test connection and query all tables
        users = User.query.all()
        managers = Manager.query.all()
        teachers = Teacher.query.all()
        students = Student.query.all()

        return f"""
        Connected to the database successfully.
        Number of users: {len(users)}
        Number of managers: {len(managers)}
        Number of teachers: {len(teachers)}
        Number of students: {len(students)}
        """
    except Exception as e:
        return f"Failed to connect to the database or query tables. Error: {str(e)}"

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