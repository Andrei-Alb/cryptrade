# Documento de Requisitos de Produto (PRD) - Etapa 4
## Integração com Genial Investimentos e Profit Pro para Execução de Ordens

**Versão:** 2.0  
**Data:** Julho 2025  
**Desenvolvedor:** Solo  
**Objetivo:** Integrar robô de trading com Genial Investimentos via Profit Pro usando ProfitDLL.dll para execução automática de ordens  
**Status:** PRONTO PARA DESENVOLVIMENTO - ARQUITETURA CORRIGIDA

---

## 1. Visão Geral

### 1.1 Objetivo da Etapa 4
Implementar integração completa com a **Genial Investimentos** através da plataforma **Profit Pro da Nelogica** usando a **ProfitDLL.dll** para execução automática de ordens de compra e venda de mini-índice (WIN) baseadas nas decisões da IA local.

### 1.2 Contexto
- Sistema de coleta de dados da B3 já implementado e funcionando
- IA local (Ollama + Llama 3.1 8B) analisando e tomando decisões
- Conta ativa na Genial Investimentos com acesso ao Profit Pro
- Necessário conectar decisões da IA com execução real de ordens via DLL
- Sistema deve operar com segurança e controle de risco
- **Solução 100% gratuita** rodando localmente no Windows

### 1.3 Premissas Corrigidas
- Conta na Genial Investimentos ativa e operacional
- Acesso ao Profit Pro da Nelogica configurado
- Capital disponível para operações (mínimo R$ 1.000)
- Sistema de IA funcionando corretamente
- Decisões da IA com confiança ≥ 70% são válidas para execução
- **Sistema Windows obrigatório** para execução da DLL
- **ProfitDLL.dll** disponível gratuitamente com conta Genial
- **Integração local** via ctypes Python, não API REST

---

## 2. Análise da Plataforma - Realidade Técnica

### 2.1 Genial Investimentos
**Características:**
- Corretora brasileira com foco em day trade
- Suporte a mini-índice (WIN) e outros ativos
- Plataforma Profit Pro da Nelogica
- **API disponível apenas para IaaS/BaaS** (não para trading individual)
- Custos competitivos para day trade

**Realidade da Integração:**
- **NÃO há API de trading** para clientes individuais
- Integração ocorre via Profit Pro da Nelogica
- Conta demo gratuita disponível para testes

### 2.2 Profit Pro da Nelogica
**Características:**
- Plataforma profissional de trading
- **Integração via ProfitDLL.dll** (não API REST)
- Suporte a ordens automatizadas
- Integração com múltiplas corretoras
- **Documentação técnica via DLL**

**Funcionalidades Disponíveis via DLL:**
- Envio de ordens (compra/venda)
- Consulta de posições
- Consulta de saldo
- Histórico de ordens
- Cancelamento de ordens
- **Stop loss e take profit via lógica local**

### 2.3 ProfitDLL.dll - Componente Central
**Natureza:**
- Biblioteca de Vínculo Dinâmico (DLL) para Windows
- Desenvolvida em C++/Delphi
- **Gratuita com conta Genial**
- Requer sistema Windows 64-bit

**Funcionamento:**
- **Chamadas de Função**: Para enviar comandos ao sistema
- **Callbacks**: Para receber dados assíncronos
- **Autenticação**: Via chave de ativação e credenciais
- **Comunicação**: Direta com servidores Nelogica

---

## 3. Requisitos Funcionais

### 3.1 Autenticação e Configuração (RF-401)
**Descrição:** Configurar autenticação com Profit Pro via ProfitDLL.dll

**Detalhes:**
- Configurar chave de ativação da DLL
- Configurar credenciais da conta Genial
- Implementar inicialização da DLL
- Validar conexão com a corretora
- Testar acesso à conta

**Critérios de Aceitação:**
- [ ] DLL carregada com sucesso
- [ ] Autenticação com Profit Pro funcionando
- [ ] Conexão com Genial estabelecida
- [ ] Acesso à conta validado
- [ ] Credenciais seguras (variáveis de ambiente)
- [ ] Logs de autenticação implementados

