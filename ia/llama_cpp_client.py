import json
import logging
import subprocess
from typing import Dict, Any, Optional
import hashlib
import time

logger = logging.getLogger(__name__)

class LlamaCppClient:
    def __init__(self, model_path: str = "phi3:mini", timeout: int = 45, cache_ttl: int = 30):
        """
        Inicializa cliente Llama usando Ollama com modelo otimizado para velocidade
        """
        self.model_name = model_path
        self.timeout = timeout
        self.cache: Dict[str, tuple] = {}  # Cache simples para decisões
        self.cache_ttl = cache_ttl  # TTL configurável
        logger.info(f"[IA] Cliente Llama otimizado inicializado com modelo: {self.model_name} (timeout: {self.timeout}s, cache_ttl: {self.cache_ttl}s)")
    
    def _criar_prompt_trading_otimizado(self, dados: Dict[str, Any]) -> str:
        """Prompt otimizado para resposta preditiva e inteligente"""
        rsi = dados.get('rsi', 50.0)
        tendencia = dados.get('tendencia', 'lateral')
        volatilidade = dados.get('volatilidade', 0.02)
        preco = dados.get('preco_atual', 0.0)
        symbol = dados.get('symbol', 'BTCUSDT')
        volume_info = ""
        if 'volume_24h' in dados:
            volume_info = f", Volume24h={dados['volume_24h']:.0f}"
        
        return f"""ANÁLISE TÉCNICA PREDITIVA - {symbol}
Dados: RSI={rsi:.1f}, Tendência={tendencia}, Volatilidade={volatilidade:.4f}, Preço=${preco:.2f}{volume_info}

REGRAS:
- Preveja o próximo movimento provável do preço.
- Defina um alvo de saída (take profit) baseado na previsão.
- Defina um stop loss inicial para proteção.
- Explique cenários de permanência e saída.
- Justifique a previsão com base nos indicadores.

IMPORTANTE: Responda APENAS com JSON válido, usando valores numéricos para previsao_alvo e stop_loss.

RESPONDA APENAS COM JSON VÁLIDO:
{{
  "decisao": "comprar|vender|aguardar",
  "confianca": 0.0-1.0,
  "previsao_alvo": valor_numérico_do_alvo,
  "stop_loss": valor_numérico_do_stop,
  "cenario_permanencia": "explicação curta de quando permanecer",
  "cenario_saida": "explicação curta de quando sair",
  "razao": "justificativa técnica concisa"
}}"""

    def _gerar_cache_key(self, dados: Dict[str, Any]) -> str:
        """Gera chave de cache baseada nos dados essenciais"""
        dados_essenciais = {
            'rsi': round(dados.get('rsi', 50.0), 1),
            'tendencia': dados.get('tendencia', 'lateral'),
            'volatilidade': round(dados.get('volatilidade', 0.02), 3),
            'preco': round(dados.get('preco_atual', 0.0), 2)
        }
        return hashlib.md5(json.dumps(dados_essenciais, sort_keys=True).encode()).hexdigest()

    def _verificar_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Verifica se existe decisão em cache"""
        if cache_key in self.cache:
            timestamp, decisao = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"[IA] Usando decisão do cache")
                return decisao
            else:
                del self.cache[cache_key]
        return None

    def _salvar_cache(self, cache_key: str, decisao: Dict[str, Any]):
        """Salva decisão no cache"""
        self.cache[cache_key] = (time.time(), decisao)

    def _processar_resposta(self, resposta_bruta: str) -> Optional[Dict[str, Any]]:
        """
        Processa resposta do modelo e extrai JSON válido
        """
        if not resposta_bruta or not resposta_bruta.strip():
            logger.error("[IA] Resposta vazia do modelo")
            return None
        
        # Limpar resposta
        resposta_limpa = resposta_bruta.strip()
        
        # Procurar por JSON válido
        try:
            # Tentar encontrar JSON entre { e }
            inicio = resposta_limpa.find('{')
            fim = resposta_limpa.rfind('}')
            
            if inicio != -1 and fim != -1 and fim > inicio:
                json_str = resposta_limpa[inicio:fim+1]
                resultado = json.loads(json_str)
                logger.info(f"[IA] JSON extraído com sucesso: {resultado}")
                return resultado
            else:
                logger.error(f"[IA] Nenhum JSON válido encontrado na resposta: {resposta_limpa}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"[IA] Erro ao decodificar JSON: {e}")
            logger.error(f"[IA] Resposta problemática: {resposta_limpa}")
            return None
        except Exception as e:
            logger.error(f"[IA] Erro inesperado ao processar resposta: {e}")
            return None

    def _converter_para_serializavel(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Converte dados para formato serializável em JSON"""
        try:
            dados_serializaveis = {}
            for key, value in dados.items():
                if hasattr(value, 'to_dict'):
                    dados_serializaveis[key] = value.to_dict()
                elif isinstance(value, (dict, list, str, int, float, bool)):
                    dados_serializaveis[key] = value
                else:
                    dados_serializaveis[key] = str(value)
            return dados_serializaveis
        except Exception as e:
            logger.error(f"[IA] Erro ao converter dados: {e}")
            return dados

    def _extrair_json(self, texto: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON válido do texto de resposta"""
        try:
            # Procurar por JSON no texto
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, texto)
            
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"[IA] Erro ao extrair JSON: {e}")
            return None

    def _validar_e_normalizar_decisao(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e normaliza os valores da decisão da IA"""
        try:
            # Normalizar confiança
            confianca = decisao.get('confianca', 0.5)
            confianca = max(0.1, min(1.0, float(confianca)))
            
            # Normalizar quantidade
            quantidade = decisao.get('quantidade', 1)
            quantidade = max(1, min(10, int(quantidade)))
            
            # Normalizar stop loss (entre -5% e -1%)
            stop_loss = decisao.get('stop_loss', -2.0)
            if isinstance(stop_loss, str):
                stop_loss = stop_loss.replace('$', '').replace('%', '').replace(',', '.').strip()
                try:
                    stop_loss = float(stop_loss)
                except Exception:
                    stop_loss = -2.0
            stop_loss = max(-5.0, min(-1.0, float(stop_loss)))
            
            # Normalizar take profit (entre +1% e +10%)
            take_profit = decisao.get('take_profit', 3.0)
            if isinstance(take_profit, str):
                take_profit = take_profit.replace('$', '').replace('%', '').replace(',', '.').strip()
                try:
                    take_profit = float(take_profit)
                except Exception:
                    take_profit = 3.0
            take_profit = max(1.0, min(10.0, float(take_profit)))
            
            return {
                'decisao': decisao.get('decisao', 'aguardar'),
                'confianca': confianca,
                'razao': decisao.get('razao', 'Análise técnica'),
                'quantidade': quantidade,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'acao_ordem': decisao.get('acao_ordem', 'manter')
            }
        except Exception as e:
            logger.error(f"[IA] Erro ao validar decisão: {e}")
            return {
                'decisao': 'aguardar',
                'confianca': 0.5,
                'razao': 'Erro na validação',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.0,
                'acao_ordem': 'manter'
            }

    def _analise_tecnica_fallback(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Análise técnica inteligente como fallback quando IA falha"""
        rsi = dados.get('rsi', 50.0)
        tendencia = dados.get('tendencia', 'lateral')
        volatilidade = dados.get('volatilidade', 0.02)
        symbol = dados.get('symbol', 'BTCUSDT')
        
        # Verificar condições de mercado desfavoráveis
        if volatilidade < 0.005:
            return {
                'decisao': 'aguardar',
                'confianca': 0.0,
                'razao': f'Volatilidade muito baixa ({volatilidade:.4f})',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.0,
                'acao_ordem': 'manter'
            }
        
        if volatilidade > 0.05:
            return {
                'decisao': 'aguardar',
                'confianca': 0.0,
                'razao': f'Volatilidade muito alta ({volatilidade:.4f})',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.0,
                'acao_ordem': 'manter'
            }
        
        # Lógica de trading baseada em RSI e tendência
        if rsi < 25:  # Extremamente sobrevendido
            return {
                'decisao': 'comprar',
                'confianca': 0.85,
                'razao': f'RSI extremamente sobrevendido ({rsi:.1f})',
                'quantidade': 2,
                'stop_loss': -1.5,
                'take_profit': 4.0,
                'acao_ordem': 'manter'
            }
        elif rsi < 30:  # Sobrevendido
            if tendencia == 'baixa':
                return {
                    'decisao': 'aguardar',
                    'confianca': 0.3,
                    'razao': f'RSI sobrevendido mas tendência baixa ({rsi:.1f})',
                    'quantidade': 1,
                    'stop_loss': -2.0,
                    'take_profit': 3.0,
                    'acao_ordem': 'manter'
                }
            else:
                return {
                    'decisao': 'comprar',
                    'confianca': 0.75,
                    'razao': f'RSI sobrevendido com tendência favorável ({rsi:.1f})',
                    'quantidade': 2,
                    'stop_loss': -2.0,
                    'take_profit': 4.0,
                    'acao_ordem': 'manter'
                }
        elif rsi > 75:  # Extremamente sobrecomprado
            return {
                'decisao': 'vender',
                'confianca': 0.85,
                'razao': f'RSI extremamente sobrecomprado ({rsi:.1f})',
                'quantidade': 2,
                'stop_loss': -1.5,
                'take_profit': 4.0,
                'acao_ordem': 'manter'
            }
        elif rsi > 70:  # Sobrecomprado
            if tendencia == 'alta':
                return {
                    'decisao': 'aguardar',
                    'confianca': 0.3,
                    'razao': f'RSI sobrecomprado mas tendência alta ({rsi:.1f})',
                    'quantidade': 1,
                    'stop_loss': -2.0,
                    'take_profit': 3.0,
                    'acao_ordem': 'manter'
                }
            else:
                return {
                    'decisao': 'vender',
                    'confianca': 0.75,
                    'razao': f'RSI sobrecomprado com tendência favorável ({rsi:.1f})',
                    'quantidade': 2,
                    'stop_loss': -2.0,
                    'take_profit': 4.0,
                    'acao_ordem': 'manter'
                }
        elif tendencia == 'alta' and 40 <= rsi <= 60:
            return {
                'decisao': 'comprar',
                'confianca': 0.65,
                'razao': f'Tendência alta com RSI neutro ({rsi:.1f})',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.5,
                'acao_ordem': 'manter'
            }
        elif tendencia == 'baixa' and 40 <= rsi <= 60:
            return {
                'decisao': 'vender',
                'confianca': 0.65,
                'razao': f'Tendência baixa com RSI neutro ({rsi:.1f})',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.5,
                'acao_ordem': 'manter'
            }
        else:
            # Mercado lateral ou condições neutras
            return {
                'decisao': 'aguardar',
                'confianca': 0.2,
                'razao': f'Condições neutras - RSI: {rsi:.1f}, Tendência: {tendencia}',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.0,
                'acao_ordem': 'manter'
            }

    def _extrair_json_melhorado(self, texto: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON válido do texto de resposta com múltiplas estratégias"""
        if not texto or not texto.strip():
            return None
        
        texto_limpo = texto.strip()
        
        # Estratégia 1: Procurar JSON completo entre { e }
        try:
            import re
            # Padrão mais robusto para encontrar JSON
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, texto_limpo)
            
            for match in matches:
                try:
                    resultado = json.loads(match)
                    if isinstance(resultado, dict) and 'decisao' in resultado:
                        logger.info(f"[IA] JSON extraído com sucesso: {resultado}")
                        return resultado
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.debug(f"[IA] Erro na estratégia 1: {e}")
        
        # Estratégia 2: Procurar por chaves específicas
        try:
            # Tentar encontrar decisão e confiança no texto
            decisao_match = re.search(r'"decisao"\s*:\s*"([^"]+)"', texto_limpo, re.IGNORECASE)
            confianca_match = re.search(r'"confianca"\s*:\s*([0-9.]+)', texto_limpo, re.IGNORECASE)
            razao_match = re.search(r'"razao"\s*:\s*"([^"]+)"', texto_limpo, re.IGNORECASE)
            
            if decisao_match:
                decisao = decisao_match.group(1).lower()
                confianca = float(confianca_match.group(1)) if confianca_match else 0.5
                razao = razao_match.group(1) if razao_match else "Análise técnica"
                
                resultado = {
                    'decisao': decisao,
                    'confianca': confianca,
                    'razao': razao,
                    'quantidade': 1,
                    'stop_loss': -2.0,
                    'take_profit': 3.0,
                    'acao_ordem': 'manter'
                }
                logger.info(f"[IA] JSON extraído por regex: {resultado}")
                return resultado
        except Exception as e:
            logger.debug(f"[IA] Erro na estratégia 2: {e}")
        
        # Estratégia 3: Procurar por palavras-chave simples
        try:
            texto_lower = texto_limpo.lower()
            if 'comprar' in texto_lower:
                decisao = 'comprar'
            elif 'vender' in texto_lower:
                decisao = 'vender'
            else:
                decisao = 'aguardar'
            
            # Extrair confiança se possível
            confianca_match = re.search(r'confiança?\s*:?\s*([0-9.]+)', texto_lower)
            confianca = float(confianca_match.group(1)) if confianca_match else 0.5
            
            resultado = {
                'decisao': decisao,
                'confianca': confianca,
                'razao': 'Análise por palavras-chave',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.0,
                'acao_ordem': 'manter'
            }
            logger.info(f"[IA] JSON extraído por palavras-chave: {resultado}")
            return resultado
        except Exception as e:
            logger.debug(f"[IA] Erro na estratégia 3: {e}")
        
        return None

    def analisar_dados_mercado(self, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analisa dados de mercado e retorna decisão da IA - VERSÃO OTIMIZADA"""
        try:
            # Verificar cache primeiro
            cache_key = self._gerar_cache_key(dados)
            decisao_cache = self._verificar_cache(cache_key)
            if decisao_cache:
                return decisao_cache

            # Converter dados para formato serializável
            dados_serializaveis = self._converter_para_serializavel(dados)
            
            # PROMPT OTIMIZADO - muito mais conciso (80% menor)
            prompt = self._criar_prompt_trading_otimizado(dados_serializaveis)
            
            logger.info(f"[IA] Prompt enviado ao modelo:\n{prompt}")
            logger.info(f"[IA] Enviando prompt otimizado para modelo {self.model_name}")
            
            # Executar comando ollama com timeout REDUZIDO (60s → 15s)
            resultado = subprocess.run(
                ['ollama', 'run', self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout  # Aumentado para 30 segundos
            )
            
            if resultado.returncode != 0:
                logger.error(f"[IA] Erro ao executar Ollama: {resultado.stderr}")
                return None
                
            resposta_bruta = resultado.stdout.strip()
            logger.info(f"[IA] Resposta bruta do modelo: {resposta_bruta}")
            
            # Extrair JSON da resposta
            json_extraido = self._extrair_json_melhorado(resposta_bruta)
            
            if json_extraido:
                logger.info(f"[IA] JSON extraído com sucesso: {json_extraido}")
                
                # Validar e normalizar decisão
                decisao_validada = self._validar_e_normalizar_decisao(json_extraido)
                
                # Salvar no cache
                self._salvar_cache(cache_key, decisao_validada)
                
                return decisao_validada
            else:
                logger.error("[IA] Falha ao extrair JSON da IA - NENHUMA DECISÃO TOMADA")
                # NÃO USAR FALLBACK - IA deve ser a única responsável
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"[IA] Timeout ao analisar dados ({self.timeout}s) - NENHUMA DECISÃO TOMADA")
            # NÃO USAR FALLBACK - IA deve ser a única responsável
            return None
        except Exception as e:
            logger.error(f"[IA] Erro inesperado na análise: {e}")
            return None

    def limpar_cache(self):
        """Limpa o cache de decisões"""
        self.cache.clear()
        logger.info("[IA] Cache limpo")

    def obter_estatisticas_cache(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            'tamanho_cache': len(self.cache),
            'chaves_cache': list(self.cache.keys())
        } 