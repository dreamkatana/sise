#!/bin/bash
# Deploy Script para SISE Flask em Produção

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SISE Flask - Deploy em Produção${NC}"
echo "================================="

# Função para log
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

# Verificar se estamos no diretório correto
if [ ! -f "app/__init__.py" ]; then
    error "Este script deve ser executado no diretório raiz do projeto SISE"
    exit 1
fi

# 1. Verificar dependências
log "Verificando dependências..."

if ! command -v docker &> /dev/null; then
    error "Docker não está instalado"
    exit 1
fi

if ! command -v nginx &> /dev/null; then
    error "Nginx não está instalado"
    exit 1
fi

# 2. Verificar se o arquivo .env.production existe
if [ ! -f ".env.production" ]; then
    error "Arquivo .env.production não encontrado"
    echo "Execute: cp .env.example .env.production e configure as variáveis"
    exit 1
fi

# 3. Backup da configuração atual do nginx
log "Fazendo backup da configuração do nginx..."
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)

# 4. Parar container existente (se houver)
log "Parando container existente..."
docker stop sise-flask 2>/dev/null || true
docker rm sise-flask 2>/dev/null || true

# 5. Build da nova imagem
log "Construindo imagem Docker..."
if docker build -t sise-flask:latest -f Dockerfile .; then
    log "Imagem construída com sucesso"
else
    error "Falha ao construir imagem Docker"
    exit 1
fi

# 6. Testar se a aplicação inicia
log "Testando aplicação..."
docker run -d --name sise-flask-test -p 5006:5000 --env-file .env.production sise-flask:latest

# Aguardar alguns segundos
sleep 10

# Verificar se está respondendo
if curl -f http://localhost:5006/api > /dev/null 2>&1; then
    log "Aplicação está respondendo corretamente"
    docker stop sise-flask-test
    docker rm sise-flask-test
else
    error "Aplicação não está respondendo"
    docker logs sise-flask-test
    docker stop sise-flask-test
    docker rm sise-flask-test
    exit 1
fi

# 7. Atualizar configuração do nginx
echo ""
read -p "Deseja atualizar a configuração do nginx? (y/N): " update_nginx

if [[ $update_nginx =~ ^[Yy]$ ]]; then
    log "Atualizando configuração do nginx..."
    
    # Escolher qual configuração usar
    echo "Escolha a configuração do nginx:"
    echo "1) Básica (nginx-config-updated.conf)"
    echo "2) Avançada com cache (nginx-config-advanced.conf)"
    read -p "Opção (1-2): " nginx_choice
    
    case $nginx_choice in
        1)
            config_file="nginx-config-updated.conf"
            ;;
        2)
            config_file="nginx-config-advanced.conf"
            ;;
        *)
            config_file="nginx-config-updated.conf"
            ;;
    esac
    
    if [ -f "$config_file" ]; then
        sudo cp "$config_file" /etc/nginx/sites-available/default
        
        # Testar configuração
        if sudo nginx -t; then
            log "Configuração do nginx válida"
        else
            error "Configuração do nginx inválida - revertendo backup"
            sudo cp /etc/nginx/sites-available/default.backup.* /etc/nginx/sites-available/default
            exit 1
        fi
    else
        error "Arquivo de configuração $config_file não encontrado"
        exit 1
    fi
fi

# 8. Iniciar container em produção
log "Iniciando container em produção..."
docker run -d \
    --name sise-flask \
    --restart unless-stopped \
    -p 5006:5000 \
    --env-file .env.production \
    -v "$(pwd)/logs:/app/logs" \
    sise-flask:latest

# Verificar se o container está rodando
sleep 5
if docker ps | grep -q sise-flask; then
    log "Container iniciado com sucesso"
else
    error "Falha ao iniciar container"
    docker logs sise-flask
    exit 1
fi

# 9. Recarregar nginx
if [[ $update_nginx =~ ^[Yy]$ ]]; then
    log "Recarregando nginx..."
    sudo systemctl reload nginx
fi

# 10. Testes finais
log "Executando testes finais..."

# Testar aplicação local
if curl -f http://localhost:5006/api > /dev/null 2>&1; then
    log "✓ Aplicação respondendo localmente"
else
    error "✗ Aplicação não responde localmente"
fi

# Testar através do nginx (se configurado)
if [[ $update_nginx =~ ^[Yy]$ ]]; then
    if curl -f https://servicos.educorp.unicamp.br/pdg/api > /dev/null 2>&1; then
        log "✓ Aplicação respondendo através do nginx"
    else
        warn "⚠ Aplicação pode não estar acessível através do nginx"
        echo "   Verifique: certificado SSL, DNS, firewall"
    fi
fi

# 11. Instruções finais
echo ""
echo -e "${BLUE}📋 Próximos passos:${NC}"
echo "1. Configure o redirect URI no Keycloak:"
echo "   https://servicos.educorp.unicamp.br/pdg/api/auth/callback"
echo ""
echo "2. Monitore os logs:"
echo "   docker logs -f sise-flask"
echo "   tail -f /var/log/nginx/sise_flask.*.log"
echo ""
echo "3. Para parar a aplicação:"
echo "   docker stop sise-flask"
echo ""

# 12. Status final
echo -e "${GREEN}🎉 Deploy concluído!${NC}"
echo "Aplicação: http://localhost:5006"
echo "Produção: https://servicos.educorp.unicamp.br/pdg"
echo ""
echo "Status dos serviços:"
docker ps --filter name=sise-flask --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Mostrar logs recentes
echo ""
log "Logs recentes da aplicação:"
docker logs --tail 20 sise-flask