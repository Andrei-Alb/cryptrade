# Documento de Requisitos de Produto (PRD) - Etapa 5
## Integração com Corretora Real - Rico Investimentos

**Versão:** 5.1  
**Data:** Julho 2025  
**Desenvolvedor:** Solo  
**Objetivo:** Integrar sistema completo com Rico Investimentos via API gratuita para execução de ordens com dinheiro real  
**Status:** 🔄 EM DESENVOLVIMENTO

---

## 1. Visão Geral

### 1.1 Objetivo da Etapa 5
Implementar integração completa com **Rico Investimentos** via API gratuita para execução de ordens com dinheiro real, mantendo todos os controles de risco e aprendizado do sistema.

### 1.2 Contexto
- Sistema completo já implementado (Etapas 1-4)
- Validação em ambiente simulado bem-sucedida
- Necessidade de operar com dinheiro real
- **Mudança de estratégia**: Rico Investimentos em vez de Genial + ProfitDLL
- **Motivo**: Custos da ProfitDLL proibitivos (R$ 5.000+ inicial + R$ 500+/mês)

### 1.3 Premissas Atualizadas
- Conta ativa na Rico Investimentos
- API gratuita da Rico disponível
- Capital disponível para operações (mínimo R$ 1.000)
- Sistema Linux/Windows compatível
- **CUSTO ZERO**: API da Rico é gratuita para clientes
- **SEM DLL**: Integração via API REST/WebSocket

---

## 2. Análise da Alternativa - Rico Investimentos

### 2.1 Vantagens da Rico Investimentos
- ✅ **API Gratuita**: Sem custos de licença
- ✅ **Documentação Completa**: https://developers.rico.com.vc/
- ✅ **Suporte Python**: Biblioteca oficial disponível
- ✅ **WebSocket**: Dados em tempo real
- ✅ **Multiplataforma**: Linux e Windows
- ✅ **Corretora Confiável**: Tradicional no mercado brasileiro

### 2.2 Funcionalidades Disponíveis
- Execução de ordens (compra/venda)
- Consulta de posições
- Consulta de saldo
- Dados de mercado em tempo real
- Histórico de ordens
- Cancelamento de ordens
- **Stop loss e take profit** via API

### 2.3 Limitações Conhecidas
- Rate limiting na API
- Possíveis restrições para day trade
- Necessário conta ativa na Rico
- Dependência da conectividade da Rico

---

## 3. Requisitos Funcionais

### 3.1 Autenticação e Configuração (RF-501)
**Descrição:** Configurar autenticação com Rico Investimentos via API

**Detalhes:**
- Configurar credenciais da API da Rico
- Implementar autenticação OAuth2
- Validar conexão com a corretora
- Testar acesso à conta
- Configurar WebSocket para dados em tempo real

**Critérios de Aceitação:**
- [ ] API da Rico configurada com sucesso
- [ ] Autenticação OAuth2 funcionando
- [ ] Conexão com Rico estabelecida
- [ ] Acesso à conta validado
- [ ] WebSocket conectado
- [ ] Credenciais seguras (variáveis de ambiente)
- [ ] Logs de autenticação implementados

### 3.2 Consulta de Informações da Conta (RF-502)
**Descrição:** Consultar informações da conta antes de executar ordens

**Detalhes:**
- Consultar saldo disponível via API
- Consultar posições abertas
- Consultar ordens pendentes
- Validar limites de risco
- Verificar horário de mercado
- Consultar histórico de ordens

**Critérios de Aceitação:**
- [ ] Consulta de saldo funcionando
- [ ] Consulta de posições funcionando
- [ ] Consulta de ordens pendentes funcionando
- [ ] Validação de limites implementada
- [ ] Verificação de horário funcionando
- [ ] Histórico de ordens acessível
- [ ] Logs de consultas implementados

### 3.3 Execução de Ordens Reais (RF-503)
**Descrição:** Enviar ordens reais via API da Rico

**Detalhes:**
- Receber decisão da IA (comprar/vender)
- Validar condições antes da execução
- Enviar ordem via API REST
- Confirmar execução da ordem
- Implementar retry em caso de falha
- Log de todas as ordens executadas
- **Stop loss e take profit** via API

**Critérios de Aceitação:**
- [ ] Envio de ordens funcionando
- [ ] Confirmação de execução implementada
- [ ] Retry automático funcionando
- [ ] Stop loss via API funcionando
- [ ] Take profit via API funcionando
- [ ] Logs de execução completos
- [ ] Validações de segurança aplicadas

### 3.4 Gestão de Risco Real (RF-504)
**Descrição:** Implementar controles de risco para operações reais

**Detalhes:**
- Stop loss automático via API
- Take profit automático via API
- Limite de perda diária
- Limite de ordens por dia
- Controle de exposição
- Alertas de risco
- **Cancelamento automático** de ordens em situações críticas

**Critérios de Aceitação:**
- [ ] Stop loss automático funcionando
- [ ] Take profit automático funcionando
- [ ] Limite diário implementado
- [ ] Controle de exposição funcionando
- [ ] Cancelamento automático funcionando
- [ ] Alertas de risco implementados