### 3.2 Consulta de Informações da Conta (RF-402)
**Descrição:** Consultar informações da conta antes de executar ordens

**Detalhes:**
- Consultar saldo disponível via DLL
- Consultar posições abertas
- Consultar ordens pendentes
- Validar limites de risco
- Verificar horário de mercado

**Critérios de Aceitação:**
- [ ] Consulta de saldo funcionando
- [ ] Consulta de posições funcionando
- [ ] Validação de limites implementada
- [ ] Verificação de horário funcionando
- [ ] Logs de consultas implementados

### 3.3 Execução de Ordens (RF-403)
**Descrição:** Enviar ordens de compra/venda via DLL

**Detalhes:**
- Receber decisão da IA (compra/venda)
- Validar condições antes da execução
- Enviar ordem via funções da DLL
- Confirmar execução da ordem
- Implementar retry em caso de falha
- Log de todas as ordens executadas

**Critérios de Aceitação:**
- [ ] Envio de ordens funcionando
- [ ] Confirmação de execução implementada
- [ ] Retry automático funcionando
- [ ] Logs de execução completos
- [ ] Validações de segurança aplicadas

### 3.4 Gestão de Risco (RF-404)
**Descrição:** Implementar controles de risco para operações

**Detalhes:**
- **Stop loss automático via lógica local**
- **Take profit automático via lógica local**
- Limite de perda diária
- Limite de ordens por dia
- Controle de exposição
- Alertas de risco

**Critérios de Aceitação:**
- [ ] Stop loss automático funcionando
- [ ] Take profit automático funcionando
- [ ] Limite diário implementado
- [ ] Controle de exposição funcionando
- [ ] Alertas de risco implementados

### 3.5 Monitoramento de Posições (RF-405)
**Descrição:** Monitorar posições abertas e performance

**Detalhes:**
- Acompanhar posições em tempo real via callbacks
- Calcular P&L (lucro/prejuízo)
- Monitorar drawdown
- Gerar relatórios de performance
- Alertas de posições críticas

**Critérios de Aceitação:**
- [ ] Monitoramento em tempo real funcionando
- [ ] Cálculo de P&L implementado
- [ ] Relatórios de performance gerados
- [ ] Alertas de posições funcionando
- [ ] Dashboard de performance criado

---

## 4. Design Técnico - Arquitetura Corrigida

### 4.1 Arquitetura da Integração via DLL
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Decisão IA    │    │   Validador     │    │   Executor      │
│   (Confiança)   │───▶│   de Risco      │───▶│   de Ordens     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Wrapper       │    │   ProfitDLL     │    │   Callbacks     │
│   Python        │───▶│   .dll          │───▶│   Assíncronos   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Servidores    │    │   Corretora     │    │   Monitor de    │
│   Nelogica      │    │   Genial        │    │   Posições      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 4.2 Estrutura de Arquivos Corrigida
```
robo_trading/
├── app/
│   ├── __init__.py
│   ├── main.py                # Ponto de entrada da aplicação
│   ├── trade_logic.py         # Processa decisão da IA
│   └── risk_manager.py        # Gestão de risco local
├── integration/
│   ├── __init__.py
│   ├── profit_dll_wrapper.py  # Wrapper principal da DLL
│   ├── profit_callbacks.py    # Callbacks assíncronos
│   └── profit_structs.py      # Estruturas ctypes
├── dlls/
│   └── ProfitDLL64.dll        # Biblioteca proprietária
├── config/
│   └── config.yaml            # Configuração unificada
├── logs/
│   ├── app.log
│   └── orders.log
└── reports/
    └── performance/
```

### 4.3 Configurações da Integração Corrigidas
```yaml
# config/config.yaml
nelogica_integration:
  dll_path: "C:/robo_trading/dlls/ProfitDLL64.dll"
  activation_key: "${NELOGICA_ACTIVATION_KEY}"

account_info:
  account_id: "${GENIAL_ACCOUNT_ID}"
  broker_id: "Genial"
  trading_password: "${GENIAL_TRADING_PASSWORD}"

trading_params:
  asset: "WINZ25"
  quantity: 1
  confidence_threshold: 0.7

risk_management:
  stop_loss_points: 100
  take_profit_points: 200
  max_daily_loss_brl: 1000.0
  max_open_contracts: 5
  market_open_time: "09:00:00"
  market_close_time: "17:00:00"
```

