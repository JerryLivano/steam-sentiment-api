from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from model import SteamApp


class SteamAppRepository:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_all(self) -> list[SteamApp] | None:
        try:
            result = self.db.session.query(SteamApp).all()
            if not result:
                return []
            return result
        except SQLAlchemyError:
            return None

    def get_by_guid(self, guid: str) -> SteamApp | None:
        try:
            result = self.db.session.query(SteamApp).filter_by(guid=guid).first()
            if not result:
                return None
            return result
        except SQLAlchemyError:
            return None

    def get_by_app_id(self, app_id: str) -> SteamApp | None:
        try:
            result = self.db.session.query(SteamApp).filter_by(app_id=app_id).first()
            if not result:
                return None
            return result
        except SQLAlchemyError:
            return None

    def create(self, steam_app: SteamApp) -> SteamApp | None:
        try:
            self.db.session.add(steam_app)
            self.db.session.commit()
            return steam_app
        except SQLAlchemyError:
            self.db.session.rollback()
            return None

    def delete(self, guid: str) -> bool:
        try:
            steam_app = self.db.session.query(SteamApp).get(guid)
            if not steam_app:
                return False
            self.db.session.delete(steam_app)
            self.db.session.commit()
            return True
        except SQLAlchemyError:
            self.db.session.rollback()
            return False

