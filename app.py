import CORS
from flask import redirect
from app import AppFactory
from controller.admin_controller import AdminController
from controller.steam_app_controller import SteamAppController
from model import db
from app.database import Database

factory = AppFactory()
Database.create_db_context()
app = factory.get_app()

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

with app.app_context():
    db.create_all()
    AdminController(app, db)
    SteamAppController(app, db)

@app.route('/')
def index():
    return redirect('/apidocs')

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
