#!/usr/bin/env python3
"""
Teste local do SISE Flask com APPLICATION_ROOT
"""
import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask import url_for

def test_application_root():
    print("=== Teste de APPLICATION_ROOT ===")
    
    # Teste em modo de produção
    app = create_app('Production')
    
    with app.app_context():
        print(f"APPLICATION_ROOT: {app.config.get('APPLICATION_ROOT')}")
        print(f"SERVER_NAME: {app.config.get('SERVER_NAME')}")
        
        # Teste de geração de URLs
        try:
            login_url = url_for('auth.direct_login')
            print(f"URL gerada para auth.direct_login: {login_url}")
            
            dashboard_url = url_for('lms.dashboard', _external=False)
            print(f"URL gerada para lms.dashboard: {dashboard_url}")
            
        except Exception as e:
            print(f"Erro ao gerar URLs: {e}")
    
    print("\n=== Fim do teste ===")

if __name__ == '__main__':
    test_application_root()