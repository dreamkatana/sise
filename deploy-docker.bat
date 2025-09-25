@echo off
echo 🚀 SISE Flask - Deploy com Docker (Windows)

echo 🛑 Parando container anterior...
docker stop sise-flask-prod 2>nul
docker rm sise-flask-prod 2>nul

echo 🔨 Construindo imagem...
docker build -t sise-flask:latest .

if %errorlevel% neq 0 (
    echo ❌ Erro no build da imagem
    exit /b 1
)

echo 🚀 Iniciando container...
docker run -d ^
  --name sise-flask-prod ^
  --restart unless-stopped ^
  -p 5006:5006 ^
  --env-file .env.production ^
  -e FLASK_ENV=production ^
  sise-flask:latest

if %errorlevel% neq 0 (
    echo ❌ Erro ao iniciar container
    exit /b 1
)

echo ⏳ Aguardando inicialização...
timeout /t 10 /nobreak

echo 📊 Status do container:
docker ps --filter name=sise-flask-prod --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo 📋 Logs recentes:
docker logs --tail=20 sise-flask-prod

echo ✅ Deploy concluído!
echo 🌐 Aplicação disponível em: http://localhost:5006