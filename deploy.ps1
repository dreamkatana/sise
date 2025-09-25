# SISE Flask - Deploy Script (PowerShell)
param(
    [string]$Environment = "production"
)

Write-Host "🚀 SISE Flask - Deploy com Docker" -ForegroundColor Green

# Verificar se Docker está disponível
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker não encontrado. Instale o Docker primeiro." -ForegroundColor Red
    exit 1
}

Write-Host "🛑 Parando container anterior..." -ForegroundColor Yellow
docker stop sise-flask-prod 2>$null
docker rm sise-flask-prod 2>$null

Write-Host "🔨 Construindo nova imagem..." -ForegroundColor Cyan
$buildResult = docker build -t sise-flask:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build da imagem" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Iniciando container..." -ForegroundColor Green

$envFile = if ($Environment -eq "production") { ".env.production" } else { ".env" }

if (-not (Test-Path $envFile)) {
    Write-Host "❌ Arquivo de configuração $envFile não encontrado." -ForegroundColor Red
    exit 1
}

$runResult = docker run -d `
    --name sise-flask-prod `
    --restart unless-stopped `
    -p 5006:5006 `
    --env-file $envFile `
    -e FLASK_ENV=$Environment `
    sise-flask:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao iniciar container" -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Aguardando inicialização..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "📊 Status do container:" -ForegroundColor Cyan
docker ps --filter name=sise-flask-prod --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "📋 Logs recentes:" -ForegroundColor Cyan
docker logs --tail=20 sise-flask-prod

Write-Host "✅ Deploy concluído!" -ForegroundColor Green
Write-Host "🌐 Aplicação disponível em: http://localhost:5006" -ForegroundColor White

# Testar conectividade
Write-Host "🔍 Testando conectividade..." -ForegroundColor Cyan
for ($i = 1; $i -le 5; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5006/api" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Aplicação respondendo corretamente!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "⏳ Aguardando resposta... ($i/5)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

Write-Host "🎉 Deploy finalizado! Acesse http://localhost:5006" -ForegroundColor Green