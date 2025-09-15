from flask import Blueprint, request, jsonify, current_app
from keycloak import KeycloakOpenID
import config.config as config
import jwt
from functools import wraps

auth_bp = Blueprint('auth', __name__)

keycloak_openid = KeycloakOpenID(
    server_url=config.KEYCLOAK_SERVER_URL,
    client_id=config.KEYCLOAK_CLIENT_ID,
    realm_name=config.KEYCLOAK_REALM,
    client_secret_key=config.KEYCLOAK_CLIENT_SECRET
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
            # Valida o token usando o endpoint do Keycloak
            keycloak_openid.introspect(token)
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
