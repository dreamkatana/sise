"""
App de teste completo para debug de blueprints
"""
from flask import Flask
from test_courses_debug import simple_courses_bp

def create_test_app():
    app = Flask(__name__)
    
    # Registra o blueprint de teste
    app.register_blueprint(simple_courses_bp, url_prefix='/api')
    
    @app.route('/')
    def home():
        # BREAKPOINT AQUI TAMBÉM ↓
        return "App de teste rodando!"
    
    return app

if __name__ == '__main__':
    app = create_test_app()
    print("=== INSTRUÇÕES DE TESTE ===")
    print("1. Coloque breakpoints nos arquivos:")
    print("   - test_courses_debug.py (linhas 11 e 21)")
    print("   - test_full_debug.py (linha 14)")
    print("2. Acesse:")
    print("   - http://127.0.0.1:5002/ (teste home)")
    print("   - http://127.0.0.1:5002/api/test-courses (teste blueprint)")
    print("   - http://127.0.0.1:5002/api/test-courses-2 (teste blueprint 2)")
    print("==============================")
    
    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5002)