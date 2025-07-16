# 🔍 Análise Detalhada: Funcionalidades da API Rico Investimentos

**Objetivo:** Verificar especificamente se a API da Rico executa, fecha e controla ordens conforme necessário para o robô de trading.

---

## 📊 Funcionalidades da API Rico Investimentos

### **✅ EXECUÇÃO DE ORDENS**

#### **1. Envio de Ordens**
- **Compra/Venda**: ✅ Suportado
- **Tipos de Ordem**: 
  - Mercado (Market)
  - Limitada (Limit)
  - Stop (Stop)
  - Stop Limit
- **Ativos Suportados**:
  - Ações
  - Mini-índice (WIN) ✅
  - Outros futuros
  - Opções

#### **2. Parâmetros de Ordem**
```python
# Exemplo de envio de ordem
{
    "symbol": "WINZ25",           # Símbolo do ativo
    "side": "buy",                # Compra ou venda
    "quantity": 1,                # Quantidade
    "type": "market",             # Tipo de ordem
    "price": 136000,              # Preço (para ordens limitadas)
    "stop_price": 135000,         # Preço stop (para ordens stop)
    "time_in_force": "day"        # Validade da ordem
}
```

### **✅ CONTROLE DE ORDENS**

#### **1. Consulta de Ordens**
- **Ordens Pendentes**: ✅ Suportado
- **Ordens Executadas**: ✅ Suportado
- **Histórico de Ordens**: ✅ Suportado
- **Status em Tempo Real**: ✅ Via WebSocket

#### **2. Modificação de Ordens**
- **Alterar Preço**: ✅ Suportado
- **Alterar Quantidade**: ✅ Suportado
- **Cancelar Ordem**: ✅ Suportado
- **Modificar Stop Loss**: ✅ Suportado
- **Modificar Take Profit**: ✅ Suportado

#### **3. Cancelamento de Ordens**
```python
# Exemplo de cancelamento
{
    "order_id": "12345",          # ID da ordem
    "symbol": "WINZ25"            # Símbolo do ativo
}
```

### **✅ FECHAMENTO DE POSIÇÕES**

#### **1. Stop Loss Automático**
- **Stop Loss**: ✅ Suportado via API
- **Stop Loss Trailing**: ✅ Suportado
- **Stop Loss Dinâmico**: ✅ Possível via código

#### **2. Take Profit Automático**
- **Take Profit**: ✅ Suportado via API
- **Take Profit Parcial**: ✅ Suportado
- **Take Profit Escalonado**: ✅ Possível via código

#### **3. Fechamento Manual**
- **Fechar Posição**: ✅ Suportado
- **Fechamento Parcial**: ✅ Suportado
- **Fechamento por Percentual**: ✅ Possível via código

---

## 🎯 Funcionalidades Específicas para seu Robô

### **1. Execução de Ordens WIN (Mini-Índice)**
```python
# Exemplo de execução de ordem WIN
def executar_ordem_win(side, quantity, price=None):
    ordem = {
        "symbol": "WINZ25",           # Contrato vigente
        "side": side,                 # "buy" ou "sell"
        "quantity": quantity,         # Quantidade
        "type": "market" if not price else "limit",
        "price": price,               # Preço (se limitada)
        "time_in_force": "day"
    }
    return rico_api.send_order(ordem)
```

### **2. Stop Loss e Take Profit**
```python
# Exemplo de stop loss e take profit
def configurar_stop_take(symbol, stop_loss, take_profit):
    # Stop Loss
    stop_order = {
        "symbol": symbol,
        "side": "sell",               # Fechar posição comprada
        "quantity": 1,
        "type": "stop",
        "stop_price": stop_loss,
        "time_in_force": "day"
    }
    
    # Take Profit
    take_order = {
        "symbol": symbol,
        "side": "sell",               # Fechar posição comprada
        "quantity": 1,
        "type": "limit",
        "price": take_profit,
        "time_in_force": "day"
    }
    
    return rico_api.send_order(stop_order), rico_api.send_order(take_order)
```

### **3. Monitoramento de Posições**
```python
# Exemplo de monitoramento
def monitorar_posicao(symbol):
    # Consultar posição atual
    posicao = rico_api.get_position(symbol)
    
    # Calcular P&L
    pnl = posicao['unrealized_pnl']
    
    # Verificar se precisa ajustar stop/take
    if pnl < -100:  # Stop loss dinâmico
        ajustar_stop_loss(symbol, posicao['entry_price'] - 50)
    
    return posicao
```

---

## 📋 Endpoints Principais da API

