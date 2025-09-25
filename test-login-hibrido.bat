@echo off
echo === TESTE LOGIN HIBRIDO - PYTHON-KEYCLOAK + CURL FALLBACK ===
echo.

echo 1. Ativando ambiente virtual...
call .venv\Scripts\activate

echo.
echo 2. Configurando ambiente local...
set FLASK_ENV=development
set APPLICATION_ROOT=/
set SERVER_NAME=localhost:5000

echo.
echo 3. Iniciando servidor com login híbrido...
echo.
echo === MÉTODO HÍBRIDO ===
echo ✅ Método 1: python-keycloak (funcionava antes)
echo ✅ Método 2: curl fallback (para casos SSL)
echo ✅ Username limpo: remove @unicamp.br automaticamente
echo ✅ URL corrigida: sem barra dupla
echo ✅ Teste com ambos formatos de username
echo.
echo TESTE:
echo 1. Acesse: http://localhost:5000/login
echo 2. Teste com: educorp@unicamp.br ou educorp
echo 3. Deve funcionar com ambos os métodos
echo.
echo Para ver logs: acompanhe o console
echo.

python run.py