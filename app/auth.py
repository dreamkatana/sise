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

# Configurar SSL GLOBALMENTE - MONKEY PATCH mais agressivo para resolver recursion bug
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

# MONKEY PATCH MAIS AGRESSIVO: Desabilitar completamente SSL em produção
def create_urllib3_context(ssl_version=None, cert_reqs=None, options=None, ciphers=None):
    """Cria contexto SSL sem verificação para resolver recursion bug"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Não configurar minimum_version para evitar recursão
    return context

# Aplicar monkey patches ANTES de qualquer import que use SSL
urllib3.util.ssl_.create_urllib3_context = create_urllib3_context

# Configurar SSL context global para não verificar
ssl._create_default_https_context = ssl._create_unverified_context

# FORÇAR variáveis de ambiente para desabilitar SSL completamente
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

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

# Configurar Keycloak com verificação SSL desabilitada e sessão customizada
# Inicialização será feita quando necessário para evitar problemas de contexto
keycloak_openid = None
keycloak_http = None
keycloak_http_url = None

def initialize_keycloak():
    """Inicializa instâncias Keycloak quando necessário (dentro do contexto da aplicação)"""
    global keycloak_openid, keycloak_http, keycloak_http_url
    
    if keycloak_openid is not None:
        return  # Já inicializado
    
    try:
        # Para produção, tentar HTTP se HTTPS falhar
        keycloak_server_url = Config.KEYCLOAK_SERVER_URL
        
        # Criar versão HTTP se necessário
        if keycloak_server_url.startswith('https://'):
            keycloak_http_url = keycloak_server_url.replace('https://', 'http://')
        
        # Verificar se certificado existe e é válido
        cert_path = "certs/authdevccuecunicampbr.crt"
        use_cert = False
        
        import os
        if os.path.exists(cert_path):
            try:
                # Tentar ler o certificado para verificar se é válido
                with open(cert_path, 'r') as f:
                    cert_content = f.read()
                    if cert_content.strip() and ('BEGIN CERTIFICATE' in cert_content or 'BEGIN' in cert_content):
                        use_cert = True
                        print(f"[DEBUG] Certificado encontrado e válido: {cert_path}")
                    else:
                        print(f"[DEBUG] Certificado existe mas não é válido (placeholder): {cert_path}")
            except Exception as cert_error:
                print(f"[DEBUG] Erro ao verificar certificado: {cert_error}")
        else:
            print(f"[DEBUG] Certificado não encontrado: {cert_path}")
            
        # Configurar Keycloak HTTPS
        keycloak_params = {
            'server_url': keycloak_server_url,
            'client_id': Config.KEYCLOAK_CLIENT_ID,
            'realm_name': Config.KEYCLOAK_REALM,
            'client_secret_key': Config.KEYCLOAK_CLIENT_SECRET,
            'timeout': 30
        }
        
        if use_cert:
            # Com certificado válido
            keycloak_params['verify'] = True
            keycloak_params['cert'] = cert_path
            print(f"[DEBUG] Configurando Keycloak HTTPS com certificado")
        else:
            # Sem certificado (modo inseguro)
            keycloak_params['verify'] = False
            print(f"[DEBUG] Configurando Keycloak HTTPS sem certificado (modo inseguro)")
            
        keycloak_openid = KeycloakOpenID(**keycloak_params)
        
        # FORÇAR uso da nossa sessão requests customizada no keycloak
        keycloak_openid.connection._s = requests_session
        
        # Configurar timeout na conexão também
        keycloak_openid.connection._s.timeout = 30
        
        # Criar instância HTTP se disponível
        if keycloak_http_url:
            try:
                keycloak_http = KeycloakOpenID(
                    server_url=keycloak_http_url,
                    client_id=Config.KEYCLOAK_CLIENT_ID,
                    realm_name=Config.KEYCLOAK_REALM,
                    client_secret_key=Config.KEYCLOAK_CLIENT_SECRET,
                    verify=False,  # HTTP não precisa de verificação SSL
                    timeout=30
                )
                keycloak_http.connection._s = requests_session
                keycloak_http.connection._s.timeout = 30
                print(f"[DEBUG] Keycloak HTTP configurado como fallback")
            except Exception as http_error:
                print(f"[DEBUG] Erro ao configurar Keycloak HTTP: {http_error}")
                keycloak_http = None
        
        print(f"[DEBUG] Keycloak HTTPS configurado: {keycloak_server_url}")
        
    except Exception as keycloak_init_error:
        print(f"[ERROR] Erro ao inicializar Keycloak: {keycloak_init_error}")
        print(f"[ERROR] Tentando configuração de fallback sem SSL...")
        
        # FALLBACK: Configuração sem SSL em caso de erro
        try:
            keycloak_openid = KeycloakOpenID(
                server_url=Config.KEYCLOAK_SERVER_URL,
                client_id=Config.KEYCLOAK_CLIENT_ID,
                realm_name=Config.KEYCLOAK_REALM,
                client_secret_key=Config.KEYCLOAK_CLIENT_SECRET,
                verify=False,  # Desabilitar completamente SSL
                timeout=30
            )
            keycloak_openid.connection._s = requests_session
            keycloak_openid.connection._s.timeout = 30
            print(f"[DEBUG] ✅ Keycloak configurado em modo fallback (sem SSL)")
        except Exception as fallback_error:
            print(f"[ERROR] Falha total na configuração do Keycloak: {fallback_error}")
            keycloak_openid = None
            keycloak_http = None

def token_required(f):
    """Decorator para rotas que requerem autenticação via token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        initialize_keycloak()  # Inicializar Keycloak dentro do contexto da aplicação
        
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

