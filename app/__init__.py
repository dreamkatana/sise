from flask import Flask
from app.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config/config.py')
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return 'SISE Flask rodando!'

    return app
