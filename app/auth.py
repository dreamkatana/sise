from flask import Blueprint, request, jsonify, g
from keycloak import KeycloakOpenID
from config.config import Config  # Alteração para importar a classe Config
from functools import wraps

auth_bp = Blueprint('auth', __name__)

keycloak_openid = KeycloakOpenID(
    server_url=Config.KEYCLOAK_SERVER_URL,
    client_id=Config.KEYCLOAK_CLIENT_ID,
    realm_name=Config.KEYCLOAK_REALM,
    client_secret_key=Config.KEYCLOAK_CLIENT_SECRET
)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        try:
            # Valida o token e obtém informações do usuário
            userinfo = keycloak_openid.userinfo(token)
            g.user = userinfo
        except Exception as e:
            return jsonify({'error': 'Token inválido ou expirado', 'details': str(e)}), 401
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    try:
        token = keycloak_openid.token(username, password)
        userinfo = keycloak_openid.userinfo(token['access_token'])
        return jsonify({"token": token, "userinfo": userinfo})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'Acesso autorizado!'}), 200
