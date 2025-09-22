from flask import Flask
from app.auth import auth_bp
from app.courses import courses_bp
from app.lms import lms_bp
from app.extensions import db
import os

def create_app(config_name='Debug'):
    app = Flask(__name__)

    # Configuração básica para desenvolvimento
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sise.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Tentar carregar configuração específica se existir
    try:
        from config.config import DebugConfig, ProductionConfig
        if config_name == 'Production':
            app.config.from_object(ProductionConfig)
        else:
            app.config.from_object(DebugConfig)
    except ImportError:
        # Se não existir config.py, usar configuração básica
        pass

    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(lms_bp, url_prefix='/')

    @app.route('/api')
    def api_index():
        return 'SISE API rodando!'

    return app
