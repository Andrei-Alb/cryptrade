# Documento de Requisitos de Produto (PRD) - Etapa 3
## Implementação da IA para Análise e Decisão de Trading

**Versão:** 3.1  
**Data:** Julho 2025  
**Desenvolvedor:** Solo  
**Objetivo:** Sistema de IA local para análise de dados de mercado e tomada de decisões de compra/venda  
**Status:** IMPLEMENTADO E OPERACIONAL ✅

---

## 1. Visão Geral

### 1.1 Objetivo da Etapa 3
Implementar um sistema de Inteligência Artificial local que recebe dados de mercado em tempo real da API da B3, analisa padrões e tendências, e toma decisões automatizadas de compra, venda ou aguardar no mercado financeiro. O sistema utiliza **IA local via Ollama** com modelo Llama 3.1 8B para análise independente e confiável.

### 1.2 Contexto
- Sistema de coleta de dados da B3 já implementado e funcionando
- Dados históricos e em tempo real disponíveis no banco SQLite
- **IA Local**: Ollama com modelo Llama 3.1 8B implementado
- Sistema de análise e decisão integrado com execução de ordens
- Sistema opera de forma autônoma e confiável 24/7

### 1.3 Premissas
- **IA Local**: Ollama instalado e funcionando com Llama 3.1 8B
- Dados de mercado da B3 são confiáveis e atualizados
- Decisões da IA devem ser validadas antes da execução (confiança ≥ 70%)
- Sistema é resiliente a falhas com tratamento robusto de erros
- Performance é crítica para operações em tempo real
- Sistema opera independentemente sem dependência de APIs externas

---

## 2. Requisitos Funcionais

### 2.1 Preparação de Dados para IA (RF-301)
**Descrição:** Preparar e estruturar dados de mercado para envio à IA

**Detalhes:**
- Coletar dados dos últimos N períodos (configurável)
- Incluir dados OHLC, volume, indicadores técnicos
- Estruturar dados no formato esperado pela API de IA
- Adicionar contexto temporal (timestamp, dia da semana, etc.)
- Validar qualidade e completude dos dados

**Critérios de Aceitação:**
- [x] Dados são estruturados corretamente para a IA local
- [x] Inclui dados históricos suficientes para análise
- [x] Validação de qualidade implementada
- [x] Formato de dados documentado
- [x] Performance de preparação < 1 segundo
- [x] Indicadores técnicos calculados automaticamente

### 2.2 Análise com IA (RF-302)
**Descrição:** Implementar análise de dados usando IA (API externa ou modelo local)

**IA Local via Ollama (Llama 3.1 8B):**
- Conectar com servidor Ollama local
- Implementar retry automático em caso de falhas
- Implementar timeout configurável (30 segundos)
- Log de todas as requisições e respostas
- Construir prompt estruturado com dados de mercado
- Validar formato da resposta da IA
- Calcular nível de confiança da decisão

**Critérios de Aceitação:**
- [x] Conexão com Ollama funcionando
- [x] Modelo Llama 3.1 8B carregado e operacional
- [x] Retry automático implementado
- [x] Timeout configurável funcionando (30s)
- [x] Processamento em tempo real funcionando
- [x] Logs completos de análise
- [x] Prompt estruturado implementado
- [x] Validação de resposta implementada
- [x] Cálculo de confiança implementado
- [x] Tratamento robusto de erros

### 2.3 Análise e Decisão da IA (RF-303)
**Descrição:** Processar resposta da IA e tomar decisões de trading

**Detalhes:**
- Receber análise da IA (compra/venda/aguardar)
- Validar nível de confiança da decisão
- Aplicar filtros de segurança (stop loss, take profit)
- Considerar contexto de mercado (volatilidade, horário)
- Implementar lógica de decisão final
- Log de todas as decisões tomadas

