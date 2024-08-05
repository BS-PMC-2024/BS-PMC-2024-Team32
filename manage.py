# manage.py
from flask.cli import FlaskGroup
from app import app, db
from app.models import Manager

cli = FlaskGroup(app)

@cli.command("create_manager")
def create_manager():
    username = input("Enter manager username: ")
    password = input("Enter manager password: ")
    
    manager = Manager(username=username, user_type='manager')
    manager.set_password(password)
    
    db.session.add(manager)
    db.session.commit()
    
    print(f"Manager {username} created successfully.")

if __name__ == "__main__":
    cli()