# Documento de Requisitos de Produto (PRD)
## Robô de Trading Pessoal - Mini-Índice B3

**Versão:** 2.0  
**Data:** Julho 2025  
**Desenvolvedor:** Solo  
**Objetivo:** Robô pessoal para operar mini-índice (WIN) na B3 com IA local  
**Status:** Sistema completo implementado e operacional ✅

---

## 1. Visão Geral

### 1.1 Objetivo do Projeto
Desenvolver um robô de trading pessoal que coleta dados do mini-índice (WIN) da B3, analisa com IA local (Llama 3.1 8B) e executa ordens automaticamente na plataforma de trading.

### 1.2 Premissas
- Sistema 100% local (sem servidor na nuvem)
- IA local via Ollama (Llama 3.1 8B)
- Desenvolvimento solo
- Foco em simplicidade e baixo custo
- Uso de fontes oficiais e confiáveis de dados (API B3)
- Operação 24/7 com respeito ao horário de mercado

### 1.3 Benefícios Esperados
- Automação de operações de trading
- Eliminação de erros emocionais
- Operação 24/7 (durante horário de mercado)
- Baixo custo de implementação
- Dados de mercado reais e robustos
- IA local sem dependência de APIs externas
- Controle total sobre o sistema

---

## 2. Requisitos Funcionais

### 2.1 Coleta de Dados (RF-001)
**Descrição:** Extrair dados do mini-índice (WIN) e IBOV diretamente da API oficial da B3

**Detalhes:**
- Coletar preço atual (bid/ask)
- Coletar dados de OHLC (Open, High, Low, Close)
- Frequência: A cada 30 segundos durante horário de mercado
- Fonte: API oficial da B3
- Suporte automático ao contrato vigente do WIN (ex: WINZ25)
- Tratamento de erros e retry automático

**Critérios de Aceitação:**
- [x] Script acessa API oficial da B3
- [x] Extrai dados reais do IBOV e WIN vigente
- [x] Dados são atualizados em tempo real
- [x] Coleta dados a cada 30 segundos
- [x] Tratamento robusto de erros
- [x] Logs detalhados de coleta

### 2.2 Armazenamento de Dados (RF-002)
**Descrição:** Salvar dados coletados localmente em SQLite

**Detalhes:**
- Armazenar em SQLite local
- Estrutura: timestamp, preço, volume, OHLC, símbolo
- Retenção: últimos 30 dias de dados
- Backup automático diário
- Tabelas: precos, analises, ordens

**Critérios de Aceitação:**
- [x] Dados são salvos localmente em SQLite
- [x] Estrutura de dados consistente
- [x] Backup automático funcionando
- [x] Consultas rápidas (< 1 segundo)
- [x] Tabelas de preços, análises e ordens

### 2.3 Análise com IA Local (RF-003)
**Descrição:** Analisar dados com IA local via Ollama (Llama 3.1 8B)

**Detalhes:**
- Preparar dados com indicadores técnicos
- Enviar para IA local (Llama 3.1 8B via Ollama)
- Receber resultado da análise (compra/venda/aguardar)
- Calcular nível de confiança da decisão
- Log de todas as análises realizadas
- Timeout de 30 segundos por análise

**Critérios de Aceitação:**
- [x] IA local via Ollama funcionando
- [x] Modelo Llama 3.1 8B carregado
- [x] Recebe resposta da IA com decisão
- [x] Calcula confiança da decisão
- [x] Log de análises é mantido
- [x] Timeout configurado
- [x] Tratamento de erros robusto

### 2.4 Execução de Ordens (RF-004)
**Descrição:** Enviar ordens para plataforma de trading

**Detalhes:**
- Receber sinal de compra/venda da IA
- Validar confiança mínima (≥ 70%)
- Enviar ordem via API da plataforma
- Confirmar execução da ordem
- Log de todas as ordens executadas
- Controle de risco e limites

**Critérios de Aceitação:**
- [x] Envia ordem quando recebe sinal
- [x] Valida confiança mínima
- [x] Confirma execução da ordem
- [x] Log de ordens é mantido
- [x] Validações de segurança funcionam
- [x] Controle de risco implementado

### 2.5 Sistema de Controle e Monitoramento (RF-005)
**Descrição:** Scripts de controle e monitoramento em tempo real

**Detalhes:**
- Script de inicialização com verificações
- Script de parada segura
- Monitor em tempo real
- Logs detalhados
- Tratamento robusto de erros
- Verificações automáticas de dependências

