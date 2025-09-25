@echo off
echo === Reiniciando SISE Flask Container ===
echo.

echo Parando container atual...
docker stop sise-flask-prod 2>nul

echo Iniciando container com nova configuracao...
docker start sise-flask-prod

echo.
echo Aguardando container inicializar...
timeout /t 10 /nobreak >nul

echo.
echo Status do container:
docker ps --filter name=sise-flask-prod --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Testando aplicacao...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:5006/api' -TimeoutSec 5 | Out-Null; Write-Host '✓ Container respondendo na porta 5006' -ForegroundColor Green } catch { Write-Host '✗ Container não responde' -ForegroundColor Red }"

echo.
echo === Configuracao nginx-config-clean.conf ===
echo Para aplicar no servidor:
echo 1. Copie o arquivo nginx-config-clean.conf
echo 2. Execute: sudo cp nginx-config-clean.conf /etc/nginx/sites-available/default
echo 3. Execute: sudo nginx -t
echo 4. Execute: sudo systemctl reload nginx
echo.

pause