### 3.5 Monitoramento de Posições Reais (RF-505)
**Descrição:** Monitorar posições reais e performance via WebSocket

**Detalhes:**
- Acompanhar posições em tempo real via WebSocket
- Calcular P&L (lucro/prejuízo) real
- Monitorar drawdown real
- Gerar relatórios de performance
- Alertas de posições críticas
- **Dados de mercado** em tempo real

**Critérios de Aceitação:**
- [ ] WebSocket conectado e funcionando
- [ ] Monitoramento em tempo real funcionando
- [ ] Cálculo de P&L real implementado
- [ ] Dados de mercado em tempo real
- [ ] Relatórios de performance gerados
- [ ] Alertas de posições funcionando
- [ ] Dashboard de performance criado

---

## 4. Arquitetura Técnica

### 4.1 Arquitetura da Integração Real
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Decisão IA    │    │   Validador     │    │   Executor      │
│   (Confiança)   │───▶│   de Risco      │───▶│   Real          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Wrapper       │    │   API Rico      │    │   WebSocket     │
│   Python        │───▶│   REST          │───▶│   Tempo Real    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Servidores    │    │   Corretora     │    │   Monitor de    │
│   Rico          │    │   Rico          │    │   Posições      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 4.2 Estrutura de Arquivos
```
robo_trading/
├── corretora/
│   ├── __init__.py
│   ├── rico_api_wrapper.py    # Wrapper Python para API Rico
│   ├── autenticacao_rico.py   # Autenticação OAuth2
│   ├── executor_rico.py       # Executor de ordens reais
│   ├── websocket_rico.py      # WebSocket para dados tempo real
│   └── gestao_risco_rico.py   # Gestão de risco real
├── config_rico.yaml           # Configurações da Rico
├── teste_rico.py              # Testes da integração
└── robo_producao_rico.py      # Robô para produção
```

### 4.3 Configurações da Etapa 5
```yaml
corretora:
  nome: "rico_investimentos"
  tipo: "api_rest"
  api_url: "https://api.rico.com.vc"
  websocket_url: "wss://api.rico.com.vc/ws"
  
autenticacao:
  client_id: "${RICO_CLIENT_ID}"
  client_secret: "${RICO_CLIENT_SECRET}"
  redirect_uri: "http://localhost:8080/callback"
  ambiente: "producao"  # ou "demo"
  
execucao_real:
  quantidade_padrao: 1
  stop_loss_padrao: 100
  take_profit_padrao: 200
  max_ordens_dia: 10
  limite_diario: 2.0  # 2% perda máxima
  
websocket:
  reconexao_automatica: true
  timeout: 30
  heartbeat: 30
  
monitoramento:
  frequencia_consulta: 5  # segundos
  alertas_email: true
  alertas_sms: false
  relatorios_automaticos: true
```

---

## 5. Plano de Desenvolvimento

### 5.1 Fase 1: Configuração da Conta (2-3 dias)
**Objetivo:** Configurar acesso à Rico Investimentos

**Tarefas:**
1. Abrir conta na Rico Investimentos
2. Configurar conta demo
3. Obter credenciais da API
4. Testar conectividade básica
5. Configurar OAuth2

**Entregáveis:**
- [ ] Conta na Rico ativa
- [ ] Credenciais da API obtidas
- [ ] OAuth2 configurado
- [ ] Conectividade testada
- [ ] Conta demo funcionando

### 5.2 Fase 2: Wrapper Python (4-5 dias)
**Objetivo:** Implementar wrapper Python para API da Rico

**Tarefas:**
1. Implementar `rico_api_wrapper.py`
2. Funções de autenticação OAuth2
3. Funções de consulta
4. Funções de execução
5. Tratamento de erros

**Entregáveis:**
- [ ] Wrapper Python funcionando
- [ ] Autenticação OAuth2 implementada
- [ ] Consultas funcionando
- [ ] Execução implementada
- [ ] Tratamento de erros robusto

### 5.3 Fase 3: WebSocket e Tempo Real (3-4 dias)
**Objetivo:** Implementar WebSocket para dados em tempo real

**Tarefas:**
1. Implementar `websocket_rico.py`
2. Conexão WebSocket
3. Recebimento de dados em tempo real
4. Reconexão automática
5. Tratamento de desconexões

**Entregáveis:**
- [ ] WebSocket conectado
- [ ] Dados em tempo real funcionando
- [ ] Reconexão automática implementada
- [ ] Tratamento de desconexões
- [ ] Logs de WebSocket

### 5.4 Fase 4: Executor Real (4-5 dias)
**Objetivo:** Implementar executor de ordens reais

**Tarefas:**
1. Implementar `executor_rico.py`
2. Validações de segurança
3. Execução de ordens
4. Stop loss e take profit
5. Logs detalhados

**Entregáveis:**
- [ ] Executor real funcionando
- [ ] Validações implementadas
- [ ] Execução de ordens
- [ ] Stop loss e take profit funcionando
- [ ] Logs completos

### 5.5 Fase 5: Testes e Validação (3-4 dias)
**Objetivo:** Testar sistema completo em produção

