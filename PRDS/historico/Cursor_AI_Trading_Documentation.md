# Documentação Cursor AI para Robô de Trading

**Data:** Julho 2025  
**Versão:** 2.0  
**Objetivo:** Sistema de IA local com Ollama para análise de dados de trading  
**Status:** IMPLEMENTADO E OPERACIONAL ✅

---

## 1. Visão Geral

O **Cursor AI** é um IDE com IA integrada que pode ser conectado a **modelos locais** através de ferramentas como Ollama. Isso nos permite ter análise de IA para trading sem depender de APIs externas.

### 1.1 Vantagens desta Abordagem
- ✅ **Sem custos por uso** - Modelos locais
- ✅ **Privacidade total** - Dados não saem do seu computador
- ✅ **Sem dependência de internet** - Funciona offline
- ✅ **Controle total** - Você escolhe o modelo
- ✅ **Integração com Cursor** - IDE familiar

### 1.2 Limitações
- ❌ **Recursos computacionais** - Precisa de GPU/CPU potente
- ❌ **Qualidade dos modelos** - Depende do modelo escolhido
- ❌ **Configuração inicial** - Mais complexo de configurar

---

## 2. Arquitetura Proposta

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dados B3      │    │   Cursor AI     │    │   Modelo Local  │
│   (API)         │───▶│   + Ollama      │───▶│   (Llama/Mistral)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Preparador    │    │   Interface     │    │   Análise       │
│   de Dados      │    │   de Chat       │    │   de Trading    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 3. Configuração do Ambiente

### 3.1 Instalação do Ollama
```bash
# Ubuntu/Debian
curl -fsSL https://ollama.ai/install.sh | sh

# Verificar instalação
ollama --version
```

### 3.2 Instalação do OllamaLink
```bash
# Clonar repositório
git clone https://github.com/feos7c5/OllamaLink.git
cd OllamaLink

# Instalar dependências
pip install -r requirements.txt

# Executar
python ollamalink.py
```

### 3.3 Configuração do Cursor AI
1. Abrir Cursor AI
2. Ir em Settings > AI
3. Configurar para usar OllamaLink
4. Testar conexão

---

## 4. Modelos Recomendados para Trading

### 4.1 Llama 3.1 8B (Recomendado)
```bash
# Baixar modelo
ollama pull llama3.1:8b

# Executar
ollama run llama3.1:8b
```

**Características:**
- **Tamanho**: 8B parâmetros
- **RAM necessária**: ~8GB
- **Qualidade**: Boa para análise de dados
- **Velocidade**: Rápido

### 4.2 Mistral 7B
```bash
# Baixar modelo
ollama pull mistral:7b

# Executar
ollama run mistral:7b
```

**Características:**
- **Tamanho**: 7B parâmetros
- **RAM necessária**: ~6GB
- **Qualidade**: Excelente para análise
- **Velocidade**: Muito rápido

### 4.3 CodeLlama 34B (Para análises complexas)
```bash
# Baixar modelo
ollama pull codellama:34b

# Executar
ollama run codellama:34b
```

**Características:**
- **Tamanho**: 34B parâmetros
- **RAM necessária**: ~20GB
- **Qualidade**: Excelente
- **Velocidade**: Mais lento

---

## 5. Implementação para Trading

