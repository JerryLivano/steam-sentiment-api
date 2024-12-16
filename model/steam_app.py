from datetime import datetime
from app.database import db

class SteamApp(db.Model):
    __tablename__ = 'steam_app'

    guid = db.Column(db.String(50), primary_key=True)
    app_name = db.Column(db.String(200), nullable=False)
    app_id = db.Column(db.String(50), nullable=False, unique=True)
    created_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # relation
    admin_guid = db.Column(db.String(50), db.ForeignKey('admin.guid'), nullable=False)
    admin = db.relationship('Admin', back_populates='steam_apps')

    def __init__(self, guid: str, app_name: str, app_id: str, created_date: datetime, admin_guid: str):
        self.guid = guid
        self.app_name = app_name
        self.app_id = app_id
        self.created_date = created_date
        self.admin_guid = admin_guid

    def __repr__(self):
        return f"<SteamApp {self.app_id}>"