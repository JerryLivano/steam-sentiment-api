class RegisterDto:
    def __init__(self, name: str, email: str, password: str, confirm_password: str):
        self.name = name
        self.email = email
        self.password = password
        self.confirm_password = confirm_password