@echo off
REM Deploy Script para SISE Flask em Produção - Windows

echo.
echo =====================================
echo   SISE Flask - Deploy em Producao
echo =====================================
echo.

REM Verificar se estamos no diretório correto
if not exist "app\__init__.py" (
    echo [ERROR] Este script deve ser executado no diretorio raiz do projeto SISE
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker nao esta instalado ou nao esta no PATH
    pause
    exit /b 1
)

REM Verificar arquivo de configuração
if not exist ".env.production" (
    echo [ERROR] Arquivo .env.production nao encontrado
    echo Execute: copy .env.example .env.production e configure as variaveis
    pause
    exit /b 1
)

echo [INFO] Parando container existente...
docker stop sise-flask >nul 2>&1
docker rm sise-flask >nul 2>&1

echo [INFO] Construindo imagem Docker...
docker build -t sise-flask:latest -f Dockerfile .
if errorlevel 1 (
    echo [ERROR] Falha ao construir imagem Docker
    pause
    exit /b 1
)

echo [INFO] Testando aplicacao...
docker run -d --name sise-flask-test -p 5006:5000 --env-file .env.production sise-flask:latest

REM Aguardar alguns segundos
timeout /t 10 /nobreak >nul

REM Testar se está respondendo (usando curl ou PowerShell)
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:5006/api' -TimeoutSec 5 | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo [ERROR] Aplicacao nao esta respondendo
    docker logs sise-flask-test
    docker stop sise-flask-test >nul 2>&1
    docker rm sise-flask-test >nul 2>&1
    pause
    exit /b 1
) else (
    echo [INFO] Aplicacao esta respondendo corretamente
    docker stop sise-flask-test >nul 2>&1
    docker rm sise-flask-test >nul 2>&1
)

echo [INFO] Iniciando container em producao...
docker run -d --name sise-flask --restart unless-stopped -p 5006:5000 --env-file .env.production -v "%CD%\logs:/app/logs" sise-flask:latest

REM Verificar se o container está rodando
timeout /t 5 /nobreak >nul
docker ps | findstr sise-flask >nul
if errorlevel 1 (
    echo [ERROR] Falha ao iniciar container
    docker logs sise-flask
    pause
    exit /b 1
) else (
    echo [INFO] Container iniciado com sucesso
)

echo [INFO] Executando testes finais...

REM Testar aplicação local
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:5006/api' -TimeoutSec 5 | Out-Null; Write-Host '[INFO] Aplicacao respondendo localmente' -ForegroundColor Green } catch { Write-Host '[ERROR] Aplicacao nao responde localmente' -ForegroundColor Red }"

echo.
echo =====================================
echo   Proximos passos:
echo =====================================
echo 1. Configure o redirect URI no Keycloak:
echo    https://servicos.educorp.unicamp.br/pdg/api/auth/callback
echo.
echo 2. Configure o nginx com um dos arquivos:
echo    - nginx-config-updated.conf (basico)
echo    - nginx-config-advanced.conf (com cache)
echo.
echo 3. Monitore os logs:
echo    docker logs -f sise-flask
echo.
echo 4. Para parar a aplicacao:
echo    docker stop sise-flask
echo.

echo =====================================
echo   Deploy concluido!
echo =====================================
echo Aplicacao: http://localhost:5006
echo Producao: https://servicos.educorp.unicamp.br/pdg
echo.

echo Status do container:
docker ps --filter name=sise-flask --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Logs recentes da aplicacao:
docker logs --tail 20 sise-flask

pause