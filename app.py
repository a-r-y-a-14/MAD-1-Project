from flask import Flask
from application.database import db

app=None #initialise app as a variable with none

def create_app():
    app=Flask(__name__) #flask object is created
    app.debug=True
    app.config['SECRET_KEY'] = 'abc123xyz'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///inventory.sqlite3'
    db.init_app(app)
    app.app_context().push()
    return app

app=create_app()

from application.controllers import *

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        admin=Admin.query.filter_by(username="admin1").first()
        if admin is None:
            admin=Admin(username="admin1", email="admin@example.com", password="admin@1234")
            db.session.add(admin)
            db.session.commit()
    app.run() 