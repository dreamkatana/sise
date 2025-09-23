import os
from app import create_app

# Detecta automaticamente o ambiente
config_name = 'Production' if os.getenv('FLASK_ENV') == 'production' else 'Debug'
app = create_app(config_name)

if __name__ == '__main__':
    # Configuração específica para debug no VS Code (desenvolvimento)
    if config_name == 'Debug':
        app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)
    else:
        # Em produção, usar Gunicorn ao invés do Flask dev server
        print("⚠️  Para produção, use: gunicorn --config gunicorn.conf.py wsgi:app")
        app.run(debug=False, host='0.0.0.0', port=5006)
