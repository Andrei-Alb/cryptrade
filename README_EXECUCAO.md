# 🤖 ROBÔ DE TRADING IA - GUIA DE EXECUÇÃO

Este guia te mostra como ativar o robô de trading que coleta dados da B3 em tempo real e usa IA local para tomar decisões de compra/venda **com aprendizado automático**.

## ⚡ INICIAR BOT RÁPIDO

### 🚀 PASSO A PASSO DIRETO
streamlit run robo_trading/monitor_visual.py
```bash
# 1. Ir para o diretório do robô
cd /home/andrei/Documents/EU/TRADE/AI/robo_trading

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Verificar se Ollama está rodando
ollama list

# 4. INICIAR O ROBÔ (escolha uma opção)
./rodar_robo.sh                    # ← RECOMENDADO: Inicia em background
# OU
python3 iniciar_robo.py            # ← Inicia com verificações detalhadas
# OU  
python3 robo_ia_tempo_real.py      # ← Inicia diretamente

# 5. Em outro terminal, monitorar
python3 monitor.py                 # ← Status em tempo real
# OU
tail -f logs/robo_background.log   # ← Logs em tempo real
```

### 🛑 PARAR O ROBÔ

```bash
./parar_robo.sh
```

### 🧪 TESTE RÁPIDO (ANTES DE INICIAR)

```bash
python3 teste_rapido.py
```

### 🧠 TESTE DO SISTEMA DE APRENDIZADO

```bash
python3 teste_sistema_aprendizado.py  # ← NOVO: Testa aprendizado da IA
```

---

## 🚀 COMO ATIVAR O ROBÔ (DETALHADO)

### 1. Verificar Pré-requisitos

Antes de iniciar, certifique-se de que:

- ✅ Ollama está rodando: `ollama serve`
- ✅ Modelo Llama 3.1 8B está instalado: `ollama pull llama3.1:8b`
- ✅ Ambiente virtual está ativo: `source venv/bin/activate`
- ✅ Todas as dependências estão instaladas: `pip install -r requirements.txt`

### 2. Iniciar o Robô

**Opção 1: Script Automático (RECOMENDADO)**
```bash
./rodar_robo.sh
```

**Opção 2: Execução Manual**
```bash
python3 iniciar_robo.py
```

**Opção 3: Execução Direta**
```bash
python3 robo_ia_tempo_real.py
```

## 📊 MONITORAMENTO

### Ver Status em Tempo Real
```bash
python3 monitor.py
```

### Ver Logs em Tempo Real
```bash
tail -f logs/robo_background.log
```

### Ver Logs de Inicialização
```bash
tail -f logs/inicializacao.log
```

## 🧠 MONITORAMENTO DO SISTEMA DE APRENDIZADO

### 📈 Ver Estatísticas de Aprendizado
```bash
# Ver estatísticas gerais do aprendizado
python3 -c "
from ia.sistema_aprendizado import SistemaAprendizado
sistema = SistemaAprendizado()
stats = sistema.obter_estatisticas_aprendizado()
print(f'📊 Estatísticas de Aprendizado:')
print(f'   Registros: {stats.get(\"total_registros_aprendizado\", 0)}')
print(f'   Taxa de acerto: {stats.get(\"taxa_acerto_geral\", 0):.1f}%')
print(f'   Ajustes realizados: {stats.get(\"total_ajustes_realizados\", 0)}')
"
```

### 🔧 Ver Parâmetros Otimizados
```bash
# Ver parâmetros atuais otimizados pela IA
python3 -c "
from ia.sistema_aprendizado import SistemaAprendizado
sistema = SistemaAprendizado()
params = sistema.obter_parametros_otimizados()
print('🔧 Parâmetros Otimizados pela IA:')
for param, valor in params.items():
    print(f'   {param}: {valor}')
"
```

### 📊 Analisar Desempenho Recente
```bash
# Analisar desempenho dos últimos 7 dias
python3 -c "
from ia.sistema_aprendizado import SistemaAprendizado
sistema = SistemaAprendizado()
analise = sistema.analisar_desempenho_recente(dias=7)
print(f'📊 Análise de Desempenho (7 dias):')
print(f'   Total de ordens: {analise.get(\"total_ordens\", 0)}')
print(f'   Taxa de acerto geral: {analise.get(\"taxa_acerto_geral\", 0):.1f}%')
print(f'   Lucro médio: {analise.get(\"lucro_medio\", 0):.3f}%')
print('💡 Recomendações:')
for rec in analise.get('recomendacoes', []):
    print(f'   • {rec}')
"
```

