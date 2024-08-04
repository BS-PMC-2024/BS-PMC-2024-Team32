from app import db
from app.models import User

def create_test_user():
    username = 'test_user1'
    password = '123'
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, user_type='manager')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Test user created: {username}")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        create_test_user()