### 5.1 Script de Integração
```python
# ia/cursor_ai_client.py
import subprocess
import json
import requests
from typing import Dict, Any
from loguru import logger

class CursorAITradingClient:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434"
        
    def analisar_dados_mercado(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa dados de mercado usando Cursor AI + Ollama
        """
        try:
            # Preparar prompt
            prompt = self._criar_prompt_trading(dados)
            
            # Enviar para Ollama
            resposta = self._enviar_para_ollama(prompt)
            
            # Processar resposta
            decisao = self._processar_resposta(resposta)
            
            logger.info(f"Análise Cursor AI concluída: {decisao['decisao']}")
            return decisao
            
        except Exception as e:
            logger.error(f"Erro na análise Cursor AI: {e}")
            return self._decisao_fallback()
    
    def _criar_prompt_trading(self, dados: Dict[str, Any]) -> str:
        """
        Cria prompt estruturado para análise de trading
        """
        return f"""Você é um analista especializado em trading de mini-índice (WIN) na B3.

Analise os seguintes dados de mercado e tome uma decisão de trading:

DADOS DE MERCADO:
- Ativo: {dados.get('ativo', 'WINZ25')}
- Preço atual: {dados.get('preco_atual', 'N/A')}
- Bid/Ask: {dados.get('bid', 'N/A')}/{dados.get('ask', 'N/A')}
- Volume: {dados.get('volume', 'N/A')}
- Variação: {dados.get('variacao', 'N/A')}%

INDICADORES TÉCNICOS:
- RSI: {dados.get('rsi', 'N/A')}
- MACD: {dados.get('macd', 'N/A')}
- Bandas de Bollinger: Superior {dados.get('bb_upper', 'N/A')}, Inferior {dados.get('bb_lower', 'N/A')}

CONTEXTO:
- Dia da semana: {dados.get('dia_semana', 'N/A')}
- Hora: {dados.get('hora', 'N/A')}
- Volatilidade: {dados.get('volatilidade', 'N/A')}

Responda APENAS no seguinte formato JSON:
{{
  "decisao": "comprar|vender|aguardar",
  "confianca": 0.0-1.0,
  "razao": "explicação detalhada da decisão",
  "parametros": {{
    "quantidade": 1,
    "stop_loss": 100,
    "take_profit": 200
  }}
}}"""
    
    def _enviar_para_ollama(self, prompt: str) -> str:
        """
        Envia prompt para Ollama via API
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Baixa temperatura para respostas consistentes
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()['response']
    
    def _processar_resposta(self, resposta: str) -> Dict[str, Any]:
        """
        Processa resposta do modelo e extrai decisão
        """
        try:
            # Tentar extrair JSON da resposta
            import re
            json_match = re.search(r'\{.*\}', resposta, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback se não encontrar JSON
                return self._parsear_resposta_texto(resposta)
        except json.JSONDecodeError:
            return self._parsear_resposta_texto(resposta)
    
    def _parsear_resposta_texto(self, resposta: str) -> Dict[str, Any]:
        """
        Parseia resposta em texto para extrair decisão
        """
        resposta_lower = resposta.lower()
        
        if "comprar" in resposta_lower:
            decisao = "comprar"
        elif "vender" in resposta_lower:
            decisao = "vender"
        else:
            decisao = "aguardar"
        
        # Extrair confiança (procurar por números entre 0 e 1)
        import re
        confianca_match = re.search(r'0\.\d+', resposta)
        confianca = float(confianca_match.group()) if confianca_match else 0.5
        
        return {
            "decisao": decisao,
            "confianca": confianca,
            "razao": resposta[:200],  # Primeiros 200 caracteres
            "parametros": {
                "quantidade": 1,
                "stop_loss": 100,
                "take_profit": 200
            }
        }
    
    def _decisao_fallback(self) -> Dict[str, Any]:
        """
        Decisão de fallback em caso de erro
        """
        return {
            "decisao": "aguardar",
            "confianca": 0.0,
            "razao": "Erro na análise - usando fallback",
            "parametros": {
                "quantidade": 0,
                "stop_loss": 0,
                "take_profit": 0
            }
        }
```

### 5.2 Uso do Cliente
```python
# Exemplo de uso
from ia.cursor_ai_client import CursorAITradingClient

# Inicializar cliente
client = CursorAITradingClient(model_name="llama3.1:8b")

# Dados de mercado
dados_mercado = {
    "ativo": "WINZ25",
    "preco_atual": 123456,
    "bid": 123455,
    "ask": 123457,
    "volume": 1500,
    "variacao": 0.5,
    "rsi": 65.5,
    "macd": 12.3,
    "bb_upper": 123470,
    "bb_lower": 123430,
    "dia_semana": 2,
    "hora": 14,
    "volatilidade": 0.8
}

# Analisar dados
try:
    decisao = client.analisar_dados_mercado(dados_mercado)
    print(f"Decisão: {decisao['decisao']}")
    print(f"Confiança: {decisao['confianca']}")
    print(f"Razão: {decisao['razao']}")
except Exception as e:
    print(f"Erro: {e}")
```

---

## 6. Configuração no Sistema

### 6.1 Arquivo de Configuração
```yaml
# config/config_ia.yaml
ia:
  tipo: "cursor_ai_local"
  modelo:
    nome: "llama3.1:8b"
    temperatura: 0.1
    max_tokens: 1000
    top_p: 0.9
    
  ollama:
    url: "http://localhost:11434"
    timeout: 30
    retry_attempts: 3
    
  dados:
    periodos_historico: 100
    indicadores_tecnicos: true
    incluir_volume: true
    incluir_contexto: true
    
  decisao:
    confianca_minima: 0.6
    filtro_volatilidade: true
    max_ordens_dia: 10
    stop_loss_padrao: 100
    take_profit_padrao: 200
```

