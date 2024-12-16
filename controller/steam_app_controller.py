from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dto.steam_app.create_steam_dto import CreateSteamDto
from service.steam_app_service import SteamAppService


class SteamAppController:
    def __init__(self, app: Flask, db: SQLAlchemy):
        self._steam_service = SteamAppService(db)

        app.add_url_rule('/steam', 'get_all_steam', self.get_all_steam, methods=['GET'])
        app.add_url_rule('/steam', 'create_steam', self.create_steam, methods=['POST'])
        app.add_url_rule('/steam/<string:guid>', 'delete_steam', self.delete_steam, methods=['DELETE'])

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