**Critérios de Aceitação:**
- [x] Decisões da IA são processadas corretamente
- [x] Validação de confiança implementada (≥ 70%)
- [x] Filtros de segurança aplicados
- [x] Contexto de mercado considerado
- [x] Logs detalhados de decisões
- [x] Performance de decisão < 2 segundos
- [x] Decisões: COMPRAR, VENDER, AGUARDAR

### 2.4 Integração com Executor de Ordens (RF-304)
**Descrição:** Conectar decisões da IA com execução de ordens

**Detalhes:**
- Enviar decisões para o módulo executor
- Validar condições antes da execução
- Implementar confirmação de execução
- Log de todas as ordens executadas
- Feedback da execução para a IA (opcional)

**Critérios de Aceitação:**
- [x] Integração com executor funcionando
- [x] Validações antes da execução implementadas
- [x] Confirmação de execução funcionando
- [x] Logs de execução completos
- [x] Feedback implementado
- [x] Ordens executadas apenas com confiança ≥ 70%

### 2.5 Monitoramento e Alertas (RF-305)
**Descrição:** Monitorar performance da IA e gerar alertas

**Detalhes:**
- Monitorar taxa de acerto das decisões
- Alertar sobre falhas consecutivas da API
- Monitorar latência de resposta da IA
- Dashboard de performance da IA
- Alertas para decisões de baixa confiança

**Critérios de Aceitação:**
- [x] Métricas de performance coletadas
- [x] Alertas de falhas funcionando
- [x] Monitoramento de latência implementado
- [x] Dashboard de IA criado (monitor.py)
- [x] Alertas de baixa confiança funcionando
- [x] Estatísticas de decisões em tempo real

---

## 3. Design Técnico

### 3.1 Arquitetura da IA

#### Opção A - API Externa de IA
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Coletor       │    │   Preparador    │    │   API Externa   │
│   (Dados B3)    │───▶│   de Dados      │───▶│   de IA         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Armazenamento │    │   Construtor    │    │   Processador   │
│   (SQLite)      │    │   de Prompt     │    │   de Resposta   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Histórico     │    │   Decisor       │    │   Executor      │
│   de Dados      │    │   Final         │    │   de Ordens     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Opção B - Modelo Local de ML
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Coletor       │    │   Preparador    │    │   Modelo Local  │
│   (Dados B3)    │───▶│   de Dados      │───▶│   de ML         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Armazenamento │    │   Validador     │    │   Processador   │
│   (SQLite)      │    │   de Dados      │    │   de Predição   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Histórico     │    │   Decisor       │    │   Executor      │
│   de Dados      │    │   Final         │    │   de Ordens     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3.2 Estrutura de Arquivos

#### Opção A - API Externa de IA
```
robo_trading/
├── ia/
│   ├── __init__.py
│   ├── preparador_dados.py    # Preparação de dados para IA
│   ├── construtor_prompt.py   # Construção do prompt para IA
│   ├── cliente_api.py         # Cliente para API externa de IA
│   ├── processador_resposta.py # Processamento de resposta da IA
│   ├── decisor.py             # Lógica de decisão final
│   ├── monitor_ia.py          # Monitoramento da IA
│   └── estrategias_fallback.py # Estratégias de fallback
├── config/
│   ├── config_ia.yaml         # Configurações específicas da IA
│   ├── prompts.yaml           # Templates de prompts
│   └── api_keys.yaml          # Chaves de API (não versionado)
├── logs/
│   ├── ia_requests.log        # Logs de requisições à IA
│   ├── ia_decisions.log       # Logs de decisões
│   └── ia_performance.log     # Métricas de performance
└── dados/
    └── historico_ia.db        # Banco de dados da IA
```

