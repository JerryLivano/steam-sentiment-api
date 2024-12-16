from datetime import datetime, timedelta
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from dto.admin.login_dto import LoginDto
from dto.admin.register_dto import RegisterDto
from dto.admin.token_request_dto import TokenRequestDto
from dto.admin.token_response_dto import TokenResponseDto
from handler.bcrypt_handler import BCryptHandler
from handler.jwt_handler import JWTHandler
from model import Admin
from repository.admin_repository import AdminRepository


class AdminService:
    def __init__(self, db: SQLAlchemy):
        self._db = db
        self._bcrypt = BCryptHandler()
        self._admin_repository = AdminRepository(db)
        self._jwt_handler = JWTHandler()

    def register(self, dto: RegisterDto) -> int:
        try:
            if dto.password != dto.confirm_password:
                return -2
            if self._admin_repository.get_by_email(dto.email):
                return -3
            admin = Admin(
                guid=str(uuid4()),
                name=dto.name,
                email=dto.email,
                password=self._bcrypt.hash_password(dto.password),
                created_date=datetime.utcnow() + timedelta(hours=7)
            )
            result = self._admin_repository.create(admin)
            if not result:
                return 0
            return 1
        except Exception as e:
            print(e)
            return -1

    def login(self, dto: LoginDto) -> TokenResponseDto | None:
        try:
            admin = self._admin_repository.get_by_email(dto.email)
            if not admin or not self._bcrypt.verify_password(dto.password, admin.password):
                return None

            token = TokenRequestDto(
                guid=admin.guid,
                name=admin.name,
                email=admin.email
            )
            return TokenResponseDto(
                token=self._jwt_handler.generate_token(token)
            )

        except Exception as e:
            print(e)
            return None
