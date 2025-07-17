"""
Decisor de IA para Trading - VERSÃO OTIMIZADA
Processa decisões da IA com cache e métricas de performance
"""

import logging
import yaml
from typing import Dict, Any, Optional
from .llama_cpp_client import LlamaCppClient
from .metricas_ia import MetricasIA
from .filtros_qualidade import FiltrosQualidade
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Decisor:
    def __init__(self, config_path: str = "config.yaml", **kwargs):
        """
        Inicializa o sistema de decisão da IA otimizado
        Aceita argumentos extras para compatibilidade (ignorados se não usados)
        """
        # Verificar se config_path é um dicionário ou string
        if isinstance(config_path, dict):
            self.config = config_path
        else:
            self.config = self._carregar_config(config_path)
        
        # Inicializar cliente IA otimizado
        modelo_principal = self.config.get('ia', {}).get('modelo_principal', 'phi3:mini')
        timeout_ia = self.config.get('ia', {}).get('timeout_inferencia', 45)
        cache_ttl = self.config.get('ia', {}).get('cache_ttl', 30)
        self.cliente_ia = LlamaCppClient(modelo_principal, timeout=timeout_ia, cache_ttl=cache_ttl)
        
        # Sistema de métricas
        self.metricas = MetricasIA()
        
        # Sistema de filtros de qualidade
        self.filtros = FiltrosQualidade()
        
        logger.info(f"[DECISOR] Sistema otimizado inicializado com modelo: {modelo_principal}")
    
    def _carregar_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"[DECISOR] Erro ao carregar config: {e}")
            return {}
    
    def _preparar_dados_simples(self, dados_mercado: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados de forma simples para IA"""
        return {
            'rsi': dados_mercado.get('rsi', 50.0),
            'tendencia': dados_mercado.get('tendencia', 'lateral'),
            'volatilidade': dados_mercado.get('volatilidade', 0.02),
            'preco_atual': dados_mercado.get('preco_atual', 0.0),
            'volume_24h': dados_mercado.get('volume_24h', 0),
            'volume_1h': dados_mercado.get('volume_1h', 0),
            'symbol': dados_mercado.get('symbol', 'BTCUSDT')
        }
    
    def analisar_mercado(self, dados_mercado: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analisa dados de mercado e retorna decisão da IA com métricas
        """
        inicio_analise = time.time()
        
        try:
            # Preparar dados de forma simples
            dados_preparados = self._preparar_dados_simples(dados_mercado)
            
            if not dados_preparados:
                logger.error("[DECISOR] Falha ao preparar dados")
                self.metricas.registrar_inferencia(0, erro=True)
                return None
            
            # Verificar cache primeiro
            cache_key = self.cliente_ia._gerar_cache_key(dados_preparados)
            decisao_cache = self.cliente_ia._verificar_cache(cache_key)
            
            if decisao_cache:
                tempo_total = time.time() - inicio_analise
                self.metricas.registrar_inferencia(tempo_total, cache_hit=True)
                logger.info(f"[DECISOR] Decisão do cache em {tempo_total:.3f}s")
                return decisao_cache
            
            # Analisar com IA
            inicio_ia = time.time()
            decisao_ia = self.cliente_ia.analisar_dados_mercado(dados_preparados)
            tempo_ia = time.time() - inicio_ia
            
            if decisao_ia:
                # Registrar métricas
                tempo_total = time.time() - inicio_analise
                self.metricas.registrar_inferencia(tempo_total, cache_hit=False)
                
                logger.info(f"[DECISOR] Decisão IA em {tempo_ia:.3f}s (total: {tempo_total:.3f}s)")
                return decisao_ia
            else:
                # Erro inesperado (não timeout, pois timeout agora usa fallback)
                tempo_total = time.time() - inicio_analise
                self.metricas.registrar_inferencia(tempo_total, erro=True)
                logger.error(f"[DECISOR] Erro inesperado na análise IA após {tempo_total:.3f}s")
                return None
                
        except Exception as e:
            tempo_total = time.time() - inicio_analise
            self.metricas.registrar_inferencia(tempo_total, erro=True)
            logger.error(f"[DECISOR] Erro na análise: {e}")
            return None
    
    def processar_decisao_ia(self, decisao: Dict[str, Any], dados_mercado: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa decisão da IA e retorna decisão final com filtros de qualidade e previsões"""
        try:
            # Validar decisão
            if not decisao or 'decisao' not in decisao:
                logger.warning("[DECISOR] Decisão inválida recebida")
                return None
            
            # Extrair previsões da IA
            previsoes = self._extrair_previsoes(decisao)
            
            # Normalizar decisão
            decisao_normalizada = {
                'decisao': decisao.get('decisao', 'aguardar'),
                'confianca': float(decisao.get('confianca', 0.5)),
                'razao': decisao.get('razao', 'Análise técnica'),
                'previsoes': previsoes,  # Incluir previsões
                'parametros': {
                    'rsi': dados_mercado.get('rsi', 50.0),
                    'volatilidade': dados_mercado.get('volatilidade', 0.02),
                    'tendencia': dados_mercado.get('tendencia', 'lateral'),
                    'preco_atual': dados_mercado.get('preco_atual', 0.0),
                    'stop_loss': previsoes.get('stop_loss', -2.0),
                    'take_profit': previsoes.get('take_profit', 3.0),
                    'quantidade': 1
                }
            }
            
            # APLICAR FILTROS DE QUALIDADE
            if decisao_normalizada['decisao'] in ['comprar', 'vender']:
                aprovado, motivo = self.filtros.verificar_qualidade_entrada(decisao_normalizada, dados_mercado)
                
                if not aprovado:
                    logger.warning(f"[DECISOR] Entrada rejeitada pelos filtros: {motivo}")
                    return {
                        'decisao': 'aguardar',
                        'confianca': 0.0,
                        'razao': f'Filtros de qualidade: {motivo}',
                        'previsoes': previsoes,
                        'parametros': decisao_normalizada['parametros']
                    }
                else:
                    logger.info(f"[DECISOR] Entrada aprovada pelos filtros: {motivo}")
            
            logger.info(f"[DECISOR] Decisão processada: {decisao_normalizada['decisao']} (confiança: {decisao_normalizada['confianca']:.2f})")
            logger.info(f"[DECISOR] Previsões: Target {previsoes.get('target', 'N/A')}, Stop {previsoes.get('stop_loss', 'N/A')}")
            return decisao_normalizada
            
        except Exception as e:
            logger.error(f"[DECISOR] Erro ao processar decisão: {e}")
            return None
    
    def _extrair_previsoes(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai previsões da resposta da IA"""
        try:
            previsoes = {
                'target': None,
                'stop_loss': None,
                'cenarios': {
                    'manter': None,
                    'sair_lucro': None,
                    'sair_perda': None
                },
                'justificativa': decisao.get('razao', 'Análise técnica')
            }
            
            # Extrair target e stop loss diretamente do JSON da IA
            previsoes['target'] = decisao.get('previsao_alvo') or decisao.get('target')
            previsoes['stop_loss'] = decisao.get('stop_loss')
            
            # Extrair cenários se presentes
            cenario_permanencia = decisao.get('cenario_permanencia')
            cenario_saida = decisao.get('cenario_saida')
            
            if cenario_permanencia:
                previsoes['cenarios']['manter'] = cenario_permanencia
            if cenario_saida:
                if 'lucro' in cenario_saida.lower() or 'alvo' in cenario_saida.lower():
                    previsoes['cenarios']['sair_lucro'] = cenario_saida
                elif 'perda' in cenario_saida.lower() or 'stop' in cenario_saida.lower():
                    previsoes['cenarios']['sair_perda'] = cenario_saida
            
            # Fallback: tentar extrair da justificativa se não encontrou nos campos diretos
            if not previsoes['target'] or not previsoes['stop_loss']:
                razao = decisao.get('razao', '')
                if 'target:' in razao.lower():
                    try:
                        import re
                        target_match = re.search(r'target[:\s]+([\d.]+)', razao, re.IGNORECASE)
                        if target_match:
                            previsoes['target'] = float(target_match.group(1))
                    except:
                        pass
                
                if 'stop:' in razao.lower():
                    try:
                        import re
                        stop_match = re.search(r'stop[:\s]+([\d.]+)', razao, re.IGNORECASE)
                        if stop_match:
                            previsoes['stop_loss'] = float(stop_match.group(1))
                    except:
                        pass
            
            return previsoes
            
        except Exception as e:
            logger.error(f"[DECISOR] Erro ao extrair previsões: {e}")
            return {
                'target': None,
                'stop_loss': None,
                'cenarios': {'manter': None, 'sair_lucro': None, 'sair_perda': None},
                'justificativa': 'Erro na extração de previsões'
            }
    
    def decidir_ordem_aberta(self, ordem: Dict[str, Any], dados_mercado: Dict[str, Any]) -> Dict[str, Any]:
        """Decide se deve manter, fechar ou ajustar uma ordem aberta"""
        try:
            # Extrair dados da ordem
            preco_entrada = ordem.get('preco_entrada', 0)
            preco_atual = dados_mercado.get('preco_atual', 0)
            tipo_ordem = ordem.get('tipo_ordem', 'compra')
            confianca_entrada = ordem.get('confianca_ia', 0.5)
            
            if preco_entrada == 0 or preco_atual == 0:
                return {'acao': 'manter', 'razao': 'Dados insuficientes'}
            
            # Calcular PnL
            if tipo_ordem == 'compra':
                pnl_percentual = ((preco_atual - preco_entrada) / preco_entrada) * 100
            else:  # venda
                pnl_percentual = ((preco_entrada - preco_atual) / preco_entrada) * 100
            
            # Análise técnica para decisão
            rsi = dados_mercado.get('rsi', 50.0)
            tendencia = dados_mercado.get('tendencia', 'lateral')
            volatilidade = dados_mercado.get('volatilidade', 0.02)
            
            # Lógica de decisão baseada em PnL e indicadores
            if pnl_percentual >= 3.0:  # Take profit atingido
                return {'acao': 'fechar', 'razao': f'Take profit atingido: {pnl_percentual:.2f}%'}
            
            elif pnl_percentual <= -2.0:  # Stop loss atingido
                return {'acao': 'fechar', 'razao': f'Stop loss atingido: {pnl_percentual:.2f}%'}
            
            # Análise de reversão de tendência
            elif tipo_ordem == 'compra' and rsi > 70 and tendencia == 'baixa':
                return {'acao': 'fechar', 'razao': f'RSI sobrecomprado ({rsi:.1f}) e tendência baixa'}
            
            elif tipo_ordem == 'venda' and rsi < 30 and tendencia == 'alta':
                return {'acao': 'fechar', 'razao': f'RSI sobrevendido ({rsi:.1f}) e tendência alta'}
            
            # Volatilidade alta - ser mais conservador
            elif volatilidade > 0.03 and abs(pnl_percentual) > 1.0:
                return {'acao': 'fechar', 'razao': f'Alta volatilidade ({volatilidade:.3f}) e PnL: {pnl_percentual:.2f}%'}
            
            # Manter ordem
            else:
                return {'acao': 'manter', 'razao': f'Condições favoráveis - PnL: {pnl_percentual:.2f}%'}
                
        except Exception as e:
            logger.error(f"[DECISOR] Erro ao decidir ordem aberta: {e}")
            return {'acao': 'manter', 'razao': f'Erro na análise: {e}'}
    
    def obter_metricas(self) -> Dict[str, Any]:
        """Retorna métricas de performance"""
        return self.metricas.obter_estatisticas()
    
    def exibir_metricas(self):
        """Exibe métricas formatadas"""
        self.metricas.exibir_estatisticas()
    
    def verificar_alertas(self) -> list:
        """Verifica alertas de performance"""
        return self.metricas.verificar_alertas()
    
    def registrar_resultado_operacao(self, symbol: str, resultado: str, lucro: float):
        """Registra resultado de uma operação para análise de performance"""
        try:
            # Registrar no sistema de filtros
            self.filtros.registrar_resultado(resultado, lucro)
            
            # Ajustar parâmetros dinamicamente
            status_filtros = self.filtros.obter_status_filtros()
            self.filtros.ajustar_parametros_dinamicos(status_filtros)
            
            logger.info(f"[DECISOR] Resultado registrado: {symbol} - {resultado} - ${lucro:.4f}")
            
        except Exception as e:
            logger.error(f"[DECISOR] Erro ao registrar resultado: {e}")
    
    def obter_status_filtros(self) -> Dict[str, Any]:
        """Retorna status dos filtros de qualidade"""
        return self.filtros.obter_status_filtros()
    
    def limpar_cache(self):
        """Limpa cache da IA"""
        self.cliente_ia.limpar_cache()
        logger.info("[DECISOR] Cache limpo")
    
    def resetar_metricas(self):
        """Reseta métricas"""
        self.metricas.resetar_metricas()
        logger.info("[DECISOR] Métricas resetadas") 

DecisorIA = Decisor 