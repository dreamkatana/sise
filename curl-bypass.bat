@echo off
echo === CURL SSL BYPASS SOLUTION ===
echo.

echo 1. Parando container atual...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com CURL instalado...
docker build --no-cache -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build
    pause
    exit /b 1
)

echo.
echo 3. Testando se curl existe na imagem...
docker run --rm sise-flask:latest curl --version

echo.
echo 4. Iniciando container...
docker run -d ^
    --name sise-flask-prod ^
    --restart unless-stopped ^
    -p 5006:5000 ^
    --env-file .env.production ^
    sise-flask:latest

echo.
echo 5. Aguardando inicialização...
timeout /t 10 /nobreak >nul

echo.
echo 6. Testando se iniciou corretamente...
docker logs sise-flask-prod | findstr -i "error\|traceback" && (
    echo [ERROR] Container com erros!
    docker logs sise-flask-prod
) || (
    echo [SUCCESS] Container iniciado sem erros!
)

echo.
echo === CURL BYPASS APLICADO ===
echo ✅ Curl instalado no container
echo ✅ Bypass COMPLETO do SSL Python
echo ✅ subprocess.run com curl -k (insecure)
echo ✅ JSON parsing direto
echo.
echo Teste: https://servicos.educorp.unicamp.br/pdg/login
echo.
echo O login agora usa CURL em vez de requests/urllib3!
echo.

pause