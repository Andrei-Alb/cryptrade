"""
Analisador de IA para Robô de Trading
Integra com sistema de IA local usando Ollama
"""

import logging
from typing import Dict, Any, Optional
from ia.cursor_ai_client import CursorAITradingClient
from ia.preparador_dados import PreparadorDadosIA
from ia.decisor import DecisorIA
from config import load_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalisadorIA:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa analisador de IA
        
        Args:
            config: Configurações do sistema
        """
        self.config = config if config is not None else load_config()
        
        # Inicializar componentes
        self.cliente_ia = CursorAITradingClient(
            model_name=self.config.get('ia', {}).get('modelo', 'llama3.1:8b')
        )
        self.preparador = PreparadorDadosIA()
        # Passar string de configuração em vez de dict
        self.decisor = DecisorIA("config.yaml")
        
        logger.info("Analisador de IA inicializado")
    
    def analisar_com_ia(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa dados de mercado usando IA
        
        Args:
            dados: Dados de mercado para análise
            
        Returns:
            Decisão de trading processada
        """
        try:
            logger.info(f"Iniciando análise IA para ativo: {dados.get('simbolo', 'N/A')}")
            
            # 1. Preparar dados para IA
            dados_preparados = self.preparador.preparar_dados_analise(dados)
            logger.info("Dados preparados para análise")
            
            # 2. Analisar com IA
            decisao_ia = self.cliente_ia.analisar_dados_mercado(dados_preparados)
            logger.info(f"Análise IA concluída: {decisao_ia['decisao']}")
            
            # 3. Processar decisão e aplicar filtros
            decisao_final = self.decisor.processar_decisao_ia(decisao_ia, dados_preparados)
            
            # 4. Verificar se decisao_final não é None antes de acessar
            if decisao_final is None:
                logger.error("Decisão final é None, retornando decisão de erro")
                return self._decisao_erro(dados)
            
            # 5. Adicionar metadados
            decisao_final['timestamp'] = dados_preparados.get('timestamp')
            decisao_final['ativo'] = dados.get('simbolo') or dados_preparados.get('ativo', 'WINZ25')
            decisao_final['preco_analise'] = dados.get('preco_atual') or dados_preparados.get('preco_atual', 0.0)
            
            logger.info(f"Análise completa: {decisao_final['decisao']} "
                       f"(confiança: {decisao_final['confianca']:.2f})")
            
            return decisao_final
            
        except Exception as e:
            logger.error(f"Erro na análise IA: {e}")
            return self._decisao_erro(dados)
    
    def _decisao_erro(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retorna decisão de erro
        """
        return {
            "decisao": "aguardar",
            "confianca": 0.0,
            "razao": "Erro na análise de IA",
            "parametros": {
                "quantidade": 1,
                "stop_loss": 100,
                "take_profit": 200
            },
            "indicadores_analisados": ["rsi", "macd", "bollinger", "media_movel", "volume", "tendencia"],
            "timestamp": None,
            "ativo": dados.get('simbolo') or 'WINZ25',
            "preco_analise": dados.get('preco_atual', 0.0)
        }
    
    def testar_conexao(self) -> bool:
        """
        Testa conexão com Ollama
        """
        return self.cliente_ia.testar_conexao()
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema
        """
        return self.decisor.obter_metricas()

# Função de compatibilidade com código existente
def analisar_com_ia(dados: Dict[str, Any], ordem_aberta: bool = False) -> Dict[str, Any]:
    """
    Função de compatibilidade para código existente, agora aceita ordem_aberta.
    
    Args:
        dados: Dados de mercado
        ordem_aberta: True se já houver ordem ativa para o símbolo
    Returns:
        Decisão de trading
    """
    analisador = AnalisadorIA()
    return analisador.analisar_com_ia(dados) 