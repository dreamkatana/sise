#!/bin/bash

# SISE Flask - Deployment Script
# Para usar: ./deploy.sh [production|development]

set -e

ENV=${1:-production}

echo "🚀 Iniciando deployment do SISE Flask em ambiente: $ENV"

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Configurar arquivo de ambiente
if [ "$ENV" == "production" ]; then
    ENV_FILE=".env.production"
else
    ENV_FILE=".env"
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Arquivo de configuração $ENV_FILE não encontrado."
    exit 1
fi

echo "📋 Usando configurações de: $ENV_FILE"

# Parar container anterior se existir
echo "🛑 Parando containers existentes..."
docker-compose down --remove-orphans 2>/dev/null || true

# Limpar imagens antigas (opcional)
echo "🧹 Limpando imagens antigas..."
docker image prune -f

# Build da nova imagem
echo "🔨 Construindo nova imagem..."
docker-compose build --no-cache

# Iniciar os serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d

# Verificar status
echo "📊 Verificando status dos containers..."
sleep 10
docker-compose ps

# Testar se a aplicação está respondendo
echo "🔍 Testando conectividade..."
for i in {1..10}; do
    if curl -f http://localhost:5006/api >/dev/null 2>&1; then
        echo "✅ Aplicação está rodando em http://localhost:5006"
        echo "🎉 Deployment concluído com sucesso!"
        exit 0
    fi
    echo "⏳ Aguardando aplicação inicializar... ($i/10)"
    sleep 5
done

echo "❌ Aplicação não respondeu dentro do tempo esperado"
echo "📋 Logs do container:"
docker-compose logs --tail=50 sise-app
exit 1