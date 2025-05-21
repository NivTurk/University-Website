from flask import Flask
from flask_pymongo import PyMongo
from config import Config


mongo = PyMongo()

def create_app(config_class = Config):
    app =Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)

    from app.routes.courses import courses_bp
    app.register_blueprint(courses_bp)


    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    with app.app_context():
        mongo.db.courses.create_index('name', unique=True)

    return app