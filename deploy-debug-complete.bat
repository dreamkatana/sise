@echo off
echo === DEPLOY COM DEBUG COMPLETO ===
echo.

echo 1. Parando container anterior...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com debug URLs e logs...
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
echo === DEBUG ATIVO ===
echo ✅ JavaScript console.log nas URLs
echo ✅ Python debug logs no logout
echo ✅ Flash messages funcionando
echo.
echo COMO TESTAR:
echo 1. Acesse: https://servicos.educorp.unicamp.br/pdg/login
echo 2. Faça login com suas credenciais
echo 3. Abra DevTools (F12) - aba Console
echo 4. Clique no botão "Sair"
echo 5. Veja no console do navegador qual URL está sendo chamada
echo 6. Verifique se o logout funciona corretamente
echo.
echo LOGS DO CONTAINER:
echo docker logs -f sise-flask-prod
echo.
echo Se ainda redirecionar para URL errada, é problema no nginx.
echo.

pause