# SISE Flask - LMS Educacional

Sistema de Gerenciamento de Aprendizagem (LMS) integrado com Red Hat SSO (SISE) usando python-keycloak.

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