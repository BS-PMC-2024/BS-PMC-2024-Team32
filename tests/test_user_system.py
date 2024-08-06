import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import app, db
from app.models import User, Manager, Teacher, Student
from flask import session

@pytest.fixture(scope='function')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.session.remove()
            db.drop_all()

def test_login_logout(test_client):
    with app.app_context():
        # Change this line
        manager = Manager(username='testuser', user_type='manager')
        manager.set_password('testpassword')
        db.session.add(manager)
        db.session.commit()

    response = test_client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert response.status_code == 200
    with test_client.session_transaction() as sess:
        assert 'user_id' in sess
        assert sess['user_type'] == 'manager'

    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with test_client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_add_teacher(test_client):
    with app.app_context():
        manager = Manager(username='testmanager', user_type='manager')
        manager.set_password('testpassword')
        db.session.add(manager)
        db.session.commit()

        with test_client.session_transaction() as sess:
            sess['user_id'] = manager.id
            sess['user_type'] = 'manager'

    response = test_client.post('/add_teacher', data=dict(
        username='newteacher',
        password='teacherpass',
        confirm_password='teacherpass',
        name='John Doe'
    ), follow_redirects=True)
    assert response.status_code == 200
    
    with app.app_context():
        teacher = Teacher.query.filter_by(username='newteacher').first()
        assert teacher is not None
        assert teacher.name == 'John Doe'
        assert teacher.manager_id == manager.id

def test_add_student(test_client):
    with app.app_context():
        # Create a manager if not exists
        manager = Manager.query.filter_by(username='testmanager').first()
        if not manager:
            manager = Manager(username='testmanager', user_type='manager')
            manager.set_password('testpassword')
            db.session.add(manager)
            db.session.commit()

        # Create a teacher
        teacher = Teacher(username='newteacher2', name='Jane Smith', user_type='teacher', manager_id=manager.id)
        teacher.set_password('teacherpass')
        db.session.add(teacher)
        db.session.commit()

        teacher_id = teacher.id  # Store the teacher's id

        # Set session to mimic logged in manager
        with test_client.session_transaction() as sess:
            sess['user_id'] = manager.id
            sess['user_type'] = 'manager'

    # Add student
    response = test_client.post('/add_student', data=dict(
        username='newstudent',
        password='studentpass',
        confirm_password='studentpass',
        name='Alice Johnson',
        teacher_id=teacher_id
    ), follow_redirects=True)
    assert response.status_code == 200

    # Verify student was added
    with app.app_context():
        student = Student.query.filter_by(username='newstudent').first()
        assert student is not None
        assert student.name == 'Alice Johnson'
        assert student.teacher_id == teacher_id