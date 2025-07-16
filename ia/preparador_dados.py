"""
Preparador de dados para análise de IA
Estrutura e enriquece dados de mercado para análise
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreparadorDadosIA:
    def __init__(self, db_path: str = "dados/trading.db"):
        """
        Inicializa preparador de dados
        
        Args:
            db_path: Caminho para banco de dados SQLite
        """
        self.db_path = db_path
        
    def preparar_dados_analise(self, dados_atual: Dict[str, Any], 
                              periodos_historico: int = 50) -> Dict[str, Any]:
        """
        Prepara dados para análise de IA
        
        Args:
            dados_atual: Dados atuais do mercado
            periodos_historico: Número de períodos históricos para incluir
            
        Returns:
            Dicionário com dados estruturados para IA
        """
        try:
            # Obter dados históricos
            dados_historicos = self._obter_dados_historicos(
                dados_atual.get('simbolo', 'WINZ25'),
                periodos_historico
            )
            
            # Calcular indicadores técnicos
            indicadores = self._calcular_indicadores_tecnicos(dados_historicos)
            
            # Estruturar dados para IA
            dados_ia = self._estruturar_dados_ia(dados_atual, indicadores)
            
            logger.info(f"Dados preparados para IA: {len(dados_historicos)} períodos históricos")
            return dados_ia
            
        except Exception as e:
            logger.error(f"Erro ao preparar dados para IA: {e}")
            return self._dados_fallback(dados_atual)
    
    def _obter_dados_historicos(self, simbolo: str, periodos: int) -> pd.DataFrame:
        """
        Obtém dados históricos do banco de dados real (tabela precos)
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            conn.execute("PRAGMA journal_mode=WAL;")
            query = """
            SELECT timestamp, preco_atual, volume, bid, ask
            FROM precos
            WHERE simbolo = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=[simbolo, periodos])
            conn.close()
            # Ordenar por timestamp (mais antigo primeiro)
            df = df.sort_values('timestamp').reset_index(drop=True)
            return df
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos: {e}")
            return pd.DataFrame(columns=pd.Index(['timestamp', 'preco_atual', 'volume', 'bid', 'ask']))
    
    def _calcular_indicadores_tecnicos(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula indicadores técnicos
        """
        if df.empty or len(df) < 20:
            return self._indicadores_fallback()
        
        try:
            precos = np.asarray(df['preco_atual'])
            volumes = np.asarray(df['volume'])
            
            # RSI (14 períodos)
            rsi = self._calcular_rsi(precos, 14)
            rsi_last = float(rsi[-1]) if isinstance(rsi, np.ndarray) and len(rsi) > 0 else 50.0
            
            # Médias móveis
            ma_20 = self._calcular_media_movel(precos, 20)
            ma_20_last = float(ma_20[-1]) if isinstance(ma_20, np.ndarray) and len(ma_20) > 0 else float(precos[-1]) if len(precos) > 0 else 0.0
            ma_50 = self._calcular_media_movel(precos, 50)
            ma_50_last = float(ma_50[-1]) if isinstance(ma_50, np.ndarray) and len(ma_50) > 0 else float(precos[-1]) if len(precos) > 0 else 0.0
            
            # Bandas de Bollinger (20 períodos, 2 desvios)
            bb_upper, bb_lower = self._calcular_bollinger(precos, 20, 2)
            bb_upper_last = float(bb_upper[-1]) if isinstance(bb_upper, np.ndarray) and len(bb_upper) > 0 else (float(precos[-1]) * 1.02 if len(precos) > 0 else 0.0)
            bb_lower_last = float(bb_lower[-1]) if isinstance(bb_lower, np.ndarray) and len(bb_lower) > 0 else (float(precos[-1]) * 0.98 if len(precos) > 0 else 0.0)
            
            # MACD (12, 26, 9)
            macd, signal = self._calcular_macd(precos, 12, 26, 9)
            macd_last = float(macd[-1]) if isinstance(macd, np.ndarray) and len(macd) > 0 else 0.0
            signal_last = float(signal[-1]) if isinstance(signal, np.ndarray) and len(signal) > 0 else 0.0
            
            # Volatilidade
            volatilidade = self._calcular_volatilidade(precos, 20)
            
            # Volume médio
            volume_medio = np.mean(volumes[-20:]) if len(volumes) >= 20 else (np.mean(volumes) if len(volumes) > 0 else 0.0)
            
            # Tendência
            tendencia = self._calcular_tendencia(precos, 20) if len(precos) >= 20 else "lateral"
            
            return {
                'rsi': rsi_last,
                'ma_20': ma_20_last,
                'ma_50': ma_50_last,
                'bb_upper': bb_upper_last,
                'bb_lower': bb_lower_last,
                'macd': macd_last,
                'macd_signal': signal_last,
                'volatilidade': float(volatilidade),
                'volume_medio': float(volume_medio),
                'tendencia': tendencia,
                'historico_precos': precos[-5:].tolist() if len(precos) >= 5 else precos.tolist() if len(precos) > 0 else []
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {e}")
            return self._indicadores_fallback()
    
    def _calcular_rsi(self, precos: np.ndarray, periodo: int = 14) -> np.ndarray:
        """Calcula RSI"""
        if len(precos) < periodo + 1:
            return np.array([])
        deltas = np.diff(precos)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gains_series = pd.Series(gains).rolling(window=periodo).mean()
        avg_gains = avg_gains_series.to_numpy()
        avg_losses_series = pd.Series(losses).rolling(window=periodo).mean()
        avg_losses = avg_losses_series.to_numpy()
        rs = avg_gains / (avg_losses + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        if isinstance(rsi, np.ndarray):
            return rsi
        return np.array([rsi])
    
    def _calcular_media_movel(self, precos: np.ndarray, periodo: int) -> np.ndarray:
        """Calcula média móvel"""
        if len(precos) < periodo:
            return np.array([])
        return np.array(pd.Series(precos).rolling(window=periodo).mean())
        
    def _calcular_bollinger(self, precos: np.ndarray, periodo: int = 20, desvios: int = 2) -> tuple:
        """Calcula Bandas de Bollinger"""
        if len(precos) < periodo:
            return np.array([]), np.array([])
        ma_series = pd.Series(precos).rolling(window=periodo).mean()
        ma = ma_series.to_numpy()
        std_series = pd.Series(precos).rolling(window=periodo).std()
        std = std_series.to_numpy()
        upper = ma + (std * desvios)
        lower = ma - (std * desvios)
        if not isinstance(upper, np.ndarray):
            upper = np.array([upper])
        if not isinstance(lower, np.ndarray):
            lower = np.array([lower])
        return upper, lower
    
    def _calcular_macd(self, precos: np.ndarray, rapida: int = 12, lenta: int = 26, sinal: int = 9) -> tuple:
        """Calcula MACD"""
        if len(precos) < lenta:
            return np.array([]), np.array([])
        ema_rapida_series = pd.Series(precos).ewm(span=rapida).mean()
        ema_rapida = ema_rapida_series.to_numpy()
        ema_lenta_series = pd.Series(precos).ewm(span=lenta).mean()
        ema_lenta = ema_lenta_series.to_numpy()
        macd = ema_rapida - ema_lenta
        signal_series = pd.Series(macd).ewm(span=sinal).mean()
        signal = signal_series.to_numpy()
        if not isinstance(macd, np.ndarray):
            macd = np.array([macd])
        if not isinstance(signal, np.ndarray):
            signal = np.array([signal])
        return macd, signal
    
    def _calcular_volatilidade(self, precos: np.ndarray, periodo: int = 20) -> float:
        """Calcula volatilidade"""
        if len(precos) < periodo:
            return 0.0
        
        returns = np.diff(precos) / precos[:-1]
        return float(np.std(returns[-periodo:]))
    
    def _calcular_tendencia(self, precos: np.ndarray, periodo: int = 20) -> str:
        """Calcula tendência"""
        if len(precos) < periodo:
            return "lateral"
        
        preco_atual = precos[-1]
        preco_anterior = precos[-periodo]
        
        if preco_atual > preco_anterior * 1.01:  # 1% de alta
            return "alta"
        elif preco_atual < preco_anterior * 0.99:  # 1% de baixa
            return "baixa"
        else:
            return "lateral"
    
    def _estruturar_dados_ia(self, dados_atual: Dict[str, Any], 
                           indicadores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estrutura dados para análise de IA
        """
        agora = datetime.now()
        
        return {
            # Dados atuais
            'ativo': dados_atual.get('simbolo', 'WINZ25'),
            'preco_atual': dados_atual.get('preco_atual', 0.0),
            'bid': dados_atual.get('bid', 0.0),
            'ask': dados_atual.get('ask', 0.0),
            'volume': dados_atual.get('volume', 0),
            'variacao': dados_atual.get('variacao', 0.0),
            
            # Indicadores técnicos
            'rsi': indicadores.get('rsi', 50.0),
            'ma_20': indicadores.get('ma_20', dados_atual.get('preco_atual', 0.0)),
            'ma_50': indicadores.get('ma_50', dados_atual.get('preco_atual', 0.0)),
            'bb_upper': indicadores.get('bb_upper', dados_atual.get('preco_atual', 0.0) * 1.02),
            'bb_lower': indicadores.get('bb_lower', dados_atual.get('preco_atual', 0.0) * 0.98),
            'macd': indicadores.get('macd', 0.0),
            'volatilidade': indicadores.get('volatilidade', 0.0),
            'volume_medio': indicadores.get('volume_medio', 0.0),
            'tendencia': indicadores.get('tendencia', 'lateral'),
            'historico_precos': indicadores.get('historico_precos', []),
            
            # Indicadores analisados
            'indicadores_analisados': ['rsi', 'macd', 'bollinger', 'media_movel', 'volume', 'tendencia'],
            
            # Contexto temporal
            'dia_semana': agora.strftime('%A'),
            'hora': agora.strftime('%H:%M'),
            'timestamp': agora.isoformat()
        }
    
    def _indicadores_fallback(self) -> Dict[str, Any]:
        """Retorna indicadores de fallback"""
        return {
            'rsi': 50.0,
            'ma_20': 0.0,
            'ma_50': 0.0,
            'bb_upper': 0.0,
            'bb_lower': 0.0,
            'macd': 0.0,
            'macd_signal': 0.0,
            'volatilidade': 0.0,
            'volume_medio': 0.0,
            'tendencia': 'lateral',
            'historico_precos': []
        }
    
    def _dados_fallback(self, dados_atual: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna dados de fallback"""
        agora = datetime.now()
        
        return {
            'ativo': dados_atual.get('simbolo', 'WINZ25'),
            'preco_atual': dados_atual.get('preco_atual', 0.0),
            'bid': dados_atual.get('bid', 0.0),
            'ask': dados_atual.get('ask', 0.0),
            'volume': dados_atual.get('volume', 0),
            'variacao': dados_atual.get('variacao', 0.0),
            'rsi': 50.0,
            'ma_20': dados_atual.get('preco_atual', 0.0),
            'ma_50': dados_atual.get('preco_atual', 0.0),
            'bb_upper': dados_atual.get('preco_atual', 0.0) * 1.02,
            'bb_lower': dados_atual.get('preco_atual', 0.0) * 0.98,
            'macd': 0.0,
            'volatilidade': 0.0,
            'volume_medio': 0.0,
            'tendencia': 'lateral',
            'historico_precos': [],
            'dia_semana': agora.strftime('%A'),
            'hora': agora.strftime('%H:%M'),
            'timestamp': agora.isoformat()
        } 