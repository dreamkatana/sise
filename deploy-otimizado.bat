@echo off
echo === DEPLOY PRODUÇÃO - MÉTODO OTIMIZADO ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com detecção inteligente de ambiente...
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
timeout /t 15 /nobreak >nul

echo.
echo 5. Testando método de produção...
docker logs --tail=20 sise-flask-prod

echo.
echo === OTIMIZAÇÃO APLICADA ===
echo ✅ PRODUÇÃO: Usa CURL direto (mais rápido e confiável)
echo ✅ LOCAL: Usa python-keycloak + fallback curl
echo ✅ Detecção automática por FLASK_ENV
echo ✅ Performance otimizada por ambiente
echo ✅ Zero tentativas desnecessárias em produção
echo.
echo TESTE AGORA:
echo https://servicos.educorp.unicamp.br/pdg/login
echo.
echo Deve funcionar para todos os usuários!
echo.

pause