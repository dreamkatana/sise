"""
Teste específico para a função get_user_courses
"""
from app import create_app
from app.lms import get_user_courses

app = create_app('Debug')

with app.app_context():
    try:
        print("Testando função get_user_courses...")
        
        # Teste com email de exemplo
        test_email = "joaoedu@unicamp.br"
        courses = get_user_courses(test_email)
        
        print(f"Resultado para {test_email}:")
        print(f"Número de cursos encontrados: {len(courses)}")
        
        if courses:
            print("Primeiro curso encontrado:")
            for key, value in courses[0].items():
                print(f"  {key}: {value}")
        else:
            print("Nenhum curso encontrado (isso é normal se o banco estiver vazio)")
            
        print("✅ Função get_user_courses executada sem erros!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()