---

## 5. Implementação - Código Real via ctypes

### 5.1 Wrapper Principal da DLL
```python
# integration/profit_dll_wrapper.py
import ctypes
from ctypes import (WinDLL, CFUNCTYPE, POINTER,
                    c_wchar_p, c_short, c_int, c_double, c_uint,
                    Structure)
from loguru import logger

class TAssetID(Structure):
    _fields_ = [("ticker", c_wchar_p * 25),
                ("bolsa", c_wchar_p * 15)]

class ProfitDLLWrapper:
    def __init__(self, dll_path: str, activation_key: str):
        try:
            self.dll = WinDLL(dll_path)
            logger.info(f"DLL carregada: {dll_path}")
        except OSError as e:
            raise ConnectionError(f"Erro ao carregar DLL: {e}")

        self.activation_key = c_wchar_p(activation_key)
        self._setup_function_prototypes()
        self._register_callbacks()
        self._initialize_dll()
        
    def _setup_function_prototypes(self):
        """Define protótipos das funções da DLL"""
        try:
            # SendBuyOrder
            self.dll.SendBuyOrder.argtypes = [
                c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, 
                c_wchar_p, c_double, c_int
            ]
            self.dll.SendBuyOrder.restype = c_short

            # SendSellOrder
            self.dll.SendSellOrder.argtypes = [
                c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, 
                c_wchar_p, c_double, c_int
            ]
            self.dll.SendSellOrder.restype = c_short

            logger.info("Protótipos das funções configurados")
        except AttributeError as e:
            raise NotImplementedError(f"Função não encontrada: {e}")

    def _register_callbacks(self):
        """Registra callbacks assíncronos"""
        # Callback de estado
        StateCallbackType = CFUNCTYPE(None, c_int)
        self.state_callback_instance = StateCallbackType(self._on_state_change)
        
        # Callback de trade
        TradeCallbackType = CFUNCTYPE(None, POINTER(TAssetID))
        self.trade_callback_instance = TradeCallbackType(self._on_new_trade)
        
        logger.info("Callbacks registrados")

    def _initialize_dll(self):
        """Inicializa a DLL com credenciais"""
        # Implementar inicialização baseada na documentação
        pass

    @staticmethod
    def _on_state_change(new_state: int):
        """Callback de mudança de estado"""
        logger.info(f"Estado da conexão: {new_state}")

    @staticmethod
    def _on_new_trade(trade_data_ptr):
        """Callback de novo trade"""
        trade_info = trade_data_ptr.contents
        logger.info(f"Novo trade: {trade_info.ticker}")

    def enviar_ordem_compra(self, account_id: str, asset: str, 
                           price: float, quantity: int) -> bool:
        """Envia ordem de compra"""
        try:
            result = self.dll.SendBuyOrder(
                c_wchar_p(account_id),
                c_wchar_p("Genial"),
                c_wchar_p("SENHA"),
                c_wchar_p(asset),
                c_wchar_p("BMF"),
                c_double(price),
                c_int(quantity)
            )
            
            if result == 0:
                logger.success(f"Ordem de compra enviada: {asset} {quantity} @ {price}")
                return True
            else:
                logger.error(f"Erro ao enviar ordem: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Exceção ao enviar ordem: {e}")
            return False

    def enviar_ordem_venda(self, account_id: str, asset: str, 
                          price: float, quantity: int) -> bool:
        """Envia ordem de venda"""
        try:
            result = self.dll.SendSellOrder(
                c_wchar_p(account_id),
                c_wchar_p("Genial"),
                c_wchar_p("SENHA"),
                c_wchar_p(asset),
                c_wchar_p("BMF"),
                c_double(price),
                c_int(quantity)
            )
            
            if result == 0:
                logger.success(f"Ordem de venda enviada: {asset} {quantity} @ {price}")
                return True
            else:
                logger.error(f"Erro ao enviar ordem: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Exceção ao enviar ordem: {e}")
            return False
```