### 🎯 Testar Sistema de Aprendizado Completo
```bash
# Teste completo do sistema de aprendizado
python3 teste_sistema_aprendizado.py
```

## 🛑 COMO PARAR O ROBÔ

### Parada Segura
```bash
./parar_robo.sh
```

### Parada Forçada (se necessário)
```bash
# Encontrar PID
cat logs/robo.pid

# Parar processo
kill -KILL <PID>
```

## ⚙️ CONFIGURAÇÕES

### Horário de Mercado
- **Dias**: Segunda a Sexta
- **Horário**: 09:00 às 17:00
- **Frequência**: Análise a cada 30 segundos

### Modelo IA
- **Modelo**: Llama 3.1 8B
- **Confiança mínima**: 25% (ajustável automaticamente)
- **Confiança alta**: 60% (ajustável automaticamente)
- **Timeout**: 30 segundos por análise

### Sistema de Aprendizado
- **Ajuste automático**: Ativo
- **Análise de performance**: A cada 10 ordens
- **Otimização de parâmetros**: Baseada em resultados reais
- **Registro detalhado**: Cada decisão é salva para aprendizado

### Símbolos Analisados
- **Foco**: Contratos WIN (Mini Índice)
- **Dados**: Preço atual, volume, variação, etc.

## 📈 O QUE O ROBÔ FAZ

### 1. Coleta de Dados
- Coleta preços em tempo real da B3
- Salva dados no banco SQLite local
- Monitora múltiplos símbolos simultaneamente

### 2. Análise com IA
- Calcula indicadores técnicos
- Envia dados para IA local (Llama 3.1 8B)
- Recebe decisões: COMPRAR, VENDER ou AGUARDAR
- Calcula nível de confiança da decisão

### 3. Execução de Ordens
- Executa ordens com confiança ajustável automaticamente
- Salva todas as ordens no banco
- Registra respostas da API de trading

### 4. Sistema de Aprendizado (NOVO)
- **Aprende de cada ordem** executada
- **Ajusta parâmetros** automaticamente baseado no desempenho
- **Registra aprendizado detalhado** com confiança, resultado e acerto
- **Otimiza threshold de confiança** dinamicamente
- **Recomenda melhorias** baseadas em dados reais

### 5. Monitoramento
- Logs detalhados de todas as operações
- Métricas de performance em tempo real
- Tratamento de erros e recuperação automática
- **Estatísticas de aprendizado** em tempo real

## 🔍 TROUBLESHOOTING

### Robô não inicia
```bash
# Verificar Ollama
ollama list

# Verificar ambiente virtual
which python3

# Verificar dependências
pip list | grep -E "(requests|loguru|sqlite3)"
```

### IA não responde
```bash
# Testar conexão
curl http://localhost:11434/api/tags

# Verificar modelo
ollama list | grep llama3.1
```

### Sem dados da B3
```bash
# Testar coletor manualmente
python3 -c "from coletor import Coletor; c = Coletor(); print(c.coletar_dados())"
```

### Erro de banco de dados
```bash
# Verificar permissões
ls -la dados/

# Recriar banco
rm dados/trading.db
python3 -c "from armazenamento import Armazenamento; a = Armazenamento()"
```

### Sistema de Aprendizado não funciona
```bash
# Verificar tabelas de aprendizado
sqlite3 dados/trading.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%aprendizado%';"

# Verificar registros de aprendizado
sqlite3 dados/trading.db "SELECT COUNT(*) FROM aprendizado_detalhado;"

# Testar sistema de aprendizado
python3 teste_sistema_aprendizado.py
```

## 📋 COMANDOS ÚTEIS

### Verificar Status
```bash
# Status do processo
ps aux | grep robo_ia_tempo_real

# Status do Ollama
ps aux | grep ollama

# Verificar logs
ls -la logs/
```

### Análise de Dados
```bash
# Ver últimas análises
sqlite3 dados/trading.db "SELECT * FROM analises ORDER BY timestamp DESC LIMIT 10;"

# Ver últimas ordens
sqlite3 dados/trading.db "SELECT * FROM ordens ORDER BY timestamp DESC LIMIT 10;"

# Estatísticas
sqlite3 dados/trading.db "SELECT COUNT(*) as total FROM precos;"
```

