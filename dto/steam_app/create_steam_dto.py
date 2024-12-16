class CreateSteamDto:
    def __init__(self, app_name: str, app_id: str, admin_guid: str):
        self.app_name = app_name
        self.app_id = app_id
        self.admin_guid = admin_guid