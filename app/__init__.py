from flask import Flask, g
from app.auth import auth_bp
from app.courses import courses_bp

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config/config.py')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')

    @app.teardown_appcontext
    def teardown_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.route('/')
    def index():
        return 'SISE Flask rodando!'

    return app
