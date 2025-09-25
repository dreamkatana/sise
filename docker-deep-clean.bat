@echo off
echo === LIMPEZA COMPLETA DOCKER + REBUILD ===
echo.

echo 1. Parando TODOS containers SISE...
for /f "tokens=*" %%i in ('docker ps -aq --filter name=sise') do docker stop %%i 2>nul
for /f "tokens=*" %%i in ('docker ps -aq --filter name=sise') do docker rm %%i 2>nul

echo.
echo 2. Removendo TODAS imagens sise-flask...
for /f "tokens=*" %%i in ('docker images -q sise-flask') do docker rmi -f %%i 2>nul

echo.
echo 3. Limpando cache Docker...
docker system prune -f
docker builder prune -f

echo.
echo 4. Verificando Dockerfile Python version...
findstr "FROM python" Dockerfile

echo.
echo 5. Build ZERO cache + verificação Python...
docker build --no-cache --progress=plain -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build
    pause
    exit /b 1
)

echo.
echo 6. Verificando versão Python na imagem...
docker run --rm sise-flask:latest python --version

echo.
echo 7. Iniciando container...
docker run -d ^
    --name sise-flask-prod ^
    --restart unless-stopped ^
    -p 5006:5000 ^
    --env-file .env.production ^
    sise-flask:latest

echo.
echo 8. Aguardando e verificando logs...
timeout /t 10 /nobreak >nul
docker logs sise-flask-prod

echo.
echo === VERIFICAÇÃO FINAL ===
echo Versão Python no container:
docker exec sise-flask-prod python --version
echo.
echo Path Python no container:
docker exec sise-flask-prod which python
echo.

pause