@echo off
echo === CORRIGINDO LOGIN E DEBUG ===
echo.

echo 1. Parando container...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo.
echo 2. Build com correções...
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
echo === CORREÇÕES APLICADAS ===
echo ✅ Removido placeholder "joaoedu" hardcoded
echo ✅ Placeholder genérico: "seu_usuario"
echo ✅ Debug expandido para curl commands
echo ✅ Melhor tratamento de erros Keycloak
echo ✅ Logs específicos por usuário
echo.
echo TESTE AGORA:
echo 1. https://servicos.educorp.unicamp.br/pdg/login
echo 2. Verificar se placeholder não é mais "joaoedu"
echo 3. Testar login com outros usuários
echo 4. Ver logs: docker logs -f sise-flask-prod
echo.
echo Para debug de usuário específico:
echo - Teste com outro usuário que estava falhando
echo - Verifique os logs detalhados do erro
echo.

pause