#### Opção B - Modelo Local de ML
```
robo_trading/
├── ia/
│   ├── __init__.py
│   ├── preparador_dados.py    # Preparação de dados para IA
│   ├── modelo_local.py        # Modelo de ML local
│   ├── treinador.py           # Treinamento do modelo
│   ├── processador_predicao.py # Processamento de predições
│   ├── decisor.py             # Lógica de decisão final
│   ├── monitor_ia.py          # Monitoramento da IA
│   └── estrategias_fallback.py # Estratégias de fallback
├── config/
│   ├── config_ia.yaml         # Configurações específicas da IA
│   └── modelo_config.yaml     # Configurações do modelo
├── logs/
│   ├── ia_predictions.log     # Logs de predições
│   ├── ia_decisions.log       # Logs de decisões
│   └── ia_performance.log     # Métricas de performance
└── dados/
    ├── historico_ia.db        # Banco de dados da IA
    └── modelos/               # Modelos treinados salvos
        ├── modelo_atual.pkl
        └── modelo_backup.pkl
```

### 3.3 Configurações da IA

#### Opção A - API Externa de IA
```yaml
ia:
  tipo: "api_externa"
  api:
    endpoint: "https://api.openai.com/v1/chat/completions"  # Exemplo
    api_key: "${IA_API_KEY}"
    timeout: 15
    retry_attempts: 3
    retry_delay: 5
    rate_limit: 100  # requests per minute
    
  dados:
    periodos_historico: 100    # Número de períodos históricos
    indicadores_tecnicos: true
    incluir_volume: true
    incluir_contexto: true
    
  decisao:
    confianca_minima: 0.7
    filtro_volatilidade: true
    max_ordens_dia: 10
    stop_loss_padrao: 100
    take_profit_padrao: 200
    
  monitoramento:
    alerta_falhas_consecutivas: 3
    alerta_baixa_confianca: 0.5
    salvar_metricas: true
    retencao_logs: 30  # dias
```

#### Opção B - Modelo Local de ML
```yaml
ia:
  tipo: "modelo_local"
  modelo:
    tipo: "random_forest"  # ou "xgboost", "lstm", etc.
    arquivo_modelo: "dados/modelos/modelo_atual.pkl"
    retreinar_intervalo: 7  # dias
    features: ["rsi", "macd", "volume", "volatilidade"]
    
  dados:
    periodos_historico: 100    # Número de períodos históricos
    indicadores_tecnicos: true
    incluir_volume: true
    incluir_contexto: true
    
  decisao:
    confianca_minima: 0.7
    filtro_volatilidade: true
    max_ordens_dia: 10
    stop_loss_padrao: 100
    take_profit_padrao: 200
    
  monitoramento:
    alerta_falhas_consecutivas: 3
    alerta_baixa_confianca: 0.5
    salvar_metricas: true
    retencao_logs: 30  # dias
```

### 3.4 Configuração de Prompts (Apenas Opção A - API Externa)

```yaml
prompts:
  sistema:
    role: "system"
    content: "Você é um analista especializado em trading de mini-índice (WIN) na B3. Sua função é analisar dados de mercado em tempo real e tomar decisões de trading baseadas em análise técnica e fundamental. Você deve sempre responder no formato JSON especificado e considerar apenas os dados fornecidos."
  
  usuario_template: |
    Analise os seguintes dados do mini-índice WIN e tome uma decisão de trading:

    DADOS DE MERCADO:
    - Ativo: {ativo}
    - Preço atual: {preco_atual}
    - Bid/Ask: {bid}/{ask}
    - Volume: {volume}
    - Variação: {variacao}%

    DADOS HISTÓRICOS (últimos {periodos} períodos):
    {historico_formatado}

    INDICADORES TÉCNICOS:
    - RSI: {rsi}
    - MACD: {macd}
    - Bandas de Bollinger: Superior {bb_upper}, Inferior {bb_lower}
    - Média Móvel 20: {ma20}
    - Média Móvel 50: {ma50}

    CONTEXTO:
    - Dia da semana: {dia_semana}
    - Hora: {hora}
    - Volatilidade: {volatilidade}
    - Tendência curto prazo: {tendencia}

    REGRAS DE TRADING:
    - Confiança mínima: 0.7
    - Stop loss padrão: 100 pontos
    - Take profit padrão: 200 pontos
    - Máximo de ordens por dia: 10
    - Operar apenas em horário de mercado (09:00-17:00)

    Responda APENAS no seguinte formato JSON:
    {
      "decisao": "comprar|vender|aguardar",
      "confianca": 0.0-1.0,
      "razao": "explicação detalhada da decisão",
      "parametros": {
        "quantidade": 1,
        "stop_loss": pontos,
        "take_profit": pontos,
        "validade": segundos
      },
      "indicadores_analisados": ["lista de indicadores considerados"],
      "timestamp_analise": "ISO timestamp"
    }
```