### 5.2 Executor de Ordens Integrado
```python
# app/trade_logic.py
from typing import Dict, Any
from loguru import logger
from integration.profit_dll_wrapper import ProfitDLLWrapper
from .risk_manager import RiskManager

class TradeLogic:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.profit_wrapper = ProfitDLLWrapper(
            config['nelogica_integration']['dll_path'],
            config['nelogica_integration']['activation_key']
        )
        self.risk_manager = RiskManager(config)
        
    def executar_decisao(self, decisao_ia: Dict[str, Any], dados_mercado: Dict[str, Any]):
        """Executa decisão da IA"""
        try:
            # 1. Validar decisão
            if not self.risk_manager.validar_decisao(decisao_ia):
                logger.warning("Decisão rejeitada pelo gestor de risco")
                return None
                
            # 2. Validar saldo
            if not self.risk_manager.validar_saldo_suficiente(decisao_ia):
                logger.warning("Saldo insuficiente para ordem")
                return None
                
            # 3. Enviar ordem
            account_id = self.config['account_info']['account_id']
            asset = self.config['trading_params']['asset']
            quantity = self.config['trading_params']['quantity']
            price = dados_mercado['preco_atual']
            
            if decisao_ia['decisao'] == 'comprar':
                sucesso = self.profit_wrapper.enviar_ordem_compra(
                    account_id, asset, price, quantity
                )
            elif decisao_ia['decisao'] == 'vender':
                sucesso = self.profit_wrapper.enviar_ordem_venda(
                    account_id, asset, price, quantity
                )
            else:
                logger.info("Decisão: aguardar - nenhuma ordem enviada")
                return None
                
            # 4. Registrar resultado
            if sucesso:
                self.risk_manager.registrar_ordem_executada(decisao_ia)
                logger.success(f"Ordem executada: {decisao_ia['decisao']} {asset}")
                return {'status': 'executada', 'decisao': decisao_ia['decisao']}
            else:
                logger.error("Falha na execução da ordem")
                return None
                
        except Exception as e:
            logger.error(f"Erro na execução: {e}")
            return None
```

### 5.3 Gestor de Risco Local
```python
# app/risk_manager.py
from typing import Dict, Any
from loguru import logger
from datetime import datetime, time

class RiskManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ordens_hoje = 0
        self.perda_hoje = 0.0
        self.posicoes_abertas = 0
        
    def validar_decisao(self, decisao_ia: Dict[str, Any]) -> bool:
        """Valida se decisão pode ser executada"""
        # 1. Confiança mínima
        if decisao_ia['confianca'] < self.config['trading_params']['confidence_threshold']:
            logger.info(f"Confiança insuficiente: {decisao_ia['confianca']}")
            return False
            
        # 2. Horário de mercado
        agora = datetime.now().time()
        inicio = time.fromisoformat(self.config['risk_management']['market_open_time'])
        fim = time.fromisoformat(self.config['risk_management']['market_close_time'])
        
        if not (inicio <= agora <= fim):
            logger.info("Fora do horário de mercado")
            return False
            
        # 3. Limite de ordens diárias
        if self.ordens_hoje >= self.config['risk_management']['max_open_contracts']:
            logger.warning("Limite de ordens diárias atingido")
            return False
            
        # 4. Limite de perda diária
        if self.perda_hoje >= self.config['risk_management']['max_daily_loss_brl']:
            logger.warning("Limite de perda diária atingido")
            return False
            
        return True
        
    def validar_saldo_suficiente(self, decisao_ia: Dict[str, Any]) -> bool:
        """Valida se há saldo suficiente para a operação"""
        # Implementar consulta de saldo via DLL
        # Por enquanto, assume que há saldo
        return True
        
    def registrar_ordem_executada(self, decisao_ia: Dict[str, Any]):
        """Registra ordem executada para controle de risco"""
        self.ordens_hoje += 1
        logger.info(f"Ordem registrada. Total hoje: {self.ordens_hoje}")
```

---

## 6. Plano de Desenvolvimento

