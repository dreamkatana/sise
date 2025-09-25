@echo off
echo === CORRIGINDO LOGOUT URLs ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com correções de URL...
docker build --no-cache -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build
    pause
    exit /b 1
)

echo.
echo 3. Iniciando container...
docker run -d ^
    --name sise-flask-prod ^
    --restart unless-stopped ^
    -p 5006:5000 ^
    --env-file .env.production ^
    sise-flask:latest

echo.
echo 4. Aguardando inicialização...
timeout /t 10 /nobreak >nul

echo.
echo === CORREÇÕES APLICADAS ===
echo ✅ WSGI middleware para SCRIPT_NAME
echo ✅ url_for_with_prefix helper function  
echo ✅ URLs forçadas com /pdg nos templates
echo ✅ Debug expandido em /debug-urls
echo.
echo TESTE AGORA:
echo 1. Acesse: https://servicos.educorp.unicamp.br/pdg/api/auth/debug-urls
echo 2. Verifique se "logout_url_relative_fixed" tem /pdg
echo 3. Teste logout no dashboard
echo.

pause