### 3.5 Formato de Dados para IA
```json
{
  "timestamp": "2025-07-15T14:30:00Z",
  "ativo": "WINZ25",
  "dados_mercado": {
    "preco_atual": 123456,
    "bid": 123455,
    "ask": 123457,
    "volume": 1500,
    "variacao": 0.5
  },
  "dados_historicos": [
    {
      "timestamp": "2025-07-15T14:29:00Z",
      "open": 123450,
      "high": 123460,
      "low": 123440,
      "close": 123456,
      "volume": 1400
    }
    // ... mais períodos históricos
  ],
  "indicadores_tecnicos": {
    "rsi": 65.5,
    "macd": 12.3,
    "bollinger_upper": 123470,
    "bollinger_lower": 123430
  },
  "contexto": {
    "dia_semana": 2,
    "hora": 14,
    "volatilidade": 0.8,
    "tendencia_curto_prazo": "alta"
  }
}
```

### 3.6 Prompt para a IA (Apenas Opção A - API Externa)
**Descrição:** Estrutura do prompt que será enviado para a API externa de IA

**Formato do Prompt:**
```json
{
  "role": "system",
  "content": "Você é um analista especializado em trading de mini-índice (WIN) na B3. Sua função é analisar dados de mercado em tempo real e tomar decisões de trading baseadas em análise técnica e fundamental. Você deve sempre responder no formato JSON especificado e considerar apenas os dados fornecidos."
},
{
  "role": "user", 
  "content": "Analise os seguintes dados do mini-índice WIN e tome uma decisão de trading:\n\nDADOS DE MERCADO:\n- Ativo: {ativo}\n- Preço atual: {preco_atual}\n- Bid/Ask: {bid}/{ask}\n- Volume: {volume}\n- Variação: {variacao}%\n\nDADOS HISTÓRICOS (últimos {periodos} períodos):\n{historico_formatado}\n\nINDICADORES TÉCNICOS:\n- RSI: {rsi}\n- MACD: {macd}\n- Bandas de Bollinger: Superior {bb_upper}, Inferior {bb_lower}\n- Média Móvel 20: {ma20}\n- Média Móvel 50: {ma50}\n\nCONTEXTO:\n- Dia da semana: {dia_semana}\n- Hora: {hora}\n- Volatilidade: {volatilidade}\n- Tendência curto prazo: {tendencia}\n\nREGRAS DE TRADING:\n- Confiança mínima: 0.7\n- Stop loss padrão: 100 pontos\n- Take profit padrão: 200 pontos\n- Máximo de ordens por dia: 10\n- Operar apenas em horário de mercado (09:00-17:00)\n\nResponda APENAS no seguinte formato JSON:\n{\n  \"decisao\": \"comprar|vender|aguardar\",\n  \"confianca\": 0.0-1.0,\n  \"razao\": \"explicação detalhada da decisão\",\n  \"parametros\": {\n    \"quantidade\": 1,\n    \"stop_loss\": pontos,\n    \"take_profit\": pontos,\n    \"validade\": segundos\n  },\n  \"indicadores_analisados\": [\"lista de indicadores considerados\"],\n  \"timestamp_analise\": \"ISO timestamp\"\n}"
}
```

