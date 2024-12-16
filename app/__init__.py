from flask import Flask
from app.database import Database
from app.swagger import SwaggerConfig
from model import db


class AppFactory:
    def __init__(self):
        self.app = Flask(__name__)
        self._setup_config()
        self._init_services()

    def _setup_config(self):
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/db_steam'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def _init_services(self):
        Database.init_app(self.app)
        SwaggerConfig.init_app(self.app)

    def get_app(self):
        return self.app