**Critérios de Aceitação:**
- [x] Script de inicialização (`iniciar_robo.py`)
- [x] Script de execução em background (`rodar_robo.sh`)
- [x] Script de parada segura (`parar_robo.sh`)
- [x] Monitor em tempo real (`monitor.py`)
- [x] Teste rápido do sistema (`teste_rapido.py`)
- [x] Logs organizados e rotacionados
- [x] Tratamento robusto de erros

---

## 3. Arquitetura Técnica

### 3.1 Componentes Principais
- **Coletor**: Coleta dados da B3 em tempo real
- **Armazenamento**: SQLite local para dados
- **Analisador IA**: Integração com Ollama (Llama 3.1 8B)
- **Executor**: Envio de ordens para plataforma
- **Monitor**: Interface de monitoramento
- **Controlador**: Scripts de controle e inicialização

### 3.2 Tecnologias Utilizadas
- **Python 3.8+**: Linguagem principal
- **SQLite**: Banco de dados local
- **Ollama**: Servidor de IA local
- **Llama 3.1 8B**: Modelo de IA
- **Loguru**: Sistema de logging
- **Requests**: Comunicação HTTP
- **YAML**: Configurações

### 3.3 Configurações
- **Horário de Mercado**: 09:00-17:00 (Seg-Sex)
- **Frequência de Análise**: 30 segundos
- **Confiança Mínima**: 70%
- **Timeout IA**: 30 segundos
- **Retry Attempts**: 3 tentativas

---

## 4. Observações Técnicas Recentes

### 4.1 Melhorias Implementadas
- ✅ **IA Local**: Integração completa com Ollama e Llama 3.1 8B
- ✅ **Tratamento de Erros**: Sistema robusto de tratamento de falhas
- ✅ **Scripts de Controle**: Inicialização, parada e monitoramento automatizados
- ✅ **Configuração Flexível**: Adição automática de seções faltantes
- ✅ **Verificações Inteligentes**: Separação entre verificações críticas e opcionais
- ✅ **Logs Detalhados**: Sistema completo de logging com rotação
- ✅ **Monitoramento**: Interface em tempo real do status do sistema

### 4.2 Robustez do Sistema
- A coleta de dados utiliza a API oficial da B3, garantindo robustez e confiabilidade
- O sistema identifica automaticamente o contrato vigente do WIN
- IA local elimina dependência de APIs externas
- Tratamento robusto de erros previne falhas do sistema
- Scripts de controle garantem operação contínua

---

## 5. Progresso Atual
- ✅ **Ambiente Python e dependências**: 100% concluído
- ✅ **Coletor de dados reais da B3**: 100% concluído
- ✅ **Armazenamento SQLite**: 100% concluído
- ✅ **IA local com Ollama**: 100% concluído
- ✅ **Sistema de análise**: 100% concluído
- ✅ **Execução de ordens**: 100% concluído
- ✅ **Scripts de controle**: 100% concluído
- ✅ **Monitoramento**: 100% concluído
- ✅ **Tratamento de erros**: 100% concluído
- ✅ **Sistema completo**: 100% concluído e operacional

---

## 6. Como Usar

### 6.1 Inicialização Rápida
```bash
cd /home/andrei/Documents/EU/TRADE/AI/robo_trading
source venv/bin/activate
./rodar_robo.sh
```

### 6.2 Monitoramento
```bash
python3 monitor.py
tail -f logs/robo_background.log
```

### 6.3 Parada
```bash
./parar_robo.sh
```

---

## 7. Próximos Passos
- [ ] Implementar backtesting com dados históricos
- [ ] Adicionar mais indicadores técnicos
- [ ] Otimizar prompts da IA
- [ ] Implementar alertas por email/SMS
- [ ] Dashboard web para monitoramento
- [ ] Estratégias de trading mais avançadas

---

## 8. Histórico de Versões
- **1.0**: Estrutura inicial, scraping TradingView (não confiável)
- **1.1**: Banco de dados, integração IA, execução mock
- **1.2**: Coleta de dados reais da B3 implementada e validada (JUL/2025)
- **2.0**: Sistema completo com IA local, scripts de controle e tratamento robusto de erros (JUL/2025)

---

## 9. Status Final
**🎯 SISTEMA 100% OPERACIONAL**

O robô de trading está completamente implementado e pronto para operação:
- ✅ Coleta dados reais da B3
- ✅ Analisa com IA local (Llama 3.1 8B)
- ✅ Executa ordens automaticamente
- ✅ Monitora em tempo real
- ✅ Trata erros robustamente
- ✅ Opera 24/7 respeitando horário de mercado

**O sistema está pronto para uso em produção!** 