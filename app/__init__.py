from flask import Flask
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

    # Registrar blueprints
    from app.auth import auth_bp
    from app.courses import courses_bp
    from app.lms import lms_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(lms_bp, url_prefix='/')

    @app.route('/')
    def index():
        return 'SISE Flask rodando!'

    @app.route('/api')
    def api_index():
        return 'SISE API rodando!'

    return app
