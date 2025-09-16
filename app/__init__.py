from flask import Flask
from app.auth import auth_bp
from app.courses import courses_bp
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config/config.py')

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return 'SISE Flask rodando!'

    return app
