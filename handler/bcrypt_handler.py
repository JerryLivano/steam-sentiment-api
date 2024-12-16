import bcrypt


class BCryptHandler:
    @staticmethod
    def generate_salt() -> bytes:
        return bcrypt.gensalt(rounds=12)

    def hash_password(self, password: str) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), self.generate_salt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
