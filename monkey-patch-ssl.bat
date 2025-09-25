@echo off
echo === MONKEY PATCH SSL FIX ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com monkey patch...
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
echo 5. Verificando se iniciou sem erros...
docker logs sise-flask-prod

echo.
echo === MONKEY PATCH APLICADO ===
echo ✅ urllib3.util.ssl_.create_urllib3_context monkey patched
echo ✅ SSL context sem minimum_version (evita recursão)
echo ✅ Python 3.11 estável
echo.
echo Teste: https://servicos.educorp.unicamp.br/pdg/login
echo.

pause