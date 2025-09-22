"""
Arquivo de teste para verificar breakpoints
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test-breakpoint')
def test_breakpoint():
    # Coloque um breakpoint nesta linha
    message = "Breakpoint teste!"
    return jsonify({"message": message})

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)