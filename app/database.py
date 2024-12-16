from flask_sqlalchemy import SQLAlchemy
import pymysql

db = SQLAlchemy()

class Database:
    @staticmethod
    def init_app(app):
        db.init_app(app)

    @staticmethod
    def create_db_context():
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = connection.cursor()

        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS db_steam")
        except pymysql.MySQLError as e:
            print(f"Error while create db: {e}")
        finally:
            cursor.close()
            connection.close()