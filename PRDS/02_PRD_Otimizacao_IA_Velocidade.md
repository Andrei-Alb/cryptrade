# PRD - Otimização de Velocidade da IA de Trading
## Documento de Requisitos do Produto

**Versão:** 1.0  
**Data:** 15/07/2025  
**Autor:** Análise de Sistema  
**Status:** Em Análise  

---

## 📋 Resumo Executivo

Este PRD documenta as oportunidades de otimização identificadas no sistema de IA de trading para **reduzir significativamente o tempo de resposta** (de 60s para 5-15s) **sem comprometer a qualidade e acertividade** das decisões.

### Objetivos Principais
- ⚡ **Reduzir tempo de inferência de 60s para 5-15s**
- 🎯 **Manter ou melhorar acertividade atual**
- 💾 **Implementar cache inteligente**
- 🔄 **Otimizar processamento em lote**
- 📊 **Sistema de fallback rápido**

---

## 🔍 Análise da Situação Atual

### Problemas Identificados

#### 1. **Timeout Excessivo**
- **Problema:** Timeout de 60 segundos para cada inferência
- **Impacto:** Perda de oportunidades de trading
- **Frequência:** Múltiplos timeouts detectados nos logs

#### 2. **Modelo Pesado**
- **Modelo Atual:** Llama 3.1 8B (4.9GB)
- **Problema:** Lento para inferência em tempo real
- **Alternativas Disponíveis:** phi3:mini, qwen2.5:0.5b

#### 3. **Prompt Verboso**
- **Tamanho Atual:** ~500 caracteres + dados completos
- **Problema:** Processamento desnecessário
- **Oportunidade:** Reduzir para ~100 caracteres

#### 4. **Processamento Sequencial**
- **Problema:** Análise de pares um por vez
- **Impacto:** Latência acumulativa
- **Solução:** Processamento paralelo

#### 5. **Sistema de Aprendizado Complexo**
- **Problema:** Múltiplas consultas ao banco durante decisão
- **Impacto:** Overhead desnecessário
- **Solução:** Cache de aprendizado

---

## 🎯 Objetivos e Métricas

### Objetivos Primários
1. **Velocidade:** Reduzir tempo de inferência para 5-15 segundos
2. **Qualidade:** Manter acertividade > 60%
3. **Disponibilidade:** Reduzir timeouts para < 5%
4. **Eficiência:** Aumentar throughput de decisões

### Métricas de Sucesso
- ⏱️ **Tempo médio de inferência:** < 15s
- 🎯 **Taxa de timeout:** < 5%
- 📈 **Throughput:** > 4 decisões/minuto
- 💰 **Acertividade:** Mantida ou melhorada
- 🔄 **Cache hit rate:** > 40%

---

## 🚀 Soluções Propostas

### 1. **Otimização do Modelo**

#### 1.1 Modelo Mais Rápido
```bash
# Opção 1: phi3:mini (3.8B - muito rápido)
ollama pull phi3:mini

# Opção 2: qwen2.5:0.5b (0.5B - extremamente rápido)
ollama pull qwen2.5:0.5b

# Opção 3: llama2:7b-chat (já disponível)
# Manter como fallback
```

**Benefícios:**
- ⚡ 3-5x mais rápido que Llama 3.1 8B
- 💾 Menor uso de memória
- 🎯 Qualidade similar para trading

#### 1.2 Configuração Otimizada
```yaml
ia:
  modelo_principal: "phi3:mini"
  modelo_fallback: "llama2:7b-chat"
  timeout_inferencia: 15  # Reduzido de 60
  max_tokens: 150         # Limitado para velocidade
  temperature: 0.3        # Mais determinístico
```

### 2. **Prompt Otimizado**

#### 2.1 Prompt Atual (Verboso)
```
Você é um trader especializado em criptomoedas. Analise os dados de mercado fornecidos e tome uma decisão de trading.

DADOS DE MERCADO:
{json_completo_dos_dados}

INSTRUÇÕES IMPORTANTES:
1. Analise tendências, indicadores técnicos e volume
2. Tome decisão: "comprar", "vender" ou "aguardar"
3. Confiança deve ser entre 0.1 e 1.0
4. Quantidade deve ser entre 1 e 10
5. Stop Loss deve ser entre -5% e -1% do preço atual
6. Take Profit deve ser entre +1% e +10% do preço atual
7. Ação para ordens abertas: "manter", "fechar" ou "ajustar"

EXEMPLO DE RESPOSTA VÁLIDA:
{
  "decisao": "comprar",
  "confianca": 0.85,
  "razao": "Tendência ascendente e indicadores técnicos favoráveis",
  "quantidade": 2,
  "stop_loss": -2.5,
  "take_profit": 5.0,
  "acao_ordem": "manter"
}

RESPONDA APENAS COM JSON VÁLIDO, SEM TEXTO ADICIONAL:
```

