@echo off
echo === CORREÇÃO SSL DEFINITIVA ===
echo.

echo 1. Build com SSL fix completo...
docker build -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build
    pause
    exit /b 1
)

echo.
echo 2. Removendo container antigo...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 3. Iniciando container com SSL fix...
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
echo === CORREÇÕES APLICADAS ===
echo ✅ SSL context global desabilitado
echo ✅ urllib3 warnings desabilitados
echo ✅ Sessão requests customizada
echo ✅ URL Keycloak corrigida (sem barra dupla)
echo ✅ Python 3.11 (mais estável que 3.13)
echo.
echo Teste agora: https://servicos.educorp.unicamp.br/pdg/login
echo.
echo Para monitorar: docker logs -f sise-flask-prod
echo.

pause