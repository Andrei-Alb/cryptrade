# Documento de Requisitos de Produto (PRD) - Etapa 2
## Implementação da Coleta Contínua de Dados - Robô de Trading Pessoal

**Versão:** 2.1  
**Data:** Julho 2025  
**Desenvolvedor:** Solo  
**Objetivo:** Sistema de coleta contínua e automática de dados da API B3  
**Status:** IMPLEMENTADO E OPERACIONAL ✅

---

## 1. Visão Geral

### 1.1 Objetivo da Etapa 2
Implementar um sistema de coleta contínua e automática de dados da API oficial da B3, com testes de frequência e otimização da taxa de atualização, **respeitando dias úteis e horário de mercado (09:00–17:00)**. Fora desse período, o sistema entra em modo de espera, sem realizar coletas.

### 1.2 Contexto
- A API da B3 está funcionando e retornando dados reais
- Precisamos determinar a frequência ideal de coleta
- Sistema deve operar automaticamente durante horário de mercado, aguardando fora dele
- Necessário implementar tratamento de erros robusto
- **Modo de teste disponível para simular coleta contínua a qualquer momento, ignorando restrições de horário**

### 1.3 Premissas
- API da B3 tem limitações de rate limiting não documentadas
- Dados podem ter latência variável
- Sistema deve ser resiliente a falhas temporárias
- Coleta deve ser eficiente (não sobrecarregar a API)

---

## 2. Requisitos Funcionais

### 2.1 Teste de Frequência da API (RF-201)
**Descrição:** Determinar a frequência máxima e ideal de coleta da API da B3

**Detalhes:**
- Testar frequências de 1, 5, 10, 15, 30, 60 segundos
- Monitorar latência de resposta da API
- Identificar rate limiting e erros 429
- Medir taxa de sucesso por frequência
- Testar durante diferentes horários de mercado

**Critérios de Aceitação:**
- [x] Script de teste implementado
- [x] Testes executados por 2 horas cada frequência
- [x] Relatório de performance gerado
- [x] Frequência ideal identificada (30s)
- [x] Limites da API documentados
- [x] Sistema de coleta contínua operacional

### 2.2 Coleta Contínua Automática (RF-202)
**Descrição:** Implementar sistema de coleta contínua baseado na frequência otimizada

**Detalhes:**
- Executar coleta em loop contínuo
- Frequência configurável (padrão: 30 segundos)
- **Operar apenas durante horário de mercado (09:00–17:00, dias úteis)**
- **Fora do horário de mercado, entrar em modo de espera e aguardar o próximo período útil**
- Pausar automaticamente fora do horário
- Reiniciar automaticamente em caso de erro
- **Modo de teste disponível para simular coleta contínua sem restrição de horário**

**Critérios de Aceitação:**
- [x] Loop de coleta implementado
- [x] Controle de horário de mercado funcionando
- [x] Modo de espera fora do horário funcionando
- [x] Modo de teste disponível
- [x] Reinicialização automática implementada
- [x] Logs detalhados de cada coleta
- [x] Sistema roda 24/7 sem interrupção
- [x] Integração com robô de IA completo

### 2.3 Tratamento de Erros Robusto (RF-203)
**Descrição:** Implementar tratamento de erros para garantir continuidade da coleta

**Detalhes:**
- Tratar erros de rede (timeout, connection refused)
- Tratar rate limiting (HTTP 429)
- Implementar backoff exponencial
- Fallback para dados simulados se necessário
- Alertas para falhas críticas

**Critérios de Aceitação:**
- [x] Tratamento de timeout implementado
- [x] Backoff exponencial funcionando
- [x] Fallback para dados simulados
- [x] Alertas configurados *(logs e warnings)*
- [x] Sistema se recupera automaticamente

### 2.4 Monitoramento e Logs (RF-204)
**Descrição:** Implementar sistema de monitoramento e logs detalhados

**Detalhes:**
- Log de cada tentativa de coleta
- Métricas de performance (latência, taxa de sucesso)
- Alertas para falhas consecutivas
- Dashboard simples de status
- Histórico de disponibilidade da API

**Critérios de Aceitação:**
- [x] Logs estruturados implementados
- [x] Métricas de performance coletadas
- [x] Alertas configurados
- [x] Dashboard básico funcionando *(monitor.py, modo CLI)*
- [x] Histórico mantido por 7 dias *(logs rotativos)*

### 2.5 Funcionamento do Horário de Mercado e Modo de Teste (NOVO)
**Descrição:** O sistema respeita automaticamente o horário de mercado brasileiro (09:00–17:00, dias úteis). Fora desse período, entra em modo de espera, sem realizar requisições à API, e verifica periodicamente se o mercado abriu. Para depuração e validação, há um modo de teste que ignora as restrições de horário e executa a coleta contínua a qualquer momento.

**Detalhes:**
- Coleta real ocorre apenas em dias úteis e horário de mercado
- Fora desse período, o sistema aguarda e não faz requisições
- Logs informam claramente quando está aguardando o mercado abrir
- Modo de teste executa ciclos de coleta contínua sem restrição de horário, útil para desenvolvimento e validação
- Armazenamento dos dados em banco SQLite local
- Logs detalhados de operação e erros
- Uso da API oficial da B3 como fonte principal de dados

**Critérios de Aceitação:**
- [x] Sistema entra em modo de espera fora do horário de mercado
- [x] Logs informam status de espera e retomada
- [x] Modo de teste disponível e funcional
- [x] Dados reais salvos corretamente em SQLite
- [x] Uso da API oficial da B3 comprovado nos logs