### 6.2 Integração com Sistema Existente
```python
# Atualizar analisador.py
from ia.cursor_ai_client import CursorAITradingClient
from config import load_config

def analisar_com_ia(dados):
    config = load_config()
    
    if config['ia']['tipo'] == 'cursor_ai_local':
        client = CursorAITradingClient(
            model_name=config['ia']['modelo']['nome']
        )
        return client.analisar_dados_mercado(dados)
    else:
        # Fallback para outros métodos
        return {'resultado': 'aguardar', 'confianca': 0.5}
```

---

## 7. Requisitos de Sistema

### 7.1 Hardware Mínimo
- **CPU**: Intel i5 ou AMD Ryzen 5 (4+ cores)
- **RAM**: 16GB (mínimo)
- **GPU**: Opcional, mas recomendado NVIDIA GTX 1060+
- **Armazenamento**: 10GB livres

### 7.2 Hardware Recomendado
- **CPU**: Intel i7 ou AMD Ryzen 7 (8+ cores)
- **RAM**: 32GB
- **GPU**: NVIDIA RTX 3060+ ou AMD RX 6600+
- **Armazenamento**: SSD 50GB+

### 7.3 Software
- **Sistema**: Ubuntu 20.04+ ou Windows 10+
- **Python**: 3.8+
- **Ollama**: Última versão
- **Cursor AI**: Última versão

---

## 8. Monitoramento e Performance

### 8.1 Métricas Importantes
- **Latência de resposta** (deve ser < 5 segundos)
- **Uso de memória** do modelo
- **Taxa de acerto** das decisões
- **Temperatura da GPU/CPU**

### 8.2 Logs Estruturados
```python
logger.info("Cursor AI Analysis", extra={
    "model": self.model_name,
    "latency_ms": latency,
    "memory_usage_mb": memory_usage,
    "decisao": decisao['decisao'],
    "confianca": decisao['confianca'],
    "tokens_used": tokens_used
})
```

---

## 9. Otimizações

### 9.1 Para Melhor Performance
```bash
# Usar GPU se disponível
export CUDA_VISIBLE_DEVICES=0

# Aumentar threads do Ollama
export OLLAMA_NUM_PARALLEL=4

# Otimizar memória
export OLLAMA_HOST=0.0.0.0:11434
```

### 9.2 Modelos Otimizados
- **Llama 3.1 8B Q4_K_M**: Boa qualidade, menor uso de memória
- **Mistral 7B Q4_K_M**: Excelente qualidade, rápido
- **CodeLlama 13B Q4_K_M**: Melhor para análises complexas

---

## 10. Status Atual da Implementação

### ✅ **SISTEMA IMPLEMENTADO E OPERACIONAL**

**Componentes Implementados:**
- ✅ **Ollama**: Instalado e funcionando
- ✅ **Modelo Llama 3.1 8B**: Carregado e operacional
- ✅ **Cliente Python**: Implementado (`ia/cursor_ai_client.py`)
- ✅ **Integração**: Conectado ao sistema de trading
- ✅ **Análise**: Funcionando em tempo real
- ✅ **Decisões**: COMPRAR, VENDER, AGUARDAR
- ✅ **Confiança**: Cálculo automático
- ✅ **Logs**: Sistema completo de logging

**Configuração Atual:**
- **Modelo**: Llama 3.1 8B
- **Timeout**: 30 segundos
- **Confiança mínima**: 70%
- **Frequência**: Análise a cada 30 segundos
- **Horário**: 09:00-17:00 (Seg-Sex)

**Como Usar:**
```bash
# Iniciar robô completo
cd /home/andrei/Documents/EU/TRADE/AI/robo_trading
./rodar_robo.sh

# Monitorar
python3 monitor.py
```

---

## 11. Próximos Passos

1. ✅ **Instalar Ollama** e baixar modelo - CONCLUÍDO
2. ✅ **Implementar cliente Python** - CONCLUÍDO
3. ✅ **Testar com dados reais** - CONCLUÍDO
4. ✅ **Integrar com sistema existente** - CONCLUÍDO
5. ✅ **Monitorar performance** - CONCLUÍDO
6. [ ] **Otimizar prompts** para melhor precisão
7. [ ] **Implementar backtesting** com dados históricos
8. [ ] **Adicionar mais indicadores** técnicos

---

## 12. Recursos Adicionais

- **Ollama**: https://ollama.ai
- **Cursor AI**: https://cursor.sh
- **Modelos disponíveis**: https://ollama.ai/library
- **Documentação do sistema**: README_EXECUCAO.md 