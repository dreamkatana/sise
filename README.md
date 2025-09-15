# SISE Flask

Projeto Flask para integração com Red Hat SSO (SISE) usando python-keycloak.

## Como usar

1. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```

2. Inicie o servidor Flask:
   ```powershell
   C:/gitprojetos2/sise/.venv/Scripts/python.exe run.py
   ```

3. Faça login:
   Envie um POST para `/login` com JSON:
   ```json
   {
     "username": "SEU_USUARIO",
     "password": "SUA_SENHA"
   }
   ```
   O retorno será o token de acesso e informações do usuário.

4. Acesse rota protegida:
   Envie um GET para `/protected` com o header:
   ```
   Authorization: Bearer SEU_TOKEN_DE_ACESSO
   ```
   Se o token for válido, receberá `{"message": "Acesso autorizado!"}`.
