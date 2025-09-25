from flask import Blueprint, request, jsonify, g, session, redirect, url_for, flash, current_app
from keycloak import KeycloakOpenID
from config.config import Config
from functools import wraps
import secrets
import base64
import urllib.parse
import requests
import ssl
import urllib3
import traceback

# Configurar SSL GLOBALMENTE - MONKEY PATCH para resolver recursion bug
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# MONKEY PATCH: Forçar SSL context sem verificação
def create_urllib3_context(ssl_version=None, cert_reqs=None, options=None, ciphers=None):
    """Cria contexto SSL sem verificação para resolver recursion bug"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Remove a configuração que causa recursão - NÃO configurar minimum_version
    return context

# Aplicar monkey patch ANTES de qualquer import que use SSL
urllib3.util.ssl_.create_urllib3_context = create_urllib3_context

# Configurar SSL context global 
ssl._create_default_https_context = ssl._create_unverified_context

# Desabilitar warnings SSL (apenas os que existem)
try:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except AttributeError:
    pass

try:
    urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
except AttributeError:
    pass

try:
    urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
except AttributeError:
    pass

# Configurar sessão requests com SSL desabilitado
requests_session = requests.Session()
requests_session.verify = False

# Configurar adapter com retry e SSL desabilitado
adapter = HTTPAdapter(
    max_retries=Retry(
        total=3,
        status_forcelist=[500, 502, 503, 504],
        backoff_factor=1
    )
)
requests_session.mount("http://", adapter)
requests_session.mount("https://", adapter)

auth_bp = Blueprint('auth', __name__)

def url_for_with_prefix(endpoint, **values):
    """url_for que força o prefixo /pdg em produção"""
    url = url_for(endpoint, **values)
    # Se estamos em produção e a URL não começa com /pdg, adiciona
    if current_app.config.get('APPLICATION_ROOT') == '/pdg':
        if not url.startswith('/pdg') and not url.startswith('http'):
            url = '/pdg' + url
    return url

# Configurar Keycloak com verificação SSL desabilitada
keycloak_openid = KeycloakOpenID(
    server_url=Config.KEYCLOAK_SERVER_URL,
    client_id=Config.KEYCLOAK_CLIENT_ID,
    realm_name=Config.KEYCLOAK_REALM,
    client_secret_key=Config.KEYCLOAK_CLIENT_SECRET,
    verify=False  # Desabilitar verificação SSL para resolver bug do Python 3.13
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
    """Login direto - método otimizado por ambiente"""
    print(f"[DEBUG] direct_login chamado - METHOD: {request.method}")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    print(f"[DEBUG] Form data: {request.form}")
    
    try:
        username = request.form.get('username') or request.json.get('username')
        password = request.form.get('password') or request.json.get('password')
        
        print(f"[DEBUG] Username: {username}, Password: {'***' if password else None}")
        
        if not username or not password:
            flash('Username e password são obrigatórios', 'error')
            return redirect(url_for('lms.login_page'))
        
        # Processar username - se vier com @unicamp.br, remover para testar
        clean_username = username.replace('@unicamp.br', '') if '@unicamp.br' in username else username
        print(f"[DEBUG] Clean username: {clean_username}")
        
        # DETECÇÃO INTELIGENTE: Produção usa CURL, Local usa python-keycloak
        is_production = current_app.config.get('FLASK_ENV') == 'production'
        print(f"[DEBUG] Ambiente: {'PRODUÇÃO' if is_production else 'LOCAL'}")
        
        token_data = None
        userinfo = None
        
        if is_production:
            # PRODUÇÃO: Usar CURL direto (sabemos que funciona)
            print(f"[DEBUG] PRODUÇÃO: Usando método CURL...")
            token_data, userinfo = _authenticate_with_curl(clean_username, password)
        else:
            # LOCAL: Tentar python-keycloak primeiro, curl como fallback
            print(f"[DEBUG] LOCAL: Tentando python-keycloak primeiro...")
            try:
                token_data = keycloak_openid.token(clean_username, password)
                userinfo = keycloak_openid.userinfo(token_data['access_token'])
                print(f"[DEBUG] LOCAL: python-keycloak SUCESSO")
            except Exception as e:
                print(f"[DEBUG] LOCAL: python-keycloak falhou ({e}), usando curl...")
                token_data, userinfo = _authenticate_with_curl(clean_username, password)
        
        # Se chegou aqui, autenticação funcionou
        print(f"[DEBUG] UserInfo: {userinfo}")
        
        # Armazena informações do usuário na sessão
        session['user_email'] = userinfo.get('email')
        session['user_name'] = userinfo.get('name', userinfo.get('preferred_username', userinfo.get('given_name', 'Usuário')))
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token')
        
        # Verifica se é admin
        admin_emails = ['joaoedu@unicamp.br']
        session['is_admin'] = userinfo.get('email') in admin_emails
        
        print(f"[DEBUG] Sessão criada para: {session['user_email']}")
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
            print(f"[DEBUG] Redirecionando para dashboard...")
            return redirect(url_for('lms.dashboard'))
        
    except Exception as e:
        error_msg = f'{str(e)}'
        print(f"[ERROR] {error_msg}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        flash(error_msg, 'error')
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': error_msg}), 401
        else:
            return redirect(url_for('lms.login_page'))

def _authenticate_with_curl(username, password):
    """Autenticação usando curl diretamente (para contornar problemas de SSL)"""
    import subprocess
    import json
    
    # Corrigir URL - remover barra dupla
    base_url = Config.KEYCLOAK_SERVER_URL.rstrip('/')
    token_url = f"{base_url}/realms/{Config.KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    # Testar diferentes formatos de username
    usernames_to_try = [
        username,
        f"{username}@unicamp.br" if "@" not in username else username.split("@")[0]
    ]
    
    for test_username in usernames_to_try:
        print(f"[DEBUG] - Testando curl com username: {test_username}")
        
        # Preparar dados do token
        token_data = {
            'grant_type': 'password',
            'client_id': Config.KEYCLOAK_CLIENT_ID,
            'client_secret': Config.KEYCLOAK_CLIENT_SECRET,
            'username': test_username,
            'password': password
        }
        
        # Construir comando curl para token
        curl_token_cmd = [
            'curl', '-k', '-X', 'POST',
            f'{token_url}',
            '-H', 'Content-Type: application/x-www-form-urlencoded'
        ]
        
        # Adicionar dados do formulário
        for key, value in token_data.items():
            curl_token_cmd.extend(['-d', f'{key}={value}'])
        
        try:
            # Executar comando para obter token
            print(f"[DEBUG] - Executando comando curl para token...")
            result = subprocess.run(curl_token_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"[DEBUG] - Curl falhou (código {result.returncode}): {result.stderr}")
                continue
            
            # Parsear resposta do token
            try:
                token_response = json.loads(result.stdout)
                if 'access_token' not in token_response:
                    print(f"[DEBUG] - Token não encontrado na resposta: {result.stdout}")
                    continue
            except json.JSONDecodeError as e:
                print(f"[DEBUG] - Erro ao parsear JSON do token: {e}")
                continue
            
            # Obter informações do usuário
            access_token = token_response['access_token']
            userinfo_url = f"{base_url}/realms/{Config.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
            curl_userinfo_cmd = [
                'curl', '-k', '-X', 'GET',
                f'{userinfo_url}',
                '-H', f'Authorization: Bearer {access_token}'
            ]
            
            print(f"[DEBUG] - Executando comando curl para userinfo...")
            userinfo_result = subprocess.run(curl_userinfo_cmd, capture_output=True, text=True, timeout=30)
            
            if userinfo_result.returncode != 0:
                print(f"[DEBUG] - Curl userinfo falhou: {userinfo_result.stderr}")
                continue
            
            try:
                userinfo = json.loads(userinfo_result.stdout)
                print(f"[DEBUG] ✅ CURL SUCESSO com username {test_username}")
                return token_response, userinfo
                
            except json.JSONDecodeError as e:
                print(f"[DEBUG] - Erro ao parsear JSON do userinfo: {e}")
                continue
                
        except subprocess.TimeoutExpired:
            print(f"[DEBUG] - Timeout no curl")
            continue
        except Exception as e:
            print(f"[DEBUG] - Erro inesperado: {e}")
            continue
    
    # Se chegou aqui, todas as tentativas falharam
    raise Exception("Falha na autenticação via curl")

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
    
    # Debug: log da URL atual
    print(f"DEBUG: logout chamado, URL: {request.url}")
    print(f"DEBUG: request.host: {request.host}")
    print(f"DEBUG: request.path: {request.path}")
    print(f"DEBUG: APPLICATION_ROOT: {current_app.config.get('APPLICATION_ROOT')}")
    
    # Tenta fazer logout no Keycloak se tiver refresh token
    try:
        if 'refresh_token' in session:
            keycloak_openid.logout(session['refresh_token'])
    except Exception as e:
        print(f"Erro ao fazer logout no Keycloak: {e}")
    
    # Limpa a sessão
    session.clear()
    
    flash(f'Logout realizado com sucesso! Até logo, {user_name}!', 'success')
    return redirect(url_for_with_prefix('lms.login_page'))

@auth_bp.route('/debug-urls')
def debug_urls():
    """Endpoint para debug das URLs"""
    return jsonify({
        'logout_url_relative': url_for('auth.logout'),
        'logout_url_relative_fixed': url_for_with_prefix('auth.logout'),
        'logout_url_external': url_for('auth.logout', _external=True),
        'login_url': url_for('lms.login_page'),
        'login_url_fixed': url_for_with_prefix('lms.login_page'),
        'current_url': request.url,
        'script_name': request.environ.get('SCRIPT_NAME', ''),
        'application_root': current_app.config.get('APPLICATION_ROOT'),
        'server_name': current_app.config.get('SERVER_NAME'),
        'blueprint_prefix': auth_bp.url_prefix
    })

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
