from flask import redirect
from app import AppFactory
from controller.admin_controller import AdminController
from model import db
from app.database import Database

factory = AppFactory()
Database.create_db_context()
app = factory.get_app()

with app.app_context():
    db.create_all()
    AdminController(app, db)

@app.route('/')
def index():
    return redirect('/apidocs')

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