**Variáveis do Prompt:**
- `{ativo}`: Código do ativo (ex: WINZ25)
- `{preco_atual}`: Preço atual do ativo
- `{bid}/{ask}`: Melhor bid e ask
- `{volume}`: Volume negociado
- `{variacao}`: Variação percentual
- `{periodos}`: Número de períodos históricos
- `{historico_formatado}`: Dados históricos formatados
- `{rsi}`, `{macd}`, etc.: Valores dos indicadores técnicos
- `{dia_semana}`, `{hora}`: Contexto temporal
- `{volatilidade}`, `{tendencia}`: Contexto de mercado

### 3.7 Formato de Resposta da IA
**Descrição:** Formato de resposta esperado tanto da API externa quanto do modelo local

```json
{
  "decisao": "comprar",  // "comprar", "vender", "aguardar"
  "confianca": 0.85,     // 0.0 a 1.0
  "razao": "Tendência de alta confirmada com volume crescente",
  "parametros": {
    "quantidade": 1,
    "stop_loss": 100,
    "take_profit": 200,
    "validade": 300  // segundos
  },
  "indicadores_analisados": ["rsi", "macd", "volume"],
  "timestamp_analise": "2025-07-15T14:30:05Z"
}
```

**Nota:** Este formato é padronizado para ambas as opções (API externa e modelo local), garantindo compatibilidade no processamento das decisões.

---

## 4. Plano de Desenvolvimento

### 4.1 Fase 1: Preparação de Dados (2-3 dias)
**Objetivo:** Implementar módulo de preparação de dados para IA

**Tarefas:**
1. Implementar `preparador_dados.py`
2. Criar estrutura de dados para IA
3. Implementar validação de qualidade
4. Testar com dados reais da B3
5. Otimizar performance

**Entregáveis:**
- [ ] Módulo de preparação funcionando
- [ ] Estrutura de dados definida
- [ ] Validação implementada
- [ ] Performance otimizada
- [ ] Testes com dados reais

### 4.2 Fase 2: Implementação da IA (2-3 dias)
**Objetivo:** Implementar análise com IA (escolher entre API externa ou modelo local)

**Opção A - API Externa de IA:**
1. Implementar `construtor_prompt.py`
2. Implementar `cliente_api.py`
3. Configurar autenticação com API key
4. Implementar retry e tratamento de erros
5. Testar comunicação com API real

**Opção B - Modelo Local de ML:**
1. Implementar `modelo_local.py`
2. Implementar `treinador.py`
3. Treinar modelo com dados históricos
4. Implementar processamento em tempo real
5. Validar qualidade das predições

**Entregáveis:**
- [ ] **Opção A**: Construtor de prompts implementado
- [ ] **Opção A**: Cliente da API funcionando
- [ ] **Opção A**: Autenticação configurada
- [ ] **Opção A**: Tratamento de erros implementado
- [ ] **Opção B**: Modelo local implementado
- [ ] **Opção B**: Treinamento funcionando
- [ ] **Opção B**: Processamento em tempo real
- [ ] Fallback funcionando

### 4.3 Fase 3: Processamento de Resposta (2-3 dias)
**Objetivo:** Implementar processamento de resposta da IA

**Tarefas:**
1. Implementar `processador_resposta.py`
2. Criar lógica de validação de confiança
3. Implementar filtros de segurança
4. Integrar com contexto de mercado
5. Testar cenários de decisão

**Entregáveis:**
- [ ] Processador de resposta funcionando
- [ ] Validação de confiança implementada
- [ ] Filtros de segurança aplicados
- [ ] Contexto de mercado integrado
- [ ] Testes de cenários completos

### 4.4 Fase 4: Integração e Testes (2-3 dias)
**Objetivo:** Integrar todos os módulos e testar sistema completo

**Tarefas:**
1. Integrar todos os módulos da IA
2. Conectar com executor de ordens
3. Implementar monitoramento
4. Testes end-to-end
5. Otimizações finais

**Entregáveis:**
- [ ] Sistema completo integrado
- [ ] Execução de ordens funcionando
- [ ] Monitoramento implementado
- [ ] Testes end-to-end passando
- [ ] Sistema otimizado

---

## 5. Critérios de Sucesso

