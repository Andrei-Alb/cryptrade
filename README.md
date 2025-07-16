# 🤖 CryptoTrade - Sistema de Trading com IA Autônoma

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Produção-brightgreen.svg)]()

> **Sistema avançado de trading automatizado com IA local e aprendizado contínuo**

## 📋 Visão Geral

O **CryptoTrade** é um sistema completo de trading automatizado que utiliza inteligência artificial local para tomar decisões de compra e venda em criptomoedas. O sistema possui aprendizado autônomo, monitoramento em tempo real e execução de ordens automatizada.

### 🎯 Características Principais

- 🤖 **IA Local Autônoma** - Usa modelos Llama/Phi3 para decisões
- 📊 **Aprendizado Contínuo** - Sistema que aprende com resultados
- ⚡ **Tempo Real** - Análise e execução em tempo real
- 🔒 **Seguro** - Execução local, sem dependência de APIs externas
- 📈 **Monitoramento** - Dashboard completo de performance
- 🎮 **Modo Simulação** - Teste sem risco real

## 🚀 Funcionalidades

### 🤖 Sistema de IA
- **Modelos Locais**: Llama 3.1 8B, Phi3 Mini, Qwen2.5
- **Aprendizado Autônomo**: Sistema que ajusta confiança baseado em resultados
- **Análise Técnica**: RSI, MACD, Bollinger Bands, Tendências
- **Cache Inteligente**: Otimização de performance

### 📊 Trading
- **Múltiplos Pares**: BTC/USDT, ETH/USDT, etc.
- **Gestão de Risco**: Stop Loss, Take Profit automático
- **Ordens Dinâmicas**: Ajuste automático baseado em mercado
- **Simulação**: Modo teste sem risco

### 📈 Monitoramento
- **Dashboard Real-time**: Performance e estatísticas
- **Logs Detalhados**: Histórico completo de operações
- **Alertas**: Notificações de eventos importantes
- **Relatórios**: Análise de performance

## 🛠️ Instalação

### Pré-requisitos
```bash
# Python 3.10+
python --version

# Ollama (para modelos de IA)
curl -fsSL https://ollama.ai/install.sh | sh

# Git
git --version
```

### Instalação do Projeto
```bash
# Clone o repositório
git clone https://github.com/Andrei-Alb/cryptrade.git
cd cryptrade

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure credenciais
cp credenciais_exemplo.py credenciais.py
# Edite credenciais.py com suas chaves da corretora
```

### Configuração dos Modelos de IA
```bash
# Instale modelos otimizados
ollama pull phi3:mini      # Modelo rápido (recomendado)
ollama pull llama2:7b-chat # Modelo alternativo
```

## ⚙️ Configuração

### 1. Credenciais da Corretora
```python
# credenciais.py
BYBIT_API_KEY = "sua_api_key"
BYBIT_API_SECRET = "sua_api_secret"
```

### 2. Configuração do Sistema
```yaml
# config.yaml
trading:
  pares: ["BTCUSDT", "ETHUSDT"]
  quantidade_padrao: 0.001
  stop_loss_padrao: 2.0
  take_profit_padrao: 3.0

ia:
  modelo_principal: "phi3:mini"
  timeout_inferencia: 15
```

## 🚀 Uso

### Execução Rápida
```bash
# Modo simulação (recomendado para testes)
./executar_robo.sh

# Modo produção (cuidado!)
./executar_tudo.sh
```

### Execução Manual
```python
# Inicializar sistema
python main.py

# Apenas treinamento
python robo_treinamento.py

# Tempo real
python robo_tempo_real.py
```

### Scripts Úteis
```bash
# Parar robô
./parar_robo.sh

# Alternar modo (simulação/produção)
python alternar_modo.py

# Testar conectividade
python teste_conectividade.py
```

## 📊 Monitoramento

### Dashboard Web
```bash
# Acesse o dashboard
http://localhost:8080
```

### Logs
```bash
# Visualizar logs em tempo real
tail -f logs/robo_ia_tempo_real.log

# Análise de performance
python analisador.py
```

## 🔧 Arquitetura

```
cryptrade/
├── ia/                          # Sistema de IA
│   ├── decisor.py              # Tomada de decisões
│   ├── llama_cpp_client.py     # Cliente IA local
│   ├── sistema_aprendizado_autonomo.py  # Aprendizado
│   └── preparador_dados.py     # Preparação de dados
├── executor.py                  # Execução de ordens
├── coletor.py                   # Coleta de dados
├── monitor.py                   # Monitoramento
├── config.yaml                  # Configurações
└── PRDS/                        # Documentação técnica
```

## 📈 Performance

### Métricas Atuais
- ⚡ **Tempo de Inferência**: 15-60s (otimização em andamento)
- 🎯 **Acertividade**: 60-70% (varia com mercado)
- 📊 **Throughput**: 1-4 decisões/minuto
- 💾 **Uso de Memória**: 4-5GB (modelo atual)

### Otimizações Planejadas
- ⚡ **75-92% mais rápido** (PRD de otimização)
- 📈 **300% mais decisões** por minuto
- 💾 **60-80% menos memória**

## 📚 Documentação

### PRDs (Product Requirements Documents)
- [📋 PRD Otimização de Velocidade](PRDS/02_PRD_Otimizacao_IA_Velocidade.md)
- [📊 Resumo Executivo](PRDS/02_PRD_Otimizacao_IA_Velocidade_RESUMO.md)
- [📈 Histórico de PRDs](PRDS/historico/)

### Guias
- [🚀 Como Executar](README_EXECUCAO.md)
- [🧠 Acompanhar IA Aprendendo](COMO_ACOMPANHAR_IA_APRENDENDO.md)
- [📊 Relatório de Melhorias](RELATORIO_MELHORIAS.md)

## 🔒 Segurança

### Boas Práticas
- ✅ **Nunca** commite credenciais reais
- ✅ Use sempre modo simulação primeiro
- ✅ Monitore logs regularmente
- ✅ Configure limites de risco adequados

### Configurações de Segurança
```yaml
risco:
  max_drawdown_diario: 5.0
  max_exposicao: 50.0
  stop_emergencia: 10.0
```

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Padrões de Código
- Use Python 3.10+
- Siga PEP 8
- Documente funções importantes
- Adicione testes para novas funcionalidades

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Disclaimer

**ATENÇÃO**: Trading automatizado envolve riscos significativos. Este software é fornecido "como está" sem garantias. Use por sua conta e risco.

### Recomendações
- 🧪 **Sempre teste em simulação primeiro**
- 💰 **Comece com valores pequenos**
- 📊 **Monitore constantemente**
- 🎓 **Entenda os riscos antes de usar**

## 📞 Suporte

### Issues
- [GitHub Issues](https://github.com/Andrei-Alb/cryptrade/issues)
- [Discussions](https://github.com/Andrei-Alb/cryptrade/discussions)

### Comunidade
- 📧 Email: [seu-email@exemplo.com]
- 💬 Discord: [link-do-discord]
- 📱 Telegram: [@seu-usuario]

---

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

**🔄 Atualizações regulares com melhorias de performance e novas funcionalidades.** 