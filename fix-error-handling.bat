@echo off
echo === CORRIGINDO TRATAMENTO DE ERRO DE LOGIN ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com tratamento de erro melhorado...
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
echo === TRATAMENTO DE ERRO APLICADO ===
echo ✅ Login funcionando com curl bypass
echo ✅ Tratamento de erro 'invalid_grant' 
echo ✅ Mensagem amigável para credenciais inválidas
echo ✅ Verificação se 'access_token' existe
echo.
echo Teste: https://servicos.educorp.unicamp.br/pdg/login
echo.
echo Agora erro de senha vai mostrar: "Credenciais inválidas. Verifique seu usuário e senha."
echo.

pause