from flask import Blueprint, jsonify, g, request
from app.auth import token_required
from app.models import CursoAperf, FichaCol, CursoAperfCol, FrequenciaTurma
from app.extensions import db
from sqlalchemy import case, and_
import json

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses', methods=['GET'])
@token_required
def get_courses():
    try:
        user_email = g.user.get('email')
        if not user_email:
            return jsonify({'error': 'Email não encontrado no token'}), 400

        course_config = load_course_config()
        codcua_order = course_config.get('codcua_order', [])

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

        return jsonify(courses)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

CONFIG_FILE = 'course_config.json'

def load_course_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'codcua_order': []}

def save_course_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

@courses_bp.route('/admin/courses', methods=['GET', 'POST'])
@token_required
def admin_courses():
    config = load_course_config()
    user_email = g.user.get('email')

    if user_email not in config.get('admin_emails', []):
        return jsonify({'error': 'Acesso não autorizado'}), 403

    if request.method == 'GET':
        return jsonify(config)

    if request.method == 'POST':
        data = request.json
        if 'codcua_order' in data and isinstance(data['codcua_order'], list):
            config['codcua_order'] = data['codcua_order']
            save_course_config(config)
            return jsonify({'message': 'Configuração de cursos atualizada com sucesso!'}), 200
        else:
            return jsonify({'error': 'Formato de dados inválido. "codcua_order" deve ser uma lista.'}), 400
