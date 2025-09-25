@echo off
echo === Corrigindo SSL Keycloak ===
echo.

echo 1. Build com SSL fix...
docker build -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build
    pause
    exit /b 1
)

echo.
echo 2. Restart container...
docker stop sise-flask-prod
docker rm sise-flask-prod

docker run -d ^
    --name sise-flask-prod ^
    --restart unless-stopped ^
    -p 5006:5000 ^
    --env-file .env.production ^
    sise-flask:latest

echo.
echo 3. Aguardando inicialização...
timeout /t 10 /nobreak >nul

echo.
echo === SSL Fix aplicado ===
echo Teste novamente o login em:
echo https://servicos.educorp.unicamp.br/pdg/login
echo.
echo Monitore com: docker logs -f sise-flask-prod
echo.

pause