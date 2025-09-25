@echo off
echo === CORRIGINDO FLASH MESSAGES NO LOGIN ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com flash messages no login...
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
echo === FLASH MESSAGES ADICIONADOS ===
echo ✅ Template login.html agora tem flash messages
echo ✅ Bootstrap JS adicionado para funcionalidade de alerts
echo ✅ Mensagens de erro aparecerão com estilo Bootstrap
echo ✅ Botão de fechar nos alerts
echo.
echo Teste: https://servicos.educorp.unicamp.br/pdg/login
echo.
echo Agora quando errar a senha, deve aparecer:
echo [ALERT VERMELHO] "Usuário ou senha incorretos. Verifique suas credenciais."
echo.

pause