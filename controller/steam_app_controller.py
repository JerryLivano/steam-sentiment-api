from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dto.steam_app.create_steam_dto import CreateSteamDto
from service.sentiment_analysis_service import SentimentAnalysisService
from service.steam_app_service import SteamAppService
import requests


class SteamAppController:
    def __init__(self, app: Flask, db: SQLAlchemy):
        self._steam_service = SteamAppService(db)
        self._sentiment_service = SentimentAnalysisService()

        app.add_url_rule('/steam', 'get_all_steam', self.get_all_steam, methods=['GET'])
        app.add_url_rule('/steam/reviews/<string:app_id>', 'get_reviews', self.get_reviews, methods=['GET'])
        app.add_url_rule('/steam', 'create_steam', self.create_steam, methods=['POST'])
        app.add_url_rule('/steam/<string:guid>', 'delete_steam', self.delete_steam, methods=['DELETE'])
        app.add_url_rule('/steam/analyze/<string:app_id>', 'analyze_sentiment', self.analyze_sentiment, methods=['POST'])
        app.add_url_rule('/steam/get_api', 'fetch_steam_app', self.fetch_steam_app, methods=['GET'])

    def get_all_steam(self):
        """
            Register a new admin
            ---
            tags: ['Steam App']
            responses:
                200:
                    description: Get all data
                400:
                    description: Failed to get data
                500:
                    description: Internal server error
        """
        try:
            result = self._steam_service.get_all()
            if result is None:
                return jsonify({
                    'status': 400,
                    'message': 'Failed to get data'
                }), 400

            return jsonify({
                'status': 200,
                'message': 'Data get successfully',
                'data': [data.to_dict() for data in result]
            })
        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500

    def get_reviews(self, app_id: str):
        """
            Get Reviews
            ---
            tags: ['Steam App']
            parameters:
              - name: app_id
                in: path
                required: true
                type: string
                description: App ID
            responses:
                200:
                    description: Data retrieved successfully
                500:
                    description: Internal server error
        """
        try:
            results = self._steam_service.get_reviews_by_app(app_id)
            return jsonify({
                'status': 200,
                'message': 'Data successfully analyzed',
                'data': [result.__dict__ for result in results]
            }), 200
        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500

    def fetch_steam_app(self):
        """
            Fetch Steam Apps
            ---
            tags: ['Steam App']
            responses:
                200:
                    description: Get all data
                500:
                    description: Internal server error
        """
        try:
            response = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json')

            return jsonify({
                'status': 200,
                'message': 'Data get successfully',
                'data': response.json()['applist']['apps'][216485:216535]
            })
        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500

    def create_steam(self):
        """
            Create a new steam app
            ---
            tags: ['Steam App']
            parameters:
              - name: CreateSteamDto
                in: body
                required: true
                schema:
                  id: CreateSteamDto
                  properties:
                    app_name:
                      type: string
                      required: True
                      description: App name
                    app_id:
                      type: string
                      required: True
                      description: App unique identifier
                    admin_guid:
                      type: string
                      required: True
                      description: Admin guid
            responses:
                201:
                    description: Data created successfully
                400:
                    description: Failed to create data
                403:
                    description: Invalid payload
                404:
                    description: Data not found
                500:
                    description: Internal server error
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'status': 403,
                    'message': 'Invalid payload'
                }), 403

            create_dto = CreateSteamDto(**data)
            result = self._steam_service.create(create_dto)

            if result == 0:
                return jsonify({
                    'status': 404,
                    'message': 'Data already exist'
                }), 404

            if result == -1:
                return jsonify({
                    'status': 400,
                    'message': 'Failed to create data'
                }), 400

            return jsonify({
                'status': 200,
                'message': 'Data created successfully',
            }), 200
        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500

    def delete_steam(self, guid: str):
        """
            Delete Steam
            ---
            tags: ['Steam App']
            parameters:
              - name: guid
                in: path
                required: true
                type: string
                description: GUID of the steam to retrieve
            responses:
                200:
                    description: Data deleted successfully
                400:
                    description: Failed to delete
                404:
                    description: Request not found
                500:
                    description: Internal server error
        """
        try:
            result = self._steam_service.delete(guid)

            if result == 0:
                return jsonify({
                    'status': 404,
                    'message': 'Data not found'
                }), 404

            if result == -1:
                return jsonify({
                    'status': 400,
                    'message': 'Failed to delete'
                }), 400

            return jsonify({
                'status': 200,
                'message': 'Data deleted'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500

    def analyze_sentiment(self, app_id: str):
        """
            Analyze Sentiment
            ---
            tags: ['Steam App']
            parameters:
              - name: app_id
                in: path
                required: true
                type: string
                description: App ID
            responses:
                200:
                    description: Data deleted successfully
                500:
                    description: Internal server error
        """
        try:
            result = self._sentiment_service.analyze_app(app_id)

            return jsonify({
                'status': 200,
                'message': 'Data successfully analyzed',
                'data': result.__dict__
            }), 200
        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500