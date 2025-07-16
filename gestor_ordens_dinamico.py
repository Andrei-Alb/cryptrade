#!/usr/bin/env python3
"""
Gestor de Ordens Dinâmico da IA
IA controla totalmente stop loss, take profit, timing de saída e ajustes dinâmicos
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger
import sqlite3
from dataclasses import dataclass
from enum import Enum

class TipoOrdem(Enum):
    COMPRA = "compra"
    VENDA = "venda"

class StatusOrdem(Enum):
    ABERTA = "aberta"
    FECHADA = "fechada"
    CANCELADA = "cancelada"

@dataclass
class ConfiguracaoOrdem:
    """Configuração dinâmica de uma ordem"""
    stop_loss_inicial: float
    take_profit_inicial: float
    stop_loss_atual: float
    take_profit_atual: float
    tempo_maximo_segundos: int = 300  # 5 minutos padrão
    trailing_stop_ativado: bool = False
    trailing_stop_distancia: float = 0.0
    saida_inteligente_ativada: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializável"""
        return {
            'stop_loss_inicial': self.stop_loss_inicial,
            'take_profit_inicial': self.take_profit_inicial,
            'stop_loss_atual': self.stop_loss_atual,
            'take_profit_atual': self.take_profit_atual,
            'tempo_maximo_segundos': self.tempo_maximo_segundos,
            'trailing_stop_ativado': self.trailing_stop_ativado,
            'trailing_stop_distancia': self.trailing_stop_distancia,
            'saida_inteligente_ativada': self.saida_inteligente_ativada
        }

