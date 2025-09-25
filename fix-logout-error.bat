@echo off
echo === CORRIGINDO URLS DE LOGOUT ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com URL fix...
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
echo ✅ Mensagem de erro melhorada: "Usuário ou senha incorretos"
echo ✅ Tratamento de "invalid user credentials"
echo ✅ URL logout corrigida
echo.
echo Teste: https://servicos.educorp.unicamp.br/pdg/login
echo.
echo 1. Teste senha errada - deve aparecer mensagem amigável
echo 2. Teste logout - deve funcionar corretamente
echo.

pause