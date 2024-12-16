from flasgger import Swagger


class SwaggerConfig:
    SWAGGER_TEMPLATE = {
        "info": {
            "title": "Scrape-ME API Documentation",
            "description": "List of all API used in Scrape-ME system",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    @staticmethod
    def init_app(app):
        Swagger(app, template=SwaggerConfig.SWAGGER_TEMPLATE)
