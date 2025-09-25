@echo off
echo === Aplicando debug melhorado ao SISE Flask ===
echo.

echo 1. Build da nova imagem com debug...
docker build -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build
    pause
    exit /b 1
)

echo.
echo 2. Restart do container...
docker stop sise-flask-prod
docker rm sise-flask-prod

docker run -d ^
    --name sise-flask-prod ^
    --restart unless-stopped ^
    -p 5006:5000 ^
    --env-file .env.production ^
    sise-flask:latest

echo.
echo 3. Aguardando container...
timeout /t 10 /nobreak >nul

echo.
echo === Teste de login ===
echo 1. Acesse: https://servicos.educorp.unicamp.br/pdg/login
echo 2. Faça login
echo 3. Monitore os logs com:
echo    docker logs -f sise-flask-prod
echo.
echo O debug vai mostrar:
echo - Se conseguiu autenticar no Keycloak
echo - Dados do usuario retornados
echo - Erro especifico se houver falha
echo.

pause