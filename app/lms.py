from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from app.models import CursoAperf, FichaCol, CursoAperfCol, FrequenciaTurma
from app.extensions import db
from app.auth import login_required
from sqlalchemy import case, and_, func, desc
from datetime import datetime, timedelta
import json

lms_bp = Blueprint('lms', __name__)

def load_course_config():
    """Carrega configuração dos cursos do arquivo JSON"""
    try:
        with open('course_config.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'codcua_order': [], 'admin_emails': ['joaoedu@unicamp.br']}

def save_course_config(config):
    """Salva configuração dos cursos no arquivo JSON"""
    with open('course_config.json', 'w') as f:
        json.dump(config, f, indent=4)

def get_user_courses(user_email):
    """Busca cursos do usuário baseado no email"""
    # COLOQUE UM BREAKPOINT NESTA LINHA ↓
    print(f"DEBUG: Buscando cursos para o email: {user_email}")
    
    try:
        course_config = load_course_config()
        codcua_order = course_config.get('codcua_order', [])

        # COLOQUE UM BREAKPOINT NESTA LINHA ↓  
        print(f"DEBUG: Configuração carregada - códigos: {codcua_order}")

        query = db.session.query(
            FichaCol.NUMCAD.label('MATRICULA'),
            CursoAperf.CODCUA.label('CÓDIGO CURSO'),
            CursoAperfCol.TMACUA.label('CÓDIGO TURMA'),
            CursoAperf.NOMCUA.label('NOME CURSO'),
            CursoAperfCol.PERINI.label('DATA INICIO'),
            CursoAperfCol.PERFIM.label('DATA FINAL'),
            CursoAperfCol.DESSITCUA.label('SITUACAO DA TURMA'),
            CursoAperfCol.CARHOR.label('CARGA HORÁRIA'),
            FrequenciaTurma.QTDFAL.label('QUANTIDADE DE FALTAS'),
            FrequenciaTurma.HORFAL.label('HORAS_FALTA')
        ).join(
            CursoAperfCol,
            and_(FichaCol.TIPCOL == CursoAperfCol.TIPCOL, FichaCol.NUMCAD == CursoAperfCol.NUMCAD)
        ).join(
            CursoAperf,
            CursoAperf.CODCUA == CursoAperfCol.CODCUA
        ).join(
            FrequenciaTurma,
            and_(
                FichaCol.TIPCOL == FrequenciaTurma.TIPCOL,
                FichaCol.NUMCAD == FrequenciaTurma.NUMCAD,
                CursoAperfCol.CODCUA == FrequenciaTurma.CODCUA,
                CursoAperfCol.TMACUA == FrequenciaTurma.TMACUA
            )
        ).filter(FichaCol.EMACOM == user_email)

        if codcua_order:
            query = query.filter(CursoAperf.CODCUA.in_(codcua_order))
            order_logic = case(
                {codcua: index for index, codcua in enumerate(codcua_order)},
                value=CursoAperf.CODCUA
            )
            query = query.order_by(order_logic)

        results = query.all()
        courses = [dict(row._mapping) for row in results]
        
        # Adicionar status dos cursos baseado nas datas
        now = datetime.now()
        for course in courses:
            # Dividir carga horária por 60 para obter o valor correto
            if course['CARGA HORÁRIA'] is not None:
                course['CARGA HORÁRIA'] = course['CARGA HORÁRIA'] / 60
            
            # Calcular porcentagem de progresso para cursos em andamento
            if course['DATA FINAL'] and course['DATA FINAL'] < now:
                course['status'] = 'completed'
                course['progress_percentage'] = 100
            elif course['DATA INICIO'] and course['DATA INICIO'] > now:
                course['status'] = 'upcoming'
                course['progress_percentage'] = 0
            else:
                course['status'] = 'progress'
                # Calcular porcentagem baseada nas datas
                if course['DATA INICIO'] and course['DATA FINAL']:
                    data_inicio = course['DATA INICIO']
                    data_final = course['DATA FINAL']
                    total_days = (data_final - data_inicio).days
                    elapsed_days = (now - data_inicio).days
                    
                    if total_days > 0:
                        progress = min(max((elapsed_days / total_days) * 100, 0), 100)
                        course['progress_percentage'] = round(progress, 1)
                    else:
                        course['progress_percentage'] = 50  # Fallback se as datas forem iguais
                else:
                    course['progress_percentage'] = 50  # Fallback se não houver datas
                
        return courses
    except Exception as e:
        print(f"Erro ao buscar cursos: {e}")
        return []

def get_course_stats(courses):
    """Calcula estatísticas dos cursos"""
    stats = {
        'em_andamento': 0,
        'concluidos': 0,
        'proximos': 0,
        'total_horas': 0
    }
    
    for course in courses:
        if course['status'] == 'progress':
            stats['em_andamento'] += 1
        elif course['status'] == 'completed':
            stats['concluidos'] += 1
        elif course['status'] == 'upcoming':
            stats['proximos'] += 1
            
        if course['CARGA HORÁRIA']:
            stats['total_horas'] += course['CARGA HORÁRIA']
    
    return stats

def create_dummy_data():
    """Cria dados dummy para demonstração"""
    # Esta função seria chamada para popular o banco com dados de exemplo
    # Para o MVP, vamos usar dados estáticos
    now = datetime.now()
    
    dummy_courses = [
        {
            'MATRICULA': 12345,
            'CÓDIGO CURSO': 101,
            'CÓDIGO TURMA': 1,
            'NOME CURSO': 'Python para Iniciantes',
            'DATA INICIO': now - timedelta(days=30),
            'DATA FINAL': now + timedelta(days=30),
            'SITUACAO DA TURMA': 'Em andamento',
            'CARGA HORÁRIA': 40,
            'QUANTIDADE DE FALTAS': 2,
            'HORAS_FALTA': 4,
            'status': 'progress'
        },
        {
            'MATRICULA': 12345,
            'CÓDIGO CURSO': 102,
            'CÓDIGO TURMA': 1,
            'NOME CURSO': 'Banco de Dados Fundamentals',
            'DATA INICIO': now - timedelta(days=90),
            'DATA FINAL': now - timedelta(days=30),
            'SITUACAO DA TURMA': 'Concluído',
            'CARGA HORÁRIA': 32,
            'QUANTIDADE DE FALTAS': 0,
            'HORAS_FALTA': 0,
            'status': 'completed'
        },
        {
            'MATRICULA': 12345,
            'CÓDIGO CURSO': 103,
            'CÓDIGO TURMA': 1,
            'NOME CURSO': 'Desenvolvimento Web Avançado',
            'DATA INICIO': now + timedelta(days=15),
            'DATA FINAL': now + timedelta(days=75),
            'SITUACAO DA TURMA': 'Aguardando início',
            'CARGA HORÁRIA': 60,
            'QUANTIDADE DE FALTAS': None,
            'HORAS_FALTA': None,
            'status': 'upcoming'
        }
    ]
    
    # Aplicar o mesmo cálculo de progresso usado na função get_user_courses
    for course in dummy_courses:
        if course['status'] == 'completed':
            course['progress_percentage'] = 100
        elif course['status'] == 'upcoming':
            course['progress_percentage'] = 0
        else:  # progress
            if course['DATA INICIO'] and course['DATA FINAL']:
                data_inicio = course['DATA INICIO']
                data_final = course['DATA FINAL']
                total_days = (data_final - data_inicio).days
                elapsed_days = (now - data_inicio).days
                
                if total_days > 0:
                    progress = min(max((elapsed_days / total_days) * 100, 0), 100)
                    course['progress_percentage'] = round(progress, 1)
                else:
                    course['progress_percentage'] = 50
            else:
                course['progress_percentage'] = 50
    
    return dummy_courses

@lms_bp.route('/login')
def login_page():
    """Página de login - apenas exibe a página, o login real é feito pelo Keycloak"""
    # Se o usuário já está logado, redireciona para o dashboard
    if 'user_email' in session:
        return redirect(url_for('lms.dashboard'))
    
    return render_template('login.html')

@lms_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Mantém compatibilidade - redireciona para login_page"""
    return redirect(url_for('lms.login_page'))

@lms_bp.route('/logout/ajax', methods=['POST'])
def logout_ajax():
    """Endpoint para logout via AJAX - redireciona para logout do auth"""
    if 'user_email' in session:
        return jsonify({
            'success': True, 
            'message': 'Redirecionando para logout...',
            'redirect': url_for('auth.logout')
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Usuário não está logado',
            'redirect': url_for('lms.login_page')
        })

@lms_bp.route('/')
@lms_bp.route('/dashboard')
@login_required
def dashboard():
    
    user_email = session['user_email']
    
    # Tentar buscar cursos do banco, se falhar usar dados dummy
    try:
        courses = get_user_courses(user_email)
        if not courses:  # Se não encontrar cursos no banco, usar dados dummy
            courses = create_dummy_data()
    except:
        courses = create_dummy_data()
    
    stats = get_course_stats(courses)
    
    # Separar cursos por status
    cursos_andamento = [c for c in courses if c['status'] == 'progress'][:3]
    cursos_proximos = [c for c in courses if c['status'] == 'upcoming'][:5]
    cursos_concluidos = [c for c in courses if c['status'] == 'completed'][:3]
    
    return render_template('dashboard.html',
                         stats=stats,
                         cursos_andamento=cursos_andamento,
                         cursos_proximos=cursos_proximos,
                         cursos_concluidos=cursos_concluidos)

@lms_bp.route('/courses')
@login_required
def courses():
    user_email = session['user_email']
    
    # Tentar buscar cursos do banco, se falhar usar dados dummy
    try:
        courses = get_user_courses(user_email)
        if not courses:  # Se não encontrar cursos no banco, usar dados dummy
            courses = create_dummy_data()
    except:
        courses = create_dummy_data()
    
    return render_template('courses.html', cursos=courses)

@lms_bp.route('/admin')
@login_required
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Acesso negado! Área restrita para administradores.', 'error')
        return redirect(url_for('lms.dashboard'))
    
    # Estatísticas administrativas (dados simulados)
    admin_stats = {
        'total_usuarios': 156,
        'cursos_ativos': 12,
        'certificados': 89,
        'total_horas': 2840
    }
    
    course_config = load_course_config()
    
    return render_template('admin_dashboard.html',
                         admin_stats=admin_stats,
                         course_config=course_config)

@lms_bp.route('/admin/courses/config', methods=['POST'])
@login_required
def admin_courses_config():
    if not session.get('is_admin'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        data = request.json
        config = load_course_config()
        
        if 'codcua_order' in data:
            config['codcua_order'] = data['codcua_order']
        
        if 'admin_emails' in data:
            config['admin_emails'] = data['admin_emails']
        
        save_course_config(config)
        
        return jsonify({'message': 'Configuração atualizada com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