### 6.1 Fases de Desenvolvimento
**Fase 1: Integração DLL (2-3 semanas)**
- Configuração do ambiente Windows
- Download e instalação da ProfitDLL.dll
- Implementação do wrapper Python
- Testes de conectividade básica
- Documentação da DLL

**Fase 2: Execução de Ordens (1 semana)**
- Implementação de envio de ordens
- Sistema de confirmação
- Retry automático
- Logs de execução

**Fase 3: Gestão de Risco (1 semana)**
- Stop loss automático
- Take profit automático
- Limites diários
- Alertas de risco

**Fase 4: Monitoramento (1 semana)**
- Dashboard de posições
- Relatórios de performance
- Alertas em tempo real
- Backup e recuperação

### 6.2 Cronograma Detalhado
```
Semana 1-2: Setup DLL
├── Configuração ambiente Windows
├── Download ProfitDLL.dll
├── Implementação wrapper básico
└── Testes de conectividade

Semana 3: Execução
├── Funções de envio de ordens
├── Sistema de confirmação
├── Retry automático
└── Logs completos

Semana 4: Risco
├── Stop loss automático
├── Take profit automático
├── Limites diários
└── Alertas

Semana 5: Monitoramento
├── Dashboard posições
├── Relatórios performance
├── Alertas tempo real
└── Testes finais
```

---

## 7. Estratégia de Testes

### 7.1 Testes de Integração DLL
**Teste 1: Carregamento da DLL**
- Verificar se DLL carrega corretamente
- Validar protótipos das funções
- Testar inicialização

**Teste 2: Autenticação**
- Testar login com credenciais
- Validar conexão com servidores
- Verificar callbacks de estado

**Teste 3: Consultas Básicas**
- Consultar saldo da conta
- Consultar posições abertas
- Validar dados retornados

### 7.2 Testes de Execução
**Teste 4: Envio de Ordens**
- Testar ordem de compra
- Testar ordem de venda
- Validar confirmações
- Testar cancelamento

**Teste 5: Gestão de Risco**
- Testar stop loss automático
- Testar take profit automático
- Validar limites diários
- Testar alertas

### 7.3 Testes de Produção
**Teste 6: Operação Completa**
- Teste com conta demo
- Operações com valores pequenos
- Monitoramento de performance
- Validação de relatórios

---

## 8. Plano de Deploy

### 8.1 Ambiente de Desenvolvimento
**Requisitos:**
- Windows 10/11 64-bit
- Python 3.9+
- Profit Pro instalado
- Conta Genial ativa
- DLL da Nelogica

**Setup:**
```bash
# 1. Instalar Python
# 2. Clonar repositório
# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com credenciais

# 5. Testar DLL
python -m integration.test_dll
```

### 8.2 Ambiente de Produção
**Configuração:**
- Máquina dedicada Windows
- Conexão estável com internet
- Backup automático
- Monitoramento 24/7

**Deploy:**
```bash
# 1. Setup da máquina
# 2. Instalação do sistema
# 3. Configuração de credenciais
# 4. Testes de conectividade
# 5. Início das operações
```

---

## 9. Gestão de Riscos

### 9.1 Riscos Técnicos
**Risco 1: DLL Indisponível**
- **Probabilidade:** Baixa
- **Impacto:** Alto
- **Mitigação:** Backup da DLL, documentação completa

**Risco 2: Mudanças na API da DLL**
- **Probabilidade:** Média
- **Impacto:** Alto
- **Mitigação:** Monitoramento de atualizações, testes regulares

**Risco 3: Problemas de Conectividade**
- **Probabilidade:** Média
- **Impacto:** Médio
- **Mitigação:** Retry automático, alertas

### 9.2 Riscos Operacionais
**Risco 4: Erros de Execução**
- **Probabilidade:** Baixa
- **Impacto:** Alto
- **Mitigação:** Validações rigorosas, testes extensivos

**Risco 5: Falhas de Segurança**
- **Probabilidade:** Baixa
- **Impacto:** Alto
- **Mitigação:** Credenciais seguras, logs completos

**Risco 6: Perdas Financeiras**
- **Probabilidade:** Média
- **Impacto:** Alto
- **Mitigação:** Limites rigorosos, stop loss automático

