"""
Teste simples para verificar breakpoints em blueprints
"""
from flask import Flask, Blueprint, jsonify

app = Flask(__name__)

# Blueprint de teste
test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test_route():
    # COLOQUE UM BREAKPOINT NESTA LINHA ↓
    message = "Teste de breakpoint funcionando!"
    print(f"Debug: {message}")  # Esta linha deve aparecer no console
    return jsonify({"status": "success", "message": message})

@app.route('/')
def home():
    # COLOQUE UM BREAKPOINT NESTA LINHA ↓
    return "App funcionando!"

# Registra o blueprint
app.register_blueprint(test_bp, url_prefix='/api')

if __name__ == '__main__':
    print("Iniciando servidor de teste...")
    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5001)