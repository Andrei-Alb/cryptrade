#!/usr/bin/env python3
"""
Sistema de Aprendizado Autônomo da IA
A IA determina sua própria confiança e aprende com resultados
"""

import sqlite3
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class ResultadoTrade:
    """Resultado de um trade para aprendizado"""
    timestamp: str
    symbol: str  # <--- trocado de par para symbol
    direcao: str  # compra/venda
    preco_entrada: float
    preco_saida: float
    quantidade: float
    pnl: float
    pnl_percentual: float
    duracao: float  # segundos
    rsi_entrada: float
    volatilidade_entrada: float
    tendencia_entrada: str
    confianca_entrada: float
    stop_loss: float
    take_profit: float
    motivo_saida: str  # take_profit/stop_loss/tempo
    indicadores_entrada: Dict[str, Any]
    sucesso: bool

@dataclass
class ParametrosIA:
    """Parâmetros dinâmicos que a IA pode modificar"""
    # Indicadores
    rsi_periodo: int = 14
    rsi_sobrecompra: float = 70.0
    rsi_sobrevenda: float = 30.0
    volatilidade_periodo: int = 20
    tendencia_periodo: int = 50
    
    # Gestão de Risco
    stop_loss_padrao: float = -2.0
    take_profit_padrao: float = 3.0
    max_ordens_simultaneas: int = 3
    max_ordens_por_direcao: int = 1
    max_ordens_por_par: int = 2
    
    # Timing
    tempo_minimo_entre_ordens: int = 30  # segundos
    tempo_maximo_ordem: int = 300  # segundos
    
    # Confiança
    confianca_minima: float = 0.5
    confianca_maxima: float = 0.95
    
    # Aprendizado
    taxa_aprendizado: float = 0.1
    memoria_resultados: int = 100
    
    # Adaptação
    adaptacao_ativa: bool = True
    ajuste_automatico: bool = True