#### 2.2 Prompt Otimizado (Conciso)
```
Analise: RSI={rsi:.1f}, Tend={tendencia}, Vol={volatilidade:.3f}, Preço={preco:.2f}
Decisão: {"decisao":"comprar|vender|aguardar","confianca":0.0-1.0,"razao":"breve explicação"}
```

**Benefícios:**
- 📉 80% redução no tamanho do prompt
- ⚡ 2-3x mais rápido
- 🎯 Foco nos dados essenciais

### 3. **Sistema de Cache Inteligente**

#### 3.1 Cache de Decisões
```python
class CacheDecisoes:
    def __init__(self, ttl=30):  # 30 segundos TTL
        self.cache = {}
        self.ttl = ttl
    
    def gerar_chave(self, dados):
        # Chave baseada em dados essenciais
        essenciais = {
            'rsi': round(dados.get('rsi', 50.0), 1),
            'tendencia': dados.get('tendencia', 'lateral'),
            'volatilidade': round(dados.get('volatilidade', 0.02), 3),
            'preco': round(dados.get('preco_atual', 0.0), 2)
        }
        return hashlib.md5(json.dumps(essenciais, sort_keys=True).encode()).hexdigest()
```

#### 3.2 Cache de Aprendizado
```python
class CacheAprendizado:
    def __init__(self, ttl=300):  # 5 minutos TTL
        self.cache = {}
        self.ttl = ttl
    
    def obter_recomendacao_cache(self, symbol, contexto):
        # Cache de recomendações do sistema de aprendizado
        chave = f"{symbol}_{hash_contexto(contexto)}"
        return self.cache.get(chave)
```

**Benefícios:**
- ⚡ Resposta instantânea para cenários similares
- 📊 Redução de 40-60% nas consultas ao banco
- 🎯 Melhoria na consistência das decisões

### 4. **Processamento Paralelo**

#### 4.1 Análise Simultânea de Pares
```python
import asyncio
import concurrent.futures

class AnalisadorParalelo:
    def __init__(self, max_workers=3):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    async def analisar_pares_simultaneamente(self, pares, dados_mercado):
        # Analisar múltiplos pares em paralelo
        tasks = []
        for par in pares:
            task = self.executor.submit(self._analisar_par, par, dados_mercado[par])
            tasks.append(task)
        
        resultados = await asyncio.gather(*tasks)
        return dict(zip(pares, resultados))
```

**Benefícios:**
- ⚡ Redução de 60-70% no tempo total de análise
- 📈 Melhor utilização de recursos
- 🎯 Análise mais abrangente

### 5. **Sistema de Fallback Rápido**

#### 5.1 Análise Técnica Simples
```python
class AnaliseTecnicaRapida:
    def analisar_rapido(self, dados):
        rsi = dados.get('rsi', 50.0)
        tendencia = dados.get('tendencia', 'lateral')
        volatilidade = dados.get('volatilidade', 0.02)
        
        # Lógica simples e rápida
        if rsi < 30:
            return {'decisao': 'comprar', 'confianca': 0.7, 'razao': f'RSI sobrevendido ({rsi:.1f})'}
        elif rsi > 70:
            return {'decisao': 'vender', 'confianca': 0.7, 'razao': f'RSI sobrecomprado ({rsi:.1f})'}
        elif tendencia == 'alta' and rsi < 60:
            return {'decisao': 'comprar', 'confianca': 0.6, 'razao': f'Tendência alta ({rsi:.1f})'}
        elif tendencia == 'baixa' and rsi > 40:
            return {'decisao': 'vender', 'confianca': 0.6, 'razao': f'Tendência baixa ({rsi:.1f})'}
        else:
            return {'decisao': 'aguardar', 'confianca': 0.3, 'razao': 'Condições neutras'}
```

#### 5.2 Estratégia de Fallback
```python
def analisar_com_fallback(self, dados):
    # Tentar IA principal com timeout reduzido
    try:
        decisao = self.ia_principal.analisar_dados_mercado(dados, timeout=10)
        if decisao:
            return decisao
    except TimeoutError:
        pass
    
    # Fallback para análise técnica rápida
    return self.analise_tecnica_rapida.analisar_rapido(dados)
```

**Benefícios:**
- ⚡ Resposta garantida em < 1 segundo
- 🎯 Decisões baseadas em indicadores técnicos
- 📊 Redução de 90% nos timeouts

---

## 📊 Análise de Impacto

### Melhorias Esperadas

| Métrica | Atual | Otimizado | Melhoria |
|---------|-------|-----------|----------|
| Tempo de Inferência | 60s | 5-15s | **75-92%** |
| Timeouts | 15% | <5% | **67%** |
| Throughput | 1 decisão/min | 4+ decisões/min | **300%** |
| Cache Hit Rate | 0% | 40-60% | **N/A** |
| Uso de Memória | 4.9GB | 1-2GB | **60-80%** |

### Análise de Risco

#### Riscos Baixos
- ✅ **Qualidade:** Modelos menores mantêm qualidade para trading
- ✅ **Compatibilidade:** Mudanças são transparentes para o usuário
- ✅ **Reversibilidade:** Sistema pode voltar ao modelo anterior

