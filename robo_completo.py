#!/usr/bin/env python3
"""
🤖 ROBÔ COMPLETO DE TRADING CRYPTO
===================================

Sistema completo que integra:
✅ Coleta de dados em tempo real
✅ IA com aprendizado autônomo  
✅ Gestão dinâmica de ordens
✅ Modo simulação/real
✅ Monitoramento completo
✅ Estatísticas em tempo real

Autor: Sistema de Trading Crypto
Data: Julho 2025
"""

import sys
import time
import signal
import yaml
import json
import threading
from queue import Queue, Empty
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from loguru import logger

# Importar componentes
from coletor import ColetorBybit
from executor_simulado import ExecutorSimulado
from executor import ExecutorBybit
from armazenamento import ArmazenamentoCrypto
from gestor_ordens_dinamico import GestorOrdensDinamico, TipoOrdem

# Importar IA
from ia.decisor import DecisorIA
from ia.sistema_aprendizado_autonomo import SistemaAprendizadoAutonomo
from ia.llama_cpp_client import LlamaCppClient

class RoboCompleto:
    """Robô completo que integra todos os componentes"""
    
    def __init__(self):
        """Inicializa o robô completo"""
        self.config = self._carregar_config()
        self.executando = False
        self.ciclos_executados = 0
        
        # Componentes principais
        self.coletor = None
        self.executor = None
        self.armazenamento = None
        self.decisor = None
        self.sistema_aprendizado = None
        self.gestor_ordens = None
        self.ai_client = LlamaCppClient()
        
        # Estatísticas
        self.estatisticas = {
            'ciclos_executados': 0,
            'analises_realizadas': 0,
            'decisoes_tomadas': 0,
            'ordens_executadas': 0,
            'wins': 0,
            'losses': 0,
            'capital_inicial': 0,
            'capital_atual': 0,
            'inicio_execucao': None
        }
        
        # Configurar sinais para parada graciosa
        self._configurar_sinais()
        
        self.buffer_dados = Queue(maxsize=1000)  # Buffer thread-safe para candles/dados
        self.analise_ia_intervalo = self.config.get('batch_interval', 5)
        logger.info(f"⏳ Intervalo de análise em lote (batch_interval): {self.analise_ia_intervalo} segundos")
        self.thread_analise_ia = None
        self._parar_threads = threading.Event()
        
        logger.info("🚀 Robô Completo inicializando...")
    
    def _carregar_config(self) -> dict:
        """Carrega configurações"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"❌ Erro ao carregar config.yaml: {e}")
            sys.exit(1)
    
    def _configurar_sinais(self):
        """Configura handlers para sinais de parada"""
        signal.signal(signal.SIGINT, self._handler_parada)
        signal.signal(signal.SIGTERM, self._handler_parada)
    
    def _handler_parada(self, signum, frame):
        """Handler para parada graciosa"""
        logger.info("🛑 Sinal de parada recebido. Finalizando...")
        self.executando = False
        self.fechar_todas_ordens()
        self.parar()

    def fechar_todas_ordens(self):
        """Fecha todas as ordens abertas imediatamente"""
        if self.gestor_ordens and hasattr(self.gestor_ordens, 'ordens_ativas'):
            ordens_ativas = list(self.gestor_ordens.ordens_ativas.values())
            for ordem in ordens_ativas:
                try:
                    order_id = ordem.get('order_id') or ordem.get('ordem_id')
                    if order_id is None:
                        logger.warning(f"Ordem sem order_id: {ordem}. Usando fallback para fechamento.")
                        order_id = str(ordem)
                    symbol = ordem.get('symbol')
                    preco_atual = ordem.get('preco_atual', ordem.get('preco_entrada', 0))
                    razao = 'Fechamento forçado por Ctrl+C'
                    dados_mercado = {'forcado': True}
                    self.gestor_ordens.fechar_ordem_dinamica(str(order_id), preco_atual, razao, dados_mercado)
                    logger.info(f"🔴 Ordem {order_id} ({symbol}) fechada por parada do sistema.")
                except Exception as e:
                    logger.error(f"Erro ao fechar ordem {ordem}: {e}")
        else:
            logger.info("Nenhuma ordem ativa para fechar.")
    
    def inicializar_componentes(self):
        """Inicializa todos os componentes do sistema"""
        try:
            logger.info("🔧 Inicializando componentes...")
            
            # 1. Armazenamento
            logger.info("📊 Inicializando armazenamento...")
            self.armazenamento = ArmazenamentoCrypto()
            
            # 2. Coletor
            logger.info("📡 Inicializando coletor...")
            self.coletor = ColetorBybit()
            
            # 3. Sistema de Aprendizado Autônomo
            logger.info("🧠 Inicializando sistema de aprendizado...")
            self.sistema_aprendizado = SistemaAprendizadoAutonomo()
            
            # 4. Decisor IA
            logger.info("🤖 Inicializando decisor IA...")
            self.decisor = DecisorIA(self.config, sistema_aprendizado=self.sistema_aprendizado, ia_client=self.ai_client)
            
            # 5. Gestor de Ordens Dinâmico
            logger.info("🎯 Inicializando gestor de ordens...")
            risco_maximo = self.config.get('risco_maximo_permitido', 3.0)
            # Se estiver dentro de 'risco', ler de lá
            if 'risco' in self.config and 'risco_maximo_permitido' in self.config['risco']:
                risco_maximo = self.config['risco']['risco_maximo_permitido']
            self.gestor_ordens = GestorOrdensDinamico(risco_maximo_permitido=risco_maximo, decisor_ia=self.decisor, sistema_aprendizado=self.sistema_aprendizado)
            
            # 6. Executor (Simulado ou Real)
            if self.config['simulacao']['ativo']:
                logger.info("🎮 Inicializando executor simulado...")
                self.executor = ExecutorSimulado(self.config)
                # self.executor.decisor_ia = self.decisor  # Removido: atributo não existe
                # self.executor.gestor_ordens = self.gestor_ordens  # Removido: atributo não existe
                self.estatisticas['capital_inicial'] = self.config['simulacao']['capital_inicial']
                self.estatisticas['capital_atual'] = self.config['simulacao']['capital_inicial']
            else:
                logger.info("💰 Inicializando executor real...")
                self.executor = ExecutorBybit()
            
            # 7. Reimportar ordens abertas do banco ao iniciar
            if self.gestor_ordens and hasattr(self.gestor_ordens, 'carregar_ordens_abertas'):
                self.gestor_ordens.carregar_ordens_abertas()
            # Processar ordens abertas ao iniciar
            self.processar_ordens_abertas_ao_iniciar()
            
            logger.success("✅ Todos os componentes inicializados!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar componentes: {e}")
            return False

    def processar_ordens_abertas_ao_iniciar(self):
        """Processa todas as ordens abertas ao iniciar: atualiza PnL, status e fecha se necessário."""
        if not self.gestor_ordens or not hasattr(self.gestor_ordens, 'ordens_ativas'):
            logger.info("Nenhuma ordem ativa para processar ao iniciar.")
            return
        for ordem_id, ordem in list(self.gestor_ordens.ordens_ativas.items()):
            symbol = ordem.get('symbol')
            preco_entrada = ordem.get('preco_entrada')
            quantidade = ordem.get('quantidade', 1)
            if not symbol or preco_entrada is None:
                logger.warning(f"Ordem {ordem_id} sem dados suficientes para análise inicial.")
                continue
            # Buscar preço atual
            preco_atual = None
            if not self.coletor or not hasattr(self.coletor, 'obter_preco_atual'):
                logger.warning(f"Coletor não disponível para obter preço de {symbol}. PnL não atualizado.")
                continue
            try:
                preco_atual = self.coletor.obter_preco_atual(symbol)
            except Exception as e:
                logger.error(f"Erro ao obter preço atual de {symbol}: {e}")
            if preco_atual is None:
                continue
            # Calcular PnL
            pnl = (preco_atual - preco_entrada) * quantidade if ordem.get('tipo_ordem', 'compra') == 'compra' else (preco_entrada - preco_atual) * quantidade
            perc = (pnl / (preco_entrada * quantidade)) * 100 if preco_entrada else 0.0
            # Atualizar no banco
            try:
                import sqlite3
                conn = sqlite3.connect(self.gestor_ordens.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE ordens_dinamicas SET lucro_prejuizo = ?, pnl_percentual = ? WHERE order_id = ?
                """, (pnl, perc, ordem_id))
                conn.commit()
                conn.close()
                logger.info(f"🔄 Ordem {ordem_id} PnL atualizado: {pnl:.2f} ({perc:.2f}%)")
            except Exception as e:
                logger.error(f"Erro ao atualizar PnL no banco para ordem {ordem_id}: {e}")
            # Chamar lógica de fechamento/inteligente
            try:
                dados_mercado = {
                    'symbol': symbol,
                    'preco_atual': preco_atual,
                    'rsi': 50.0,  # Valor padrão para processamento inicial
                    'volatilidade': 0.02,
                    'tendencia': 'lateral'
                }
                ordem_completa = {
                    'order_id': ordem_id,
                    'symbol': symbol,
                    'preco_entrada': preco_entrada,
                    'quantidade': quantidade,
                    'tipo_ordem': ordem.get('tipo_ordem', 'compra'),
                    'timestamp_abertura': ordem.get('timestamp_abertura', datetime.now()),
                    'config': ordem.get('config', {})
                }
                self.gestor_ordens._processar_ordem_ativa(ordem_completa, dados_mercado)
            except Exception as e:
                logger.error(f"Erro ao processar ordem ativa {ordem_id}: {e}")
    
    def verificar_conectividade(self) -> bool:
        """Verifica conectividade com todos os serviços"""
        try:
            logger.info("🔗 Verificando conectividade...")
            
            # Testar coletor
            if not self.coletor or not hasattr(self.coletor, "verificar_conectividade") or not self.coletor.verificar_conectividade():
                logger.error("❌ Falha na conectividade do coletor")
                return False
            
            # Testar armazenamento
            if not self.armazenamento or not hasattr(self.armazenamento, "obter_estatisticas_crypto"):
                logger.error("❌ Falha no armazenamento: componente não inicializado")
                return False
            try:
                self.armazenamento.obter_estatisticas_crypto()
            except Exception as e:
                logger.error(f"❌ Falha no armazenamento: {e}")
                return False
            
            # Testar IA (se disponível)
            if not self.decisor or not hasattr(self.decisor, "processar_decisao_ia"):
                logger.warning("⚠️ IA pode não estar disponível: componente não inicializado")
            else:
                try:
                    dados_teste = {
                        'symbol': 'BTCUSDT',
                        'preco_atual': 117000.0,
                        'rsi': 50.0,
                        'tendencia': 'lateral'
                    }
                    self.decisor.processar_decisao_ia({'decisao': 'aguardar', 'confianca': 0.0}, dados_teste)
                except Exception as e:
                    logger.warning(f"⚠️ IA pode não estar disponível: {e}")
            
            logger.success("✅ Conectividade verificada!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de conectividade: {e}")
            return False
    
    def iniciar(self):
        """Inicia o robô completo"""
        try:
            logger.info("🚀 INICIANDO ROBÔ COMPLETO DE TRADING")
            logger.info("=" * 50)
            
            # Verificar modo
            if self.config['simulacao']['ativo']:
                logger.info("🎮 MODO SIMULAÇÃO ATIVO")
                logger.info("✅ Ordens serão simuladas (sem dinheiro real)")
                logger.info("✅ Capital simulado: ${:.2f}".format(self.config['simulacao']['capital_inicial']))
            else:
                logger.warning("💰 MODO REAL ATIVO")
                logger.warning("⚠️ ATENÇÃO: Ordens serão executadas com dinheiro real!")
            
            # Inicializar componentes
            if not self.inicializar_componentes():
                logger.error("❌ Falha na inicialização dos componentes")
                return False
            
            # Verificar conectividade
            if not self.verificar_conectividade():
                logger.error("❌ Falha na verificação de conectividade")
                return False
            
            # Iniciar coleta e análise em threads separadas
            self._parar_threads.clear()
            self.thread_analise_ia = threading.Thread(target=self._thread_analise_ia, daemon=True)
            self.thread_analise_ia.start()
            self._loop_coleta_continua()
            
            # Configurar estatísticas
            self.estatisticas['inicio_execucao'] = datetime.now()
            self.executando = True
            
            logger.success("🎉 Robô iniciado com sucesso!")
            logger.info("📊 Pressione Ctrl+C para parar")
            
            # Loop principal
            self._loop_principal()
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar robô: {e}")
            return False
    
    def _loop_principal(self):
        """Loop principal do robô"""
        try:
            while self.executando:
                # Atualizar PnL de todas as ordens abertas antes de cada ciclo
                self.atualizar_pnl_ordens_abertas()
                # Executar ciclo de análise
                self._executar_ciclo_completo()
                if not self.executando:
                    logger.info("⏹️ Execução interrompida durante ciclo.")
                    break
                # Aguardar próximo ciclo
                time.sleep(self.config['coleta']['frequencia'])
                if not self.executando:
                    logger.info("⏹️ Execução interrompida durante sleep.")
                    break
                # Exibir estatísticas a cada 10 ciclos
                if self.ciclos_executados % 10 == 0:
                    self._exibir_estatisticas_tempo_real()
        except KeyboardInterrupt:
            logger.info("🛑 Interrupção do usuário")
        except Exception as e:
            logger.error(f"❌ Erro no loop principal: {e}")
        finally:
            self.parar()

    def _loop_coleta_continua(self):
        """Loop principal de coleta contínua de dados (thread principal)"""
        try:
            while self.executando and not self._parar_threads.is_set():
                for par in self.config['trading']['pares']:
                    if not self.executando or self._parar_threads.is_set():
                        break
                    dados_mercado = self._coletar_dados_par(par)
                    if dados_mercado:
                        try:
                            self.buffer_dados.put_nowait(dados_mercado)
                        except:
                            logger.warning("Buffer de dados cheio, descartando candle.")
                time.sleep(self.config['coleta']['frequencia'])
        except Exception as e:
            logger.error(f"❌ Erro no loop de coleta contínua: {e}")
        finally:
            self._parar_threads.set()

    def _thread_analise_ia(self):
        """Thread que processa lotes de dados do buffer e executa análise IA"""
        while not self._parar_threads.is_set():
            lote = []
            try:
                # Coletar lote de dados do buffer
                while len(lote) < len(self.config['trading']['pares']):
                    try:
                        dados = self.buffer_dados.get(timeout=1)
                        lote.append(dados)
                    except Empty:
                        break
                if lote:
                    threads = []
                    for dados_ia in lote:
                        t = threading.Thread(target=self._processar_lote_ia_com_log, args=(dados_ia,))
                        t.start()
                        threads.append(t)
                    for t in threads:
                        t.join()
            except Exception as e:
                logger.error(f"❌ Erro na thread de análise IA: {e}")
            time.sleep(self.analise_ia_intervalo)  # Mantém apenas o delay do batch, que será ajustável

    def _processar_lote_ia(self, dados_ia):
        """Processa um lote de dados pela IA e executa decisão"""
        try:
            risco_maximo = self.config.get('risco_maximo_permitido', 3.0)
            dados_ia['risco_maximo_permitido'] = risco_maximo
            decisao_ia = self._analisar_com_ia(dados_ia)
            if decisao_ia:
                if self.sistema_aprendizado and hasattr(self.sistema_aprendizado, "registrar_decisao_autonoma"):
                    self.sistema_aprendizado.registrar_decisao_autonoma(
                        dados_ia['symbol'], decisao_ia, dados_ia['dados_mercado']
                    )
                if self.decisor and hasattr(self.decisor, "processar_decisao_ia"):
                    decisao_processada = self.decisor.processar_decisao_ia(decisao_ia, dados_ia['dados_mercado'])
                else:
                    decisao_processada = None
                if decisao_processada and decisao_processada.get('decisao') != 'aguardar':
                    self._executar_decisao(dados_ia['par'], decisao_processada, dados_ia)
                self.estatisticas['analises_realizadas'] += 1
                self.estatisticas['decisoes_tomadas'] += 1
                if self.config['simulacao']['ativo'] and self.executor and hasattr(self.executor, "capital_atual"):
                    self.estatisticas['capital_atual'] = getattr(self.executor, "capital_atual", self.estatisticas['capital_atual'])
        except Exception as e:
            logger.error(f"❌ Erro ao processar lote IA: {e}")

    def _processar_lote_ia_com_log(self, dados_ia):
        par = dados_ia.get('par', 'N/A')
        logger.info(f"[IA] Iniciando análise paralela para {par}")
        inicio = time.time()
        self._processar_lote_ia(dados_ia)
        fim = time.time()
        logger.info(f"[IA] Análise paralela para {par} finalizada em {fim-inicio:.2f}s")

    def atualizar_pnl_ordens_abertas(self):
        """Atualiza o PnL de todas as ordens abertas no banco em tempo real e processa fechamento inteligente."""
        if not self.gestor_ordens or not hasattr(self.gestor_ordens, 'ordens_ativas'):
            return
        threads = []
        for ordem_id, ordem in list(self.gestor_ordens.ordens_ativas.items()):
            t = threading.Thread(target=self._atualizar_e_processar_ordem_thread, args=(ordem_id, ordem))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def _atualizar_e_processar_ordem_thread(self, ordem_id, ordem):
        symbol = ordem.get('symbol')
        preco_entrada = ordem.get('preco_entrada')
        quantidade = ordem.get('quantidade', 1)
        if not symbol or preco_entrada is None:
            return
        logger.info(f"[ORD] Iniciando processamento paralelo de ordem {ordem_id} ({symbol})")
        inicio = time.time()
        preco_atual = None
        if not self.coletor or not hasattr(self.coletor, 'obter_preco_atual'):
            logger.warning(f"Coletor não disponível para obter preço de {symbol}. PnL não atualizado.")
            return
        try:
            preco_atual = self.coletor.obter_preco_atual(symbol)
        except Exception as e:
            logger.error(f"Erro ao obter preço atual de {symbol}: {e}")
        if preco_atual is None:
            return
        pnl = (preco_atual - preco_entrada) * quantidade if ordem.get('tipo_ordem', 'compra') == 'compra' else (preco_entrada - preco_atual) * quantidade
        perc = (pnl / (preco_entrada * quantidade)) * 100 if preco_entrada else 0.0
        if self.gestor_ordens and hasattr(self.gestor_ordens, 'db_path'):
            try:
                import sqlite3
                conn = sqlite3.connect(self.gestor_ordens.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE ordens_dinamicas SET lucro_prejuizo = ?, pnl_percentual = ? WHERE order_id = ?
                """, (pnl, perc, ordem_id))
                conn.commit()
                conn.close()
                logger.debug(f"🔄 [Realtime] Ordem {ordem_id} PnL atualizado: {pnl:.2f} ({perc:.2f}%)")
            except Exception as e:
                logger.error(f"Erro ao atualizar PnL no banco para ordem {ordem_id}: {e}")
        if self.gestor_ordens and hasattr(self.gestor_ordens, '_processar_ordem_ativa'):
            try:
                dados_mercado = {
                    'symbol': symbol,
                    'preco_atual': preco_atual,
                    'rsi': 50.0,  # Valor padrão para processamento
                    'volatilidade': 0.02,
                    'tendencia': 'lateral'
                }
                ordem_completa = {
                    'order_id': ordem_id,
                    'symbol': symbol,
                    'preco_entrada': preco_entrada,
                    'quantidade': quantidade,
                    'tipo_ordem': ordem.get('tipo_ordem', 'compra'),
                    'timestamp_abertura': ordem.get('timestamp_abertura', datetime.now()),
                    'config': ordem.get('config', {})
                }
                self.gestor_ordens._processar_ordem_ativa(ordem_completa, dados_mercado)
            except Exception as e:
                logger.error(f"Erro ao processar ordem ativa {ordem_id} (fechamento inteligente): {e}")
        fim = time.time()
        logger.info(f"[ORD] Processamento paralelo de ordem {ordem_id} finalizado em {fim-inicio:.2f}s")
    
    def _executar_ciclo_completo(self):
        """Executa um ciclo completo de análise e execução"""
        try:
            self.ciclos_executados += 1
            self.estatisticas['ciclos_executados'] = self.ciclos_executados
            risco_maximo = self.config.get('risco_maximo_permitido', 3.0)
            # Processar cada par configurado
            for par in self.config['trading']['pares']:
                if not self.executando:
                    logger.info(f"⏹️ Execução interrompida antes de processar {par}.")
                    break
                # 1. Coletar dados
                dados_mercado = self._coletar_dados_par(par)
                if not self.executando:
                    logger.info(f"⏹️ Execução interrompida após coleta de dados de {par}.")
                    break
                if not dados_mercado:
                    continue
                # Adicionar risco_maximo_permitido nos dados enviados para a IA
                dados_mercado['risco_maximo_permitido'] = risco_maximo
                # 2. Analisar com IA
                decisao_ia = self._analisar_com_ia(dados_mercado)
                if not self.executando:
                    logger.info(f"⏹️ Execução interrompida após análise IA de {par}.")
                    break
                if not decisao_ia:
                    continue
                # 3. Registrar decisão no aprendizado autônomo
                if self.sistema_aprendizado and hasattr(self.sistema_aprendizado, "registrar_decisao_autonoma"):
                    self.sistema_aprendizado.registrar_decisao_autonoma(
                        par.replace("/", ""), 
                        decisao_ia, 
                        dados_mercado['dados_mercado']
                    )
                # 4. Processar decisão com aprendizado
                if self.decisor and hasattr(self.decisor, "processar_decisao_ia"):
                    decisao_processada = self.decisor.processar_decisao_ia(decisao_ia, dados_mercado['dados_mercado'])
                else:
                    decisao_processada = None
                if not self.executando:
                    logger.info(f"⏹️ Execução interrompida após processamento decisão IA de {par}.")
                    break
                if decisao_processada and decisao_processada.get('decisao') != 'aguardar':
                    # 5. Executar decisão
                    self._executar_decisao(par, decisao_processada, dados_mercado)
                # 6. Atualizar estatísticas
                self.estatisticas['analises_realizadas'] += 1
                self.estatisticas['decisoes_tomadas'] += 1
                # 7. Atualizar capital (se simulação)
                if self.config['simulacao']['ativo'] and self.executor and hasattr(self.executor, "capital_atual"):
                    self.estatisticas['capital_atual'] = getattr(self.executor, "capital_atual", self.estatisticas['capital_atual'])
        except Exception as e:
            logger.error(f"❌ Erro no ciclo completo: {e}")
    
    def _coletar_dados_par(self, par: str) -> Optional[Dict[str, Any]]:
        """Coleta dados para um par específico"""
        try:
            if not self.executando:
                logger.info(f"⏹️ Execução interrompida antes de coletar dados de {par}.")
                return None
            # Obter preço atual
            if not self.coletor or not hasattr(self.coletor, "obter_preco_atual"):
                logger.error(f"❌ Coletor não inicializado para obter preço de {par}")
                return None
            preco_atual = self.coletor.obter_preco_atual(par)
            if not self.executando:
                logger.info(f"⏹️ Execução interrompida após obter preço de {par}.")
                return None
            if not preco_atual:
                return None
            # Obter dados históricos
            if not hasattr(self.coletor, "obter_dados_rest"):
                logger.error(f"❌ Coletor não implementa obter_dados_rest para {par}")
                return None
            dados_historicos = self.coletor.obter_dados_rest(par, "5", 100)
            if not self.executando:
                logger.info(f"⏹️ Execução interrompida após obter dados históricos de {par}.")
                return None
            if dados_historicos is None or hasattr(dados_historicos, 'empty') and dados_historicos.empty:
                return None
            # Estruturar dados para IA
            dados_ia = {
                'symbol': par.replace("/", ""),
                'par': par,
                'preco_atual': preco_atual,
                'dados_historicos': dados_historicos,
                'dados_mercado': {
                    'symbol': par.replace("/", ""),
                    'preco_atual': preco_atual,
                    'rsi': self._calcular_rsi(dados_historicos),
                    'volatilidade': self._calcular_volatilidade(dados_historicos),
                    'tendencia': self._determinar_tendencia(dados_historicos)
                }
            }
            if not self.executando:
                logger.info(f"⏹️ Execução interrompida após estruturar dados de {par}.")
                return None
            return dados_ia
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados para {par}: {e}")
            return None
    
    def _analisar_com_ia(self, dados_ia: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analisa dados com IA real (Ollama)"""
        try:
            resposta = self.ai_client.analisar_dados_mercado(dados_ia['dados_mercado'])
            if resposta and 'decisao' in resposta:
                return resposta
            logger.error("[IA] IA não retornou resposta válida. Aguardando nova análise.")
            return None
        except Exception as e:
            logger.error(f"❌ Erro na análise com IA real: {e}")
            return None
    
    def _simular_decisao_ia(self, prompt: str, dados_ia: Dict[str, Any]) -> Dict[str, Any]:
        """Simula decisão da IA baseada nos dados"""
        try:
            # Extrair dados do mercado
            dados_mercado = dados_ia['dados_mercado']
            rsi = dados_mercado.get('rsi', 50.0)
            volatilidade = dados_mercado.get('volatilidade', 0.02)
            tendencia = dados_mercado.get('tendencia', 'lateral')
            preco_atual = dados_mercado.get('preco_atual', 0.0)
            
            # Lógica simples de decisão baseada em indicadores
            decisao = 'aguardar'
            confianca = 0.0
            razao = "Análise técnica neutra"
            
            # RSI extremos
            if rsi < 30:
                decisao = 'comprar'
                confianca = 0.7
                razao = f"RSI sobrevendido ({rsi:.1f})"
            elif rsi > 70:
                decisao = 'vender'
                confianca = 0.7
                razao = f"RSI sobrecomprado ({rsi:.1f})"
            
            # Tendência forte
            elif tendencia == 'alta' and rsi < 60:
                decisao = 'comprar'
                confianca = 0.6
                razao = f"Tendência de alta com RSI neutro ({rsi:.1f})"
            elif tendencia == 'baixa' and rsi > 40:
                decisao = 'vender'
                confianca = 0.6
                razao = f"Tendência de baixa com RSI neutro ({rsi:.1f})"
            
            # Volatilidade alta - ser mais conservador
            if volatilidade > 0.03:
                confianca *= 0.8
                razao += f" | Volatilidade alta ({volatilidade:.3f})"
            
            return {
                'decisao': decisao,
                'confianca': confianca,
                'razao': razao,
                'parametros': {
                    'rsi': rsi,
                    'volatilidade': volatilidade,
                    'tendencia': tendencia,
                    'preco_atual': preco_atual
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao simular decisão da IA: {e}")
            return {
                'decisao': 'aguardar',
                'confianca': 0.3,
                'razao': f"Erro na análise: {e}",
                'parametros': {}
            }
    
    def _preparar_prompt_completo(self, dados_ia: Dict[str, Any]) -> str:
        """Prepara prompt completo para IA"""
        try:
            df = dados_ia['dados_historicos']
            preco_atual = dados_ia['preco_atual']
            symbol = dados_ia['symbol']
            
            # Calcular indicadores
            rsi = dados_ia['dados_mercado']['rsi']
            volatilidade = dados_ia['dados_mercado']['volatilidade']
            tendencia = dados_ia['dados_mercado']['tendencia']
            
            # Obter estatísticas de aprendizado
            stats_aprendizado = None
            if self.sistema_aprendizado and hasattr(self.sistema_aprendizado, "obter_estatisticas_aprendizado"):
                stats_aprendizado = self.sistema_aprendizado.obter_estatisticas_aprendizado()
            
            prompt = f"""
ANÁLISE DE TRADING CRYPTO - {symbol}

DADOS ATUAIS:
- Preço atual: ${preco_atual:.2f}
- RSI (14): {rsi:.2f}
- Volatilidade: {volatilidade:.4f}
- Tendência: {tendencia}

HISTÓRICO RECENTE (últimos 5 períodos):
"""
            
            # Adicionar histórico recente
            for i, row in df.tail(5).iterrows():
                prompt += f"- {row['timestamp'].strftime('%H:%M')}: ${row['close']:.2f} (Vol: {row['volume']:.2f})\n"
            
            # Adicionar estatísticas de aprendizado
            if stats_aprendizado:
                prompt += f"""
APRENDIZADO DA IA:
- Win Rate: {stats_aprendizado.get('win_rate', 0):.1%}
- Confiança média: {stats_aprendizado.get('confianca_media', 0):.3f}
- Sequência atual: {stats_aprendizado.get('sequencia_atual', 0)}
"""
            
            prompt += f"""
INSTRUÇÕES:
Analise os dados acima e tome uma decisão de trading para {symbol}.

Considere:
1. Tendência atual do mercado
2. Nível de RSI (sobrecomprado/sobrevendido)
3. Volatilidade atual
4. Histórico de aprendizado da IA
5. Seu nível de confiança na decisão

RESPONDA APENAS COM JSON:
{{
    "decisao": "comprar|vender|aguardar",
    "confianca": 0.0-1.0,
    "razao": "explicação da decisão"
}}
"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"❌ Erro ao preparar prompt: {e}")
            return ""
    
    def _executar_decisao(self, par: str, decisao: Dict[str, Any], dados_mercado: Dict[str, Any]):
        """Executa decisão da IA"""
        try:
            decisao_tipo = decisao.get('decisao', '').lower()
            confianca = decisao.get('confianca')
            if confianca is None:
                confianca = 0.0
            symbol = par.replace("/", "")
            # Remover este bloco para permitir múltiplas ordens por ativo:
            # if self.gestor_ordens and hasattr(self.gestor_ordens, 'ordens_ativas'):
            #     for ordem in self.gestor_ordens.ordens_ativas.values():
            #         if ordem['symbol'] == symbol:
            #             logger.info(f"⏳ Já existe ordem aberta para {symbol}, aguardando fechamento.")
            #             return
            logger.info(f"🎯 Executando decisão: {decisao_tipo} {par} (confiança: {confianca:.3f})")
            if decisao_tipo == 'comprar':
                self._abrir_ordem_dinamica(par, decisao, dados_mercado, 'compra')
            elif decisao_tipo == 'vender':
                self._abrir_ordem_dinamica(par, decisao, dados_mercado, 'venda')
            else:
                logger.info(f"⏳ Aguardando melhor oportunidade para {par}")
        except Exception as e:
            logger.error(f"❌ Erro ao executar decisão: {e}")

    def _abrir_ordem_dinamica(self, par: str, decisao: Dict[str, Any], dados_mercado: Dict[str, Any], tipo_ordem: str):
        """Abre ordem via gestor dinâmico, sempre com stop/take dinâmicos"""
        try:
            symbol = par.replace("/", "")
            confianca = decisao.get('confianca')
            if confianca is None:
                confianca = 0.0
            preco_entrada = dados_mercado['dados_mercado']['preco_atual']
            stop_loss = decisao['parametros'].get('stop_loss', preco_entrada)
            quantidade = decisao['parametros'].get('quantidade', 1.0 / preco_entrada)
            risco_maximo = self.config.get('risco_maximo_permitido', 3.0)
            risco_real = abs(preco_entrada - stop_loss) * quantidade
            if risco_real > risco_maximo and abs(preco_entrada - stop_loss) > 0:
                quantidade = risco_maximo / abs(preco_entrada - stop_loss)
                logger.warning(f"Ajustando quantidade para respeitar risco máximo: {quantidade:.8f}")
                risco_real = abs(preco_entrada - stop_loss) * quantidade
            if risco_real > risco_maximo:
                logger.error(f"Ordem NÃO aberta: risco real ({risco_real:.2f}) > risco máximo permitido ({risco_maximo:.2f})")
                return
            # Sempre operar com quantidade calculada
            # Gerar order_id único
            order_id = f"ORD_{int(time.time())}_{symbol}"
            if self.gestor_ordens and hasattr(self.gestor_ordens, 'abrir_ordem_dinamica'):
                tipo_enum = TipoOrdem.COMPRA if tipo_ordem == 'compra' else TipoOrdem.VENDA
                self.gestor_ordens.abrir_ordem_dinamica(
                    order_id, symbol, tipo_enum, preco_entrada, quantidade, dados_mercado['dados_mercado'], confianca
                )
            else:
                logger.error("❌ Gestor de ordens dinâmico não disponível para abrir ordem.")
        except Exception as e:
            logger.error(f"❌ Erro ao abrir ordem dinâmica: {e}")
    
    def _calcular_rsi(self, df, periodo=14) -> float:
        """Calcula RSI"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return 50.0
    
    def _calcular_volatilidade(self, df, periodo=20) -> float:
        """Calcula volatilidade"""
        try:
            returns = df['close'].pct_change()
            volatilidade = returns.rolling(window=periodo).std()
            return float(volatilidade.iloc[-1])
        except:
            return 0.02
    
    def _determinar_tendencia(self, df) -> str:
        """Determina tendência"""
        try:
            if len(df) < 20:
                return 'lateral'
            
            media_curta = df['close'].tail(5).mean()
            media_longa = df['close'].tail(20).mean()
            
            if media_curta > media_longa * 1.01:
                return 'alta'
            elif media_curta < media_longa * 0.99:
                return 'baixa'
            else:
                return 'lateral'
        except:
            return 'lateral'
    
    def _exibir_estatisticas_tempo_real(self):
        """Exibe estatísticas em tempo real"""
        try:
            tempo_execucao = datetime.now() - self.estatisticas['inicio_execucao']
            
            # Obter estatísticas de aprendizado
            stats_aprendizado = None
            if self.sistema_aprendizado and hasattr(self.sistema_aprendizado, "obter_estatisticas_aprendizado"):
                stats_aprendizado = self.sistema_aprendizado.obter_estatisticas_aprendizado()
            
            # Obter estatísticas de gestão
            stats_gestao = None
            if self.gestor_ordens and hasattr(self.gestor_ordens, "obter_estatisticas_gestao"):
                stats_gestao = self.gestor_ordens.obter_estatisticas_gestao()
            
            logger.info("📊 ESTATÍSTICAS EM TEMPO REAL")
            logger.info("=" * 50)
            logger.info(f"⏱️  Tempo de execução: {tempo_execucao}")
            logger.info(f"🔄 Ciclos executados: {self.estatisticas['ciclos_executados']}")
            logger.info(f"🧠 Análises realizadas: {self.estatisticas['analises_realizadas']}")
            logger.info(f"🎯 Decisões tomadas: {self.estatisticas['decisoes_tomadas']}")
            logger.info(f"📈 Ordens executadas: {self.estatisticas['ordens_executadas']}")
            
            if self.config['simulacao']['ativo']:
                logger.info(f"💰 Capital inicial: ${self.estatisticas['capital_inicial']:.2f}")
                logger.info(f"💰 Capital atual: ${self.estatisticas['capital_atual']:.2f}")
                variacao = ((self.estatisticas['capital_atual'] - self.estatisticas['capital_inicial']) / self.estatisticas['capital_inicial']) * 100
                logger.info(f"📊 Variação: {variacao:+.2f}%")
            
            if stats_aprendizado:
                logger.info(f"🧠 APRENDIZADO AUTÔNOMO:")
                logger.info(f"   Win Rate: {stats_aprendizado.get('win_rate', 0):.1%}")
                logger.info(f"   Confiança média: {stats_aprendizado.get('confianca_media', 0):.3f}")
                logger.info(f"   Sequência atual: {stats_aprendizado.get('sequencia_atual', 0)}")
            
            if stats_gestao:
                logger.info(f"🎯 GESTÃO DINÂMICA:")
                logger.info(f"   Ordens ativas: {stats_gestao.get('ordens_ativas', 0)}")
                logger.info(f"   Lucro total: ${stats_gestao.get('lucro_total', 0):.2f}")
                logger.info(f"   Ajustes realizados: {stats_gestao.get('total_ajustes', 0)}")
            
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ Erro ao exibir estatísticas: {e}")
    
    def parar(self):
        """Para o robô graciosamente"""
        try:
            logger.info("🛑 Parando robô...")
            self.executando = False
            self._parar_threads.set()
            if self.thread_analise_ia and self.thread_analise_ia.is_alive():
                self.thread_analise_ia.join(timeout=5)
            
            # Parar coletor
            if self.coletor:
                if hasattr(self.coletor, "parar_websocket"):
                    self.coletor.parar_websocket()
            
            # Parar gestor de ordens
            if self.gestor_ordens:
                if hasattr(self.gestor_ordens, "parar_monitoramento"):
                    self.gestor_ordens.parar_monitoramento()
            
            # Exibir estatísticas finais
            self._exibir_estatisticas_finais()
            
            logger.success("✅ Robô parado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar robô: {e}")
    
    def _exibir_estatisticas_finais(self):
        """Exibe estatísticas finais"""
        try:
            tempo_total = datetime.now() - self.estatisticas['inicio_execucao']
            
            logger.info("📊 ESTATÍSTICAS FINAIS")
            logger.info("=" * 50)
            logger.info(f"⏱️  Tempo total: {tempo_total}")
            logger.info(f"🔄 Total de ciclos: {self.estatisticas['ciclos_executados']}")
            logger.info(f"🧠 Total de análises: {self.estatisticas['analises_realizadas']}")
            logger.info(f"🎯 Total de decisões: {self.estatisticas['decisoes_tomadas']}")
            logger.info(f"📈 Total de ordens: {self.estatisticas['ordens_executadas']}")
            
            if self.config['simulacao']['ativo']:
                variacao = ((self.estatisticas['capital_atual'] - self.estatisticas['capital_inicial']) / self.estatisticas['capital_inicial']) * 100
                logger.info(f"💰 Resultado: {variacao:+.2f}%")
            
            # Exportar aprendizado
            if self.sistema_aprendizado and hasattr(self.sistema_aprendizado, "exportar_aprendizado"):
                self.sistema_aprendizado.exportar_aprendizado()
                logger.info(f"📁 Aprendizado exportado com sucesso!")
            
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ Erro ao exibir estatísticas finais: {e}")

    def set_batch_interval(self, novo_intervalo: int):
        """Permite ajuste dinâmico do batch_interval em tempo de execução."""
        self.analise_ia_intervalo = max(1, min(novo_intervalo, 60))  # Limite entre 1s e 60s
        logger.info(f"Novo batch_interval definido: {self.analise_ia_intervalo}s")

    def _analise_tecnica_simples(self, dados: dict) -> dict:
        rsi = dados.get('rsi', 50.0)
        volatilidade = dados.get('volatilidade', 0.02)
        tendencia = dados.get('tendencia', 'lateral')
        preco_atual = dados.get('preco_atual', 0.0)
        decisao = 'aguardar'
        confianca = 0.0
        razao = "Análise técnica neutra"
        if rsi < 30:
            decisao = 'comprar'
            confianca = 0.7
            razao = f"RSI sobrevendido ({rsi:.1f})"
        elif rsi > 70:
            decisao = 'vender'
            confianca = 0.7
            razao = f"RSI sobrecomprado ({rsi:.1f})"
        elif tendencia == 'alta' and rsi < 60:
            decisao = 'comprar'
            confianca = 0.6
            razao = f"Tendência de alta com RSI neutro ({rsi:.1f})"
        elif tendencia == 'baixa' and rsi > 40:
            decisao = 'vender'
            confianca = 0.6
            razao = f"Tendência de baixa com RSI neutro ({rsi:.1f})"
        if volatilidade > 0.03:
            confianca *= 0.8
            razao += f" | Volatilidade alta ({volatilidade:.3f})"
        return {
            'decisao': decisao,
            'confianca': confianca,
            'razao': razao,
            'parametros': {
                'rsi': rsi,
                'volatilidade': volatilidade,
                'tendencia': tendencia,
                'preco_atual': preco_atual
            }
        }

def main():
    """Função principal"""
    try:
        # Configurar logger
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # Criar e iniciar robô
        robo = RoboCompleto()
        robo.iniciar()
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrupção do usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 