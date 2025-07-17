"""
Sistema de Filtros de Qualidade para Trading IA - VERSÃO TOTALMENTE AUTÔNOMA
Implementa filtros mínimos para permitir que a IA aprenda com suas decisões
A IA controla TUDO: win rate, tempo de expiração, thresholds, etc.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import sqlite3
import json

logger = logging.getLogger(__name__)

class FiltrosQualidade:
    def __init__(self, db_path: str = "dados/trading.db"):
        """
        Inicializa sistema de filtros de qualidade TOTALMENTE AUTÔNOMO
        A IA controla todos os parâmetros dinamicamente
        """
        self.db_path = db_path
        
        # FILTROS MÍNIMOS ABSOLUTOS (apenas para evitar crashes)
        # A IA controla TUDO o resto dinamicamente
        self.max_ordens_simultaneas = 2  # Máximo 2 ordens por ativo (segurança)
        self.min_confianca = 0.1  # Confiança mínima 10% (muito baixa para permitir aprendizado)
        self.max_perdas_consecutivas = 50  # Máximo 50 perdas consecutivas (muito permissivo)
        self.tempo_pausa = 2  # Apenas 2 segundos de pausa (muito permissivo)
        
        # REMOVIDO: min_win_rate - A IA determina seu próprio win rate
        # REMOVIDO: tempo_estagnacao_fixo - A IA determina tempo dinamicamente
        
        # Histórico de performance
        self.ultimas_10_ordens: List[Dict[str, Any]] = []
        self.ultima_pausa: Optional[datetime] = None
        
        logger.info("[FILTROS] Sistema de filtros TOTALMENTE AUTÔNOMO inicializado")
        logger.info("[FILTROS] A IA controla: win rate, tempo de expiração, thresholds, etc.")
    
    def verificar_qualidade_entrada(self, decisao: Dict[str, Any], dados_mercado: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifica se a entrada atende aos critérios mínimos (TOTALMENTE PERMISSIVO)
        A IA controla todos os parâmetros dinamicamente
        Returns: (aprovado, motivo)
        """
        try:
            # 1. Filtro de Confiança Mínima (MUITO PERMISSIVO)
            confianca = decisao.get('confianca', 0.0)
            if confianca < self.min_confianca:
                return False, f"Confiança extremamente baixa: {confianca:.2f} < {self.min_confianca}"
            
            # 2. Filtro de Indicadores Técnicos (MÍNIMO ABSOLUTO)
            rsi = dados_mercado.get('rsi', 50.0)
            volatilidade = dados_mercado.get('volatilidade', 0.02)
            symbol = dados_mercado.get('symbol', 'BTCUSDT')
            
            # RSI em extremos MUITO extremos - evitar apenas casos extremos
            if rsi < 1 or rsi > 99:
                return False, f"RSI em extremo extremo: {rsi:.1f} (1-99)"
            
            # Volatilidade MUITO baixa - mercado completamente parado
            if volatilidade < 0.0001:
                return False, f"Volatilidade extremamente baixa: {volatilidade:.4f}"
            
            # Volatilidade MUITO alta - risco extremo
            if volatilidade > 0.20:
                return False, f"Volatilidade extremamente alta: {volatilidade:.4f}"
            
            # 3. Filtro de Ordens Simultâneas (SEGURANÇA)
            if not self._verificar_limite_ordens_permissivo(symbol):
                return False, f"Máximo de ordens atingido para {symbol}"
            
            # 4. Filtro de Performance Recente (MÍNIMO ABSOLUTO)
            if not self._verificar_performance_recente_permissivo():
                return False, "Performance extremamente baixa - pausa ativa"
            
            # 5. Filtro de Horário de Mercado (MÍNIMO)
            if not self._verificar_horario_mercado_permissivo():
                return False, "Horário de mercado muito desfavorável"
            
            # 6. Filtro de Volume (MÍNIMO)
            if not self._verificar_volume_permissivo(dados_mercado):
                return False, "Volume extremamente insuficiente"
            
            # 7. Filtro de Momentum (MÍNIMO)
            if not self._verificar_momentum_permissivo(dados_mercado):
                return False, "Momentum extremamente baixo"
            
            return True, "Entrada aprovada pelos filtros mínimos (modo totalmente autônomo)"
            
        except Exception as e:
            logger.error(f"[FILTROS] Erro ao verificar qualidade: {e}")
            return False, f"Erro no sistema de filtros: {e}"
    
    def _validar_tendencia_decisao_permissivo(self, tendencia: str, decisao: str, rsi: float) -> bool:
        """
        Valida se a decisão faz sentido com a tendência e RSI (PERMISSIVO)
        """
        if decisao == 'comprar':
            # Comprar em tendência baixa só se RSI MUITO baixo (sobrevendido)
            if tendencia == 'baixa' and rsi > 45:
                return False
            
            # Comprar em RSI MUITO alto só se tendência muito forte
            if rsi > 85 and tendencia != 'alta':
                return False
                
        elif decisao == 'vender':
            # Vender em tendência alta só se RSI MUITO alto (sobrecomprado)
            if tendencia == 'alta' and rsi < 55:
                return False
            
            # Vender em RSI MUITO baixo só se tendência muito forte
            if rsi < 15 and tendencia != 'baixa':
                return False
        
        return True
    
    def _verificar_limite_ordens_permissivo(self, symbol: str) -> bool:
        """
        Verifica limite de ordens simultâneas (SEGURANÇA)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM ordens_dinamicas 
                WHERE symbol = ? AND status = 'aberta'
            """, (symbol,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count < self.max_ordens_simultaneas
            
        except Exception as e:
            logger.error(f"[FILTROS] Erro ao verificar limite de ordens: {e}")
            return True  # Em caso de erro, permite
    
    def _verificar_performance_recente_permissivo(self) -> bool:
        """
        Verifica se a performance recente permite novas entradas (MÍNIMO ABSOLUTO)
        REMOVIDO: Filtro de win rate fixo - A IA controla dinamicamente
        """
        try:
            # Se está em pausa, verificar se já passou o tempo
            if self.ultima_pausa:
                tempo_pausa = (datetime.now() - self.ultima_pausa).total_seconds()
                if tempo_pausa < self.tempo_pausa:
                    return False
            
            # Obter últimas 10 ordens do banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT lucro_prejuizo FROM ordens_dinamicas 
                WHERE status = 'fechada' 
                ORDER BY timestamp_fechamento DESC 
                LIMIT 10
            """)
            
            resultados = cursor.fetchall()
            conn.close()
            
            if len(resultados) < 3:  # Poucas ordens, permite
                return True
            
            # REMOVIDO: Filtro de win rate fixo
            # A IA determina seu próprio win rate dinamicamente
            
            # Verificar perdas consecutivas (MUITO PERMISSIVO)
            perdas_consecutivas = 0
            for lucro in (r[0] or 0 for r in resultados):
                if lucro < 0:
                    perdas_consecutivas += 1
                else:
                    break
            
            if perdas_consecutivas >= self.max_perdas_consecutivas:
                self.ultima_pausa = datetime.now()
                logger.warning(f"[FILTROS] {perdas_consecutivas} perdas consecutivas - pausa ativada")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"[FILTROS] Erro ao verificar performance: {e}")
            return True  # Em caso de erro, permite
    
    def _verificar_horario_mercado_permissivo(self) -> bool:
        """
        Verifica se o horário é favorável para trading (PERMISSIVO)
        """
        agora = datetime.now()
        hora = agora.hour
        
        # Evitar apenas horários de MUITO baixa liquidez (madrugada extrema)
        if 1 <= hora <= 4:
            return False
        
        # Evitar finais de semana (se aplicável)
        if agora.weekday() >= 5:  # Sábado = 5, Domingo = 6
            return False
        
        return True
    
    def _verificar_volume_permissivo(self, dados_mercado: Dict[str, Any]) -> bool:
        """
        Verifica se o volume é suficiente (PERMISSIVO)
        """
        # Se não temos dados de volume, permitir (modo permissivo)
        volume_24h = dados_mercado.get('volume_24h')
        volume_1h = dados_mercado.get('volume_1h')
        
        # Se não temos dados de volume, permitir a entrada
        if volume_24h is None and volume_1h is None:
            return True
        
        # Volume mínimo MUITO baixo para BTC/ETH (se os dados existirem)
        min_volume_24h = 1000  # 1K USD (muito baixo)
        min_volume_1h = 10  # 100USD (muito baixo)
        
        # Verificar apenas se os dados existem
        if volume_24h is not None and volume_24h < min_volume_24h:
            return False
        
        if volume_1h is not None and volume_1h < min_volume_1h:
            return False
        
        return True
    
    def _verificar_momentum_permissivo(self, dados_mercado: Dict[str, Any]) -> bool:
        """
        Verifica se há momentum suficiente no mercado (PERMISSIVO)
        """
        rsi = dados_mercado.get('rsi', 50.0)
        volatilidade = dados_mercado.get('volatilidade', 0.02)
        
        # Momentum MUITO baixo (mercado completamente parado)
        if 48 <= rsi <= 52 and volatilidade < 0.001:
            return False
        
        return True
    
    def registrar_resultado(self, resultado: str, lucro: float):
        """
        Registra resultado de uma ordem para análise de performance
        """
        try:
            self.ultimas_10_ordens.append({
                'resultado': resultado,
                'lucro': lucro,
                'timestamp': datetime.now()
            })
            
            # Manter apenas últimas 10
            if len(self.ultimas_10_ordens) > 10:
                self.ultimas_10_ordens.pop(0)
            
            # Se foi loss, verificar se precisa pausar
            if lucro < 0:
                perdas_recentes = sum(1 for o in self.ultimas_10_ordens[-3:] if o['lucro'] < 0)
                if perdas_recentes >= self.max_perdas_consecutivas:
                    self.ultima_pausa = datetime.now()
                    logger.warning(f"[FILTROS] {perdas_recentes} perdas consecutivas - pausa ativada")
            
        except Exception as e:
            logger.error(f"[FILTROS] Erro ao registrar resultado: {e}")
    
    def obter_status_filtros(self) -> Dict[str, Any]:
        """
        Retorna status atual dos filtros
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estatísticas gerais
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN lucro_prejuizo > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN lucro_prejuizo < 0 THEN 1 ELSE 0 END) as losses,
                       AVG(lucro_prejuizo) as lucro_medio
                FROM ordens_dinamicas 
                WHERE status = 'fechada'
            """)
            
            stats = cursor.fetchone()
            total, wins, losses, lucro_medio = stats
            
            win_rate = (wins / total * 100) if total > 0 else 0
            
            # Ordens ativas por símbolo
            cursor.execute("""
                SELECT symbol, COUNT(*) as count
                FROM ordens_dinamicas 
                WHERE status = 'aberta'
                GROUP BY symbol
            """)
            
            ordens_ativas = dict(cursor.fetchall())
            conn.close()
            
            return {
                'win_rate': win_rate,
                'total_ordens': total,
                'wins': wins,
                'losses': losses,
                'lucro_medio': lucro_medio or 0,
                'ordens_ativas': ordens_ativas,
                'pausa_ativa': self.ultima_pausa is not None,
                'tempo_pausa': (datetime.now() - self.ultima_pausa).total_seconds() if self.ultima_pausa else 0,
                'filtros_config': {
                    'min_confianca': self.min_confianca,
                    'max_ordens_simultaneas': self.max_ordens_simultaneas,
                    'min_win_rate': 0, # REMOVIDO: win rate fixo
                    'max_perdas_consecutivas': self.max_perdas_consecutivas
                }
            }
            
        except Exception as e:
            logger.error(f"[FILTROS] Erro ao obter status: {e}")
            return {}
    
    def ajustar_parametros_dinamicos(self, performance: Dict[str, Any]):
        """
        Ajusta parâmetros dos filtros baseado na performance
        """
        # REMOVIDO: win_rate - A IA controla seu próprio win rate
        
        # Se performance muito baixa, tornar filtros mais rigorosos
        # A IA controla seus próprios thresholds
        if performance.get('win_rate', 0) < 0.15:  # Menos de 15%
            self.min_confianca = 0.85  # Aumentar confiança mínima
            self.max_ordens_simultaneas = 1  # Reduzir ordens simultâneas
            logger.info("[FILTROS] Filtros ajustados para modo conservador")
        
        # Se performance boa, relaxar um pouco
        # A IA controla seus próprios thresholds
        elif performance.get('win_rate', 0) > 0.35:  # Mais de 35%
            self.min_confianca = 0.70  # Reduzir confiança mínima
            self.max_ordens_simultaneas = 3  # Aumentar ordens simultâneas
            logger.info("[FILTROS] Filtros ajustados para modo agressivo")
        
        # Se performance média, manter padrão
        # A IA controla seus próprios thresholds
        else:
            self.min_confianca = 0.75
            self.max_ordens_simultaneas = 2
            logger.info("[FILTROS] Filtros mantidos em modo padrão") 