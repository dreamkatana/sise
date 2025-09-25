from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from app.extensions import db
from config.config import DebugConfig, ProductionConfig
import os

def create_app(config_name='Debug'):
    app = Flask(__name__)

    # Carrega a configuração correta
    if config_name == 'Production':
        app.config.from_object(ProductionConfig)
        
        # Força o APPLICATION_ROOT ANTES de aplicar ProxyFix
        app.config['APPLICATION_ROOT'] = '/pdg'
        
        # Aplica ProxyFix para funcionamento correto com nginx
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1,
            x_prefix=1
        )
        
        # CORREÇÃO: Middleware para adicionar APPLICATION_ROOT nas URLs
        def add_application_root(app):
            def middleware(environ, start_response):
                # Adiciona o prefixo /pdg ao SCRIPT_NAME para que o Flask saiba sobre o prefixo
                if not environ.get('SCRIPT_NAME', '').startswith('/pdg'):
                    environ['SCRIPT_NAME'] = '/pdg' + environ.get('SCRIPT_NAME', '')
                return app(environ, start_response)
            return middleware
        
        app.wsgi_app = add_application_root(app.wsgi_app)
        
        # Debug: confirmar APPLICATION_ROOT
        print(f"[CONFIG] APPLICATION_ROOT configurado como: {app.config.get('APPLICATION_ROOT')}")
            
    else:
        app.config.from_object(DebugConfig)
        # Em desenvolvimento, APPLICATION_ROOT pode vir da env ou ser /
        app.config['APPLICATION_ROOT'] = os.getenv('APPLICATION_ROOT', '/')
        print(f"[CONFIG-LOCAL] APPLICATION_ROOT: {app.config.get('APPLICATION_ROOT')}")

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
