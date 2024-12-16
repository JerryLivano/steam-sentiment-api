from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from model.admin import Admin


class AdminRepository:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create(self, admin: Admin) -> Admin | None:
        try:
            self.db.session.add(admin)
            self.db.session.commit()
            return admin
        except SQLAlchemyError:
            self.db.session.rollback()
            return None

    def get_by_email(self, email: str) -> Admin | None:
        try:
            return self.db.session.query(Admin).filter_by(email=email).first()
        except SQLAlchemyError:
            return None
