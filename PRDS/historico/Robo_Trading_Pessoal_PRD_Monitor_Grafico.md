# Documento de Requisitos de Produto (PRD)
## Monitor Visual Completo do Sistema de Trading IA

**Versão:** 1.3  
**Data:** 2024-06-09  
**Responsável:** AI/Andrei  
**Status:** EM PLANEJAMENTO

---

## 1. Visão Geral

### 1.1 Objetivo
Desenvolver uma aplicação visual moderna para monitoramento e controle em tempo real de **todo o sistema do Robô de Trading IA**, substituindo o monitor em terminal (monitor.py) por uma interface rica, intuitiva e responsiva. O monitor deve exibir de forma clara e centralizada:
- Status do robô (ligado/desligado, PID, modo de operação)
- **Botões de controle:** Iniciar Bot, Encerrar Bot, Reiniciar Bot
- **Tempo de atividade do robô** (cronômetro desde o último start)
- Situação do mercado (aberto/fechado, horário de operação, próximos eventos)
- Status do Ollama/IA (online/offline, modelo carregado, respostas)
- Estatísticas e performance do sistema de aprendizado
- Últimas análises e decisões da IA
- **Ordens ativas e histórico de ordens** (com detalhes)
- Logs e alertas do sistema
- Qualquer outra informação relevante para operação e troubleshooting

### 1.2 Justificativa
O monitor atual em terminal pisca, não é visualmente agradável e dificulta a análise rápida de informações. Uma interface visual permitirá:
- Visualização clara e organizada de **todas as informações do sistema**
- Atualização em tempo real sem "piscar" ou perder contexto
- Alertas visuais para status crítico ou erros
- **Controle direto do robô (start/stop/restart) pela interface**
- Melhor experiência para acompanhamento, diagnóstico e operação

---

## 2. Requisitos Funcionais

### RF-001: Dashboard Geral
- Exibir status do robô (rodando/parado, PID, modo de operação)
- Exibir botões de controle: Iniciar, Encerrar, Reiniciar Bot
- Exibir tempo de atividade do robô (cronômetro)
- Exibir status do Ollama/IA (online/offline, modelo carregado, respostas recentes)
- Exibir horário atual, horário de operação do robô, tempo restante de mercado
- Exibir logs recentes e alertas críticos

**Critérios de Aceitação:**
- [ ] Status do robô visível e atualizado em tempo real
- [ ] Botões de controle funcionais (executam scripts de start/stop/restart)
- [ ] Tempo de atividade exibido corretamente
- [ ] Status do Ollama/IA atualizado
- [ ] Logs e alertas visíveis

### RF-002: Status do Mercado
- Exibir situação do mercado (aberto/fechado)
- Exibir horário de abertura/fechamento
- Exibir símbolos monitorados e preços em tempo real
- Exibir variação, volume, timestamp do último preço

**Critérios de Aceitação:**
- [ ] Situação do mercado exibida corretamente
- [ ] Preços e símbolos atualizados em tempo real

### RF-003: Análises e Decisões da IA
- Exibir últimas decisões da IA (comprar, vender, aguardar) com confiança
- Exibir histórico de decisões recentes
- Exibir taxa de acerto, lucro médio, performance recente

**Critérios de Aceitação:**
- [ ] Decisões da IA visíveis e atualizadas
- [ ] Taxa de acerto e performance exibidas

### RF-004: Sistema de Aprendizado
- Exibir estatísticas de aprendizado (total de registros, taxa de acerto, ajustes realizados)
- Exibir parâmetros otimizados atuais
- Exibir recomendações e insights do sistema
- Exibir logs de aprendizado e ajustes automáticos

**Critérios de Aceitação:**
- [ ] Estatísticas de aprendizado visíveis
- [ ] Parâmetros otimizados exibidos
- [ ] Recomendações e logs acessíveis

### RF-005: Ordens
- Exibir ordens ativas (detalhes: tipo, símbolo, preço, resultado, timestamp, status)
- Exibir histórico de ordens recentes
- Exibir status de execução das ordens

**Critérios de Aceitação:**
- [ ] Ordens ativas e histórico exibidos
- [ ] Status de execução atualizado

### RF-006: Logs e Troubleshooting
- Visualização dos logs em tempo real
- Alertas de erro e status crítico
- Diagnóstico rápido de problemas

**Critérios de Aceitação:**
- [ ] Logs visíveis e atualizados
- [ ] Alertas destacados

---

## 3. Design Técnico
- Interface web (preferencialmente Streamlit para MVP)
- Atualização automática dos dados (polling ou websocket)
- Leitura dos dados do banco SQLite e arquivos de log
- Visualização de gráficos simples para apoio (ex: evolução de acerto, ordens)
- Botões de controle executam scripts de start/stop/restart do robô
- Design responsivo e dark mode
- Fácil execução: `python3 monitor_visual.py` ou `streamlit run monitor_visual.py`

---

## 4. Plano de Desenvolvimento

### Fase 1: Estrutura Inicial e Dashboard (1-2 dias)
**Tarefas:**
1. Criar estrutura do projeto e arquivo principal (`monitor_visual.py`)
2. Implementar dashboard com status do robô, IA, mercado e botões de controle
3. Exibir tempo de atividade do robô
4. Exibir logs recentes

**Entregáveis:**
- [ ] Estrutura inicial criada
- [ ] Dashboard funcional com status e botões
- [ ] Logs visíveis

### Fase 2: Integração de Dados e Visualização (2-3 dias)
**Tarefas:**
1. Integrar leitura de dados do banco SQLite (preços, ordens, análises)
2. Exibir status do mercado, símbolos e preços em tempo real
3. Exibir análises e decisões da IA
4. Exibir estatísticas de aprendizado
5. Exibir histórico de ordens

**Entregáveis:**
- [ ] Dados integrados e visíveis
- [ ] Visualização de análises, aprendizado e ordens

### Fase 3: Funcionalidades Avançadas e Polimento (2 dias)
**Tarefas:**
1. Implementar alertas visuais e logs em tempo real
2. Implementar gráficos simples de performance
3. Polir design responsivo e dark mode
4. Testar botões de controle (start/stop/restart)
5. Testes de usabilidade

**Entregáveis:**
- [ ] Alertas e logs em tempo real
- [ ] Gráficos de apoio
- [ ] Design polido
- [ ] Botões de controle testados

---

## 5. Critérios de Sucesso
- Interface visual clara, sem "piscar" ou sumir dados
- Atualização automática dos dados
- Exibe status do robô, IA, mercado, horário, tempo de atividade, botões de controle, análises, aprendizado, ordens e logs
- Fácil de rodar (um comando)
- Botões de controle funcionais (start/stop/restart)

---

## 6. Riscos e Mitigações
- **Integração dos scripts de controle pode exigir permissões elevadas:** Documentar requisitos e testar em ambiente real
- **Atualização em tempo real pode sobrecarregar SQLite:** Implementar polling eficiente
- **Design responsivo pode exigir ajustes para diferentes telas:** Testar em múltiplos dispositivos

---

## 7. Próximos Passos
- [ ] Aprovar PRD padronizado
- [ ] Iniciar implementação da Fase 1
- [ ] Validar integração dos scripts de controle
- [ ] Testar MVP com usuário final

--- 