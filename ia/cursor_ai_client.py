"""
Cliente para integração com Cursor AI usando Ollama
Analisa dados de trading usando modelos locais
"""

import requests
import json
import time
from typing import Dict, Any
from loguru import logger
from datetime import datetime

class CursorAITradingClient:
    def __init__(self, model_name: str = "llama2:7b-chat"):
        """
        Inicializa cliente de IA para trading
        
        Args:
            model_name: Nome do modelo Ollama a ser usado
        """
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434"
        self.max_retries = 3
        self.timeout = 60  # Aumentar de 30 para 60 segundos
        self.fallback_mode = True  # Ativar modo de análise técnica simples por padrão
        
        # Verificar se Ollama está rodando
        self._verificar_ollama()
    
    def _verificar_ollama(self):
        """Verifica se Ollama está rodando e modelo está disponível"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.model_name not in model_names:
                    logger.warning(f"Modelo {self.model_name} não encontrado. Modelos disponíveis: {model_names}")
                    # Usar primeiro modelo disponível como fallback
                    if model_names:
                        self.model_name = model_names[0]
                        logger.info(f"Usando modelo fallback: {self.model_name}")
                else:
                    logger.info(f"Modelo {self.model_name} disponível")
            else:
                logger.error("Não foi possível conectar ao Ollama")
                
        except Exception as e:
            logger.error(f"Erro ao verificar Ollama: {e}")
    
    def analisar_dados_mercado(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa dados de mercado usando IA local ou análise técnica simples
        
        Args:
            dados: Dicionário com dados de mercado
            
        Returns:
            Dicionário com decisão de trading
        """
        try:
            # Se estiver em modo fallback, usar análise técnica simples
            if self.fallback_mode:
                logger.info("Usando análise técnica simples (modo fallback)")
                return self._analise_tecnica_simples(dados)
            
            # Preparar prompt estruturado
            prompt = self._criar_prompt_trading(dados)
            
            # Enviar para Ollama
            resposta = self._enviar_para_ollama(prompt)
            
            # Processar resposta
            decisao = self._processar_resposta(resposta)
            
            logger.info(f"Análise IA concluída: {decisao['decisao']} (confiança: {decisao['confianca']})")
            return decisao
            
        except Exception as e:
            logger.error(f"Erro na análise IA: {e}")
            logger.info("Ativando modo fallback - usando análise técnica simples")
            self.fallback_mode = True
            return self._analise_tecnica_simples(dados)
    
    def _criar_prompt_trading(self, dados: Dict[str, Any]) -> str:
        """
        Cria prompt estruturado para análise de trading
        """
        # Calcular indicadores técnicos se não estiverem presentes
        dados = self._calcular_indicadores(dados)

        # Garantir preenchimento seguro dos campos
        safe = lambda v, default: v if v not in [None, '', [], 'N/A'] else default
        dados['ativo'] = safe(dados.get('ativo'), 'WINZ25')
        dados['preco_atual'] = safe(dados.get('preco_atual'), 0.0)
        dados['bid'] = safe(dados.get('bid'), 0.0)
        dados['ask'] = safe(dados.get('ask'), 0.0)
        dados['volume'] = safe(dados.get('volume'), 0)
        dados['variacao'] = safe(dados.get('variacao'), 0.0)
        dados['rsi'] = safe(dados.get('rsi'), 50.0)
        dados['macd'] = safe(dados.get('macd'), 0.0)
        dados['macd_signal'] = safe(dados.get('macd_signal'), 0.0)
        dados['bb_upper'] = safe(dados.get('bb_upper'), dados['preco_atual'] * 1.02)
        dados['bb_lower'] = safe(dados.get('bb_lower'), dados['preco_atual'] * 0.98)
        dados['ma_20'] = safe(dados.get('ma_20'), dados['preco_atual'])
        dados['ma_50'] = safe(dados.get('ma_50'), dados['preco_atual'])
        dados['volatilidade'] = safe(dados.get('volatilidade'), 0.0)
        dados['volume_medio'] = safe(dados.get('volume_medio'), 0.0)
        dados['tendencia'] = safe(dados.get('tendencia'), 'lateral')
        dados['historico_precos'] = safe(dados.get('historico_precos'), [dados['preco_atual']])
        dados['dia_semana'] = safe(dados.get('dia_semana'), 'N/A')
        dados['hora'] = safe(dados.get('hora'), 'N/A')
        dados['timestamp'] = safe(dados.get('timestamp'), datetime.now().isoformat())
        
        return f"""Você é um analista de trading especializado em mini-índice (WIN) na B3. Analise os dados e tome uma decisão de trading, atribuindo um nível de confiança (0 a 1) que reflita o quão forte e claro é o sinal, de acordo com os indicadores e contexto. Seja honesto: confiança alta só se o sinal for realmente forte, mas use valores intermediários se o cenário for incerto ou misto. Isso é fundamental para o aprendizado da IA.

DADOS ATUAIS:
- Ativo: {dados.get('ativo', 'WINZ25')}
- Preço: {dados.get('preco_atual', 'N/A')}
- Variação: {dados.get('variacao', 'N/A')}%

INDICADORES:
- RSI: {dados.get('rsi', 'N/A')} {'(SOBRECOMPRA)' if dados.get('rsi', 50) > 70 else '(SOBREVENDA)' if dados.get('rsi', 50) < 30 else '(NEUTRO)'}
- MACD: {dados.get('macd', 'N/A')}
- Bollinger Superior: {dados.get('bb_upper', 'N/A')}
- Bollinger Inferior: {dados.get('bb_lower', 'N/A')}
- MM20: {dados.get('ma_20', 'N/A')}
- MM50: {dados.get('ma_50', 'N/A')}
- Tendência: {dados.get('tendencia', 'N/A')}

REGRAS DE DECISÃO:
- COMPRAR: Se houver sinais claros de compra (ex: 2 ou mais indicadores alinhados para compra).
- VENDER: Se houver sinais claros de venda (ex: 2 ou mais indicadores alinhados para venda).
- AGUARDAR: Se o cenário for incerto, misto ou sem sinais claros.

NÍVEIS DE CONFIANÇA:
- 0.8-1.0: Sinais muito fortes, claros e alinhados.
- 0.5-0.8: Sinais razoáveis, mas com alguma incerteza.
- 0.2-0.5: Sinais fracos ou mistos, cenário incerto.
- <0.2: Praticamente nenhum sinal, mercado sem direção.

IMPORTANTE:
- A confiança deve ser calibrada de acordo com a clareza dos sinais, não binarize.
- O objetivo é permitir que a IA aprenda com acertos e erros em todos os níveis de confiança.
- Responda APENAS em JSON:
{{
  "decisao": "comprar|vender|aguardar",
  "confianca": 0.0-1.0,
  "razao": "explicação detalhada da decisão baseada nos indicadores",
  "parametros": {{
    "quantidade": 1,
    "stop_loss": 100,
    "take_profit": 200
  }},
  "indicadores_analisados": ["rsi", "macd", "bollinger", "media_movel", "tendencia", "variacao"]
}}"""
    
    def _calcular_indicadores(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula indicadores técnicos se não estiverem presentes"""
        dados_calculados = dados.copy()
        
        # Calcular RSI se não estiver presente
        if 'rsi' not in dados or dados['rsi'] is None:
            # Simular RSI baseado no preço e variação
            preco = dados.get('preco_atual', 100000)
            variacao = dados.get('variacao', 0.0)
            
            if variacao > 0.5:
                rsi = 65 + (variacao * 10)  # Tendência de alta
            elif variacao < -0.5:
                rsi = 35 - (abs(variacao) * 10)  # Tendência de baixa
            else:
                rsi = 45 + (variacao * 20)  # Neutro
            
            dados_calculados['rsi'] = max(0, min(100, rsi))
        
        # Calcular MACD se não estiver presente
        if 'macd' not in dados or dados['macd'] is None:
            # Simular MACD baseado na tendência
            variacao = dados.get('variacao', 0.0)
            if variacao > 0.3:
                macd = 15 + (variacao * 20)  # Positivo para alta
            elif variacao < -0.3:
                macd = -15 + (variacao * 20)  # Negativo para baixa
            else:
                macd = variacao * 10  # Neutro
            dados_calculados['macd'] = macd
        
        # Calcular Bandas de Bollinger se não estiverem presentes
        preco = dados.get('preco_atual', 100000)
        if 'bb_upper' not in dados or dados['bb_upper'] is None:
            dados_calculados['bb_upper'] = preco * 1.005  # +0.5%
        if 'bb_lower' not in dados or dados['bb_lower'] is None:
            dados_calculados['bb_lower'] = preco * 0.995  # -0.5%
        
        # Calcular Médias Móveis se não estiverem presentes
        if 'ma_20' not in dados or dados['ma_20'] is None:
            dados_calculados['ma_20'] = preco * (1 + dados.get('variacao', 0.0) * 0.1)
        if 'ma_50' not in dados or dados['ma_50'] is None:
            dados_calculados['ma_50'] = preco * (1 + dados.get('variacao', 0.0) * 0.05)
        
        # Calcular tendência se não estiver presente
        if 'tendencia' not in dados or dados['tendencia'] is None:
            variacao = dados.get('variacao', 0.0)
            if variacao > 0.5:
                dados_calculados['tendencia'] = 'alta'
            elif variacao < -0.5:
                dados_calculados['tendencia'] = 'baixa'
            else:
                dados_calculados['tendencia'] = 'lateral'
        
        return dados_calculados
    
    def _enviar_para_ollama(self, prompt: str) -> str:
        """
        Envia prompt para Ollama e retorna resposta
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Baixa temperatura para decisões mais consistentes
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        for tentativa in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()['response']
                else:
                    logger.warning(f"Tentativa {tentativa + 1}: Status {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"Tentativa {tentativa + 1} falhou: {e}")
                if tentativa < self.max_retries - 1:
                    time.sleep(1)
        
        raise Exception("Falha ao comunicar com Ollama após todas as tentativas")
    
    def _processar_resposta(self, resposta: str) -> Dict[str, Any]:
        """
        Processa resposta da IA e extrai decisão
        """
        try:
            # Tentar extrair JSON da resposta
            json_start = resposta.find('{')
            json_end = resposta.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = resposta[json_start:json_end]
                decisao = json.loads(json_str)
                
                # Validar formato da resposta
                if self._validar_resposta(decisao):
                    return decisao
            
            # Se não conseguir extrair JSON válido, usar fallback
            logger.warning("Resposta da IA não contém JSON válido, usando fallback")
            return self._decisao_fallback()
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da IA: {e}")
            return self._decisao_fallback()
    
    def _validar_resposta(self, resposta: Dict[str, Any]) -> bool:
        """
        Valida se a resposta da IA está no formato correto
        """
        campos_obrigatorios = ['decisao', 'confianca', 'razao', 'parametros']
        
        for campo in campos_obrigatorios:
            if campo not in resposta:
                return False
        
        # Validar valores
        if resposta['decisao'] not in ['comprar', 'vender', 'aguardar']:
            return False
        
        if not isinstance(resposta['confianca'], (int, float)) or not 0 <= resposta['confianca'] <= 1:
            return False
        
        return True
    
    def _decisao_fallback(self) -> Dict[str, Any]:
        """
        Retorna decisão de fallback em caso de erro
        """
        return {
            "decisao": "aguardar",
            "confianca": 0.0,
            "razao": "Erro na análise de IA - usando fallback",
            "parametros": {
                "quantidade": 1,
                "stop_loss": 100,
                "take_profit": 200
            },
            "indicadores_analisados": []
        }
    
    def _analise_tecnica_simples(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise técnica simples como fallback quando IA não está disponível
        """
        try:
            # Extrair indicadores
            rsi = dados.get('rsi', 50.0)
            macd = dados.get('macd', 0.0)
            preco_atual = dados.get('preco_atual', 100000)
            bb_upper = dados.get('bb_upper', preco_atual * 1.005)
            bb_lower = dados.get('bb_lower', preco_atual * 0.995)
            
            # Calcular variação a partir dos dados disponíveis
            preco_abertura = dados.get('preco_abertura', preco_atual)
            if preco_abertura and preco_abertura > 0:
                variacao = ((preco_atual - preco_abertura) / preco_abertura) * 100
            else:
                # Se não tiver preço de abertura, usar variação simulada baseada no preço
                variacao = (preco_atual - 136500) / 136500 * 100  # Variação em relação a um preço base
            
            # Calcular sinais
            sinais_compra = 0
            sinais_venda = 0
            confianca = 0.0
            razao = []
            
            # RSI (MUITO AGGRESSIVO)
            if rsi < 45:
                sinais_compra += 1
                razao.append("RSI sobrecompra")
                confianca += 0.3
            elif rsi > 55:
                sinais_venda += 1
                razao.append("RSI sobrevenda")
                confianca += 0.3
            
            # MACD (MUITO AGGRESSIVO)
            if macd > 1:
                sinais_compra += 1
                razao.append("MACD positivo")
                confianca += 0.25
            elif macd < -1:
                sinais_venda += 1
                razao.append("MACD negativo")
                confianca += 0.25
            
            # Bandas de Bollinger (MUITO AGGRESSIVO)
            if preco_atual <= bb_lower * 1.01:  # Próximo à banda inferior
                sinais_compra += 1
                razao.append("Próximo à banda inferior")
                confianca += 0.2
            elif preco_atual >= bb_upper * 0.99:  # Próximo à banda superior
                sinais_venda += 1
                razao.append("Próximo à banda superior")
                confianca += 0.2
            
            # Variação (MUITO AGGRESSIVO)
            if variacao > 0.05:
                sinais_compra += 1
                razao.append("Tendência de alta")
                confianca += 0.15
            elif variacao < -0.05:
                sinais_venda += 1
                razao.append("Tendência de baixa")
                confianca += 0.15
            
            # Determinar decisão (MUITO AGGRESSIVO)
            if sinais_compra > sinais_venda and confianca >= 0.2 and sinais_compra >= 2:
                decisao = "comprar"
            elif sinais_venda > sinais_compra and confianca >= 0.2 and sinais_venda >= 2:
                decisao = "vender"
            else:
                decisao = "aguardar"
                confianca = max(0.1, confianca * 0.5)  # Reduzir confiança para aguardar
            
            return {
                "decisao": decisao,
                "confianca": min(0.9, confianca),  # Limitar confiança máxima
                "razao": " | ".join(razao) if razao else "Análise técnica simples",
                "parametros": {
                    "quantidade": 1,
                    "stop_loss": 100,
                    "take_profit": 200
                },
                "indicadores_analisados": ["rsi", "macd", "bollinger", "variacao"]
            }
            
        except Exception as e:
            logger.error(f"Erro na análise técnica simples: {e}")
            return self._decisao_fallback()
    
    def testar_conexao(self) -> bool:
        """
        Testa conexão com Ollama
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False 