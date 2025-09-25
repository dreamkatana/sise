@echo off
echo === SISE - DESENVOLVIMENTO LOCAL ===
echo.

echo 1. Ativando ambiente virtual...
call .venv\Scripts\activate

echo.
echo 2. Configurando variaveis para ambiente LOCAL...
set FLASK_ENV=development
set APPLICATION_ROOT=/
set SERVER_NAME=localhost:5000

echo.
echo 3. Iniciando servidor Flask em modo DEBUG...
echo Acesse: http://localhost:5000/login
echo.
echo Para parar o servidor: Ctrl+C
echo.

python run.py