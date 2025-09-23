from flask import Blueprint, request, jsonify, g, session, redirect, url_for, flash
from keycloak import KeycloakOpenID
from config.config import Config
from functools import wraps
import secrets
import base64
import urllib.parse
import requests

auth_bp = Blueprint('auth', __name__)

keycloak_openid = KeycloakOpenID(
    server_url=Config.KEYCLOAK_SERVER_URL,
    client_id=Config.KEYCLOAK_CLIENT_ID,
    realm_name=Config.KEYCLOAK_REALM,
    client_secret_key=Config.KEYCLOAK_CLIENT_SECRET
)

def token_required(f):
    """Decorator para rotas que requerem autenticação via token"""
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

def login_required(f):
    """Decorator para rotas web que requerem login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_email' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('lms.login'))
        return f(*args, **kwargs)
    return decorated

def get_authorization_url():
    """Gera URL de autorização do Keycloak"""
    # Gera um state único para segurança
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # URL de redirecionamento após login
    redirect_uri = url_for('auth.callback', _external=True)
    
    # Constrói a URL de autorização manualmente (método mais compatível)
    auth_url = f"{Config.KEYCLOAK_SERVER_URL}/realms/{Config.KEYCLOAK_REALM}/protocol/openid-connect/auth"
    
    # Parâmetros da URL
    params = {
        'client_id': Config.KEYCLOAK_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state
    }
    
    # Codifica os parâmetros
    auth_url += '?' + urllib.parse.urlencode(params)
    
    return auth_url

def exchange_code_for_token(code, state):
    """Troca o código de autorização por um token"""
    # Verifica o state para segurança
    if state != session.get('oauth_state'):
        raise Exception("State inválido - possível ataque CSRF")
    
    # URL de redirecionamento (deve ser a mesma usada na autorização)
    redirect_uri = url_for('auth.callback', _external=True)
    
    try:
        # Troca o código pelo token usando a biblioteca python-keycloak
        token = keycloak_openid.token(
            grant_type='authorization_code',
            code=code,
            redirect_uri=redirect_uri
        )
        return token
    except Exception as e:
        # Se falhar com a biblioteca, tenta fazer request direto
        token_url = f"{Config.KEYCLOAK_SERVER_URL}/realms/{Config.KEYCLOAK_REALM}/protocol/openid-connect/token"
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': Config.KEYCLOAK_CLIENT_ID,
            'client_secret': Config.KEYCLOAK_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao trocar código por token: {response.text}")

@auth_bp.route('/login')
def login():
    """Redireciona para o Keycloak para autenticação"""
    # Para desenvolvimento local, usa formulário de login direto
    # Em produção, mudaria para redirect para Keycloak
    return redirect(url_for('lms.login_page'))

@auth_bp.route('/direct-login', methods=['POST'])
def direct_login():
    """Login direto usando Resource Owner Password Credentials (para desenvolvimento)"""
    try:
        username = request.form.get('username') or request.json.get('username')
        password = request.form.get('password') or request.json.get('password')
        
        if not username or not password:
            flash('Username e password são obrigatórios', 'error')
            return redirect(url_for('lms.login_page'))
        
        # Faz login direto no Keycloak usando Resource Owner Password Credentials
        token_data = keycloak_openid.token(username, password)
        
        # Obtém informações do usuário
        userinfo = keycloak_openid.userinfo(token_data['access_token'])
        
        # Armazena informações do usuário na sessão
        session['user_email'] = userinfo.get('email')
        session['user_name'] = userinfo.get('name', userinfo.get('preferred_username'))
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token')
        
        # Verifica se é admin
        admin_emails = ['joaoedu@unicamp.br']
        session['is_admin'] = userinfo.get('email') in admin_emails
        
        flash(f'Login realizado com sucesso! Bem-vindo, {session["user_name"]}!', 'success')
        
        # Resposta diferente para requests AJAX vs formulário
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': url_for('lms.dashboard'),
                'user': {
                    'email': session['user_email'],
                    'name': session['user_name'],
                    'is_admin': session['is_admin']
                }
            })
        else:
            return redirect(url_for('lms.dashboard'))
        
    except Exception as e:
        error_msg = f'Erro ao fazer login: {str(e)}'
        flash(error_msg, 'error')
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': error_msg}), 401
        else:
            return redirect(url_for('lms.login_page'))

@auth_bp.route('/callback')
def callback():
    """Callback do Keycloak após autenticação"""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        flash(f'Erro na autenticação: {error}', 'error')
        return redirect(url_for('lms.login_page'))
    
    if not code:
        flash('Código de autorização não fornecido', 'error')
        return redirect(url_for('lms.login_page'))
    
    try:
        # Troca o código pelo token
        token_data = exchange_code_for_token(code, state)
        
        # Obtém informações do usuário
        userinfo = keycloak_openid.userinfo(token_data['access_token'])
        
        # Armazena informações do usuário na sessão
        session['user_email'] = userinfo.get('email')
        session['user_name'] = userinfo.get('name', userinfo.get('preferred_username'))
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token')
        
        # Verifica se é admin (você pode ajustar esta lógica)
        admin_emails = ['joaoedu@unicamp.br']  # Configure conforme necessário
        session['is_admin'] = userinfo.get('email') in admin_emails
        
        flash(f'Login realizado com sucesso! Bem-vindo, {session["user_name"]}!', 'success')
        return redirect(url_for('lms.dashboard'))
        
    except Exception as e:
        flash(f'Erro ao processar login: {str(e)}', 'error')
        return redirect(url_for('lms.login_page'))

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    user_name = session.get('user_name', 'Usuário')
    
    # Tenta fazer logout no Keycloak se tiver refresh token
    try:
        if 'refresh_token' in session:
            keycloak_openid.logout(session['refresh_token'])
    except Exception as e:
        print(f"Erro ao fazer logout no Keycloak: {e}")
    
    # Limpa a sessão
    session.clear()
    
    flash(f'Logout realizado com sucesso! Até logo, {user_name}!', 'success')
    return redirect(url_for('lms.login_page'))

# Rotas de API (mantidas para compatibilidade)
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """Login via API (para uso com aplicações que consomem API)"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    try:
        token = keycloak_openid.token(username, password)
        userinfo = keycloak_openid.userinfo(token['access_token'])
        return jsonify({"token": token, "userinfo": userinfo})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/api/protected', methods=['GET'])
@token_required
def api_protected():
    """Rota protegida para API"""
    return jsonify({'message': 'Acesso autorizado!', 'user': g.user}), 200
