class TokenRequestDto:
    def __init__(self, guid: str, name: str, email: str, role = "Admin"):
        self.guid = guid
        self.name = name,
        self.email = email,
        self.role = role

