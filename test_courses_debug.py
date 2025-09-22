"""
Teste específico para breakpoints em courses
"""
from flask import Blueprint, jsonify

# Blueprint de teste
simple_courses_bp = Blueprint('simple_courses', __name__)

@simple_courses_bp.route('/test-courses')
def test_courses():
    # COLOQUE UM BREAKPOINT AQUI ↓
    print("DEBUG: Função test_courses chamada!")
    data = {
        "message": "Breakpoint teste em courses!",
        "status": "working"
    }
    return jsonify(data)

@simple_courses_bp.route('/test-courses-2')
def test_courses_2():
    # COLOQUE UM BREAKPOINT AQUI ↓
    result = "Segunda função de teste"
    print(f"DEBUG: {result}")
    return jsonify({"result": result})