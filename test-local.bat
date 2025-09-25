@echo off
echo === TESTE SISE LOCAL - SEM AFETAR PRODUCAO ===
echo.

echo Configurando apenas variaveis de ambiente...
set FLASK_ENV=development
set APPLICATION_ROOT=/
set SERVER_NAME=localhost:5000

echo.
echo Testando configuracao local...
call .venv\Scripts\activate

python -c "
import os
os.environ['FLASK_ENV'] = 'development'
os.environ['APPLICATION_ROOT'] = '/'
os.environ['SERVER_NAME'] = 'localhost:5000'

from app import create_app
from flask import url_for

app = create_app('Debug')
with app.app_context():
    print('=== URLS LOCAIS ===')
    print('Direct login URL:', url_for('auth.direct_login'))
    print('Dashboard URL:', url_for('lms.dashboard'))
    print()
    print('=== CONFIG ===')
    print('APPLICATION_ROOT:', app.config.get('APPLICATION_ROOT'))
    print('FLASK_ENV:', app.config.get('FLASK_ENV'))
    print()
    print('Tudo OK! Agora execute: run-local.bat')
"