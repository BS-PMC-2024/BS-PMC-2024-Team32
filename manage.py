# manage.py
from flask.cli import FlaskGroup
from app import app, db
from app.models import Admin

cli = FlaskGroup(app)

@cli.command("create_admin")
def create_admin():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    
    admin = Admin(username=username, user_type='admin')
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin {username} created successfully.")

if __name__ == "__main__":
    cli()