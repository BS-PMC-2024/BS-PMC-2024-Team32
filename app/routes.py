# routes.py
from flask import current_app,render_template, request, redirect, url_for, flash, session, abort,jsonify
from functools import wraps
from app import app, db
from app.models import User, Teacher, Student, Manager, SupportTicket,SupportStaff,Admin
from app.forms import LoginForm, AddTeacherForm, AddStudentForm, AddManagerForm,ContactForm,SupportTicketForm,AddSupportStaffForm,CloseTicketForm
from app.email import send_contact_email
import logging
from sqlalchemy import text

@app.route('/')
def home():
    if 'visited' not in session:
        session['visited'] = True
        show_loader = True
    else:
        show_loader = False
    return render_template('index.html', show_loader=show_loader)

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
            form.username.errors.append('Invalid username or password')
    return render_template('login.html', form=form)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


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

def support_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'support':
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

def teacher_or_student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] not in ['teacher', 'student']:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'student':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@app.route('/add_manager', methods=['GET', 'POST'])
@login_required
@admin_required
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

@app.route('/add_support_staff', methods=['GET', 'POST'])
@login_required
@admin_required
def add_support_staff():
    form = AddSupportStaffForm()
    if form.validate_on_submit():
        support_staff = SupportStaff(username=form.username.data, user_type='support')
        support_staff.set_password(form.password.data)
        db.session.add(support_staff)
        db.session.commit()
        flash('New support staff added successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_support_staff.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    user_type = session.get('user_type')
    valid_user_types = ['admin', 'support', 'manager', 'teacher', 'student']
    user = None

    if user_type == 'manager':
        user = Manager.query.get(session['user_id'])
    elif user_type == 'admin':
        user = Admin.query.get(session['user_id'])
    elif user_type == 'teacher':
        user = Teacher.query.get(session['user_id'])
    elif user_type == 'student':
        user = Student.query.get(session['user_id'])
    elif user_type == 'support':
        user = SupportStaff.query.get(session['user_id'])

    if user_type in valid_user_types and user:
        return render_template('dashboard.html', user_type=user_type, user=user)
    else:
        flash('Invalid user type or user not found', 'danger')
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

@app.route('/my_courses')
@login_required
@student_required
def my_courses():
    # Fetch the current student
    student = Student.query.get(session['user_id'])
    
    # Placeholder for courses (we'll use a list of dictionaries for now)
    courses = [
        {"id": 1, "name": "Introduction to Algebra", "teacher": "Dr. Smith"},
        {"id": 2, "name": "Geometry Basics", "teacher": "Prof. Johnson"},
        {"id": 3, "name": "Advanced Calculus", "teacher": "Dr. Williams"}
    ]
    
    return render_template('my_courses.html', student=student, courses=courses)

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



@app.route('/support', methods=['GET', 'POST'])
@login_required
@teacher_or_student_required
def support():
    form = SupportTicketForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        ticket = SupportTicket(
            user_id=user.id,
            user_type=user.user_type,
            issue_category=form.issue_category.data,
            description=form.description.data
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Your support ticket has been submitted successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('support.html', form=form)


@app.route('/close_ticket/<int:ticket_id>', methods=['POST'])
@login_required
@support_required
def close_ticket(ticket_id):
    ticket = SupportTicket.query.get(ticket_id)
    if ticket and ticket.status == 'Open':
        ticket.status = 'Closed'
        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Ticket closed successfully!'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error closing ticket: {e}")
            return jsonify({'success': False, 'message': 'Failed to close the ticket. Please try again.'}), 500
    else:
        return jsonify({'success': False, 'message': 'Ticket could not be closed. It may not exist or is already closed.'}), 400

@app.route('/support_tickets')
@login_required
@support_required
def support_tickets():
    open_tickets = SupportTicket.query.filter_by(status='Open').count()
    closed_tickets = SupportTicket.query.filter_by(status='Closed').count()
    total_tickets = open_tickets + closed_tickets

    open_percentage = (open_tickets / total_tickets) * 100 if total_tickets > 0 else 0
    closed_percentage = (closed_tickets / total_tickets) * 100 if total_tickets > 0 else 0

    tickets = db.session.query(SupportTicket, User.username).join(User).filter(SupportTicket.status == 'Open').all()

    return render_template('support_tickets.html', 
                           open_tickets=open_tickets,
                           closed_tickets=closed_tickets,
                           open_percentage=open_percentage,
                           closed_percentage=closed_percentage,
                           tickets=tickets)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Create a dictionary with form data
        inquiry_data = {
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'organization': form.organization.data,
            'role': form.role.data,
            'message': form.message.data,
            'preferred_contact': form.preferred_contact.data,
            'best_time': form.best_time.data
        }
        
        # Send email
        send_contact_email(inquiry_data)
        
        flash('Your message has been sent. We will contact you shortly!', 'success')
        return redirect(url_for('home'))
    return render_template('contact.html', form=form)

