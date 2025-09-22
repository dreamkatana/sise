"""
Script de teste para verificar os relacionamentos dos models
"""
from app import create_app
from app.models import FichaCol, CursoAperfCol, FrequenciaTurma, CursoAperf
from app.extensions import db

app = create_app('Debug')

with app.app_context():
    try:
        # Teste básico de query
        print("Testando consulta básica...")
        fichas = FichaCol.query.limit(5).all()
        print(f"Encontradas {len(fichas)} fichas")
        
        if fichas:
            ficha = fichas[0]
            print(f"Primeira ficha: {ficha.NOMFUN} - {ficha.EMACOM}")
            
            # Teste de relacionamento
            print("Testando relacionamento cursos...")
            cursos = ficha.cursos
            print(f"Cursos relacionados: {len(cursos)}")
            
            print("Teste bem-sucedido!")
        else:
            print("Nenhuma ficha encontrada (banco vazio)")
            
    except Exception as e:
        print(f"Erro no teste: {e}")