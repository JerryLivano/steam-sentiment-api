from datetime import datetime
from app.database import db

class Admin(db.Model):
    __tablename__ = 'admin'

    guid = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    steam_apps = db.relationship('SteamApp', back_populates='admin', cascade='all, delete-orphan')

    def __init__(self, guid: str, name: str, email: str, password: str, created_date: datetime):
        self.guid = guid
        self.name = name
        self.email = email
        self.password = password
        self.created_date = created_date

    def __repr__(self):
        return f"<Admin {self.email}>"