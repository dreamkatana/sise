# Relatório de Gestão de Cursos - SISE

## Visão Geral

O **Relatório de Gestão de Cursos** é uma funcionalidade completa do Painel Administrativo que permite acompanhar o progresso dos alunos em relação às disciplinas oferecidas, facilitando a análise de metas de conclusão por curso e por aluno.

**⚠️ IMPORTANTE:** O relatório exibe apenas os cursos configurados na lista do Painel de Administração (`codcua_order`). Para visualizar dados, é necessário configurar os códigos dos cursos desejados.

## Configuração Necessária

### 📋 **Pré-requisitos**
1. **Configurar Lista de Cursos:**
   - Acesse o Painel Administrativo
   - Clique em "Editar Configuração" 
   - Insira os códigos dos cursos desejados (ex: 623,722,769,804)
   - Salve a configuração

2. **Estrutura do course_config.json:**
```json
{
    "codcua_order": [623, 722, 769, 804],
    "admin_emails": ["admin@unicamp.br"]
}
```

### 🎯 **Filtro Automático**
- Apenas cursos com códigos listados em `codcua_order` aparecem no relatório
- A ordem de exibição segue a sequência configurada no painel
- Cursos não configurados são automaticamente excluídos

## Funcionalidades Principais

### 📊 **Estatísticas Gerais**
- **Total de Cursos:** Quantidade de disciplinas configuradas
- **Total de Alunos:** Número total de estudantes matriculados nos cursos ativos
- **Alunos em Andamento:** Estudantes atualmente cursando
- **Taxa de Conclusão Geral:** Percentual global de conclusão

### 📈 **Resumo por Curso**
Tabela consolidada mostrando apenas cursos configurados:
- Nome do curso e carga horária oferecida
- Número total de alunos matriculados
- Distribuição por status (concluídos, em andamento, pendentes)
- Taxa de conclusão média do curso
- Barra de progresso visual
- **Ordenação:** Segue a ordem definida em `codcua_order`

### 👥 **Detalhamento por Aluno**
Visão completa individual contendo:
- Dados do aluno (nome, email, matrícula)
- Curso e turma (apenas cursos configurados)
- Carga horária total vs horas concluídas
- Horas restantes para conclusão
- Percentual de progresso
- Status atual
- Quantidade de faltas
- Período de realização

## Interface Adaptativa

### 🚫 **Quando Não Há Cursos Configurados**
- Exibe aviso informativo centralizado
- Ícone de alerta com explicação clara
- Botão direto para configuração de cursos
- Remove botões de exportação desnecessários

### ✅ **Quando Há Cursos Configurados**
- Interface completa com todos os recursos
- Filtros funcionais por curso
- Exportação disponível
- Estatísticas detalhadas

## Filtros Avançados

### 🔍 **Opções de Filtro**
1. **Por Curso:** Lista apenas cursos configurados no admin
2. **Por Status:** Filtrar por situação do aluno
3. **Por Conclusão Mínima:** Slider para definir percentual mínimo
4. **Limpar Filtros:** Reset rápido de todos os filtros

### 📋 **Status Disponíveis**
- **Concluído** 🟢: Curso finalizado com sucesso
- **Em Andamento** 🟡: Cursando atualmente
- **Pendente** ⚫: Não iniciado ou pausado
- **Cancelado** 🔴: Cancelado/trancado

## Consulta SQL Otimizada

### 🎯 **Filtro Principal**
```sql
WHERE CursoAperf.CODCUA IN (codcua_order)
```

### 📊 **Ordenação Inteligente**
```sql
ORDER BY CASE 
    WHEN CursoAperf.CODCUA = 623 THEN 0
    WHEN CursoAperf.CODCUA = 722 THEN 1
    WHEN CursoAperf.CODCUA = 769 THEN 2
    WHEN CursoAperf.CODCUA = 804 THEN 3
    ELSE 999
END, FichaCol.NOMFUN
```

## Recursos de Exportação

### 📥 **Exportar Excel/CSV**
- Dados filtrados para análise externa
- Apenas cursos configurados no admin
- Formato compatível com planilhas
- Nome do arquivo com data automática

### 🖨️ **Impressão**
- Layout otimizado para impressão
- Mantém formatação e cores
- Versão limpa para relatórios físicos

## Gestão de Configuração

### ⚙️ **Adicionando Cursos**
1. Painel Admin → "Editar Configuração"
2. Campo "Ordem dos Cursos": `623,722,769,804`
3. Salvar configuração
4. Relatório atualiza automaticamente

### 🔄 **Removendo Cursos**
1. Editar lista `codcua_order`
2. Remover códigos indesejados
3. Salvar → Cursos desaparecem do relatório

### 📋 **Monitoramento**
- Logs mostram cursos configurados: `[DEBUG] Cursos configurados no admin: [623, 722, 769, 804]`
- Contagem de registros: `[DEBUG] Encontrados X registros para cursos configurados`

## Cálculos Realizados

### ⚡ **Horas Concluídas**
```
Horas Concluídas = Carga Horária Total - Horas de Falta
```

### 📊 **Percentual de Conclusão**
```
% Conclusão = (Horas Concluídas / Carga Horária Total) × 100
```

### 🎯 **Taxa de Conclusão por Curso**
```
Taxa Curso = (Total Horas Concluídas / Total Horas Possíveis) × 100
```

## Acesso ao Relatório

### 🔐 **Requisitos**
- Login como administrador
- Email configurado em `admin_emails`
- **Cursos configurados em `codcua_order`**

### 🌐 **URL de Acesso**
```
/admin/relatorio-gestao
```

### � **Resolução de Problemas**

**Problema:** "Nenhum curso configurado"
**Solução:** 
1. Acesse Painel Admin
2. Editar Configuração
3. Adicione códigos em "Ordem dos Cursos"
4. Salve e recarregue o relatório

**Problema:** Curso não aparece
**Solução:**
1. Verifique se o código está em `codcua_order`
2. Confirme se existem alunos matriculados
3. Verifique logs para erros SQL

## Dados de Origem

### 🗄️ **Tabelas Utilizadas**
- `V_EDUCORP_CURSO_APERF` - Informações dos cursos (FILTRADA)
- `V_EDUCORP_FICHACOL` - Dados dos colaboradores/estudantes  
- `V_EDUCORP_CURSO_APERF_COL` - Matrículas em cursos
- `V_EDUCORP_FREQUENCIA_TURMA` - Frequência e faltas

### 🔗 **Relacionamentos com Filtro**
```sql
-- JOIN principal COM FILTRO de cursos configurados
SELECT * FROM CURSO_APERF ca
JOIN CURSO_APERF_COL cac ON ca.CODCUA = cac.CODCUA
JOIN FICHACOL fc ON cac.TIPCOL = fc.TIPCOL AND cac.NUMCAD = fc.NUMCAD
LEFT JOIN FREQUENCIA_TURMA ft ON ...
WHERE ca.CODCUA IN (623, 722, 769, 804)  -- FILTRO PRINCIPAL
ORDER BY CASE ca.CODCUA                   -- ORDEM CONFIGURADA
```

## Manutenção e Suporte

### � **Configuração Dinâmica**
- Dados atualizados em tempo real
- Filtro automático por configuração admin
- Sem necessidade de restart da aplicação

### 📊 **Monitoramento**
- Logs detalhados em modo debug
- Contagem de registros processados
- Identificação de cursos configurados vs encontrados

---

*Relatório desenvolvido para o sistema SISE - Sistema Integrado de Serviços Educacionais*
*Versão 2.0 - Com filtro por configuração administrativa*