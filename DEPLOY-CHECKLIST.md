# Checklist de Deploy - SISE Flask

## ✅ Pré-Deploy

- [ ] Arquivo `.env.production` configurado com:
  - [ ] `SECRET_KEY` segura e única
  - [ ] `KEYCLOAK_SERVER_URL` correto
  - [ ] Credenciais do Keycloak válidas
  - [ ] `DATABASE_URL` de produção
  - [ ] `FLASK_ENV=production`

- [ ] Keycloak configurado:
  - [ ] Client `educorp-apoios-prod` existe
  - [ ] Redirect URI: `https://servicos.educorp.unicamp.br/pdg/api/auth/callback`
  - [ ] Valid Redirect URIs atualizado
  - [ ] Client Secret correto no `.env.production`

- [ ] Banco de dados acessível:
  - [ ] Views `V_EDUCORP_*` existem
  - [ ] Usuário da aplicação tem permissões corretas
  - [ ] Conectividade testada

## 🐳 Deploy com Docker

### Opção 1: Script Automatizado
```bash
# Linux/Mac
./deploy-production.sh

# Windows
deploy-production.bat
```

### Opção 2: Manual
```bash
# 1. Build da imagem
docker build -t sise-flask:latest -f Dockerfile .

# 2. Parar container anterior
docker stop sise-flask 2>/dev/null || true
docker rm sise-flask 2>/dev/null || true

# 3. Iniciar novo container
docker run -d \
    --name sise-flask \
    --restart unless-stopped \
    -p 5006:5000 \
    --env-file .env.production \
    -v "$(pwd)/logs:/app/logs" \
    sise-flask:latest

# 4. Verificar status
docker ps
docker logs sise-flask
```

## 🌐 Configuração do Nginx

### Escolha uma configuração:

**Básica** (`nginx-config-updated.conf`):
- Proxy reverso simples
- Headers essenciais
- Ideal para começar

**Avançada** (`nginx-config-advanced.conf`):
- Cache inteligente
- Rate limiting
- Load balancing preparado
- Logs detalhados

### Aplicar configuração:
```bash
# Backup da configuração atual
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Aplicar nova configuração
sudo cp nginx-config-updated.conf /etc/nginx/sites-available/default

# Testar configuração
sudo nginx -t

# Recarregar nginx
sudo systemctl reload nginx
```

## 🧪 Testes Pós-Deploy

### Testes Locais
- [ ] `curl http://localhost:5006/api` → Retorna JSON
- [ ] `curl http://localhost:5006/api/courses` → Requer autenticação
- [ ] Container reinicia automaticamente: `docker restart sise-flask`

### Testes via Nginx
- [ ] `curl https://servicos.educorp.unicamp.br/pdg/api` → Retorna JSON
- [ ] Login via browser funciona
- [ ] Redirecionamento após login correto
- [ ] Assets estáticos carregam (CSS, JS)

### Testes de Autenticação
- [ ] Login via Keycloak funciona
- [ ] Logout limpa sessão
- [ ] Páginas protegidas redirecionam para login
- [ ] Usuário autorizado acessa dashboard

## 📊 Monitoramento

### Logs da Aplicação
```bash
# Logs em tempo real
docker logs -f sise-flask

# Últimas 50 linhas
docker logs --tail 50 sise-flask

# Logs com timestamp
docker logs -t sise-flask
```

### Logs do Nginx
```bash
# Access logs
tail -f /var/log/nginx/educorp_prod.access_log
tail -f /var/log/nginx/sise_flask.access.log

# Error logs
tail -f /var/log/nginx/educorp_prod.error_log
tail -f /var/log/nginx/sise_flask.error.log
```

### Status dos Serviços
```bash
# Container
docker ps --filter name=sise-flask

# Nginx
sudo systemctl status nginx

# Uso de recursos
docker stats sise-flask
```

## 🚨 Troubleshooting

### Problemas Comuns

**Container não inicia:**
- Verificar `.env.production`
- Verificar logs: `docker logs sise-flask`
- Testar conectividade com banco

**Nginx 502 Bad Gateway:**
- Container está rodando? `docker ps`
- Porta 5006 acessível? `netstat -tlnp | grep 5006`
- Logs do nginx: `tail -f /var/log/nginx/error.log`

**Erro de autenticação:**
- Keycloak acessível?
- Redirect URI correto no Keycloak?
- Client secret correto?

**Problema de sessão:**
- `SECRET_KEY` deve ser fixa (não aleatória)
- Cookies seguros habilitados para HTTPS

### Comandos Úteis

```bash
# Reiniciar tudo
docker restart sise-flask
sudo systemctl reload nginx

# Ver configuração ativa do nginx
sudo nginx -T

# Testar conectividade
curl -v http://localhost:5006/api
curl -v https://servicos.educorp.unicamp.br/pdg/api

# Limpar containers antigos
docker system prune -f
```

## 🔄 Rollback

Se algo der errado:

```bash
# 1. Parar container atual
docker stop sise-flask
docker rm sise-flask

# 2. Restaurar nginx
sudo cp /etc/nginx/sites-available/default.backup /etc/nginx/sites-available/default
sudo systemctl reload nginx

# 3. Usar container anterior (se existir)
docker run -d --name sise-flask -p 5006:5000 --env-file .env.production sise-flask:previous

# 4. Ou reverter para versão anterior do código
git revert HEAD
./deploy-production.sh
```

## 📋 Checklist Final

- [ ] Aplicação respondendo em https://servicos.educorp.unicamp.br/pdg
- [ ] Login/logout funcionando
- [ ] Dashboard carregando dados
- [ ] Assets estáticos (CSS/JS) carregando
- [ ] Logs sendo gerados corretamente
- [ ] Container configura para restart automático
- [ ] Monitoramento configurado
- [ ] Equipe notificada sobre o deploy

---

**Data do Deploy:** ___________
**Versão:** ___________
**Responsável:** ___________