### 9.3 Riscos de Negócio
**Risco 7: Mudanças Regulatórias**
- **Probabilidade:** Baixa
- **Impacto:** Alto
- **Mitigação:** Monitoramento de regulamentações

**Risco 8: Lock-in Vendor**
- **Probabilidade:** Alta
- **Impacto:** Médio
- **Mitigação:** Documentação completa, código modular

---

## 10. Monitoramento e Manutenção

### 10.1 Monitoramento em Tempo Real
**Métricas Principais:**
- Status da conexão DLL
- Ordens executadas/hora
- P&L em tempo real
- Drawdown atual
- Alertas de risco

**Dashboard:**
```python
# Monitor em tempo real
class TradingMonitor:
    def __init__(self):
        self.metrics = {}
        
    def update_metrics(self, data):
        """Atualiza métricas em tempo real"""
        self.metrics.update(data)
        
    def generate_alerts(self):
        """Gera alertas baseados em métricas"""
        alerts = []
        
        if self.metrics.get('drawdown', 0) > 500:
            alerts.append("DRAWDOWN ALTO")
            
        if self.metrics.get('orders_failed', 0) > 3:
            alerts.append("MUITAS FALHAS")
            
        return alerts
```

### 10.2 Relatórios Diários
**Relatório de Performance:**
- Total de ordens executadas
- P&L do dia
- Drawdown máximo
- Ordens com falha
- Tempo médio de execução

**Relatório de Risco:**
- Exposição atual
- Limites atingidos
- Alertas gerados
- Posições abertas
- Stop loss acionados

### 10.3 Manutenção Preventiva
**Tarefas Diárias:**
- Verificar logs de erro
- Validar conectividade
- Backup de dados
- Limpeza de logs antigos

**Tarefas Semanais:**
- Análise de performance
- Otimização de parâmetros
- Atualização de documentação
- Testes de recuperação

---

## 11. Custos e Recursos

### 11.1 Custos de Desenvolvimento
**Recursos Necessários:**
- Desenvolvimento: 5 semanas (solo)
- Testes: 2 semanas
- Documentação: 1 semana
- **Total: 8 semanas**

**Custos Diretos:**
- Conta Genial: Gratuita (demo)
- Profit Pro: Gratuito com conta
- DLL: Gratuita
- **Total: R$ 0,00**

### 11.2 Custos Operacionais
**Custos Mensais:**
- Eletricidade: ~R$ 50,00
- Internet: Já existente
- Manutenção: 2h/semana
- **Total: ~R$ 50,00/mês**

### 11.3 Custos de Trading
**Capital Necessário:**
- Capital mínimo: R$ 1.000,00
- Margem por contrato: ~R$ 200,00
- **Recomendado: R$ 2.000,00**

---

## 12. Conclusão

### 12.1 Resumo da Solução
A integração com Genial Investimentos via Profit Pro usando ProfitDLL.dll oferece uma solução **100% gratuita** e **local** para execução automática de ordens. A arquitetura corrigida elimina a dependência de APIs REST inexistentes e utiliza a integração nativa via DLL.

### 12.2 Vantagens da Solução
- **Zero custos** de integração
- **Controle total** sobre execução
- **Segurança** com dados locais
- **Flexibilidade** para customizações
- **Independência** de serviços externos

### 12.3 Próximos Passos
1. **Configurar ambiente Windows**
2. **Obter ProfitDLL.dll** da Genial
3. **Implementar wrapper Python**
4. **Testar conectividade básica**
5. **Desenvolver execução de ordens**
6. **Implementar gestão de risco**
7. **Criar monitoramento**
8. **Testes em produção**

### 12.4 Critérios de Sucesso
- [ ] DLL integrada e funcionando
- [ ] Ordens executadas automaticamente
- [ ] Gestão de risco implementada
- [ ] Monitoramento em tempo real
- [ ] Sistema operacional 24/7
- [ ] Lucratividade demonstrada

---

**Status Final:** ✅ PRD COMPLETO E CORRIGIDO  
**Próxima Ação:** Iniciar desenvolvimento da integração DLL  
**Prazo Estimado:** 8 semanas para MVP completo 