class GestorOrdensDinamico:
    """Gestor de ordens onde a IA tem controle total sobre saídas"""
    def __init__(self, db_path: str = "dados/crypto_trading.db", risco_maximo_permitido: float = 3.0, decisor_ia=None, sistema_aprendizado=None):
        """
        Inicializa gestor de ordens dinâmico
        Args:
            db_path: Caminho para banco de dados
            risco_maximo_permitido: Valor máximo de risco permitido por ordem (USDT)
            decisor_ia: Instância do DecisorIA para aprendizado
            sistema_aprendizado: Instância do SistemaAprendizado para aprendizado detalhado
        """
        self.db_path = db_path
        self.ordens_ativas: Dict[str, Dict[str, Any]] = {}
        self.thread_monitoramento = None
        self.monitoramento_ativo = False
        self.risco_maximo_permitido = risco_maximo_permitido
        self.decisor_ia = decisor_ia
        self.sistema_aprendizado = sistema_aprendizado
        # Configurações dinâmicas
        self.config_dinamica = {
            'stop_loss_percentual_alvo': 0.5,  # 50% do alvo
            'trailing_stop_minimo': 0.001,     # 0.1% mínimo
            'ajuste_stop_loss_intervalo': 10,  # Ajustar a cada 10 segundos
            'saida_inteligente_intervalo': 5,  # Verificar saída a cada 5 segundos
        }
        self._criar_tabelas_gestao()
        logger.info("🎯 Gestor de Ordens Dinâmico inicializado")
    
    def _criar_tabelas_gestao(self):
        """Cria tabelas para gestão dinâmica de ordens"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de ordens dinâmicas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ordens_dinamicas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    tipo_ordem TEXT NOT NULL,
                    preco_entrada REAL NOT NULL,
                    quantidade REAL NOT NULL,
                    stop_loss_inicial REAL NOT NULL,
                    take_profit_inicial REAL NOT NULL,
                    stop_loss_atual REAL NOT NULL,
                    take_profit_atual REAL NOT NULL,
                    status TEXT NOT NULL,
                    timestamp_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
                    timestamp_fechamento DATETIME,
                    preco_saida REAL,
                    lucro_prejuizo REAL,
                    tempo_aberta_segundos INTEGER,
                    ajustes_stop_loss INTEGER DEFAULT 0,
                    ajustes_take_profit INTEGER DEFAULT 0,
                    saida_inteligente_utilizada BOOLEAN DEFAULT FALSE,
                    razao_saida TEXT,
                    dados_mercado_saida TEXT
                )
            """)
            
            # Tabela de ajustes dinâmicos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ajustes_dinamicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    tipo_ajuste TEXT NOT NULL,
                    valor_anterior REAL NOT NULL,
                    valor_novo REAL NOT NULL,
                    razao_ajuste TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    dados_mercado TEXT
                )
            """)
            
            # Tabela de aprendizado de saídas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aprendizado_saidas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    tipo_saida TEXT NOT NULL,
                    tempo_aberta_segundos INTEGER,
                    lucro_prejuizo REAL,
                    confianca_saida REAL,
                    razao_saida TEXT,
                    sucesso BOOLEAN,
                    aprendizado TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Tabelas de gestão dinâmica criadas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas de gestão: {e}")
    
    def abrir_ordem_dinamica(self, order_id: str, symbol: str, tipo_ordem: TipoOrdem, 
                           preco_entrada: float, quantidade: float, 
                           dados_mercado: Dict[str, Any], confianca_ia: float) -> Dict[str, Any]:
        """
        Abre ordem com gestão dinâmica controlada pela IA
        
        Args:
            order_id: ID único da ordem
            symbol: Símbolo do ativo
            tipo_ordem: Compra ou venda
            preco_entrada: Preço de entrada
            quantidade: Quantidade
            dados_mercado: Dados atuais do mercado
            confianca_ia: Confiança da IA na decisão
            
        Returns:
            Configuração da ordem dinâmica
        """
        try:
            # Calcular stop loss e take profit dinâmicos
            stop_loss, take_profit = self._calcular_stop_take_dinamico(
                tipo_ordem, preco_entrada, dados_mercado, confianca_ia
            )
            
            # Configuração da ordem
            config_ordem = ConfiguracaoOrdem(
                stop_loss_inicial=stop_loss,
                take_profit_inicial=take_profit,
                stop_loss_atual=stop_loss,
                take_profit_atual=take_profit,
                tempo_maximo_segundos=self._calcular_tempo_maximo(confianca_ia, dados_mercado),
                saida_inteligente_ativada=True
            )
            
            # Salvar ordem no banco
            self._salvar_ordem_dinamica(order_id, symbol, tipo_ordem, preco_entrada, 
                                      quantidade, config_ordem)
            
            # Adicionar à lista de ordens ativas
            self.ordens_ativas[order_id] = {
                'symbol': symbol,
                'tipo_ordem': tipo_ordem.value,
                'preco_entrada': preco_entrada,
                'quantidade': quantidade,
                'config': {
                    'stop_loss_inicial': config_ordem.stop_loss_inicial,
                    'take_profit_inicial': config_ordem.take_profit_inicial,
                    'stop_loss_atual': config_ordem.stop_loss_atual,
                    'take_profit_atual': config_ordem.take_profit_atual,
                    'tempo_maximo_segundos': config_ordem.tempo_maximo_segundos,
                    'trailing_stop_ativado': config_ordem.trailing_stop_ativado,
                    'trailing_stop_distancia': config_ordem.trailing_stop_distancia,
                    'saida_inteligente_ativada': config_ordem.saida_inteligente_ativada
                },
                'timestamp_abertura': datetime.now(),
                'dados_mercado_inicial': dados_mercado,
                'confianca_ia': confianca_ia,
                'ajustes_realizados': 0,
                'maior_lucro_percentual': 0.0  # Novo campo para trailing stop
            }
            
            # Iniciar monitoramento se não estiver ativo
            if not self.monitoramento_ativo:
                self._iniciar_monitoramento()
            
            logger.info(f"🎯 Ordem dinâmica aberta: {order_id} - {tipo_ordem.value} {symbol}")
            logger.info(f"   Stop Loss: ${stop_loss:.2f} | Take Profit: ${take_profit:.2f}")
            
            return {
                'order_id': order_id,
                'config': config_ordem,
                'status': 'aberta'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao abrir ordem dinâmica: {e}")
            return {}
    
    def _calcular_stop_take_dinamico(self, tipo_ordem: TipoOrdem, preco_entrada: float,
                                   dados_mercado: Dict[str, Any], confianca_ia: float) -> Tuple[float, float]:
        """Calcula stop loss e take profit dinâmicos baseado na IA"""
        
        # Calcular take profit baseado na confiança e volatilidade
        volatilidade = dados_mercado.get('volatilidade', 0.02)
        rsi = dados_mercado.get('rsi', 50.0)
        tendencia = dados_mercado.get('tendencia', 'lateral')
        
        # Take profit dinâmico
        if tipo_ordem == TipoOrdem.COMPRA:
            # Para compras: take profit acima do preço de entrada
            take_profit_pct = 2.0 + (confianca_ia * 3.0)  # 2% a 5% baseado na confiança
            take_profit = preco_entrada * (1 + take_profit_pct / 100)
            
            # Ajustar baseado na tendência
            if tendencia == 'alta':
                take_profit *= 1.1
            elif tendencia == 'baixa':
                take_profit *= 0.9
            
        else:  # VENDA
            # Para vendas: take profit abaixo do preço de entrada
            take_profit_pct = 2.0 + (confianca_ia * 3.0)  # 2% a 5% baseado na confiança
            take_profit = preco_entrada * (1 - take_profit_pct / 100)
            
            # Ajustar baseado na tendência
            if tendencia == 'baixa':
                take_profit *= 0.9
            elif tendencia == 'alta':
                take_profit *= 1.1
        
        # Stop loss = 50% do alvo (conforme solicitado)
        if tipo_ordem == TipoOrdem.COMPRA:
            # Para compras: stop loss abaixo do preço de entrada
            stop_loss = preco_entrada - (abs(take_profit - preco_entrada) * 0.5)
        else:
            # Para vendas: stop loss acima do preço de entrada
            stop_loss = preco_entrada + (abs(preco_entrada - take_profit) * 0.5)
        
        # Validar valores para evitar valores irrealistas
        if tipo_ordem == TipoOrdem.COMPRA:
            # Stop loss não pode ser menor que 90% do preço de entrada
            stop_loss_min = preco_entrada * 0.90
            if stop_loss < stop_loss_min:
                stop_loss = stop_loss_min
        else:
            # Stop loss não pode ser maior que 110% do preço de entrada
            stop_loss_max = preco_entrada * 1.10
            if stop_loss > stop_loss_max:
                stop_loss = stop_loss_max
        
        return stop_loss, take_profit
    
    def _calcular_tempo_maximo(self, confianca_ia: float, dados_mercado: Dict[str, Any]) -> int:
        """Calcula tempo máximo dinâmico baseado na IA"""
        
        # Base: 5 minutos
        tempo_base = 300
        
        # Ajustar baseado na confiança
        if confianca_ia > 0.8:
            tempo_base = 180  # 3 minutos - mais agressivo
        elif confianca_ia < 0.5:
            tempo_base = 600  # 10 minutos - mais conservador
        
        # Ajustar baseado na volatilidade
        volatilidade = dados_mercado.get('volatilidade', 0.02)
        if volatilidade > 0.03:
            tempo_base = int(tempo_base * 0.7)  # Menos tempo em alta volatilidade
        elif volatilidade < 0.01:
            tempo_base = int(tempo_base * 1.3)  # Mais tempo em baixa volatilidade
        
        return max(60, min(1800, tempo_base))  # Entre 1 min e 30 min
    
    def ajustar_stop_loss_dinamico(self, order_id: str, preco_atual: float, 
                                 dados_mercado: Dict[str, Any]) -> bool:
        """
        Ajusta stop loss dinamicamente baseado na direção do preço
        
        Args:
            order_id: ID da ordem
            preco_atual: Preço atual do ativo
            dados_mercado: Dados atuais do mercado
            
        Returns:
            True se ajuste foi feito
        """
        try:
            if order_id not in self.ordens_ativas:
                return False
            
            ordem = self.ordens_ativas[order_id]
            config = ordem['config']
            tipo_ordem = TipoOrdem(ordem['tipo_ordem'])
            
            # Calcular novo stop loss
            novo_stop_loss = self._calcular_novo_stop_loss(
                tipo_ordem, preco_atual, config['stop_loss_atual'], 
                ordem['preco_entrada'], dados_mercado
            )
            
            # Verificar se deve ajustar
            if self._deve_ajustar_stop_loss(tipo_ordem, novo_stop_loss, config['stop_loss_atual']):
                # Registrar ajuste
                self._registrar_ajuste_dinamico(order_id, 'stop_loss', 
                                              config['stop_loss_atual'], novo_stop_loss,
                                              dados_mercado)
                
                # Atualizar configuração
                config['stop_loss_atual'] = novo_stop_loss
                ordem['ajustes_realizados'] += 1
                
                logger.info(f"🎯 Stop Loss ajustado: {order_id} - ${config['stop_loss_atual']:.2f} → ${novo_stop_loss:.2f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao ajustar stop loss: {e}")
            return False
    
    def _calcular_novo_stop_loss(self, tipo_ordem: TipoOrdem, preco_atual: float,
                               stop_loss_atual: float, preco_entrada: float,
                               dados_mercado: Dict[str, Any]) -> float:
        """Calcula novo stop loss baseado na direção do preço"""
        
        if tipo_ordem == TipoOrdem.COMPRA:
            # Para compras
            if preco_atual > preco_entrada:
                # Preço subindo - mover stop loss para cima (proteger lucro)
                distancia_atual = preco_atual - stop_loss_atual
                novo_stop_loss = preco_atual - (distancia_atual * 0.3)  # 30% da distância
                return max(stop_loss_atual, novo_stop_loss)  # Só move para cima
            else:
                # Preço caindo - manter stop loss atual
                return stop_loss_atual
                
        else:  # VENDA
            # Para vendas
            if preco_atual < preco_entrada:
                # Preço caindo - mover stop loss para baixo (proteger lucro)
                distancia_atual = stop_loss_atual - preco_atual
                novo_stop_loss = preco_atual + (distancia_atual * 0.3)  # 30% da distância
                return min(stop_loss_atual, novo_stop_loss)  # Só move para baixo
            else:
                # Preço subindo - manter stop loss atual
                return stop_loss_atual
    
    def _deve_ajustar_stop_loss(self, tipo_ordem: TipoOrdem, novo_stop_loss: float,
                              stop_loss_atual: float) -> bool:
        """Determina se deve ajustar o stop loss"""
        
        if tipo_ordem == TipoOrdem.COMPRA:
            # Para compras, só ajustar se novo stop loss for maior (proteger mais)
            return novo_stop_loss > stop_loss_atual
        else:
            # Para vendas, só ajustar se novo stop loss for menor (proteger mais)
            return novo_stop_loss < stop_loss_atual
    
    def ajustar_take_profit_dinamico(self, order_id: str, preco_atual: float,
                                   dados_mercado: Dict[str, Any]) -> bool:
        """
        Ajusta take profit dinamicamente baseado na IA
        
        Args:
            order_id: ID da ordem
            preco_atual: Preço atual do ativo
            dados_mercado: Dados atuais do mercado
            
        Returns:
            True se ajuste foi feito
        """
        try:
            if order_id not in self.ordens_ativas:
                return False
            
            ordem = self.ordens_ativas[order_id]
            config = ordem['config']
            tipo_ordem = TipoOrdem(ordem['tipo_ordem'])
            
            # Calcular novo take profit
            novo_take_profit = self._calcular_novo_take_profit(
                tipo_ordem, preco_atual, config['take_profit_atual'],
                ordem['preco_entrada'], dados_mercado, ordem['confianca_ia']
            )
            
            # Verificar se deve ajustar
            if self._deve_ajustar_take_profit(tipo_ordem, novo_take_profit, config['take_profit_atual']):
                # Registrar ajuste
                self._registrar_ajuste_dinamico(order_id, 'take_profit',
                                              config['take_profit_atual'], novo_take_profit,
                                              dados_mercado)
                
                # Atualizar configuração
                config['take_profit_atual'] = novo_take_profit
                
                logger.info(f"🎯 Take Profit ajustado: {order_id} - ${config['take_profit_atual']:.2f} → ${novo_take_profit:.2f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao ajustar take profit: {e}")
            return False
    
    def _calcular_novo_take_profit(self, tipo_ordem: TipoOrdem, preco_atual: float,
                                 take_profit_atual: float, preco_entrada: float,
                                 dados_mercado: Dict[str, Any], confianca_ia: float) -> float:
        """Calcula novo take profit baseado na análise da IA"""
        
        # Análise de mercado para ajustar take profit
        rsi = dados_mercado.get('rsi', 50.0)
        volatilidade = dados_mercado.get('volatilidade', 0.02)
        tendencia = dados_mercado.get('tendencia', 'lateral')
        
        if tipo_ordem == TipoOrdem.COMPRA:
            # Para compras
            if preco_atual > preco_entrada:
                # Preço subindo - pode aumentar take profit
                if rsi < 70 and tendencia == 'alta':
                    # Mercado ainda tem força, aumentar alvo
                    return take_profit_atual * 1.05
                elif rsi > 70:
                    # Mercado sobrecomprado, reduzir alvo
                    return take_profit_atual * 0.95
            else:
                # Preço caindo - reduzir alvo para sair mais rápido
                return take_profit_atual * 0.9
                
        else:  # VENDA
            # Para vendas
            if preco_atual < preco_entrada:
                # Preço caindo - pode aumentar take profit
                if rsi > 30 and tendencia == 'baixa':
                    # Mercado ainda tem força, aumentar alvo
                    return take_profit_atual * 0.95
                elif rsi < 30:
                    # Mercado sobrevendido, reduzir alvo
                    return take_profit_atual * 1.05
            else:
                # Preço subindo - reduzir alvo para sair mais rápido
                return take_profit_atual * 1.1
        
        return take_profit_atual
    
    def _deve_ajustar_take_profit(self, tipo_ordem: TipoOrdem, novo_take_profit: float,
                                take_profit_atual: float) -> bool:
        """Determina se deve ajustar o take profit"""
        
        if tipo_ordem == TipoOrdem.COMPRA:
            # Para compras, ajustar se novo take profit for melhor
            return abs(novo_take_profit - take_profit_atual) / take_profit_atual > 0.02  # 2% de diferença
        else:
            # Para vendas, ajustar se novo take profit for melhor
            return abs(novo_take_profit - take_profit_atual) / take_profit_atual > 0.02  # 2% de diferença
    
    def verificar_saida_inteligente(self, order_id: str, preco_atual: float,
                                  dados_mercado: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifica se deve sair da ordem baseado na análise inteligente da IA
        """
        try:
            if order_id not in self.ordens_ativas:
                return False, "Ordem não encontrada"
            ordem = self.ordens_ativas[order_id]
            config = ordem['config']
            tipo_ordem = TipoOrdem(ordem['tipo_ordem'])
            preco_entrada = ordem['preco_entrada']
            # Calcular lucro/prejuízo atual (percentual)
            if tipo_ordem == TipoOrdem.COMPRA:
                lucro_atual = (preco_atual - preco_entrada) / preco_entrada
            else:
                lucro_atual = (preco_entrada - preco_atual) / preco_entrada
            # Atualizar maior lucro já atingido
            if lucro_atual > ordem.get('maior_lucro_percentual', 0.0):
                ordem['maior_lucro_percentual'] = lucro_atual
            maior_lucro = ordem.get('maior_lucro_percentual', 0.0)
            razoes_saida = []
            # 0. Prejuízo excessivo (ex: -0.5%)
            limite_prejuizo = -0.005  # -0.5%
            if lucro_atual < limite_prejuizo:
                razoes_saida.append("Prejuízo excessivo")
            # 1. Lucro rápido (30 segundos com lucro)
            tempo_aberta = (datetime.now() - ordem['timestamp_abertura']).total_seconds()
            if tempo_aberta > 30 and lucro_atual > 0.002:  # 0.2% de lucro
                razoes_saida.append("Lucro rápido atingido")
            # 2. Mudança de tendência (agora sempre fecha, mesmo com prejuízo)
            tendencia_atual = dados_mercado.get('tendencia', 'lateral')
            if tipo_ordem == TipoOrdem.COMPRA and tendencia_atual == 'baixa':
                razoes_saida.append("Reversão: tendência mudou para baixa")
            elif tipo_ordem == TipoOrdem.VENDA and tendencia_atual == 'alta':
                razoes_saida.append("Reversão: tendência mudou para alta")
            # 3. RSI extremo
            rsi = dados_mercado.get('rsi', 50.0)
            if tipo_ordem == TipoOrdem.COMPRA and rsi > 75:
                razoes_saida.append("RSI sobrecomprado")
            elif tipo_ordem == TipoOrdem.VENDA and rsi < 25:
                razoes_saida.append("RSI sobrevendido")
            # 4. Volatilidade excessiva
            volatilidade = dados_mercado.get('volatilidade', 0.02)
            if volatilidade > 0.05 and lucro_atual > 0.005:  # 0.5% de lucro
                razoes_saida.append("Proteger lucro em alta volatilidade")
            # 5. Tempo máximo atingido
            if tempo_aberta > config['tempo_maximo_segundos']:
                razoes_saida.append("Tempo máximo atingido")
            # 6. Proteção de lucro (trailing stop dinâmico)
            if maior_lucro > 0.002:  # Só ativa se já teve pelo menos 0.2% de lucro
                # Definir trailing stop conforme lucro máximo
                if maior_lucro > 0.05:
                    trailing_pct = 0.10  # 10% do lucro máximo
                elif maior_lucro > 0.02:
                    trailing_pct = 0.20  # 20% do lucro máximo
                else:
                    trailing_pct = 0.30  # 30% do lucro máximo
                if lucro_atual < maior_lucro * (1 - trailing_pct):
                    razoes_saida.append(f"Proteção de lucro: trailing stop dinâmico ({trailing_pct*100:.0f}% do lucro máximo {maior_lucro*100:.2f}%)")
            # 7. Lucro persistente: mais de 2min com lucro >1%
            if tempo_aberta > 120 and lucro_atual > 0.01:
                razoes_saida.append("Lucro persistente: mais de 2min com lucro >1%")
            deve_sair = len(razoes_saida) > 0
            razao = " | ".join(razoes_saida) if razoes_saida else "Continuar"
            return deve_sair, razao
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saída inteligente: {e}")
            return False, f"Erro: {e}"
    
    def fechar_ordem_dinamica(self, order_id: str, preco_saida: float, razao_saida: str, dados_mercado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fecha ordem dinâmica e registra aprendizado
        """
        try:
            if order_id not in self.ordens_ativas:
                return {}
            
            ordem = self.ordens_ativas[order_id]
            tipo_ordem = TipoOrdem(ordem['tipo_ordem'])
            preco_entrada = ordem['preco_entrada']
            quantidade = ordem['quantidade']
            # Corrigir cálculo do PnL: sempre em USDT
            if tipo_ordem == TipoOrdem.COMPRA:
                lucro_prejuizo = (preco_saida - preco_entrada) * quantidade
            else:
                lucro_prejuizo = (preco_entrada - preco_saida) * quantidade
            # Calcular tempo aberta
            tempo_aberta = (datetime.now() - ordem['timestamp_abertura']).total_seconds()
            sucesso = lucro_prejuizo > 0
            self._registrar_fechamento_ordem(order_id, preco_saida, lucro_prejuizo, tempo_aberta, razao_saida, dados_mercado)
            self._registrar_aprendizado_saida(order_id, razao_saida, tempo_aberta, lucro_prejuizo, ordem['confianca_ia'], sucesso)
            # Aprendizado IA global
            if self.decisor_ia is not None:
                symbol = ordem['symbol']
                resultado = 'win' if lucro_prejuizo > 0 else 'loss'
                try:
                    self.decisor_ia.registrar_resultado_operacao(symbol, resultado, lucro_prejuizo)
                except Exception as e:
                    logger.error(f"Erro ao registrar aprendizado global IA: {e}")
            # --- REGISTRO DE APRENDIZADO DETALHADO ---
            try:
                from ia.sistema_aprendizado import SistemaAprendizado
                config = ordem.get('config')
                dados_aprendizado = {
                    'ordem_id': order_id,
                    'confianca_ia': ordem.get('confianca_ia', 0),
                    'tipo': ordem.get('tipo_ordem', ''),
                    'preco_entrada': preco_entrada,
                    'preco_saida': preco_saida,
                    'quantidade': quantidade,
                    'timestamp_abertura': ordem.get('timestamp_abertura'),
                    'timestamp_fechamento': datetime.now(),
                    'razao_fechamento': razao_saida,
                    'stop_loss': config['stop_loss_atual'] if config else None,
                    'take_profit': config['take_profit_atual'] if config else None,
                    'dados_mercado_saida': dados_mercado,
                }
                # Adicionar indicadores se existirem
                if isinstance(dados_mercado, dict):
                    for k in ['rsi', 'volatilidade', 'tendencia', 'volume']:
                        if k in dados_mercado:
                            dados_aprendizado[k] = dados_mercado[k]
                # Chamar registro detalhado se sistema_aprendizado estiver disponível
                if hasattr(self, 'sistema_aprendizado') and self.sistema_aprendizado is not None:
                    self.sistema_aprendizado.registrar_aprendizado_ordem(
                        dados_aprendizado,
                        'win' if sucesso else 'loss',
                        lucro_prejuizo,
                        dados_mercado
                    )
                    logger.info(f"[APRENDIZADO] Detalhado registrado para ordem {order_id} | Resultado: {'win' if sucesso else 'loss'} | PnL: {lucro_prejuizo:.4f}")
                else:
                    logger.warning(f"[APRENDIZADO] sistema_aprendizado não está disponível para registrar aprendizado detalhado da ordem {order_id}.")
            except Exception as e:
                logger.error(f"Erro ao registrar aprendizado detalhado: {e}")
            # --- FIM REGISTRO DETALHADO ---
            del self.ordens_ativas[order_id]
            logger.info(f"🎯 Ordem fechada: {order_id} - PnL USDT: {lucro_prejuizo:.4f} ({razao_saida})")
            return {
                'order_id': order_id,
                'lucro_prejuizo': lucro_prejuizo,
                'tempo_aberta': tempo_aberta,
                'razao_saida': razao_saida,
                'sucesso': sucesso
            }
        except Exception as e:
            logger.error(f"❌ Erro ao fechar ordem: {e}")
            return {}
    
    def _iniciar_monitoramento(self):
        """Inicia thread de monitoramento das ordens"""
        self.monitoramento_ativo = True
        self.thread_monitoramento = threading.Thread(target=self._monitorar_ordens)
        self.thread_monitoramento.daemon = True
        self.thread_monitoramento.start()
        logger.info("🔄 Monitoramento de ordens iniciado")
    
    def _monitorar_ordens(self):
        """Thread de monitoramento das ordens ativas"""
        while self.monitoramento_ativo:
            try:
                # Processar cada ordem ativa
                for order_id in list(self.ordens_ativas.keys()):
                    try:
                        ordem = self.ordens_ativas[order_id]
                        # Adicionar order_id à ordem para o processamento
                        ordem['order_id'] = order_id
                        dados_mercado = self._obter_dados_mercado_simulados(ordem['symbol'])
                        
                        # Processar ordem e verificar se foi fechada
                        if self._processar_ordem_ativa(ordem, dados_mercado):
                            # Ordem foi fechada, remover da lista de ordens ativas
                            if order_id in self.ordens_ativas:
                                del self.ordens_ativas[order_id]
                                logger.info(f"🗑️ Ordem {order_id} removida da lista de ordens ativas")
                    except Exception as e:
                        logger.error(f"❌ Erro ao processar ordem {order_id}: {e}")
                
                time.sleep(5)  # Verificar a cada 5 segundos
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(10)
    
    def _processar_ordem_ativa(self, ordem: Dict[str, Any], dados_mercado: Dict[str, Any]) -> bool:
        """Processa uma ordem ativa e decide se deve fechar"""
        try:
            order_id = ordem['order_id']
            symbol = ordem['symbol']
            preco_atual = dados_mercado.get('preco_atual', 0)
            
            if not preco_atual:
                logger.warning(f"Preço atual não disponível para {symbol}")
                return False
            
            # Verificar se tem timestamp de abertura
            if not ordem.get('timestamp_abertura'):
                logger.warning(f"Ordem {order_id} sem timestamp_abertura. Não será possível calcular tempo_aberta corretamente.")
                return False
            
            # Calcular tempo que a ordem está aberta
            tempo_aberta = (datetime.now() - ordem['timestamp_abertura']).total_seconds()
            
            # Verificar se atingiu tempo máximo
            tempo_maximo = ordem.get('config', {}).get('tempo_maximo_segundos', 300)  # 5 minutos padrão
            if tempo_aberta > tempo_maximo:
                logger.info(f"⏰ Ordem {order_id} atingiu tempo máximo ({tempo_maximo}s). Fechando automaticamente.")
                self._fechar_ordem_por_tempo(order_id, "Tempo máximo excedido")
                return True
            
            # Verificar stop loss e take profit
            preco_entrada = ordem['preco_entrada']
            tipo_ordem = ordem['tipo_ordem']
            
            # Obter stop loss e take profit em preços absolutos
            stop_loss_preco = ordem.get('config', {}).get('stop_loss_atual', preco_entrada * 0.95)
            take_profit_preco = ordem.get('config', {}).get('take_profit_atual', preco_entrada * 1.05)
            
            if tipo_ordem == 'compra':
                # Verificar stop loss
                if preco_atual <= stop_loss_preco:
                    logger.info(f"🛑 Stop Loss atingido para {order_id}: {preco_atual:.2f} <= {stop_loss_preco:.2f}")
                    self._fechar_ordem_por_stop_loss(order_id, preco_atual, stop_loss_preco)
                    return True
                
                # Verificar take profit
                if preco_atual >= take_profit_preco:
                    logger.info(f"🎯 Take Profit atingido para {order_id}: {preco_atual:.2f} >= {take_profit_preco:.2f}")
                    self._fechar_ordem_por_take_profit(order_id, preco_atual, take_profit_preco)
                    return True
                    
            elif tipo_ordem == 'venda':
                # Verificar stop loss
                if preco_atual >= stop_loss_preco:
                    logger.info(f"🛑 Stop Loss atingido para {order_id}: {preco_atual:.2f} >= {stop_loss_preco:.2f}")
                    self._fechar_ordem_por_stop_loss(order_id, preco_atual, stop_loss_preco)
                    return True
                
                # Verificar take profit
                if preco_atual <= take_profit_preco:
                    logger.info(f"🎯 Take Profit atingido para {order_id}: {preco_atual:.2f} <= {take_profit_preco:.2f}")
                    self._fechar_ordem_por_take_profit(order_id, preco_atual, take_profit_preco)
                    return True
            
            # Consultar IA para decisão sobre a ordem
            if self.decisor_ia:
                decisao_ia = self.decisor_ia.decidir_ordem_aberta(ordem, dados_mercado)
            else:
                decisao_ia = None
            
            if decisao_ia:
                acao = decisao_ia.get('acao_ordem', 'manter')
                logger.info(f"[IA] Ação sugerida para ordem {order_id}: {decisao_ia}")
                
                if acao == 'fechar':
                    logger.info(f"🤖 IA sugeriu fechar ordem {order_id}")
                    self._fechar_ordem_por_decisao_ia(order_id, decisao_ia.get('razao', 'Decisão da IA'))
                    return True
                elif acao == 'ajustar':
                    # Ajustar stop loss/take profit se necessário
                    self._ajustar_parametros_ordem(order_id, decisao_ia)
            
            return False
            
        except Exception as e:
            order_id = ordem.get('order_id', 'UNKNOWN') if 'ordem' in locals() else 'UNKNOWN'
            logger.error(f"Erro ao processar ordem {order_id}: {e}")
            return False

    def _fechar_ordem_por_tempo(self, order_id: str, motivo: str):
        """Fecha ordem por tempo máximo excedido"""
        try:
            # Obter preço atual da ordem em memória
            preco_atual = None
            if order_id in self.ordens_ativas:
                # Usar preço de entrada como aproximação
                preco_atual = self.ordens_ativas[order_id]['preco_entrada']
            
            # Buscar ordem no banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ordens_dinamicas 
                SET status = 'fechada', 
                    timestamp_fechamento = ?, 
                    razao_saida = ?,
                    preco_saida = ?
                WHERE order_id = ?
            """, (datetime.now(), motivo, preco_atual, order_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Ordem {order_id} fechada por tempo: {motivo}")
            
        except Exception as e:
            logger.error(f"Erro ao fechar ordem {order_id} por tempo: {e}")

    def _fechar_ordem_por_stop_loss(self, order_id: str, preco_atual: float, stop_loss_preco: float):
        """Fecha ordem por stop loss"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ordens_dinamicas 
                SET status = 'fechada', 
                    timestamp_fechamento = ?, 
                    razao_saida = ?,
                    preco_saida = ?
                WHERE order_id = ?
            """, (datetime.now(), f"Stop Loss: {preco_atual:.2f} <= {stop_loss_preco:.2f}", preco_atual, order_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🛑 Ordem {order_id} fechada por Stop Loss")
            
        except Exception as e:
            logger.error(f"Erro ao fechar ordem {order_id} por stop loss: {e}")

    def _fechar_ordem_por_take_profit(self, order_id: str, preco_atual: float, take_profit_preco: float):
        """Fecha ordem por take profit"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ordens_dinamicas 
                SET status = 'fechada', 
                    timestamp_fechamento = ?, 
                    razao_saida = ?,
                    preco_saida = ?
                WHERE order_id = ?
            """, (datetime.now(), f"Take Profit: {preco_atual:.2f} >= {take_profit_preco:.2f}", preco_atual, order_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🎯 Ordem {order_id} fechada por Take Profit")
            
        except Exception as e:
            logger.error(f"Erro ao fechar ordem {order_id} por take profit: {e}")

    def _fechar_ordem_por_decisao_ia(self, order_id: str, motivo: str):
        """Fecha ordem por decisão da IA"""
        try:
            # Obter preço atual da ordem em memória
            preco_atual = None
            if order_id in self.ordens_ativas:
                # Usar preço de entrada como aproximação
                preco_atual = self.ordens_ativas[order_id]['preco_entrada']
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ordens_dinamicas 
                SET status = 'fechada', 
                    timestamp_fechamento = ?, 
                    razao_saida = ?,
                    preco_saida = ?
                WHERE order_id = ?
            """, (datetime.now(), f"IA: {motivo}", preco_atual, order_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🤖 Ordem {order_id} fechada por decisão da IA: {motivo}")
            
        except Exception as e:
            logger.error(f"Erro ao fechar ordem {order_id} por decisão IA: {e}")

    def _ajustar_parametros_ordem(self, order_id: str, decisao_ia: Dict[str, Any]):
        """Ajusta parâmetros da ordem baseado na decisão da IA"""
        try:
            # Implementar ajuste de stop loss/take profit se necessário
            # Por enquanto, apenas log
            logger.info(f"🔧 Ajuste de parâmetros para ordem {order_id}: {decisao_ia}")
            
        except Exception as e:
            logger.error(f"Erro ao ajustar parâmetros da ordem {order_id}: {e}")
    
    def _verificar_stop_loss(self, order_id: str, preco_atual: float, tipo_ordem: str) -> bool:
        """Verifica se stop loss foi atingido"""
        ordem = self.ordens_ativas[order_id]
        stop_loss = ordem['config']['stop_loss_atual']
        
        if tipo_ordem == 'compra':
            return preco_atual <= stop_loss
        else:
            return preco_atual >= stop_loss
    
    def _verificar_take_profit(self, order_id: str, preco_atual: float, tipo_ordem: str) -> bool:
        """Verifica se take profit foi atingido"""
        ordem = self.ordens_ativas[order_id]
        take_profit = ordem['config']['take_profit_atual']
        
        if tipo_ordem == 'compra':
            return preco_atual >= take_profit
        else:
            return preco_atual <= take_profit
    
    def _obter_dados_mercado_simulados(self, symbol=None, ultimo_preco=None) -> Dict[str, Any]:
        """Simula dados de mercado de forma realista: preço varia até 0.1% por ciclo em relação ao último preço."""
        # Buscar último preço de ordem aberta se não informado
        if symbol and ultimo_preco is None:
            for ordem in self.ordens_ativas.values():
                if ordem['symbol'] == symbol:
                    ultimo_preco = ordem['preco_entrada']
                    break
        if ultimo_preco is None:
            logger.error("Nenhum preço de entrada encontrado para o símbolo. Não é possível simular o mercado.")
            return {} # Retorna um dicionário vazio para indicar erro
        import random
        variacao = 1 + random.uniform(-0.001, 0.001)  # até 0.1% para cima ou para baixo
        preco_atual = ultimo_preco * variacao
        return {
            'preco_atual': preco_atual,
            'rsi': 50.0 + random.uniform(-10, 10),
            'volatilidade': abs(variacao - 1),
            'tendencia': random.choice(['alta', 'baixa', 'lateral'])
        }
    
    def _salvar_ordem_dinamica(self, order_id: str, symbol: str, tipo_ordem: TipoOrdem,
                             preco_entrada: float, quantidade: float, config: ConfiguracaoOrdem):
        """Salva ordem dinâmica no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ordens_dinamicas 
                (order_id, symbol, tipo_ordem, preco_entrada, quantidade,
                 stop_loss_inicial, take_profit_inicial, stop_loss_atual, take_profit_atual, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id, symbol, tipo_ordem.value, preco_entrada, quantidade,
                config.stop_loss_inicial, config.take_profit_inicial,
                config.stop_loss_atual, config.take_profit_atual, 'aberta'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar ordem dinâmica: {e}")
    
    def _registrar_ajuste_dinamico(self, order_id: str, tipo_ajuste: str,
                                 valor_anterior: float, valor_novo: float,
                                 dados_mercado: Dict[str, Any]):
        """Registra ajuste dinâmico no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ajustes_dinamicos 
                (order_id, tipo_ajuste, valor_anterior, valor_novo, razao_ajuste, dados_mercado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_id, tipo_ajuste, valor_anterior, valor_novo,
                f"Ajuste automático baseado em {dados_mercado.get('tendencia', 'mercado')}",
                json.dumps(dados_mercado)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar ajuste: {e}")
    
    def _registrar_fechamento_ordem(self, order_id: str, preco_saida: float,
                                  lucro_prejuizo: float, tempo_aberta: float,
                                  razao_saida: str, dados_mercado: Dict[str, Any]):
        """Registra fechamento da ordem no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ordens_dinamicas SET
                status = ?, timestamp_fechamento = ?, preco_saida = ?,
                lucro_prejuizo = ?, tempo_aberta_segundos = ?, razao_saida = ?,
                dados_mercado_saida = ?
                WHERE order_id = ?
            """, (
                'fechada', datetime.now(), preco_saida, lucro_prejuizo,
                tempo_aberta, razao_saida, json.dumps(dados_mercado), order_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar fechamento: {e}")
    
    def _registrar_aprendizado_saida(self, order_id: str, tipo_saida: str,
                                   tempo_aberta: float, lucro_prejuizo: float,
                                   confianca_saida: float, sucesso: bool):
        """Registra aprendizado sobre saídas"""
        try:
            aprendizado = self._gerar_aprendizado_saida(tipo_saida, tempo_aberta, sucesso)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO aprendizado_saidas 
                (order_id, tipo_saida, tempo_aberta_segundos, lucro_prejuizo,
                 confianca_saida, razao_saida, sucesso, aprendizado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id, tipo_saida, tempo_aberta, lucro_prejuizo,
                confianca_saida, tipo_saida, sucesso, aprendizado
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar aprendizado: {e}")
    
    def _gerar_aprendizado_saida(self, tipo_saida: str, tempo_aberta: float, sucesso: bool) -> str:
        """Gera aprendizado sobre a saída"""
        if sucesso:
            if tempo_aberta < 60:
                return "Saída rápida bem-sucedida - repetir estratégia"
            elif tempo_aberta < 300:
                return "Saída média bem-sucedida - estratégia eficaz"
            else:
                return "Saída lenta bem-sucedida - ser mais paciente"
        else:
            if tempo_aberta < 60:
                return "Saída rápida mal-sucedida - aguardar mais"
            elif tempo_aberta < 300:
                return "Saída média mal-sucedida - ajustar critérios"
            else:
                return "Saída lenta mal-sucedida - ser mais agressivo"
    
    def obter_estatisticas_gestao(self) -> Dict[str, Any]:
        """Retorna estatísticas da gestão dinâmica"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de ordens
            cursor.execute("SELECT COUNT(*) FROM ordens_dinamicas")
            total_ordens = cursor.fetchone()[0]
            
            # Ordens fechadas
            cursor.execute("SELECT COUNT(*) FROM ordens_dinamicas WHERE status = 'fechada'")
            ordens_fechadas = cursor.fetchone()[0]
            
            # Lucro total
            cursor.execute("SELECT SUM(lucro_prejuizo) FROM ordens_dinamicas WHERE status = 'fechada'")
            lucro_total = cursor.fetchone()[0] or 0
            
            # Tempo médio
            cursor.execute("SELECT AVG(tempo_aberta_segundos) FROM ordens_dinamicas WHERE status = 'fechada'")
            tempo_medio = cursor.fetchone()[0] or 0
            
            # Ajustes realizados
            cursor.execute("SELECT COUNT(*) FROM ajustes_dinamicos")
            total_ajustes = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_ordens': total_ordens,
                'ordens_fechadas': ordens_fechadas,
                'ordens_ativas': len(self.ordens_ativas),
                'lucro_total': lucro_total,
                'tempo_medio_segundos': tempo_medio,
                'total_ajustes': total_ajustes
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def parar_monitoramento(self):
        """Para o monitoramento de ordens"""
        self.monitoramento_ativo = False
        if self.thread_monitoramento:
            self.thread_monitoramento.join(timeout=5)
        logger.info("🛑 Monitoramento de ordens parado") 

    def carregar_ordens_abertas(self):
        """Reimporta ordens abertas do banco para o dicionário ordens_ativas ao iniciar o robô"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT order_id, symbol, tipo_ordem, preco_entrada, quantidade, stop_loss_atual, take_profit_atual, timestamp_abertura FROM ordens_dinamicas WHERE status = 'aberta'")
            rows = cursor.fetchall()
            for row in rows:
                order_id, symbol, tipo_ordem, preco_entrada, quantidade, stop_loss, take_profit, timestamp_abertura = row
                self.ordens_ativas[order_id] = {
                    'symbol': symbol,
                    'tipo_ordem': tipo_ordem,
                    'preco_entrada': preco_entrada,
                    'quantidade': quantidade,
                    'config': {
                        'stop_loss_inicial': stop_loss,
                        'take_profit_inicial': take_profit,
                        'stop_loss_atual': stop_loss,
                        'take_profit_atual': take_profit,
                        'tempo_maximo_segundos': 300
                    },
                    'timestamp_abertura': datetime.fromisoformat(timestamp_abertura) if isinstance(timestamp_abertura, str) else (timestamp_abertura if isinstance(timestamp_abertura, datetime) else datetime.now()),
                    'confianca_ia': 0.5,  # Valor padrão para ordens carregadas
                    'ajustes_realizados': 0
                }
                logger.info(f"♻️ Ordem reimportada para monitoramento: {order_id}")
            conn.close()
        except Exception as e:
            logger.error(f"❌ Erro ao reimportar ordens abertas: {e}") 