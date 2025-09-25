@echo off
echo === CORREÇÃO IMPORT URLLIB3 ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Removendo imagem antiga (força rebuild)...
docker rmi sise-flask:latest 2>nul

echo.
echo 3. Build COMPLETO com urllib3 fix...
docker build --no-cache -t sise-flask:latest .

if errorlevel 1 (
    echo [ERROR] Falha no build
    pause
    exit /b 1
)

echo.
echo 4. Iniciando container novo...
docker run -d ^
    --name sise-flask-prod ^
    --restart unless-stopped ^
    -p 5006:5000 ^
    --env-file .env.production ^
    sise-flask:latest

echo.
echo 5. Aguardando inicialização...
timeout /t 15 /nobreak >nul

echo.
echo 6. Testando se iniciou corretamente...
docker logs sise-flask-prod

echo.
echo === URLLIB3 FIX APLICADO ===
echo ✅ Python 3.11 (não 3.13)
echo ✅ urllib3 warnings com try/except
echo ✅ Rebuild completo forçado
echo.
echo Se não tiver erros acima, teste:
echo https://servicos.educorp.unicamp.br/pdg/login
echo.

pause