from app import create_app

app = create_app()
#PRODUCAO
#app = create_app('Production')

if __name__ == '__main__':
    # Configuração específica para debug no VS Code
    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)
