from flask import Flask
from app.auth import auth_bp
from app.courses import courses_bp
from app.extensions import db
from config.config import DebugConfig, ProductionConfig

def create_app(config_name='Debug'):
    app = Flask(__name__)

    # Carrega a configuração correta
    if config_name == 'Production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DebugConfig)

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return 'SISE Flask rodando!'

    return app
