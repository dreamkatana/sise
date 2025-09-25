#!/bin/bash
# Script para testar o SISE Flask

echo "=== Teste do SISE Flask ==="
echo

echo "1. Testando se o container está rodando:"
curl -s http://localhost:5006/api || echo "❌ Container não responde"

echo
echo "2. Testando rotas básicas:"
echo "GET /pdg/ através do nginx:"
curl -s -I https://servicos.educorp.unicamp.br/pdg/ | head -1

echo
echo "GET /pdg/api através do nginx:"
curl -s -I https://servicos.educorp.unicamp.br/pdg/api | head -1

echo
echo "3. Testando redirecionamentos:"
echo "GET /login (deve redirecionar para /pdg/login):"
curl -s -I https://servicos.educorp.unicamp.br/login | grep Location

echo "GET /api/auth/direct-login (deve redirecionar para /pdg/api/auth/direct-login):"
curl -s -I https://servicos.educorp.unicamp.br/api/auth/direct-login | grep Location

echo
echo "=== Fim dos testes ==="