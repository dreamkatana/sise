# SISE Flask - Sistema Integrado de Serviços Educacionais

Sistema Flask integrado com Keycloak para autenticação e consulta de dados educacionais da UNICAMP.

## 🚀 Deploy em Produção

### Pré-requisitos
- Docker e Docker Compose instalados
- Acesso ao servidor de banco de dados
- Configurações do Keycloak atualizadas

### 1. Configuração
1. Edite o arquivo `.env.production` com suas configurações:
```bash
# Banco de dados
DB_HOST=seu-servidor-db
DB_USERNAME=usuario
DB_PASS=senha
DB_NAME=nome_banco

# Keycloak - Configure no console do Keycloak:
# Redirect URI: https://servicos.educorp.unicamp.br/pdg/api/auth/callback
KEYCLOAK_CLIENT_SECRET=seu-client-secret

# Segurança
SECRET_KEY=sua-chave-secreta-forte
```

2. No console do Keycloak, configure:
   - **Valid Redirect URIs**: `https://servicos.educorp.unicamp.br/pdg/api/auth/callback`
   - **Web Origins**: `https://servicos.educorp.unicamp.br`

### 2. Deploy com Docker

#### Opção A: Script Automático
```bash
chmod +x deploy.sh
./deploy.sh production
```

#### Opção B: Manual
```bash
# Build e start
docker-compose up -d --build

# Verificar logs
docker-compose logs -f sise-app

# Verificar status
docker-compose ps
```

### 3. Verificação
- Aplicação disponível em: `http://localhost:5006` (ou porta configurada)
- Health check: `http://localhost:5006/api`
- Login: `http://localhost:5006/login`

### 4. Configuração do Reverse Proxy
Configure seu servidor web (nginx/apache) para proxy reverso:

#### Nginx
```nginx
location /pdg {
    proxy_pass http://localhost:5006;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 🛠️ Desenvolvimento

### Executar localmente
```bash
# Ativar ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env

# Executar
python run.py
```

### Docker para desenvolvimento
```bash
docker-compose -f docker-compose.dev.yml up --build
```

## 📊 Monitoramento

### Logs
```bash
# Ver logs em tempo real
docker-compose logs -f sise-app

# Ver últimas 100 linhas
docker-compose logs --tail=100 sise-app
```

### Health Check
```bash
curl -f http://localhost:5006/api
```

### Métricas do Container
```bash
docker stats sise-flask-prod
```

## 🔧 Manutenção

### Atualizar aplicação
```bash
git pull
./deploy.sh production
```

### Backup do banco
```bash
# Criar backup
docker exec sise-mariadb mysqldump -u root -p sise_db > backup.sql

# Restaurar backup
docker exec -i sise-mariadb mysql -u root -p sise_db < backup.sql
```

### Limpar Docker
```bash
# Parar tudo
docker-compose down

# Limpar volumes órfãos
docker volume prune

# Limpar imagens não utilizadas
docker image prune -a
```

## 🔐 Segurança

- ✅ HTTPS enforced
- ✅ Secure cookies
- ✅ Non-root user no container
- ✅ Health checks configurados
- ✅ Logs estruturados
- ✅ Secrets via environment variables

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs: `docker-compose logs sise-app`
2. Verificar health check: `curl http://localhost:5006/api`
3. Verificar configurações de rede e Keycloak

## 🎯 URLs de Produção

- **Aplicação**: https://servicos.educorp.unicamp.br/pdg
- **Login**: https://servicos.educorp.unicamp.br/pdg/login
- **Dashboard**: https://servicos.educorp.unicamp.br/pdg/dashboard
- **API**: https://servicos.educorp.unicamp.br/pdg/api

## Funcionalidades

### Para Estudantes
- 📊 Dashboard com visão geral dos cursos
- 📚 Acompanhamento de cursos (Em andamento, Concluídos, Próximos)
- 🏆 Visualização de certificados
- 📈 Progresso e frequência de cursos
- 🔍 Busca e filtros de cursos

### Para Administradores
- 📈 Painel administrativo com estatísticas
- ⚙️ Configuração de ordem de cursos
- 👥 Gerenciamento de emails de administradores
- 📊 Relatórios e analytics
- 🔧 Configurações do sistema

## Como usar

### 1. Instale as dependências:
```powershell
pip install -r requirements.txt
```

### 2. Configure o ambiente (opcional):
Crie um arquivo `.env` na raiz do projeto:
```
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sua-conexao-banco-dados
```

### 3. Inicie o servidor Flask:
```powershell
python run.py
```

### 4. Acesse o sistema:
Abra o navegador em: `http://localhost:5000`

## Login de Demonstração

O sistema possui login temporário com usuários de demonstração:

### Estudante:
- **Email:** aluno@unicamp.br
- **Senha:** demo123

### Administrador:
- **Email:** joaoedu@unicamp.br  
- **Senha:** demo123

## API REST (Legado)

As rotas da API original ainda estão disponíveis:

### Autenticação via Keycloak:
```bash
# Fazer login
POST /api/auth/login
{
  "username": "SEU_USUARIO",
  "password": "SUA_SENHA"
}

# Acessar rota protegida
GET /api/auth/protected
Authorization: Bearer SEU_TOKEN_DE_ACESSO
```

### Consulta de cursos:
```bash
GET /api/courses
Authorization: Bearer SEU_TOKEN_DE_ACESSO
```

## Estrutura do Projeto

```
sise/
├── app/
│   ├── templates/          # Templates HTML
│   │   ├── base.html       # Layout base
│   │   ├── login.html      # Página de login
│   │   ├── dashboard.html  # Dashboard do usuário
│   │   ├── courses.html    # Lista de cursos
│   │   └── admin_dashboard.html # Painel admin
│   ├── __init__.py         # Factory da aplicação
│   ├── auth.py            # Autenticação Keycloak
│   ├── courses.py         # API de cursos
│   ├── lms.py             # Interface web LMS
│   ├── models.py          # Modelos do banco
│   └── extensions.py      # Extensões Flask
├── config/
│   └── config.py          # Configurações
├── course_config.json     # Configuração de cursos
├── requirements.txt       # Dependências
└── run.py                # Ponto de entrada
```

## Configuração de Cursos

O arquivo `course_config.json` controla:
- **codcua_order:** Ordem de exibição dos cursos
- **admin_emails:** Emails com privilégios administrativos

Exemplo:
```json
{
    "codcua_order": [101, 102, 103],
    "admin_emails": [
        "admin@unicamp.br",
        "coordenador@unicamp.br"
    ]
}
```

## Banco de Dados

O sistema utiliza as seguintes tabelas (views) do EDUCORP:
- `V_EDUCORP_FICHACOL` - Dados dos colaboradores/estudantes
- `V_EDUCORP_CURSO_APERF` - Informações dos cursos
- `V_EDUCORP_CURSO_APERF_COL` - Matrículas em cursos
- `V_EDUCORP_FREQUENCIA_TURMA` - Frequência e faltas

## Desenvolvimento

### Adicionando novas funcionalidades:
1. Modifique os templates em `app/templates/`
2. Adicione rotas no blueprint `lms.py`
3. Atualize os modelos em `models.py` se necessário

### Integrando com Keycloak:
1. Configure as variáveis em `config/config.py`
2. Substitua o login temporário pela autenticação real
3. Use o decorator `@token_required` nas rotas protegidas