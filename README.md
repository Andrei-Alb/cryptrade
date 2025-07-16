# 🤖 Robô de Trading Pessoal - Mini-Índice B3

Sistema automatizado para coleta de dados do mini-índice (WIN) e IBOV da B3, com análise de IA e execução de ordens.

## 📋 Pré-requisitos

- Python 3.8+
- Linux (testado em Ubuntu)
- Conexão com internet

## 🚀 Instalação

```bash
# 1. Clone o repositório
cd robo_trading

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

## 📁 Estrutura do Projeto

```
robo_trading/
├── main.py                    # Script principal (coleta única)
├── main_continuo.py           # Coleta contínua (horário de mercado)
├── teste_continuo.py          # Coleta contínua (modo teste)
├── testador_frequencia.py     # Testa frequências da API B3
├── monitor.py                 # Monitoramento do sistema
├── coletor.py                 # Coleta dados da API B3
├── armazenamento.py           # Banco SQLite
├── analisador.py              # Análise com IA
├── executor.py                # Execução de ordens
├── config.py                  # Configurações
├── dados/                     # Banco SQLite
├── logs/                      # Logs do sistema
└── venv/                      # Ambiente virtual
```

## 🎯 Como Usar

**⚠️ IMPORTANTE:** Todos os comandos devem ser executados dentro da pasta `robo_trading/` com o ambiente virtual ativado.

```bash
# 1. Navegar para o diretório do projeto
cd robo_trading

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Agora executar os comandos
```

### 1. Coleta Única de Dados
**Comando:** `python3 main.py`
**O que faz:** Coleta dados uma vez e para
**Saída esperada:**
```
2025-07-13 22:45:30.123 | INFO     | coletor:coletar_dados_b3:22 - Coletando dados da B3 para IBOV
2025-07-13 22:45:30.456 | INFO     | coletor:coletar_dados:104 - Dados coletados da B3: 136187.31
2025-07-13 22:45:30.789 | INFO     | coletor:coletar_dados:112 - Dados coletados da B3 para WINZ25: 143550
2025-07-13 22:45:30.790 | INFO     | analisador:analisar_com_ia:15 - Análise IA: AGUARDAR (confiança: 0.7)
```

### 2. Coleta Contínua (Horário de Mercado)
**Comando:** `python3 main_continuo.py`
**O que faz:** Coleta dados continuamente apenas em dias úteis (09:00-17:00)
**Saída fora do horário:**
```
2025-07-13 22:30:30.649 | INFO     | __main__:executar:165 - 🚀 Iniciando Coleta Contínua de Dados
2025-07-13 22:30:30.649 | INFO     | __main__:executar:167 - 🕐 Horário de mercado: 09:00:00 - 17:00:00
2025-07-13 22:30:30.650 | INFO     | __main__:executar:177 - ⏸️  Fora do horário de mercado. Aguardando...
```

### 3. Coleta Contínua (Modo Teste)
**Comando:** `python3 teste_continuo.py`
**O que faz:** Coleta dados continuamente sem restrição de horário (5 ciclos)
**Saída esperada:**
```
2025-07-13 22:38:17.772 | INFO     | __main__:executar:160 - 🧪 Iniciando Coleta Contínua de Dados (MODO TESTE)
2025-07-13 22:38:17.772 | INFO     | __main__:executar:161 - ⏰ Frequência: 30 segundos
2025-07-13 22:38:17.772 | INFO     | __main__:executar:162 - 🔄 Ciclos máximos: 5
2025-07-13 22:38:39.921 | INFO     | coletor:coletar_dados:104 - Dados coletados da B3: 136187.31
2025-07-13 22:38:40.492 | INFO     | coletor:coletar_dados:112 - Dados coletados da B3 para WINZ25: 143550
2025-07-13 22:38:40.493 | INFO     | __main__:coletar_dados_ciclo:103 - ✅ Dados coletados - 2 símbolos - Latência: 0.953s
2025-07-13 22:38:40.493 | INFO     | __main__:executar:181 - ⏳ Aguardando 30s para próxima coleta... (1/5)
```

### 4. Teste de Frequência da API
**Comando:** `python3 testador_frequencia.py`
**O que faz:** Testa diferentes frequências de coleta (1s, 5s, 10s, 15s, 30s, 60s)
**Saída esperada:**
```
2025-07-13 22:50:00.123 | INFO     | __main__:testar_frequencia:45 - 🧪 Testando frequência: 30 segundos
2025-07-13 22:50:00.456 | INFO     | coletor:coletar_dados:104 - Dados coletados da B3: 136187.31
2025-07-13 22:50:00.789 | INFO     | coletor:coletar_dados:112 - Dados coletados da B3 para WINZ25: 143550
2025-07-13 22:50:30.123 | INFO     | __main__:testar_frequencia:45 - 🧪 Testando frequência: 30 segundos
...
2025-07-13 22:52:00.456 | INFO     | __main__:exibir_resultados:120 - 📊 RESULTADOS DO TESTE
2025-07-13 22:52:00.456 | INFO     | __main__:exibir_resultados:121 - Frequência: 30s | Sucessos: 4/4 | Latência média: 0.35s
```

### 5. Monitoramento do Sistema
**Comando:** `python3 monitor.py`
**O que faz:** Mostra status do sistema, dados recentes e estatísticas
**Saída esperada:**
```
2025-07-13 22:55:00.123 | INFO     | __main__:exibir_status:45 - 📊 STATUS DO SISTEMA
2025-07-13 22:55:00.123 | INFO     | __main__:exibir_status:46 - ============================================================
2025-07-13 22:55:00.124 | INFO     | __main__:exibir_status:47 - 🕐 Última coleta: 2025-07-13 22:38:40
2025-07-13 22:55:00.124 | INFO     | __main__:exibir_status:48 - 📈 IBOV: 136187.31
2025-07-13 22:55:00.124 | INFO     | __main__:exibir_status:49 - 📈 WINZ25: 143550
2025-07-13 22:55:00.124 | INFO     | __main__:exibir_status:50 - 💾 Total de registros: 156
2025-07-13 22:55:00.124 | INFO     | __main__:exibir_status:51 - ⏰ Horário de mercado: NÃO
```

## 📊 Dados Coletados

### Símbolos Disponíveis
- **IBOV**: Índice Bovespa
- **WINZ25**: Mini-índice (dezembro/2025)
- **WINM25**: Mini-índice (março/2025) - quando disponível
- **WINN25**: Mini-índice (novembro/2025) - quando disponível

### Estrutura dos Dados
```json
{
  "simbolo": "IBOV",
  "preco_atual": 136187.31,
  "preco_abertura": 136500.0,
  "preco_minimo": 135000.0,
  "preco_maximo": 137000.0,
  "preco_medio": 136000.0,
  "variacao": -0.5,
  "volume": 0,
  "timestamp": "2025-07-13T22:38:39.921",
  "fonte": "B3_API"
}
```

## 🗄️ Banco de Dados

**Localização:** `dados/trading.db`
**Tabelas:**
- `precos`: Dados de preços coletados
- `analises`: Resultados das análises de IA
- `ordens`: Ordens executadas

**Consultar dados:**
```bash
sqlite3 dados/trading.db "SELECT * FROM precos ORDER BY timestamp DESC LIMIT 10;"
```

## 📝 Logs

**Localização:** `logs/`
**Arquivos:**
- `robo_trading.log`: Log principal
- `coleta_continua.log`: Log da coleta contínua
- `coleta_continua_teste.log`: Log do modo teste
- `teste_frequencia.log`: Log dos testes de frequência

**Ver logs em tempo real:**
```bash
tail -f logs/coleta_continua.log
```

## ⚙️ Configurações

**Arquivo:** `config.py`
**Principais configurações:**
- Frequência de coleta: 30 segundos
- Horário de mercado: 09:00-17:00
- Dias úteis: Segunda a Sexta
- Timeout da API: 10 segundos

## 🚨 Tratamento de Erros

O sistema inclui:
- **Backoff exponencial** em caso de falhas
- **Fallback** para dados simulados se API indisponível
- **Rate limiting** automático (evita sobrecarregar API)
- **Logs detalhados** de todos os erros

## 🔧 Comandos Úteis

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Ver dados recentes no banco
sqlite3 dados/trading.db "SELECT simbolo, preco_atual, timestamp FROM precos ORDER BY timestamp DESC LIMIT 5;"

# Ver logs em tempo real
tail -f logs/coleta_continua.log

# Parar coleta contínua
Ctrl+C

# Verificar status do sistema
python3 monitor.py
```

## 📈 Status do Projeto

✅ **Implementado:**
- Coleta de dados reais da API B3
- Armazenamento em SQLite
- Coleta contínua com controle de horário
- Modo de teste sem restrições
- Teste de frequências da API
- Monitoramento do sistema
- Logs detalhados
- Tratamento de erros robusto

🔄 **Em desenvolvimento:**
- Análise com IA (mock implementado)
- Execução de ordens (mock implementado)

## 🆘 Solução de Problemas

**Erro: "No module named 'loguru'"**
```bash
source venv/bin/activate
pip install loguru
```

**Erro: "table precos has no column named simbolo"**
```bash
rm dados/trading.db
python3 main.py  # Recria o banco
```

**Sistema não coleta dados**
- Verificar se está no horário de mercado (09:00-17:00, dias úteis)
- Usar `teste_continuo.py` para testar fora do horário

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs em `logs/`
2. Consultar dados no banco SQLite
3. Usar `monitor.py` para diagnóstico
4. Verificar configurações em `config.py` 