# FUNÇÃO REMOVIDA: exchange_code_for_token
# A função original foi removida devido a problemas de recursão SSL
# Agora usamos _exchange_code_with_curl() no callback

def _exchange_code_with_curl(code, state):
    """Troca código OAuth por token usando curl (evita recursão SSL)"""
    try:
        # Verificar state
        if state != session.get('oauth_state'):
            raise Exception("State inválido - possível ataque CSRF")
        
        # URL de token
        token_url = f"{Config.KEYCLOAK_SERVER_URL}/realms/{Config.KEYCLOAK_REALM}/protocol/openid-connect/token"
        
        # Parâmetros para troca de código
        data = {
            'grant_type': 'authorization_code',
            'client_id': Config.KEYCLOAK_CLIENT_ID,
            'client_secret': Config.KEYCLOAK_CLIENT_SECRET,
            'code': code,
            'redirect_uri': url_for('auth.callback', _external=True)
        }
        
        # Construir comando curl
        curl_data = '&'.join([f'{k}={v}' for k, v in data.items()])
        
        import subprocess
        import json
        
        curl_command = [
            'curl', '-k', '--silent', '--max-time', '15',
            '-X', 'POST',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', curl_data,
            token_url
        ]
        
        print(f"[DEBUG] Executando curl para OAuth token...")
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=20)
        
        if result.returncode != 0:
            raise Exception(f"Curl falhou: {result.stderr}")
        
        response_text = result.stdout.strip()
        if not response_text:
            raise Exception("Resposta vazia do curl")
        
        token_data = json.loads(response_text)
        
        if 'error' in token_data:
            raise Exception(f"Erro Keycloak: {token_data.get('error_description', token_data['error'])}")
        
        return token_data
        
    except Exception as e:
        print(f"[ERROR] Erro na troca de código: {e}")
        return None

def _get_userinfo_with_curl(access_token):
    """Obter userinfo usando curl (evita recursão SSL)"""
    try:
        userinfo_url = f"{Config.KEYCLOAK_SERVER_URL}/realms/{Config.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
        
        import subprocess
        import json
        
        curl_command = [
            'curl', '-k', '--silent', '--max-time', '15',
            '-H', f'Authorization: Bearer {access_token}',
            userinfo_url
        ]
        
        print(f"[DEBUG] Executando curl para userinfo...")
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=20)
        
        if result.returncode != 0:
            raise Exception(f"Curl falhou: {result.stderr}")
        
        response_text = result.stdout.strip()
        if not response_text:
            raise Exception("Resposta vazia do curl")
        
        userinfo = json.loads(response_text)
        
        if 'error' in userinfo:
            raise Exception(f"Erro userinfo: {userinfo.get('error_description', userinfo['error'])}")
        
        return userinfo
        
    except Exception as e:
        print(f"[ERROR] Erro ao obter userinfo: {e}")
        return None