class SistemaAprendizadoAutonomo:
    """Sistema de IA autônoma com controle total"""
    
    def __init__(self, db_path: str = "dados/trading.db"):
        """Inicializa o sistema de aprendizado autônomo"""
        self.db_path = db_path
        self.parametros_padrao = {
            'stop_loss_padrao': -2.0,
            'take_profit_padrao': 3.0,
            'confianca_minima': 0.5,
            'quantidade_maxima': 0.001,
            'max_ordens_simultaneas': 3,
            'tempo_maximo_ordem': 300
        }
        self.resultados = deque(maxlen=100)  # Memória de resultados
        self.estatisticas = defaultdict(list)  # Estatísticas por período
        self.ultima_analise = {}  # Sempre um dicionário para contexto de análise
        self._criar_tabelas()
        self._carregar_estado()
        logger.info("🧠 Sistema de Aprendizado Autônomo inicializado")
    
    def _criar_tabelas(self):
        """Cria tabelas no banco de dados se não existirem"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ajustes_parametros (
                    timestamp TEXT PRIMARY KEY,
                    parametros TEXT NOT NULL,
                    win_rate REAL NOT NULL,
                    pnl_medio REAL NOT NULL,
                    resultado TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aprendizado_autonomo (
                    timestamp TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    direcao TEXT NOT NULL,
                    preco_entrada REAL NOT NULL,
                    preco_saida REAL NOT NULL,
                    quantidade REAL NOT NULL,
                    lucro_prejuizo REAL NOT NULL,
                    duracao REAL NOT NULL,
                    rsi_entrada REAL NOT NULL,
                    volatilidade_entrada REAL NOT NULL,
                    tendencia_entrada TEXT NOT NULL,
                    confianca_entrada REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    motivo_saida TEXT NOT NULL,
                    indicadores_entrada TEXT NOT NULL,
                    sucesso INTEGER NOT NULL,
                    contexto_order_book TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ordens_dinamicas (
                    order_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
    
    def _carregar_estado(self):
        """Carrega o estado atual do sistema do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM ajustes_parametros ORDER BY timestamp DESC LIMIT 1
            """)
            ultimo_ajuste = cursor.fetchone()
            
            if ultimo_ajuste:
                ajuste_data = json.loads(ultimo_ajuste[1])
                self.parametros = ParametrosIA(**ajuste_data)
                self.performance_global = {
                    'total_trades': 0, # Placeholder, precisa ser atualizado
                    'wins': 0, # Placeholder, precisa ser atualizado
                    'losses': 0, # Placeholder, precisa ser atualizado
                    'pnl_total': 0.0, # Placeholder, precisa ser atualizado
                    'win_rate': 0.0, # Placeholder, precisa ser atualizado
                    'avg_win': 0.0, # Placeholder, precisa ser atualizado
                    'avg_loss': 0.0, # Placeholder, precisa ser atualizado
                    'max_drawdown': 0.0 # Placeholder, precisa ser atualizado
                }
                self.historico_ajustes = [ajuste_data] # Carregar apenas o último ajuste
            else:
                self.parametros = ParametrosIA()
                self.performance_global = {
                    'total_trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'pnl_total': 0.0,
                    'win_rate': 0.0,
                    'avg_win': 0.0,
                    'avg_loss': 0.0,
                    'max_drawdown': 0.0
                }
                self.historico_ajustes = []
            
            # Carregar estado do mercado
            cursor.execute("""
                SELECT * FROM ordens_dinamicas
            """)
            ordens_ativas = cursor.fetchall()
            self.estado_mercado = {
                'btcusdt': {'ultima_ordem': None, 'ordens_ativas': 0, 'direcao_atual': None},
                'ethusdt': {'ultima_ordem': None, 'ordens_ativas': 0, 'direcao_atual': None}
            }
            for ordem in ordens_ativas:
                par = ordem[2].upper()
                if par in self.estado_mercado:
                    self.estado_mercado[par]['ordens_ativas'] = 1
                    self.estado_mercado[par]['direcao_atual'] = 'compra' if ordem[3] == 'compra' else 'venda'
                    self.estado_mercado[par]['ultima_ordem'] = datetime.fromisoformat(ordem[4]).timestamp()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar estado do sistema: {e}")
    
    def registrar_resultado(self, resultado: ResultadoTrade):
        """Registra resultado de trade no sistema de aprendizado, incluindo contexto do order book"""
        try:
            # Adicionar ao histórico de resultados
            self.resultados.append(resultado)
            
            # Atualizar estatísticas
            self._atualizar_estatisticas(resultado)
            
            # Salvar no banco de dados com contexto completo
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Incluir contexto do order book se disponível
            contexto_order_book = ""
            if hasattr(resultado, 'indicadores_entrada') and resultado.indicadores_entrada:
                ob_data = resultado.indicadores_entrada
                contexto_order_book = json.dumps({
                    'bid_ask_imbalance': ob_data.get('bid_ask_imbalance', 0),
                    'max_bid_size': ob_data.get('max_bid_size', 0),
                    'max_ask_size': ob_data.get('max_ask_size', 0),
                    'liquidity_clusters': ob_data.get('liquidity_clusters', 0)
                })
            
            cursor.execute("""
                INSERT INTO aprendizado_autonomo (
                    timestamp, symbol, direcao, preco_entrada, preco_saida, quantidade,
                    lucro_prejuizo, duracao, rsi_entrada, volatilidade_entrada,
                    tendencia_entrada, confianca_entrada, stop_loss, take_profit,
                    motivo_saida, indicadores_entrada, sucesso, contexto_order_book
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resultado.timestamp, resultado.symbol, resultado.direcao,
                resultado.preco_entrada, resultado.preco_saida, resultado.quantidade,
                resultado.pnl, resultado.duracao, resultado.rsi_entrada,
                resultado.volatilidade_entrada, resultado.tendencia_entrada,
                resultado.confianca_entrada, resultado.stop_loss, resultado.take_profit,
                resultado.motivo_saida, json.dumps(resultado.indicadores_entrada),
                1 if resultado.sucesso else 0, contexto_order_book
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Resultado registrado: {resultado.symbol} {resultado.direcao} - PnL: {resultado.pnl:.4f} ({resultado.pnl_percentual:.2f}%) - {'✅' if resultado.sucesso else '❌'}")
            
            # Ajustar parâmetros baseado no resultado
            self._ajustar_parametros_aprendizado(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar resultado: {e}")
    
    def analisar_e_ajustar(self):
        """Analisa resultados e ajusta parâmetros automaticamente"""
        if not self.parametros.adaptacao_ativa:
            return
        
        logger.info("[IA AUTÔNOMA] Iniciando análise e ajuste de parâmetros...")
        
        # Análise de performance recente
        resultados_recentes = list(self.resultados)[-20:]  # Últimos 20 trades
        
        if len(resultados_recentes) < 5:
            return
        
        # Calcular métricas recentes
        win_rate_recente = sum(1 for r in resultados_recentes if r.sucesso) / len(resultados_recentes)
        pnl_medio_recente = float(np.mean([r.pnl_percentual for r in resultados_recentes]))
        
        # Análise por par
        for par in ['BTCUSDT', 'ETHUSDT']:
            resultados_par = [r for r in resultados_recentes if r.symbol == par]
            if len(resultados_par) >= 3:
                self.ajustar_parametros_par(par, resultados_par)
        
        # Ajustes globais baseados em performance
        self.ajustar_parametros_globais(win_rate_recente, pnl_medio_recente)
        
        # Registrar ajuste
        ajuste = {
            'timestamp': datetime.now().isoformat(),
            'win_rate_recente': win_rate_recente,
            'pnl_medio_recente': pnl_medio_recente,
            'parametros_anteriores': asdict(self.parametros),
            'motivo': 'Ajuste automático baseado em performance'
        }
        self.historico_ajustes.append(ajuste)
        
        logger.info(f"[IA AUTÔNOMA] Ajuste realizado - Win Rate: {win_rate_recente:.2%}, PnL Médio: {pnl_medio_recente:.2f}%")
    
    def ajustar_parametros_par(self, par: str, resultados: List[ResultadoTrade]):
        """Ajusta parâmetros específicos para um par"""
        if not resultados:
            return
        
        # Análise de RSI
        rsi_entradas = [r.rsi_entrada for r in resultados]
        rsi_wins = [r.rsi_entrada for r in resultados if r.sucesso]
        rsi_losses = [r.rsi_entrada for r in resultados if not r.sucesso]
        
        if rsi_wins and rsi_losses:
            # Ajustar níveis de RSI baseado em performance
            rsi_win_medio = np.mean(rsi_wins)
            rsi_loss_medio = np.mean(rsi_losses)
            
            # Se RSI de wins é diferente de losses, ajustar
            if abs(rsi_win_medio - rsi_loss_medio) > 5:
                if rsi_win_medio < 50:  # Wins em RSI baixo
                    self.parametros.rsi_sobrevenda = min(35, self.parametros.rsi_sobrevenda + 1)
                else:  # Wins em RSI alto
                    self.parametros.rsi_sobrecompra = max(65, self.parametros.rsi_sobrecompra - 1)
        
        # Análise de confiança
        confiancas = [r.confianca_entrada for r in resultados]
        confianca_wins = [r.confianca_entrada for r in resultados if r.sucesso]
        
        if confianca_wins:
            confianca_win_medio = np.mean(confianca_wins)
            # Ajustar confiança mínima baseado em wins
            if confianca_win_medio > self.parametros.confianca_minima + 0.1:
                self.parametros.confianca_minima = min(0.7, self.parametros.confianca_minima + 0.05)
            elif confianca_win_medio < self.parametros.confianca_minima - 0.1:
                self.parametros.confianca_minima = max(0.3, self.parametros.confianca_minima - 0.05)
    
    def ajustar_parametros_globais(self, win_rate: float, pnl_medio: float):
        """Ajusta parâmetros globais baseado em performance"""
        
        # Ajustar stop loss e take profit baseado em performance
        if win_rate < 0.3:  # Performance ruim
            # Reduzir risco
            self.parametros.stop_loss_padrao = max(-1.5, self.parametros.stop_loss_padrao + 0.2)
            self.parametros.take_profit_padrao = min(2.0, self.parametros.take_profit_padrao - 0.2)
            self.parametros.max_ordens_simultaneas = max(2, self.parametros.max_ordens_simultaneas - 1)
            
        elif win_rate > 0.6:  # Performance boa
            # Aumentar agressividade
            self.parametros.stop_loss_padrao = min(-3.0, self.parametros.stop_loss_padrao - 0.2)
            self.parametros.take_profit_padrao = max(4.0, self.parametros.take_profit_padrao + 0.2)
            self.parametros.max_ordens_simultaneas = min(4, self.parametros.max_ordens_simultaneas + 1)
        
        # Ajustar timing baseado em duração dos trades
        duracao_media = np.mean([r.duracao for r in list(self.resultados)[-10:]])
        if duracao_media > 200:  # Trades muito longos
            self.parametros.tempo_maximo_ordem = min(180, self.parametros.tempo_maximo_ordem - 30)
        elif duracao_media < 60:  # Trades muito rápidos
            self.parametros.tempo_maximo_ordem = max(240, self.parametros.tempo_maximo_ordem + 30)
    
    def obter_parametros_otimizados(self) -> Dict[str, Any]:
        """Retorna parâmetros otimizados baseados no aprendizado"""
        try:
            # Calcular métricas de performance
            resultados_recentes = self._obter_resultados_recentes(50)
            
            if not resultados_recentes:
                return self.parametros_padrao
            
            # Calcular métricas recentes
            win_rate_recente = sum(1 for r in resultados_recentes if r.sucesso) / len(resultados_recentes)
            pnl_medio_recente = float(np.mean([r.pnl_percentual for r in resultados_recentes]))
            
            # Ajustar parâmetros baseado na performance
            parametros = self.parametros_padrao.copy()
            
            # Se win rate baixo, ser mais conservador
            if win_rate_recente < 0.3:
                parametros['stop_loss_padrao'] *= 0.8  # Reduzir stop loss
                parametros['take_profit_padrao'] *= 1.2  # Aumentar take profit
                parametros['confianca_minima'] *= 1.3  # Aumentar confiança mínima
            
            # Se PnL negativo, reduzir exposição
            if pnl_medio_recente < 0:
                parametros['quantidade_maxima'] *= 0.7  # Reduzir quantidade
                parametros['max_ordens_simultaneas'] = max(1, parametros['max_ordens_simultaneas'] - 1)
            
            # Ajustar baseado na volatilidade do mercado
            volatilidade_media = np.mean([r.volatilidade_entrada for r in resultados_recentes])
            if volatilidade_media > 0.02:  # Alta volatilidade
                parametros['stop_loss_padrao'] *= 1.2
                parametros['take_profit_padrao'] *= 1.1
            
            # Ajustar baseado no RSI médio
            rsi_medio = np.mean([r.rsi_entrada for r in resultados_recentes])
            if rsi_medio > 70 or rsi_medio < 30:  # Extremos
                parametros['confianca_minima'] *= 1.2  # Ser mais seletivo
            
            # Ajustar baseado na tendência
            tendencias = [r.tendencia_entrada for r in resultados_recentes]
            tendencia_dominante = max(set(tendencias), key=tendencias.count)
            if tendencia_dominante == 'lateral':
                parametros['quantidade_maxima'] *= 0.8  # Reduzir em mercado lateral
            
            # Salvar ajustes para aprendizado
            self._salvar_ajuste_parametros(parametros, win_rate_recente, pnl_medio_recente)
            
            return parametros
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter parâmetros otimizados: {e}")
            return self.parametros_padrao
    
    def _salvar_ajuste_parametros(self, parametros: Dict[str, Any], win_rate: float, pnl_medio: float):
        """Salva ajustes de parâmetros para aprendizado"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ajustes_parametros (
                    timestamp, parametros, win_rate, pnl_medio, resultado
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                json.dumps(parametros),
                win_rate,
                pnl_medio,
                'melhoria' if pnl_medio > 0 else 'piora'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar ajuste de parâmetros: {e}")
    
    def pode_abrir_ordem(self, par: str, decisao: str) -> bool:
        """Verifica se pode abrir ordem baseado em múltiplos fatores, incluindo pausa automática e filtros de qualidade"""
        try:
            # Pausa automática se sequência de perdas ou drawdown elevado
            if self._em_pausa(par):
                logger.warning(f"⏸️ Pausa automática ativa para {par}")
                return False
            
            # Verificar ordens abertas
            ordens_abertas = self._obter_ordens_abertas(par)
            if len(ordens_abertas) >= self.parametros_padrao['max_ordens_simultaneas']:
                return False
            
            # Verificar performance recente
            resultados_recentes = self._obter_resultados_recentes(20)
            if resultados_recentes:
                win_rate_recente = sum(1 for r in resultados_recentes if r.sucesso) / len(resultados_recentes)
                pnl_medio_recente = np.mean([r.pnl_percentual for r in resultados_recentes])
                
                # Se performance muito ruim, pausar
                if win_rate_recente < 0.1 and pnl_medio_recente < -0.01:
                    logger.warning(f"⏸️ Pausando ordens para {par} - Performance muito baixa")
                    self._registrar_pausa(par, motivo="performance baixa")
                    return False
            
            # Filtros de qualidade de sinal
            if hasattr(self, 'ultima_analise') and self.ultima_analise:
                analise = self.ultima_analise.get(par, {})
                confianca = analise.get('confianca', 0)
                volatilidade = analise.get('volatilidade', 0.01)
                tendencia = analise.get('tendencia', 'lateral')
                if confianca < self.parametros_padrao['confianca_minima']:
                    logger.info(f"🔍 Sinal rejeitado: confiança baixa para {par}")
                    return False
                if volatilidade > 0.05:
                    logger.info(f"🔍 Sinal rejeitado: volatilidade alta para {par}")
                    return False
                if tendencia == 'lateral':
                    logger.info(f"🔍 Sinal rejeitado: mercado lateral para {par}")
                    return False
            
            # Verificar tendência de mercado
            if self._mercado_lateral(par):
                logger.info(f"⏳ Mercado lateral para {par}, aguardando melhor oportunidade")
                return False
            
            # Verificar volatilidade
            if self._volatilidade_alta(par):
                logger.info(f"⚠️ Volatilidade alta para {par}, reduzindo exposição")
                return False
            
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao verificar se pode abrir ordem: {e}")
            return False

    def _em_pausa(self, par: str) -> bool:
        """Verifica se o par está em pausa automática"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM pausas_inteligentes WHERE par = ? AND ativa = 1 AND timestamp > datetime('now', '-30 minutes')
            """, (par,))
            em_pausa = cursor.fetchone()[0] > 0
            conn.close()
            return em_pausa
        except Exception as e:
            logger.error(f"❌ Erro ao verificar pausa: {e}")
            return False

    def _registrar_pausa(self, par: str, motivo: str):
        """Registra uma pausa automática para o par"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pausas_inteligentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    par TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    duracao_minutos INTEGER DEFAULT 30,
                    ativa BOOLEAN DEFAULT TRUE
                )
            """)
            cursor.execute("""
                INSERT INTO pausas_inteligentes (par, motivo, duracao_minutos, ativa) VALUES (?, ?, ?, 1)
            """, (par, motivo, 30))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Erro ao registrar pausa: {e}")
    
    def _mercado_lateral(self, par: str) -> bool:
        """Verifica se o mercado está lateral"""
        try:
            # Implementar lógica de detecção de mercado lateral
            # Por enquanto, retorna False
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar mercado lateral: {e}")
            return False
    
    def _volatilidade_alta(self, par: str) -> bool:
        """Verifica se a volatilidade está alta"""
        try:
            # Implementar lógica de detecção de volatilidade alta
            # Por enquanto, retorna False
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar volatilidade: {e}")
            return False
    
    def registrar_ordem_aberta(self, par: str, direcao: str):
        """Registra abertura de ordem"""
        estado = self.estado_mercado[par.lower()]
        estado['ultima_ordem'] = time.time()
        estado['ordens_ativas'] += 1
        estado['direcao_atual'] = direcao
    
    def registrar_ordem_fechada(self, par: str):
        """Registra fechamento de ordem"""
        estado = self.estado_mercado[par.lower()]
        estado['ordens_ativas'] = max(0, estado['ordens_ativas'] - 1)
        if estado['ordens_ativas'] == 0:
            estado['direcao_atual'] = None
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        return {
            'performance_global': self.performance_global,
            'estado_mercado': self.estado_mercado,
            'total_ajustes': len(self.historico_ajustes),
            'ultima_analise': self.ultima_analise
        }
    
    def forcar_ajuste(self, motivo: str = "Ajuste manual"):
        """Força uma análise e ajuste imediato"""
        logger.info(f"[IA AUTÔNOMA] Forçando ajuste: {motivo}")
        self.analisar_e_ajustar()
    
    def reset_parametros(self):
        """Reseta parâmetros para valores padrão"""
        self.parametros = ParametrosIA()
        logger.info("[IA AUTÔNOMA] Parâmetros resetados para valores padrão")
    
    def salvar_estado(self, arquivo: str = "estado_ia_autonoma.json"):
        """Salva estado atual do sistema"""
        estado = {
            'parametros': asdict(self.parametros),
            'performance_global': self.performance_global,
            'estado_mercado': self.estado_mercado,
            'historico_ajustes': self.historico_ajustes[-50:],  # Últimos 50 ajustes
            'timestamp': datetime.now().isoformat()
        }
        
        with open(arquivo, 'w') as f:
            json.dump(estado, f, indent=2)
        
        logger.info(f"[IA AUTÔNOMA] Estado salvo em {arquivo}")
    
    def carregar_estado(self, arquivo: str = "estado_ia_autonoma.json"):
        """Carrega estado salvo do sistema"""
        try:
            with open(arquivo, 'r') as f:
                estado = json.load(f)
            
            self.parametros = ParametrosIA(**estado['parametros'])
            self.performance_global = estado['performance_global']
            self.estado_mercado = estado['estado_mercado']
            self.historico_ajustes = estado.get('historico_ajustes', [])
            
            logger.info(f"[IA AUTÔNOMA] Estado carregado de {arquivo}")
            
        except FileNotFoundError:
            logger.info(f"[IA AUTÔNOMA] Arquivo {arquivo} não encontrado, usando estado padrão")
        except Exception as e:
            logger.error(f"[IA AUTÔNOMA] Erro ao carregar estado: {e}")
    
    def _obter_resultados_recentes(self, limite: int = 50) -> List[ResultadoTrade]:
        """Obtém resultados recentes para análise"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM aprendizado_autonomo 
                WHERE lucro_prejuizo IS NOT NULL 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limite,))
            
            resultados = []
            for row in cursor.fetchall():
                # Converter row para ResultadoTrade
                resultado = ResultadoTrade(
                    timestamp=row[1],
                    symbol=row[2],
                    direcao=row[3],
                    preco_entrada=0.0,  # Não disponível na tabela atual
                    preco_saida=0.0,
                    quantidade=0.0,
                    pnl=row[10] or 0.0,
                    pnl_percentual=0.0,
                    duracao=0.0,
                    rsi_entrada=50.0,  # Valor padrão
                    volatilidade_entrada=0.01,  # Valor padrão
                    tendencia_entrada='lateral',  # Valor padrão
                    confianca_entrada=row[4] or 0.0,
                    stop_loss=0.0,
                    take_profit=0.0,
                    motivo_saida='',
                    indicadores_entrada={},
                    sucesso=row[10] > 0 if row[10] else False
                )
                resultados.append(resultado)
            
            conn.close()
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter resultados recentes: {e}")
            return []
    
    def _obter_ordens_abertas(self, par: str) -> List[Dict[str, Any]]:
        """Obtém ordens abertas para um par específico"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM ordens_dinamicas 
                WHERE symbol = ? AND status = 'aberta'
            """, (par,))
            
            ordens = []
            for row in cursor.fetchall():
                ordens.append({
                    'order_id': row[1],
                    'symbol': row[2],
                    'status': row[11]
                })
            
            conn.close()
            return ordens
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter ordens abertas: {e}")
            return []

    def _atualizar_estatisticas(self, resultado: ResultadoTrade):
        """Atualiza estatísticas com o novo resultado"""
        try:
            self.estatisticas[resultado.symbol].append(resultado)
            
            # Atualizar estatísticas globais
            self.performance_global['total_trades'] += 1
            self.performance_global['pnl_total'] += resultado.pnl
            
            if resultado.sucesso:
                self.performance_global['wins'] += 1
            else:
                self.performance_global['losses'] += 1
            
            # Calcular métricas
            total = self.performance_global['wins'] + self.performance_global['losses']
            if total > 0:
                self.performance_global['win_rate'] = self.performance_global['wins'] / total
            
            # Calcular médias
            wins = [r.pnl for r in self.resultados if r.sucesso]
            losses = [r.pnl for r in self.resultados if not r.sucesso]
            
            if wins:
                self.performance_global['avg_win'] = np.mean(wins)
            if losses:
                self.performance_global['avg_loss'] = np.mean(losses)
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar estatísticas: {e}")
    
    def _ajustar_parametros_aprendizado(self, resultado: ResultadoTrade):
        """Ajusta parâmetros baseado no resultado do trade"""
        try:
            # Se resultado positivo, manter parâmetros
            if resultado.sucesso:
                logger.info(f"✅ Trade positivo - mantendo parâmetros para {resultado.symbol}")
                return
            
            # Se resultado negativo, ajustar parâmetros
            logger.info(f"⚠️ Trade negativo - ajustando parâmetros para {resultado.symbol}")
            
            # Reduzir confiança mínima se confiança estava alta mas trade foi negativo
            if resultado.confianca_entrada > 0.7:
                self.parametros_padrao['confianca_minima'] *= 1.1
                logger.info(f"🔧 Aumentando confiança mínima para {self.parametros_padrao['confianca_minima']:.3f}")
            
            # Ajustar stop loss se perda foi grande
            if resultado.pnl_percentual < -2.0:
                self.parametros_padrao['stop_loss_padrao'] *= 0.9
                logger.info(f"🔧 Reduzindo stop loss para {self.parametros_padrao['stop_loss_padrao']:.2f}%")
            
            # Salvar ajustes
            self._salvar_ajuste_parametros(self.parametros_padrao, 0.0, resultado.pnl_percentual)
            
        except Exception as e:
            logger.error(f"❌ Erro ao ajustar parâmetros: {e}")

# Instância global do sistema autônomo
sistema_autonomo = SistemaAprendizadoAutonomo() 