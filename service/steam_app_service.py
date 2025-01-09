from datetime import datetime, timedelta
from uuid import uuid4

import requests
from flask_sqlalchemy import SQLAlchemy
from urllib3 import request

from dto.steam_app.app_reviews_dto import AppReviewsDto
from dto.steam_app.create_steam_dto import CreateSteamDto
from model import SteamApp
from repository.steam_app_repository import SteamAppRepository


class SteamAppService:
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self._steam_repository = SteamAppRepository(db)

    def get_all(self) -> list[SteamApp] | None:
        try:
            return self._steam_repository.get_all()
        except Exception as e:
            print(e)
            return None

    def get_reviews_by_app(self, app_id: str) -> list[AppReviewsDto] | None:
        try:
            results = requests.get(f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page=20").json()['reviews']
            return [AppReviewsDto(
                review=result['review'],
                voted_up=result['voted_up']
            ) for result in results]
        except Exception as e:
            print(e)
            return None


    def create(self, dto: CreateSteamDto) -> int:
        try:
            steam_app = self._steam_repository.get_by_app_id(dto.app_id)
            if steam_app:
                return 0

            new_steam = SteamApp(
                guid=str(uuid4()),
                app_name=dto.app_name,
                app_id=dto.app_id,
                created_date=datetime.utcnow() + timedelta(hours=7),
                admin_guid=dto.admin_guid
            )

            result = self._steam_repository.create(new_steam)
            if not result:
                return -1
            return 1

        except Exception as e:
            print(e)
            return -1

    def delete(self, guid: str) -> int:
        try:
            steam = self._steam_repository.get_by_guid(guid)
            if not steam:
                return 0

            result = self._steam_repository.delete(guid)
            if not result:
                return -1
            return 1
        except Exception as e:
            print(e)
            return -1