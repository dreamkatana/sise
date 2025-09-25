@echo off
echo === Aplicando correções no SISE Flask ===
echo.

echo 1. Fazendo rebuild da imagem Docker...
docker build -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build da imagem
    pause
    exit /b 1
)

echo.
echo 2. Parando container atual...
docker stop sise-flask-prod 2>nul

echo.
echo 3. Removendo container atual...
docker rm sise-flask-prod 2>nul

echo.
echo 4. Iniciando novo container...
docker run -d ^
    --name sise-flask-prod ^
    --restart unless-stopped ^
    -p 5006:5000 ^
    --env-file .env.production ^
    sise-flask:latest

echo.
echo 5. Aguardando container inicializar...
timeout /t 10 /nobreak >nul

echo.
echo 6. Verificando status...
docker ps --filter name=sise-flask-prod

echo.
echo === Testes ===
echo Agora teste:
echo 1. https://servicos.educorp.unicamp.br/pdg/login
echo 2. Faça login e observe os logs com: docker logs -f sise-flask-prod
echo.

pause