### Análise de Aprendizado (NOVO)
```bash
# Ver registros de aprendizado detalhado
sqlite3 dados/trading.db "
SELECT 
    tipo_ordem,
    confianca_ia,
    resultado,
    acerto,
    timestamp
FROM aprendizado_detalhado 
ORDER BY timestamp DESC 
LIMIT 10;
"

# Ver taxa de acerto por confiança
sqlite3 dados/trading.db "
SELECT 
    CASE 
        WHEN confianca_ia >= 0.6 THEN 'Alta'
        WHEN confianca_ia >= 0.4 THEN 'Média'
        ELSE 'Baixa'
    END as nivel_confianca,
    COUNT(*) as total,
    SUM(CASE WHEN acerto = 1 THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(CASE WHEN acerto = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as taxa_acerto
FROM aprendizado_detalhado 
GROUP BY nivel_confianca
ORDER BY nivel_confianca;
"

# Ver ajustes realizados
sqlite3 dados/trading.db "
SELECT 
    parametro,
    valor_anterior,
    valor_novo,
    motivo,
    timestamp
FROM aprendizado_saida 
ORDER BY timestamp DESC 
LIMIT 10;
"
```

### Limpeza
```bash
# Limpar logs antigos
find logs/ -name "*.log" -mtime +7 -delete

# Backup do banco
cp dados/trading.db dados/trading_backup_$(date +%Y%m%d).db
```

## 🎯 EXEMPLO DE EXECUÇÃO

```bash
# 1. Ativar ambiente
source venv/bin/activate

# 2. Verificar Ollama
ollama list

# 3. Testar sistema de aprendizado
python3 teste_sistema_aprendizado.py

# 4. Iniciar robô
./rodar_robo.sh

# 5. Em outro terminal, monitorar
python3 monitor.py

# 6. Ver logs em tempo real
tail -f logs/robo_background.log

# 7. Verificar aprendizado (periodicamente)
python3 -c "
from ia.sistema_aprendizado import SistemaAprendizado
sistema = SistemaAprendizado()
stats = sistema.obter_estatisticas_aprendizado()
print(f'📊 Aprendizado: {stats.get(\"total_registros_aprendizado\", 0)} registros, {stats.get(\"taxa_acerto_geral\", 0):.1f}% acerto')
"
```

## 🧠 SISTEMA DE APRENDIZADO - DETALHES

### Como Funciona
1. **Coleta de Dados**: Cada ordem executada é registrada com detalhes
2. **Análise de Performance**: Sistema analisa taxa de acerto, lucro médio, etc.
3. **Ajuste Automático**: Parâmetros são otimizados baseado em resultados
4. **Registro de Aprendizado**: Cada decisão é salva para análise futura

### Parâmetros Otimizáveis
- **threshold_confianca**: Confiança mínima para executar ordens
- **threshold_confianca_alta**: Confiança para ordens de alta confiança
- **tempo_estagnacao**: Tempo máximo antes de fechar por estagnação
- **stop_loss_percentual**: Stop loss automático
- **take_profit_percentual**: Take profit automático
- **max_ordens_consecutivas**: Máximo de ordens consecutivas
- **balanceamento_compra_venda**: Balancear compras e vendas

### Benefícios
- **Melhoria Contínua**: Performance melhora automaticamente
- **Adaptação ao Mercado**: Ajusta-se às condições atuais
- **Redução de Perdas**: Identifica e corrige problemas
- **Otimização de Lucros**: Maximiza oportunidades de ganho

## ⚠️ IMPORTANTE

- **Horário de Mercado**: O robô só opera durante o horário de mercado
- **Confiança Dinâmica**: Threshold de confiança é ajustado automaticamente
- **Aprendizado Ativo**: Sistema aprende e melhora continuamente
- **Logs**: Sempre monitore os logs para detectar problemas
- **Backup**: Faça backup regular do banco de dados
- **Teste**: Sempre teste em ambiente simulado antes de usar dinheiro real

## 🆘 SUPORTE

Se encontrar problemas:

1. Verifique os logs em `logs/`
2. Execute o script de inicialização: `python3 iniciar_robo.py`
3. Verifique se o Ollama está rodando: `ollama serve`
4. Teste a conexão com IA: `python3 teste_ia.py`
5. **Teste o sistema de aprendizado**: `python3 teste_sistema_aprendizado.py`

---

**🎯 O robô está pronto para operar 24/7 com aprendizado automático, respeitando horário de mercado!** 