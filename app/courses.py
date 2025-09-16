from flask import Blueprint, jsonify, g, request
from app.auth import token_required
import mysql.connector
import config.config as config

courses_bp = Blueprint('courses', __name__)

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
    return g.db

@courses_bp.route('/courses', methods=['GET'])
@token_required
def get_courses():
    try:
        user_email = g.user.get('email')
        if not user_email:
            return jsonify({'error': 'Email não encontrado no token'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        course_config = load_course_config()

        base_query = """
        SELECT V_EDUCORP_CURSO_APERF_COL.NUMCAD AS MATRICULA,
               V_EDUCORP_CURSO_APERF.`CODCUA` AS "CÓDIGO CURSO",
               V_EDUCORP_CURSO_APERF_COL.TMACUA AS "CÓDIGO TURMA",
               V_EDUCORP_CURSO_APERF_COL.`NOMCUA` AS "NOME CURSO",
               V_EDUCORP_CURSO_APERF_COL.`PERINI` AS "DATA INICIO",
               V_EDUCORP_CURSO_APERF_COL.`PERFIM` AS "DATA FINAL",
               V_EDUCORP_CURSO_APERF_COL.`DESSITCUA` AS "SITUACAO DA TURMA",
               V_EDUCORP_CURSO_APERF_COL.`CARHOR` AS "CARGA HORÁRIA"
        FROM V_EDUCORP_CURSO_APERF
          INNER JOIN V_EDUCORP_CURSO_APERF_COL
             ON V_EDUCORP_CURSO_APERF.`CODCUA` = V_EDUCORP_CURSO_APERF_COL.`CODCUA`
          INNER JOIN V_EDUCORP_FICHACOL
             ON V_EDUCORP_FICHACOL.`TIPCOL` = V_EDUCORP_CURSO_APERF_COL.`TIPCOL`
             AND V_EDUCORP_CURSO_APERF_COL.`NUMCAD` = V_EDUCORP_FICHACOL.`NUMCAD`
        WHERE V_EDUCORP_FICHACOL.`EMACOM` = %s
        """

        params = [user_email]

        codcua_order = course_config.get('codcua_order', [])
        if codcua_order:
            # Placeholders for the IN clause
            placeholders_in = ','.join(['%s'] * len(codcua_order))
            base_query += f" AND V_EDUCORP_CURSO_APERF.CODCUA IN ({placeholders_in})"

            # Placeholders for the ORDER BY FIELD clause
            placeholders_order = ','.join(['%s'] * len(codcua_order))
            order_clause = "ORDER BY FIELD(V_EDUCORP_CURSO_APERF.CODCUA, " + placeholders_order + ")"
            base_query += " " + order_clause

            # The parameters for the IN clause and the ORDER BY FIELD clause are the same.
            # We need to provide them for both sets of placeholders.
            params_for_in = codcua_order
            params_for_order = codcua_order
            params.extend(params_for_in)
            params.extend(params_for_order)

        cursor.execute(base_query, tuple(params))
        courses = cursor.fetchall()

        cursor.close()

        return jsonify(courses)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

import json

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