#### Riscos Médios
- ⚠️ **Cache:** Possível inconsistência em cenários muito voláteis
- ⚠️ **Fallback:** Análise técnica pode ser menos sofisticada

#### Mitigações
- 🔄 **Cache TTL:** 30 segundos para dados frescos
- 🎯 **A/B Testing:** Comparar performance antes/after
- 📊 **Monitoramento:** Métricas em tempo real

---

## 🛠️ Plano de Implementação

### Fase 1: Otimizações Básicas (1-2 dias)
1. **Configurar modelo mais rápido**
   ```bash
   ollama pull phi3:mini
   ```

2. **Implementar prompt otimizado**
   - Reduzir prompt de 500 para 100 caracteres
   - Testar com dados reais

3. **Reduzir timeout**
   - Mudar de 60s para 15s
   - Monitorar impactos

### Fase 2: Cache e Fallback (2-3 dias)
1. **Implementar cache de decisões**
   - Cache com TTL de 30 segundos
   - Testar hit rate

2. **Sistema de fallback**
   - Análise técnica rápida
   - Integração com pipeline principal

### Fase 3: Processamento Paralelo (3-4 dias)
1. **Análise simultânea de pares**
   - ThreadPoolExecutor
   - Testes de concorrência

2. **Cache de aprendizado**
   - Cache de recomendações
   - Otimização de consultas ao banco

### Fase 4: Otimizações Avançadas (4-5 dias)
1. **Fine-tuning do modelo**
   - Treinar em dados específicos de trading
   - Otimizar para prompts curtos

2. **Sistema de métricas**
   - Dashboard de performance
   - Alertas automáticos

---

## 📈 Métricas de Monitoramento

### Métricas em Tempo Real
```python
class MetricasIA:
    def __init__(self):
        self.tempos_inferencia = []
        self.timeouts = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    def registrar_inferencia(self, tempo, timeout=False, cache_hit=False):
        self.tempos_inferencia.append(tempo)
        if timeout:
            self.timeouts += 1
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def obter_estatisticas(self):
        return {
            'tempo_medio': np.mean(self.tempos_inferencia[-100:]),
            'timeout_rate': self.timeouts / max(1, len(self.tempos_inferencia)),
            'cache_hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        }
```

### Alertas Automáticos
- 🔴 **Timeout Rate > 10%**
- 🟡 **Tempo médio > 20s**
- 🟢 **Cache hit rate < 30%**

---

## 💰 Análise de Custo-Benefício

### Custos de Implementação
- **Tempo de desenvolvimento:** 10-15 dias
- **Testes e validação:** 5 dias
- **Riscos:** Baixos (reversível)

### Benefícios Esperados
- **Velocidade:** 75-92% mais rápido
- **Oportunidades:** 3-4x mais decisões/minuto
- **Confiabilidade:** Redução de 67% em timeouts
- **Recursos:** 60-80% menos uso de memória

### ROI Estimado
- **Investimento:** 15-20 dias de desenvolvimento
- **Retorno:** Melhoria imediata na performance
- **Payback:** Instantâneo (redução de timeouts)

---

## 🎯 Critérios de Sucesso

### Critérios Primários
- ✅ **Tempo de inferência < 15s** (média)
- ✅ **Timeout rate < 5%**
- ✅ **Throughput > 4 decisões/minuto**
- ✅ **Cache hit rate > 40%**

### Critérios Secundários
- ✅ **Acertividade mantida ou melhorada**
- ✅ **Uso de memória reduzido em 60%**
- ✅ **Zero regressões funcionais**

### Critérios de Aceitação
- ✅ **Testes passando 100%**
- ✅ **Performance validada em produção**
- ✅ **Documentação atualizada**

---

## 📋 Checklist de Implementação

### Preparação
- [ ] Backup do sistema atual
- [ ] Configuração de ambiente de teste
- [ ] Definição de métricas baseline

### Implementação
- [ ] Instalar modelo mais rápido
- [ ] Implementar prompt otimizado
- [ ] Reduzir timeout
- [ ] Implementar cache de decisões
- [ ] Sistema de fallback
- [ ] Processamento paralelo
- [ ] Cache de aprendizado

### Validação
- [ ] Testes de performance
- [ ] Testes de qualidade
- [ ] Testes de stress
- [ ] Validação em produção

### Monitoramento
- [ ] Dashboard de métricas
- [ ] Alertas automáticos
- [ ] Logs detalhados
- [ ] Relatórios de performance

---

## 🔄 Próximos Passos

1. **Aprovação do PRD**
2. **Definição de timeline**
3. **Alocação de recursos**
4. **Início da implementação**
5. **Testes e validação**
6. **Deploy em produção**

---

## 📞 Contatos

**Responsável Técnico:** Equipe de IA  
**Stakeholders:** Equipe de Trading, DevOps  
**Revisão:** Semanal durante implementação  

---

*Este PRD será revisado e atualizado conforme necessário durante a implementação.* 