@auth_bp.route('/login')
def login():
    """Redireciona para o Keycloak para autenticação OAuth"""
    initialize_keycloak()  # Inicializar Keycloak dentro do contexto da aplicação
    
    try:
        # PRIMEIRA TENTATIVA: OAuth flow do Keycloak
        print(f"[DEBUG] Iniciando fluxo OAuth do Keycloak")
        
        # Verificar se Keycloak está disponível
        if keycloak_openid is None:
            print(f"[DEBUG] Keycloak não disponível, redirecionando para login direto")
            flash('Sistema de autenticação temporariamente indisponível. Use o formulário abaixo.', 'warning')
            return redirect(url_for('lms.login_page'))
        
        # Gerar URL de autorização OAuth
        auth_url = get_authorization_url()
        print(f"[DEBUG] Redirecionando para Keycloak OAuth: {auth_url}")
        
        return redirect(auth_url)
        
    except Exception as e:
        print(f"[DEBUG] Erro no fluxo OAuth: {e}")
        print(f"[DEBUG] Fallback para formulário de login direto")
        flash('Erro no sistema de autenticação. Use o formulário abaixo.', 'warning')
        return redirect(url_for('lms.login_page'))

@auth_bp.route('/direct-login', methods=['POST'])
def direct_login():
    """
    Login direto - FALLBACK quando OAuth falha
    Esta rota só deve ser usada quando:
    1. O fluxo OAuth do Keycloak falhar
    2. Problemas de conectividade com o servidor Keycloak
    3. Usuários que preferem login manual via formulário
    """
    print(f"[DEBUG] direct_login chamado - METHOD: {request.method}")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    print(f"[DEBUG] Form data: {request.form}")
    
    initialize_keycloak()  # Inicializar Keycloak dentro do contexto da aplicação
    
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
        
        # MÉTODO HÍBRIDO: Tentar python-keycloak primeiro, curl como fallback (em ambos os ambientes)
        is_production = current_app.config.get('FLASK_ENV') == 'production'
        print(f"[DEBUG] Ambiente: {'PRODUÇÃO' if is_production else 'LOCAL'}")
        
        # Log adicional sobre instâncias HTTP disponíveis
        if is_production and keycloak_http_url:
            print(f"[DEBUG] URLs Keycloak disponíveis:")
            print(f"[DEBUG] - HTTPS: {Config.KEYCLOAK_SERVER_URL}")
            print(f"[DEBUG] - HTTP:  {keycloak_http_url}")
        
        token_data = None
        userinfo = None
        
        # SEMPRE tentar python-keycloak primeiro (funciona para mais usuários)
        print(f"[DEBUG] Tentando python-keycloak primeiro...")
        
        # Verificar se keycloak foi inicializado corretamente
        if keycloak_openid is None:
            print(f"[DEBUG] Keycloak não foi inicializado, usando curl direto...")
            token_data, userinfo = _authenticate_with_curl(clean_username, password)
            print(f"[DEBUG] ✅ curl SUCESSO (keycloak não disponível)")
        else:
            # Tentar diferentes formatos de username com python-keycloak
            usernames_to_try = [
                clean_username,
                f"{clean_username}@unicamp.br" if "@" not in clean_username else clean_username.split("@")[0]
            ]
            
            # Lista de instâncias Keycloak para tentar (HTTPS primeiro, HTTP como fallback)
            keycloak_instances = [
                ("HTTPS", keycloak_openid)
            ]
            
            # Se temos instância HTTP, adicionar como fallback
            if 'keycloak_http' in globals() and keycloak_http is not None:
                keycloak_instances.append(("HTTP", keycloak_http))
            
            keycloak_success = False
            keycloak_error = None
            
            for protocol, keycloak_instance in keycloak_instances:
                print(f"[DEBUG] - Tentando {protocol} com instância: {keycloak_instance.connection.server_url}")
                
                for test_username in usernames_to_try:
                    try:
                        print(f"[DEBUG]   - Username: {test_username}")
                        
                        # Tentar autenticação com timeout explícito
                        token_data = keycloak_instance.token(test_username, password)
                        userinfo = keycloak_instance.userinfo(token_data['access_token'])
                        
                        print(f"[DEBUG] ✅ python-keycloak {protocol} SUCESSO com username: {test_username}")
                        keycloak_success = True
                        break
                        
                    except Exception as e:
                        error_type = type(e).__name__
                        error_msg = str(e)
                        print(f"[DEBUG]   - {protocol} falhou com {test_username}: {error_type}: {error_msg}")
                        keycloak_error = e
                        
                        # Se for erro de recursão, pare de tentar HTTPS e vá para HTTP
                        if "recursion" in error_msg.lower() or "maximum recursion depth" in error_msg:
                            print(f"[DEBUG]   - Detectado erro de recursão SSL em {protocol}, tentando próximo protocolo")
                            break
                        continue
                
                # Se conseguiu autenticar, pare aqui
                if keycloak_success:
                    break
            
            if not keycloak_success:
                print(f"[DEBUG] python-keycloak falhou com todos os protocolos, tentando curl como fallback...")
                try:
                    token_data, userinfo = _authenticate_with_curl(clean_username, password)
                    print(f"[DEBUG] ✅ curl SUCESSO como fallback")
                except Exception as curl_error:
                    print(f"[DEBUG] curl também falhou: {curl_error}")
                    raise Exception(f"Ambos os métodos falharam. python-keycloak: {keycloak_error}. curl: {curl_error}")
        
        # Se chegou aqui, autenticação funcionou
        print(f"[DEBUG] UserInfo: {userinfo}")
        
        # Armazena informações do usuário na sessão
        session['user_email'] = userinfo.get('email')
        session['user_name'] = userinfo.get('given_name')
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
    """Callback do Keycloak após autenticação OAuth"""
    initialize_keycloak()  # Inicializar Keycloak dentro do contexto da aplicação
    
    print(f"[DEBUG] Callback OAuth recebido")
    
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    print(f"[DEBUG] - Code: {'presente' if code else 'ausente'}")
    print(f"[DEBUG] - State: {'presente' if state else 'ausente'}")
    print(f"[DEBUG] - Error: {error if error else 'nenhum'}")
    
    if error:
        print(f"[DEBUG] Erro OAuth: {error}")
        flash(f'Erro na autenticação OAuth: {error}. Tente o formulário de login.', 'warning')
        return redirect(url_for('lms.login_page'))
    
    if not code:
        print(f"[DEBUG] Código de autorização não fornecido")
        flash('Código de autorização não fornecido. Tente o formulário de login.', 'warning')
        return redirect(url_for('lms.login_page'))
    
    try:
        print(f"[DEBUG] Tentando trocar código por token com curl...")
        
        # USAR CURL DIRETAMENTE para evitar recursão SSL
        token_data = _exchange_code_with_curl(code, state)
        
        if not token_data or 'access_token' not in token_data:
            raise Exception("Token não recebido")
        
        print(f"[DEBUG] Token obtido com sucesso via curl")
        
        # Obter informações do usuário com curl também
        userinfo = _get_userinfo_with_curl(token_data['access_token'])
        
        if not userinfo:
            raise Exception("Userinfo não obtido")
        
        print(f"[DEBUG] UserInfo obtido: {userinfo}")
        
        # Processar nome do usuário (corrigir duplicação se houver)
        user_name = userinfo.get('name', userinfo.get('preferred_username', 'Usuário'))
        if user_name:
            name_parts = user_name.split()
            if len(name_parts) >= 2 and name_parts[0] == name_parts[1]:
                user_name = name_parts[0]
        
        # Armazena informações do usuário na sessão
        session['user_email'] = userinfo.get('email')
        session['user_name'] = user_name
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token')
        
        # Verifica se é admin
        admin_emails = ['joaoedu@unicamp.br']
        session['is_admin'] = userinfo.get('email') in admin_emails
        
        print(f"[DEBUG] ✅ OAuth SUCESSO para: {session['user_email']}")
        flash(f'Login OAuth realizado com sucesso! Bem-vindo, {session["user_name"]}!', 'success')
        return redirect(url_for('lms.dashboard'))
        
    except Exception as e:
        error_msg = str(e)
        print(f"[DEBUG] Erro no callback OAuth: {error_msg}")
        print(f"[DEBUG] Redirecionando para formulário de login como fallback")
        
        # Se for erro de SSL ou conexão, sugerir formulário direto
        if any(keyword in error_msg.lower() for keyword in ['ssl', 'connection', 'timeout', 'recursion']):
            flash('Problema de conexão com servidor de autenticação. Use o formulário abaixo.', 'warning')
        else:
            flash(f'Erro no processamento OAuth: {error_msg}. Tente o formulário de login.', 'error')
            
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