---

## 3. Design Técnico

### 3.1 Arquitetura da Coleta Contínua
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scheduler     │    │   Coletor       │    │   Armazenamento │
│   (30s loop)    │───▶│   (API B3)      │───▶│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Controle de   │    │   Tratamento    │    │   Monitoramento │
│   Horário       │    │   de Erros      │    │   e Logs        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3.2 Estrutura de Arquivos
```
robo_trading/
├── main_continuo.py        # Script principal de coleta contínua
├── testador_frequencia.py  # Script para testar frequências
├── monitor.py              # Módulo de monitoramento
├── scheduler.py            # Módulo de agendamento
├── coletor.py              # Módulo de coleta (já existente)
├── armazenamento.py        # Módulo de banco (já existente)
├── config.py               # Configurações (já existente)
├── logs/                   # Pasta de logs
├── dados/                  # Pasta de dados
└── relatorios/             # Pasta para relatórios de teste
```

### 3.3 Configurações da Etapa 2
```yaml
coleta_continua:
  frequencia_padrao: 30  # segundos
  frequencias_teste: [1, 5, 10, 15, 30, 60]
  duracao_teste: 7200    # segundos (2 horas)
  horario_inicio: "09:00"
  horario_fim: "17:00"
  dias_semana: [1, 2, 3, 4, 5]  # Segunda a Sexta
  
tratamento_erros:
  max_tentativas: 3
  backoff_inicial: 5     # segundos
  backoff_maximo: 300    # segundos
  timeout_padrao: 10     # segundos
  
monitoramento:
  alerta_falhas_consecutivas: 5
  log_detalhado: true
  salvar_metricas: true
  retencao_logs: 7       # dias
```

---

## 4. Plano de Desenvolvimento

### 4.1 Fase 1: Teste de Frequência (2-3 dias)
**Objetivo:** Determinar a frequência ideal de coleta

**Tarefas:**
1. Implementar `testador_frequencia.py`
2. Executar testes para cada frequência
3. Coletar métricas de performance
4. Analisar resultados e identificar frequência ideal
5. Documentar limites da API

**Entregáveis:**
- [ ] Script de teste funcionando
- [ ] Relatório de performance
- [ ] Frequência ideal identificada
- [ ] Documentação dos limites da API

### 4.2 Fase 2: Implementação da Coleta Contínua (2-3 dias)
**Objetivo:** Implementar sistema de coleta automática

**Tarefas:**
1. Implementar `scheduler.py`
2. Implementar `main_continuo.py`
3. Integrar controle de horário de mercado
4. Implementar reinicialização automática
5. Testar coleta por 8 horas

**Entregáveis:**
- [ ] Sistema de coleta contínua funcionando
- [ ] Controle de horário implementado
- [ ] Reinicialização automática funcionando
- [ ] Teste de 8 horas bem-sucedido

### 4.3 Fase 3: Tratamento de Erros (1-2 dias)
**Objetivo:** Implementar tratamento robusto de erros

**Tarefas:**
1. Implementar backoff exponencial
2. Implementar fallback para dados simulados
3. Configurar alertas
4. Testar cenários de falha
5. Validar recuperação automática

**Entregáveis:**
- [ ] Tratamento de erros implementado
- [ ] Backoff exponencial funcionando
- [ ] Fallback configurado
- [ ] Alertas funcionando
- [ ] Recuperação automática validada

### 4.4 Fase 4: Monitoramento (1-2 dias)
**Objetivo:** Implementar sistema de monitoramento

**Tarefas:**
1. Implementar `monitor.py`
2. Configurar logs estruturados
3. Implementar coleta de métricas
4. Criar dashboard básico
5. Configurar retenção de logs

**Entregáveis:**
- [ ] Sistema de monitoramento funcionando
- [ ] Logs estruturados implementados
- [ ] Métricas sendo coletadas
- [ ] Dashboard básico criado
- [ ] Retenção de logs configurada

---

## 5. Critérios de Sucesso

### 5.1 Performance
- Taxa de sucesso > 95% na coleta
- Latência média < 2 segundos
- Zero falhas consecutivas > 10 tentativas
- Sistema estável por 24 horas

### 5.2 Confiabilidade
- Recuperação automática de falhas
- Fallback funcionando corretamente
- Logs completos e acessíveis
- Alertas funcionando

### 5.3 Eficiência
- Frequência otimizada identificada
- Uso eficiente da API (sem rate limiting)
- Baixo consumo de recursos
- Operação automática sem intervenção

---

## 6. Riscos e Mitigações

### 6.1 Riscos Técnicos
- **API da B3 instável**: Implementar fallback robusto
- **Rate limiting agressivo**: Usar backoff exponencial
- **Falhas de rede**: Implementar retry com timeout
- **Sobrecarga do sistema**: Monitorar recursos

### 6.2 Riscos de Negócio
- **Dados desatualizados**: Validar timestamp dos dados
- **Perda de dados**: Implementar backup em tempo real
- **Falhas durante mercado**: Alertas imediatos

---

## 7. Próximos Passos Após Etapa 2

1. **Integração com IA**: Conectar dados coletados com análise
2. **Execução de Ordens**: Implementar execução automática
3. **Dashboard Avançado**: Interface web para monitoramento
4. **Alertas Avançados**: Notificações por email/SMS
5. **Backtesting**: Testar estratégias com dados históricos

---

## 8. Histórico de Versões
- **2.0**: PRD criado para implementação da coleta contínua (JUL/2025) 