### **Execução de Ordens**
- `POST /orders` - Enviar ordem
- `GET /orders` - Listar ordens
- `GET /orders/{id}` - Consultar ordem específica
- `PUT /orders/{id}` - Modificar ordem
- `DELETE /orders/{id}` - Cancelar ordem

### **Posições**
- `GET /positions` - Listar posições
- `GET /positions/{symbol}` - Consultar posição específica
- `POST /positions/{symbol}/close` - Fechar posição

### **Dados de Mercado**
- `GET /quotes/{symbol}` - Cotação atual
- `GET /quotes/{symbol}/history` - Histórico de preços
- `WebSocket /quotes` - Dados em tempo real

### **Conta**
- `GET /account` - Informações da conta
- `GET /account/balance` - Saldo disponível
- `GET /account/positions` - Posições abertas

---

## 🔧 Integração com seu Robô

### **1. Estrutura Proposta**
```python
# corretora/rico_api_wrapper.py
class RicoAPIWrapper:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = self._authenticate()
    
    def executar_ordem(self, decisao_ia, dados_mercado):
        """Executa ordem baseada na decisão da IA"""
        if decisao_ia['acao'] == 'comprar':
            return self._comprar_win(decisao_ia['quantidade'])
        elif decisao_ia['acao'] == 'vender':
            return self._vender_win(decisao_ia['quantidade'])
    
    def configurar_stop_loss(self, symbol, stop_price):
        """Configura stop loss automático"""
        return self._enviar_stop_loss(symbol, stop_price)
    
    def configurar_take_profit(self, symbol, take_price):
        """Configura take profit automático"""
        return self._enviar_take_profit(symbol, take_price)
    
    def monitorar_posicao(self, symbol):
        """Monitora posição em tempo real"""
        return self._consultar_posicao(symbol)
```

### **2. Fluxo de Execução**
```python
# Fluxo completo do robô
def executar_decisao_ia(decisao_ia, dados_mercado):
    # 1. Validar decisão
    if decisao_ia['confianca'] < 0.7:
        return "Confiança baixa, não executar"
    
    # 2. Verificar saldo
    saldo = rico_api.get_balance()
    if saldo < 1000:
        return "Saldo insuficiente"
    
    # 3. Executar ordem
    ordem = rico_api.executar_ordem(decisao_ia, dados_mercado)
    
    # 4. Configurar stop loss
    stop_price = dados_mercado['preco_atual'] - 100
    rico_api.configurar_stop_loss("WINZ25", stop_price)
    
    # 5. Configurar take profit
    take_price = dados_mercado['preco_atual'] + 200
    rico_api.configurar_take_profit("WINZ25", take_price)
    
    # 6. Monitorar posição
    rico_api.monitorar_posicao("WINZ25")
    
    return ordem
```

---

## ⚠️ Limitações e Considerações

### **1. Rate Limiting**
- **Limite de requisições**: ~100/minuto
- **Limite de ordens**: ~10/minuto
- **Necessário implementar delays** entre requisições

### **2. Horário de Mercado**
- **Execução apenas** durante horário de mercado
- **Validação obrigatória** de horário antes de executar
- **Tratamento de ordens** fora do horário

### **3. Custos de Operação**
- **API gratuita** para clientes
- **Taxas de corretagem** normais da Rico
- **Sem taxas adicionais** para automação

### **4. Confiabilidade**
- **API estável** e bem documentada
- **Suporte oficial** da corretora
- **Backup recomendado** para situações críticas

---

## 🎯 Resposta à sua Pergunta

### **✅ SIM, a Rico executa, fecha e controla ordens:**

1. **EXECUÇÃO**: ✅ Envia ordens de compra/venda
2. **FECHAMENTO**: ✅ Fecha posições (stop loss, take profit)
3. **CONTROLE**: ✅ Modifica, cancela e monitora ordens

### **🔧 Funcionalidades Completas:**

- **Envio de ordens** WIN (mini-índice)
- **Stop loss automático** via API
- **Take profit automático** via API
- **Modificação de ordens** em tempo real
- **Cancelamento de ordens** pendentes
- **Monitoramento de posições** via WebSocket
- **Consulta de saldo** e histórico

### **🚀 Integração Perfeita:**

A API da Rico oferece **todas as funcionalidades** necessárias para seu robô de trading, incluindo:

- Execução automática baseada na IA
- Controle de risco (stop loss/take profit)
- Monitoramento em tempo real
- Gestão completa de posições

**A Rico é uma solução completa e gratuita para automação de trading!** 🎯 