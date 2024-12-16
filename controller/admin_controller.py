from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dto.admin.login_dto import LoginDto
from dto.admin.register_dto import RegisterDto
from service.admin_service import AdminService


class AdminController:
    def __init__(self, app: Flask, db: SQLAlchemy):
        self._admin_service = AdminService(db)

        app.add_url_rule('/register', 'register', self.register, methods=['POST'])
        app.add_url_rule('/login', 'login', self.login, methods=['POST'])

    def register(self):
        """
            Register a new admin
            ---
            tags: ['Admin']
            parameters:
              - name: RegisterDto
                in: body
                required: true
                schema:
                  id: RegisterDto
                  properties:
                    name:
                      type: string
                      description: Admin name
                    email:
                      type: string
                      description: The email of the admin
                    password:
                      type: string
                      description: The password of admin
                    confirm_password:
                      type: string
                      description: The confirmation password
            responses:
                201:
                    description: Registration successful
                400:
                    description: Registration failed
                403:
                    description: Invalid payload
                404:
                    description: Data not found
                500:
                    description: Internal server error
        """
        try:
            data = request.get_json()
            register_dto = RegisterDto(**data)
            result = self._admin_service.register(register_dto)

            if result == 0:
                return jsonify({
                    'status': 400,
                    'message': 'Failed to register'
                }), 400

            if result == -2:
                return jsonify({
                    'status': 403,
                    'message': 'Password not match'
                }), 403

            if result == -3:
                return jsonify({
                    'status': 404,
                    'message': 'Admin already exist'
                }), 404

            if result == -1:
                return jsonify({
                    'status': 500,
                    'message': 'Internal server error'
                }), 500

            return jsonify({
                'status': 201,
                'message': 'Register success',
            }), 201

        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500

    def login(self):
        """
            Login Admin
            ---
            tags: ['Auth']
            parameters:
              - name: LoginDto
                in: body
                required: true
                schema:
                  id: LoginDto
                  properties:
                    email:
                      type: string
                      description: The email of the admin
                    password:
                      type: string
                      description: The password of the admin
            responses:
                201:
                    description: Registration successful
                403:
                    description: Permission invalid
                500:
                    description: Internal server error
        """
        try:
            data = request.get_json()
            login_dto = LoginDto(**data)
            result = self._admin_service.login(login_dto)

            if not result:
                return jsonify({
                    'status': 404,
                    'message': 'Incorrect email or password'
                }), 404

            return jsonify({
                'status': 201,
                'message': 'Login success',
                'data': result.__dict__
            }), 201

        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Error occurred: {str(e)}'
            }), 500