### 5.1 Performance
- Latência total < 5 segundos (preparação + IA + decisão)
- Taxa de sucesso da API > 95%
- Zero falhas consecutivas > 5 tentativas
- Sistema estável por 24 horas

### 5.2 Confiabilidade
- Fallback funcionando em 100% dos casos
- Recuperação automática de falhas
- Logs completos e acessíveis
- Alertas funcionando corretamente

### 5.3 Qualidade das Decisões
- Decisões baseadas em dados confiáveis
- Validação de confiança implementada
- Filtros de segurança aplicados
- Contexto de mercado considerado

---

## 6. Riscos e Mitigações

### 6.1 Riscos Técnicos
- **API de IA indisponível**: Implementar fallback robusto
- **Latência alta**: Otimizar preparação de dados
- **Rate limiting**: Implementar controle de frequência
- **Dados inconsistentes**: Validação rigorosa

### 6.2 Riscos de Negócio
- **Decisões incorretas**: Validação de confiança
- **Perda de conectividade**: Retry automático
- **Custos da API**: Monitoramento de uso
- **Regulamentação**: Compliance com regras de trading

---

## 7. Configuração da API Key

### 7.1 Arquivo de Configuração
Criar arquivo `config/api_keys.yaml` (não versionado):
```yaml
ia_api:
  key: "sua_api_key_aqui"
  endpoint: "https://api.ia-service.com/analyze"
  version: "v1"
```

### 7.2 Variáveis de Ambiente
Alternativamente, usar variáveis de ambiente:
```bash
export IA_API_KEY="sua_api_key_aqui"
export IA_API_ENDPOINT="https://api.ia-service.com/analyze"
```

---

## 8. Comparação das Opções de IA

### 8.1 Opção A - API Externa de IA
**Vantagens:**
- ✅ Implementação rápida
- ✅ IA de última geração (GPT-4, Claude, etc.)
- ✅ Análise contextual avançada
- ✅ Explicações detalhadas das decisões
- ✅ Sem necessidade de treinamento

**Desvantagens:**
- ❌ Custos por requisição
- ❌ Dependência de conectividade
- ❌ Latência de rede
- ❌ Rate limiting
- ❌ Privacidade dos dados

### 8.2 Opção B - Modelo Local de ML
**Vantagens:**
- ✅ Sem custos por uso
- ✅ Operação offline
- ✅ Latência mínima
- ✅ Privacidade total dos dados
- ✅ Controle total sobre o modelo

**Desvantagens:**
- ❌ Desenvolvimento mais complexo
- ❌ Necessidade de treinamento
- ❌ Qualidade depende dos dados históricos
- ❌ Manutenção do modelo
- ❌ Explicabilidade limitada

### 8.3 Recomendação
- **Para início rápido**: Opção A (API Externa)
- **Para longo prazo**: Opção B (Modelo Local)
- **Híbrido**: Começar com API externa e migrar para modelo local

## 9. Próximos Passos Após Etapa 3

1. **Backtesting**: Testar estratégias com dados históricos
2. **Otimização**: Ajustar parâmetros baseado em performance
3. **Machine Learning Local**: Implementar modelos locais (se usar Opção A)
4. **Dashboard Avançado**: Interface web para monitoramento
5. **Alertas Avançados**: Notificações por email/SMS
6. **Multi-Ativos**: Expandir para outros ativos além do WIN

---

## 10. Histórico de Versões
- **3.0**: PRD criado para implementação da IA (JUL/2025) 

## Atualização: Julho 2025

- A confiança agora é determinada pela própria IA, podendo assumir qualquer valor entre 0 e 1, de acordo com a clareza dos sinais do mercado.
- O robô pode operar em todos os níveis de confiança, exceto quando a confiança for muito baixa (<0.2), para evitar ruído puro.
- O sistema de aprendizado registra todas as operações, com todos os dados relevantes, para permitir evolução contínua da IA.
- O objetivo é maximizar o aprendizado real, permitindo que a IA ajuste sua estratégia com base em acertos e erros reais do mercado. 