#!/usr/bin/env python3
"""
Executor Simulado para Treinamento da IA
Simula execução de ordens sem enviar para a exchange real
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from loguru import logger
import sqlite3
import os
import random
from gestor_ordens_dinamico import GestorOrdensDinamico, TipoOrdem

class ExecutorSimulado:
    """Executor que simula operações para treinamento da IA, com ciclo realista de ordens"""
    
    def __init__(self, config: Dict[str, Any], db_path: str = "dados/trading.db"):
        self.config = config
        self.db_path = db_path
        self.capital_atual = config['simulacao']['capital_inicial']
        self.gestor_ordens = GestorOrdensDinamico(db_path)
        self.ordens_ativas: Dict[str, Dict[str, Any]] = {}  # order_id -> info
        self.operacoes_realizadas = 0
        self.max_operacoes = config['simulacao']['max_operacoes']
        self.estatisticas = {
            'total_operacoes': 0,
            'operacoes_lucro': 0,
            'operacoes_prejuizo': 0,
            'lucro_total': 0.0,
            'prejuizo_total': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0
        }
        self._criar_tabelas()
        logger.info(f"🎮 Executor Simulado REALISTA inicializado com capital: ${self.capital_atual:.2f}")

    def _criar_tabelas(self):
        # Já criado pelo gestor_ordens_dinamico
        pass

    def enviar_ordem_market(self, symbol, side, qty, dados_mercado=None, confianca=None):
        """
        Simula envio de ordem market: abre ordem dinâmica e monitora até fechar por stop/take
        """
        if self.operacoes_realizadas >= self.max_operacoes:
            logger.warning(f"⚠️ Limite de {self.max_operacoes} operações atingido")
            return None
        if qty is None:
            qty = 0.001 if "BTC" in symbol else 0.01
        preco_entrada = self._simular_preco_execucao(symbol, side)
        order_id = f"SIM_{int(time.time() * 1000)}"
        tipo_ordem = TipoOrdem.COMPRA if side.lower() == 'buy' else TipoOrdem.VENDA
        # Abrir ordem dinâmica
        self.gestor_ordens.abrir_ordem_dinamica(
            order_id, symbol, tipo_ordem, preco_entrada, qty, dados_mercado or {}, confianca if confianca is not None else 0.5
        )
        self.ordens_ativas[order_id] = {
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'preco_entrada': preco_entrada,
            'timestamp_abertura': datetime.now(),
            'tipo_ordem': tipo_ordem
        }
        self.operacoes_realizadas += 1
        logger.info(f"🟢 Ordem dinâmica aberta: {order_id} {side} {qty} {symbol} @ {preco_entrada:.2f}")
        return {
            'orderId': order_id,
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'avgPrice': preco_entrada,
            'orderStatus': 'Open',
            'execTime': int(time.time() * 1000),
            'capital_atual': self.capital_atual
        }

    def simular_tempo_real(self, duracao_segundos=60, intervalo_tick=2):
        """
        Simula ticks de preço e monitora ordens abertas, fechando por stop/take
        """
        logger.info(f"⏳ Iniciando simulação de mercado por {duracao_segundos}s...")
        inicio = time.time()
        while time.time() - inicio < duracao_segundos:
            self._tick_simulacao()
            time.sleep(intervalo_tick)
        logger.info("⏹️ Simulação de mercado encerrada.")

    def _tick_simulacao(self):
        """
        Simula um tick de mercado: atualiza preço e verifica fechamento de ordens
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Buscar ordens abertas
        cursor.execute("SELECT order_id, symbol, tipo_ordem, preco_entrada, quantidade, stop_loss_atual, take_profit_atual, status FROM ordens_dinamicas WHERE status = 'aberta'")
        ordens = cursor.fetchall()
        for ordem in ordens:
            order_id, symbol, tipo_ordem, preco_entrada, quantidade, stop_loss, take_profit, status = ordem
            preco_atual = self._simular_preco_tick(symbol)
            # Verificar stop/take
            if tipo_ordem == 'compra':
                if preco_atual <= stop_loss:
                    self.gestor_ordens.fechar_ordem_dinamica(order_id, preco_atual, 'stop_loss', {'preco_atual': preco_atual})
                    logger.info(f"🔴 Ordem {order_id} FECHADA por STOP LOSS @ {preco_atual:.2f}")
                elif preco_atual >= take_profit:
                    self.gestor_ordens.fechar_ordem_dinamica(order_id, preco_atual, 'take_profit', {'preco_atual': preco_atual})
                    logger.info(f"🟢 Ordem {order_id} FECHADA por TAKE PROFIT @ {preco_atual:.2f}")
            else:  # venda
                if preco_atual >= stop_loss:
                    self.gestor_ordens.fechar_ordem_dinamica(order_id, preco_atual, 'stop_loss', {'preco_atual': preco_atual})
                    logger.info(f"🔴 Ordem {order_id} FECHADA por STOP LOSS @ {preco_atual:.2f}")
                elif preco_atual <= take_profit:
                    self.gestor_ordens.fechar_ordem_dinamica(order_id, preco_atual, 'take_profit', {'preco_atual': preco_atual})
                    logger.info(f"🟢 Ordem {order_id} FECHADA por TAKE PROFIT @ {preco_atual:.2f}")
        conn.close()

    def _simular_preco_execucao(self, symbol: str, side: str) -> float:
        precos_base = {'BTCUSDT': 117000.0, 'ETHUSDT': 3100.0}
        preco_base = precos_base.get(symbol, 100.0)
        variacao = random.uniform(-0.001, 0.001)
        return preco_base * (1 + variacao)

    def _simular_preco_tick(self, symbol: str) -> float:
        # Simula variação de preço a cada tick
        precos_base = {'BTCUSDT': 117000.0, 'ETHUSDT': 3100.0}
        preco_base = precos_base.get(symbol, 100.0)
        variacao = random.uniform(-0.01, 0.01)  # ±1%
        return preco_base * (1 + variacao) 

    def obter_estatisticas_ordens_simuladas(self):
        """Obtém estatísticas detalhadas das ordens simuladas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT lucro_prejuizo FROM ordens_dinamicas WHERE status = 'fechada'")
        resultados = cursor.fetchall()
        conn.close()
        total = len(resultados)
        wins = sum(1 for (lucro,) in resultados if lucro is not None and lucro > 0)
        losses = sum(1 for (lucro,) in resultados if lucro is not None and lucro < 0)
        neutras = sum(1 for (lucro,) in resultados if lucro is not None and lucro == 0)
        pnl_total = sum(lucro for (lucro,) in resultados if lucro is not None)
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0.0
        return {
            'total': total,
            'wins': wins,
            'losses': losses,
            'neutras': neutras,
            'win_rate': win_rate,
            'pnl_total': pnl_total
        } 