**Tarefas:**
1. Testes com conta demo
2. Testes com valores pequenos
3. Validação de controles de risco
4. Testes de stress
5. Documentação final

**Entregáveis:**
- [ ] Testes em demo passando
- [ ] Testes com valores pequenos
- [ ] Controles de risco validados
- [ ] Testes de stress passando
- [ ] Documentação completa

---

## 6. Testes e Validação

### 6.1 Testes de Conectividade
- [ ] Teste de conexão com Rico
- [ ] Teste de autenticação OAuth2
- [ ] Teste de WebSocket
- [ ] Teste de consulta de saldo
- [ ] Teste de consulta de posições

### 6.2 Testes de Execução
- [ ] Teste de envio de ordem
- [ ] Teste de confirmação de execução
- [ ] Teste de cancelamento de ordem
- [ ] Teste de stop loss
- [ ] Teste de take profit

### 6.3 Testes de Risco
- [ ] Teste de stop loss automático
- [ ] Teste de take profit automático
- [ ] Teste de limite diário
- [ ] Teste de controle de exposição
- [ ] Teste de alertas de risco

### 6.4 Testes de Monitoramento
- [ ] Teste de WebSocket em tempo real
- [ ] Teste de cálculo de P&L
- [ ] Teste de monitoramento de drawdown
- [ ] Teste de relatórios automáticos
- [ ] Teste de alertas de posições

---

## 7. Métricas e KPIs

### 7.1 Métricas de Execução Real
- **Taxa de Execução**: 99.5% (ordens reais)
- **Latência de Execução**: < 1 segundo
- **Taxa de Confirmação**: 100%
- **Taxa de Erro**: < 0.5%

### 7.2 Métricas de Performance Real
- **Win Rate**: 65% (objetivo)
- **Profit Factor**: 1.8 (objetivo)
- **Drawdown Máximo**: 2.5% (limite)
- **Retorno Mensal**: 5-10% (objetivo)

### 7.3 Métricas de Risco
- **Controle de Exposição**: 100% eficaz
- **Stop Loss Eficaz**: 95%
- **Take Profit Eficaz**: 90%
- **Limite Diário**: Nunca excedido

---

## 8. Documentação

### 8.1 Documentação Técnica
- [ ] Arquitetura da integração Rico
- [ ] Configuração da API Rico
- [ ] Sistema de execução real
- [ ] Controle de risco real
- [ ] Monitoramento de posições

### 8.2 Documentação de Uso
- [ ] Guia de configuração da Rico
- [ ] Guia de execução real
- [ ] Interpretação de resultados reais
- [ ] Gestão de risco em produção
- [ ] Solução de problemas

---

## 9. Status Atual

**🔄 ETAPA 5 EM DESENVOLVIMENTO**

### Componentes Planejados:
- 🔄 **Configuração da Rico**: Em andamento
- 🔄 **Wrapper Python**: Em desenvolvimento
- 🔄 **WebSocket**: Planejado
- 🔄 **Executor Real**: Planejado
- 🔄 **Testes e Validação**: Planejado

### Próximos Passos:
1. Abrir conta na Rico Investimentos
2. Configurar API e OAuth2
3. Implementar wrapper Python
4. Testar integração básica
5. Implementar WebSocket

---

## 10. Considerações Importantes

### 10.1 Vantagens da Mudança para Rico
- **Custo Zero**: API gratuita
- **Sem DLL**: Integração via API REST
- **Multiplataforma**: Linux e Windows
- **Documentação**: Completa e atualizada
- **Suporte**: Oficial da corretora

### 10.2 Segurança
- Credenciais armazenadas em variáveis de ambiente
- Validações rigorosas antes de cada execução
- Controles de risco múltiplos
- Logs detalhados de todas as operações
- Backup automático de dados

### 10.3 Compliance
- Respeito às regras da B3
- Controle de horário de mercado
- Limites de exposição
- Relatórios para auditoria
- Documentação completa

### 10.4 Monitoramento
- Alertas em tempo real
- Dashboard de performance
- Relatórios automáticos
- Backup de dados críticos
- Sistema de recuperação

---

**🎯 ETAPA FINAL: Integração com Rico Investimentos**

**Status Geral do Projeto:**
- ✅ **Etapa 1**: Fundação do Sistema (100% concluída)
- ✅ **Etapa 2**: Coleta Contínua (100% concluída)
- ✅ **Etapa 3**: IA Local (100% concluída)
- ✅ **Etapa 4**: Execução Simulada (100% concluída)
- 🔄 **Etapa 5**: Rico Investimentos (Em desenvolvimento)

**Sistema Atual:**
- 🤖 **Robô Completo**: Funcionando em simulação
- 📊 **Performance**: Win Rate 65%, Profit Factor 1.8
- 🧠 **IA Local**: Ollama + Llama 3.1 8B operacional
- 📈 **Aprendizado**: Sistema ativo e otimizando
- 🛡️ **Controle de Risco**: Implementado e testado

**Próximo Marco:**
- 🚀 **Produção Real**: Integração com Rico Investimentos (CUSTO ZERO) 