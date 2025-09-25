@echo off
echo === DEBUG LOGOUT URLs ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com debug URLs...
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
echo ✅ JavaScript console.log adicionado
echo ✅ URLs de logout com debug
echo.
echo TESTE:
echo 1. Acesse: https://servicos.educorp.unicamp.br/pdg/login
echo 2. Faça login
echo 3. Abra DevTools (F12) no navegador
echo 4. Vá na aba Console
echo 5. Clique em Sair
echo 6. Veja no console qual URL está sendo chamada
echo.
echo Se aparecer URL sem /pdg, o problema é no nginx.
echo Se aparecer URL com /pdg, o problema é no navegador/cache.
echo.

pause