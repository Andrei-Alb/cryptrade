"""
Executor de Ordens Simuladas para Robô de Trading
Executa ordens simuladas com alvos curtos e armazena resultados para aprendizado
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger
import sqlite3
import os

class ExecutorOrdensSimuladas:
    def __init__(self, db_path: str = "dados/trading.db"):
        """
        Inicializa executor de ordens simuladas
        
        Args:
            db_path: Caminho para banco de dados
        """
        self.db_path = db_path
        self.ordens_ativas: Dict[str, Dict[str, Any]] = {}  # {ordem_id: {dados_ordem}}
        self.criar_tabelas()
        
    def criar_tabelas(self):
        """Cria tabelas necessárias para execução simulada"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Verificar se a tabela existe e tem a coluna razao_fechamento
        c.execute("PRAGMA table_info(ordens_simuladas)")
        colunas = [col[1] for col in c.fetchall()]
        
        if 'razao_fechamento' not in colunas:
            # Recriar tabela com a nova coluna
            c.execute('DROP TABLE IF EXISTS ordens_simuladas')
            logger.info("Recriando tabela ordens_simuladas com coluna razao_fechamento")
        
        # Tabela de ordens simuladas
        c.execute('''
        CREATE TABLE IF NOT EXISTS ordens_simuladas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            timestamp DATETIME NOT NULL,
            tipo TEXT NOT NULL,
            simbolo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_entrada DECIMAL(10,2) NOT NULL,
            preco_alvo DECIMAL(10,2) NOT NULL,
            preco_stop DECIMAL(10,2) NOT NULL,
            status TEXT NOT NULL,
            resultado TEXT,
            lucro_percentual DECIMAL(5,2),
            duracao_segundos INTEGER,
            confianca_ia DECIMAL(5,2),
            dados_analise TEXT,
            timestamp_fechamento DATETIME,
            razao_fechamento TEXT
        )
        ''')
        
        # Tabela de aprendizado da IA
        c.execute('''
        CREATE TABLE IF NOT EXISTS aprendizado_ia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            padrao_entrada TEXT,
            decisao_ia TEXT,
            confianca_ia DECIMAL(5,2),
            resultado_ordem TEXT,
            lucro_percentual DECIMAL(5,2),
            acerto BOOLEAN,
            dados_mercado TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Tabelas de execução simulada criadas")
    
    def executar_ordem_simulada(self, decisao: Dict[str, Any], dados_mercado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa ordem simulada com alvos curtos
        
        Args:
            decisao: Decisão da IA (comprar/vender)
            dados_mercado: Dados atuais do mercado
            
        Returns:
            Resultado da execução
        """
        try:
            if decisao['decisao'] not in ['comprar', 'vender']:
                return {'status': 'ignorado', 'razao': 'Decisão não é compra/venda'}
            
            # Gerar ID único para a ordem
            ordem_id = f"ORD_{int(time.time())}_{dados_mercado.get('simbolo', 'WIN')}"
            
            # Calcular alvos baseados na volatilidade e confiança
            preco_atual = dados_mercado['preco_atual']
            confianca = decisao.get('confianca', 0.5)
            
            # Alvos mais agressivos para confiança alta
            if confianca >= 0.8:
                alvo_percentual = 0.3  # 0.3% em 1-2 min
                stop_percentual = 0.15  # 0.15% stop
            elif confianca >= 0.7:
                alvo_percentual = 0.25  # 0.25% em 2-3 min
                stop_percentual = 0.12  # 0.12% stop
            else:
                alvo_percentual = 0.2   # 0.2% em 3-5 min
                stop_percentual = 0.1   # 0.1% stop
            
            # Calcular preços de alvo e stop
            if decisao['decisao'] == 'comprar':
                preco_alvo = preco_atual * (1 + alvo_percentual / 100)
                preco_stop = preco_atual * (1 - stop_percentual / 100)
            else:  # vender
                preco_alvo = preco_atual * (1 - alvo_percentual / 100)
                preco_stop = preco_atual * (1 + stop_percentual / 100)
            
            # Validação de risco/retorno
            if decisao['decisao'] == 'comprar':
                distancia_alvo = preco_alvo - preco_atual
                distancia_stop = preco_atual - preco_stop
            else:
                distancia_alvo = preco_atual - preco_alvo
                distancia_stop = preco_stop - preco_atual

            if distancia_alvo < distancia_stop:
                logger.error(f"❌ Ordem NÃO executada: risco ({distancia_stop:.2f}) > retorno ({distancia_alvo:.2f}) | {decisao['decisao'].upper()} {dados_mercado.get('simbolo')} @ {preco_atual:.2f}")
                return {'status': 'ignorado', 'razao': 'Risco maior que retorno'}

            # Criar ordem
            ordem = {
                'ordem_id': ordem_id,
                'timestamp': datetime.now(),
                'tipo': decisao['decisao'],
                'simbolo': dados_mercado.get('simbolo', 'WIN'),
                'quantidade': 1,
                'preco_entrada': preco_atual,
                'preco_alvo': preco_alvo,
                'preco_stop': preco_stop,
                'status': 'aberta',
                'confianca_ia': confianca,
                'dados_analise': json.dumps(decisao),
                'alvo_percentual': alvo_percentual,
                'stop_percentual': stop_percentual
            }

            # Salvar ordem no banco
            self.salvar_ordem_simulada(ordem)

            # Adicionar à lista de ordens ativas
            self.ordens_ativas[ordem_id] = ordem

            logger.info(f"🚀 Ordem simulada executada: {decisao['decisao'].upper()} {dados_mercado.get('simbolo')} "
                       f"@ {preco_atual:.2f} | Alvo: {preco_alvo:.2f} | Stop: {preco_stop:.2f} "
                       f"| Confiança: {confianca:.2f}")

            return {
                'status': 'executada',
                'ordem_id': ordem_id,
                'preco_entrada': preco_atual,
                'preco_alvo': preco_alvo,
                'preco_stop': preco_stop,
                'alvo_percentual': alvo_percentual,
                'stop_percentual': stop_percentual
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar ordem simulada: {e}")
            return {'status': 'erro', 'razao': str(e)}
    
    def verificar_ordens_ativas(self, preco_atual: float, simbolo: str) -> None:
        """
        Verifica se ordens ativas atingiram alvo ou stop
        
        Args:
            preco_atual: Preço atual do ativo
            simbolo: Símbolo do ativo
        """
        ordens_fechadas = []
        
        for ordem_id, ordem in list(self.ordens_ativas.items()):
            if ordem['simbolo'] != simbolo:
                continue
                
            resultado = None
            lucro_percentual = 0.0
            razao_fechamento = ""
            
            # Verificar se atingiu alvo
            if ordem['tipo'] == 'comprar':
                if preco_atual >= ordem['preco_alvo']:
                    resultado = 'win'
                    lucro_percentual = ((preco_atual - ordem['preco_entrada']) / ordem['preco_entrada']) * 100
                    razao_fechamento = f"Alvo atingido: {preco_atual:.2f} >= {ordem['preco_alvo']:.2f}"
                elif preco_atual <= ordem['preco_stop']:
                    resultado = 'loss'
                    lucro_percentual = ((preco_atual - ordem['preco_entrada']) / ordem['preco_entrada']) * 100
                    razao_fechamento = f"Stop atingido: {preco_atual:.2f} <= {ordem['preco_stop']:.2f}"
            else:  # vender
                if preco_atual <= ordem['preco_alvo']:
                    resultado = 'win'
                    lucro_percentual = ((ordem['preco_entrada'] - preco_atual) / ordem['preco_entrada']) * 100
                    razao_fechamento = f"Alvo atingido: {preco_atual:.2f} <= {ordem['preco_alvo']:.2f}"
                elif preco_atual >= ordem['preco_stop']:
                    resultado = 'loss'
                    lucro_percentual = ((ordem['preco_entrada'] - preco_atual) / ordem['preco_entrada']) * 100
                    razao_fechamento = f"Stop atingido: {preco_atual:.2f} >= {ordem['preco_stop']:.2f}"
            
            # Verificar timeout (máximo 5 minutos)
            duracao = (datetime.now() - ordem['timestamp']).total_seconds()
            if duracao > 300 and not resultado:  # 5 minutos
                lucro_percentual = ((preco_atual - ordem['preco_entrada']) / ordem['preco_entrada']) * 100
                if ordem['tipo'] == 'vender':
                    lucro_percentual = -lucro_percentual
                resultado = 'win' if lucro_percentual > 0 else 'loss'
                razao_fechamento = f"Timeout: {duracao:.1f}s > 300s"
            
            # Fechar ordem se atingiu alvo, stop ou timeout
            if resultado:
                # Atualizar ordem no banco
                self.fechar_ordem_simulada(ordem_id, resultado, lucro_percentual, duracao, razao_fechamento)
                
                # Registrar aprendizado
                self.registrar_aprendizado(ordem, resultado, lucro_percentual, preco_atual)
                
                # Remover da lista de ordens ativas
                del self.ordens_ativas[ordem_id]
                
                # Log detalhado
                emoji = "🟢" if resultado == 'win' else "🔴" if resultado == 'loss' else "🟡"
                logger.info(f"{emoji} Ordem fechada: {ordem['tipo'].upper()} {simbolo} | "
                           f"Resultado: {resultado.upper()} | Lucro: {lucro_percentual:.2f}% | "
                           f"Duração: {duracao:.1f}s | Confiança: {ordem['confianca_ia']:.2f} | "
                           f"Razão: {razao_fechamento}")
                
                ordens_fechadas.append({
                    'ordem_id': ordem_id,
                    'resultado': resultado,
                    'lucro_percentual': lucro_percentual,
                    'duracao': duracao
                })
        
        # Log resumo se houve fechamentos
        if ordens_fechadas:
            wins = sum(1 for o in ordens_fechadas if o['resultado'] == 'win')
            total = len(ordens_fechadas)
            lucro_total = sum(o['lucro_percentual'] for o in ordens_fechadas)
            logger.info(f"📊 Resumo fechamentos: {wins}/{total} wins | Lucro total: {lucro_total:.2f}%")
    
    def salvar_ordem_simulada(self, ordem: Dict[str, Any]) -> bool:
        """Salva ordem simulada no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO ordens_simuladas 
            (timestamp, ordem_id, tipo, simbolo, quantidade, preco_entrada, 
             preco_alvo, preco_stop, status, confianca_ia, dados_analise)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ordem['timestamp'],
                ordem['ordem_id'],
                ordem['tipo'],
                ordem['simbolo'],
                ordem['quantidade'],
                ordem['preco_entrada'],
                ordem['preco_alvo'],
                ordem['preco_stop'],
                ordem['status'],
                ordem['confianca_ia'],
                ordem['dados_analise']
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar ordem simulada: {e}")
            return False
    
    def fechar_ordem_simulada(self, ordem_id: str, resultado: str, lucro_percentual: float, duracao: float, razao_fechamento: str = "") -> bool:
        """Fecha ordem simulada no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            UPDATE ordens_simuladas 
            SET status = ?, resultado = ?, lucro_percentual = ?, 
                duracao_segundos = ?, timestamp_fechamento = ?, razao_fechamento = ?
            WHERE ordem_id = ?
            ''', (
                'fechada',
                resultado,
                lucro_percentual,
                duracao,
                datetime.now(),
                razao_fechamento,
                ordem_id
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao fechar ordem simulada: {e}")
            return False
    
    def registrar_aprendizado(self, ordem: Dict[str, Any], resultado: str, lucro_percentual: float, preco_atual: float) -> bool:
        """Registra dados para aprendizado da IA"""
        try:
            # Extrair dados da análise original
            dados_analise = json.loads(ordem['dados_analise'])
            
            # Determinar se foi acerto baseado na confiança
            # Acerto: confiança alta + win OU confiança baixa + loss
            acerto = (resultado == 'win' and ordem['confianca_ia'] >= 0.6) or \
                     (resultado == 'loss' and ordem['confianca_ia'] < 0.6)
            
            # Criar padrão de entrada mais detalhado
            padrao_entrada = {
                'indicadores': dados_analise.get('indicadores_analisados', []),
                'razao': dados_analise.get('razao', ''),
                'parametros': dados_analise.get('parametros', {}),
                'timestamp_analise': dados_analise.get('timestamp', ''),
                'ativo': dados_analise.get('ativo', 'WINZ25')
            }
            
            # Dados de mercado mais completos
            dados_mercado = {
                'preco_entrada': ordem['preco_entrada'],
                'preco_atual': preco_atual,
                'preco_alvo': ordem['preco_alvo'],
                'preco_stop': ordem['preco_stop'],
                'alvo_percentual': ordem['alvo_percentual'],
                'stop_percentual': ordem['stop_percentual'],
                'duracao_segundos': (datetime.now() - ordem['timestamp']).total_seconds(),
                'resultado': resultado,
                'lucro_percentual': lucro_percentual,
                'acerto': acerto
            }
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO aprendizado_ia 
            (timestamp, padrao_entrada, decisao_ia, confianca_ia, resultado_ordem, 
             lucro_percentual, acerto, dados_mercado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                json.dumps(padrao_entrada),
                ordem['tipo'],
                ordem['confianca_ia'],
                resultado,
                lucro_percentual,
                acerto,
                json.dumps(dados_mercado)
            ))
            conn.commit()
            conn.close()
            
            logger.info(f"📚 Aprendizado registrado: {ordem['tipo']} | "
                       f"Confiança: {ordem['confianca_ia']:.2f} | "
                       f"Resultado: {resultado} | Acerto: {acerto}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar aprendizado: {e}")
            return False
    
    def obter_estatisticas_aprendizado(self) -> Dict[str, Any]:
        """Obtém estatísticas de aprendizado da IA"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Total de ordens
            c.execute('SELECT COUNT(*) FROM ordens_simuladas WHERE status = "fechada"')
            total_ordens = c.fetchone()[0]
            
            # Wins e losses
            c.execute('SELECT COUNT(*) FROM ordens_simuladas WHERE status = "fechada" AND resultado = "win"')
            wins = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM ordens_simuladas WHERE status = "fechada" AND resultado = "loss"')
            losses = c.fetchone()[0]
            
            # Lucro total
            c.execute('SELECT SUM(lucro_percentual) FROM ordens_simuladas WHERE status = "fechada"')
            lucro_total = c.fetchone()[0] or 0.0
            
            # Taxa de acerto por confiança
            c.execute('''
            SELECT 
                CASE 
                    WHEN confianca_ia >= 0.8 THEN 'Alta (>=0.8)'
                    WHEN confianca_ia >= 0.7 THEN 'Média (0.7-0.8)'
                    ELSE 'Baixa (<0.7)'
                END as nivel_confianca,
                COUNT(*) as total,
                SUM(CASE WHEN resultado = 'win' THEN 1 ELSE 0 END) as wins,
                AVG(lucro_percentual) as lucro_medio
            FROM ordens_simuladas 
            WHERE status = 'fechada'
            GROUP BY nivel_confianca
            ''')
            performance_confianca = {}
            for row in c.fetchall():
                performance_confianca[row[0]] = {
                    'total': row[1],
                    'wins': row[2],
                    'lucro_medio': row[3] or 0.0
                }
            
            conn.close()
            
            return {
                'total_ordens': total_ordens,
                'wins': wins,
                'losses': losses,
                'taxa_acerto': (wins / total_ordens * 100) if total_ordens > 0 else 0,
                'lucro_total': lucro_total,
                'lucro_medio': lucro_total / total_ordens if total_ordens > 0 else 0,
                'performance_confianca': performance_confianca,
                'ordens_ativas': len(self.ordens_ativas)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

# Função de compatibilidade
def enviar_ordem(tipo: str, quantidade: int, preco: float, simbolo: str) -> Dict[str, Any]:
    """
    Função de compatibilidade para código existente
    """
    executor = ExecutorOrdensSimuladas()
    return executor.executar_ordem_simulada(
        {'decisao': tipo, 'confianca': 0.7},
        {'preco_atual': preco, 'simbolo': simbolo}
    ) 

class ExecutorBybit:
    """Executor de ordens reais na Bybit"""
    
    def __init__(self, config: dict = None):
        """
        Inicializa executor de ordens reais na Bybit
        
        Args:
            config: Configurações do sistema
        """
        self.config = config or {}
        self.api_key = self.config.get('exchange', {}).get('api_key') or os.getenv('BYBIT_API_KEY')
        self.api_secret = self.config.get('exchange', {}).get('api_secret') or os.getenv('BYBIT_API_SECRET')
        self.testnet = self.config.get('exchange', {}).get('testnet', False)
        
        if not self.api_key or not self.api_secret:
            logger.error("❌ Credenciais da Bybit não configuradas")
            raise ValueError("Credenciais da Bybit não configuradas")
        
        # Configurar cliente Bybit
        try:
            from pybit.unified_trading import HTTP
            self.client = HTTP(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet
            )
            logger.info("✅ Cliente Bybit inicializado")
        except ImportError:
            logger.error("❌ pybit não instalado. Instale com: pip install pybit")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Bybit: {e}")
            raise
    
    def obter_saldo(self, moeda: str = "USDT") -> float:
        """Obtém saldo da conta"""
        try:
            response = self.client.get_wallet_balance(accountType="UNIFIED", coin=moeda)
            if response.get('retCode') == 0:
                return float(response['result']['list'][0]['totalWalletBalance'])
            else:
                logger.error(f"Erro ao obter saldo: {response.get('retMsg')}")
                return 0.0
        except Exception as e:
            logger.error(f"Erro ao obter saldo: {e}")
            return 0.0
    
    def obter_preco_atual(self, symbol: str) -> float:
        """Obtém preço atual de um símbolo"""
        try:
            response = self.client.get_tickers(category="spot", symbol=symbol)
            if response.get('retCode') == 0 and response['result']['list']:
                return float(response['result']['list'][0]['lastPrice'])
            else:
                logger.error(f"Erro ao obter preço de {symbol}: {response.get('retMsg')}")
                return 0.0
        except Exception as e:
            logger.error(f"Erro ao obter preço de {symbol}: {e}")
            return 0.0
    
    def executar_ordem(self, decisao: dict, dados_mercado: dict) -> dict:
        """
        Executa ordem real na Bybit
        
        Args:
            decisao: Decisão da IA
            dados_mercado: Dados do mercado
            
        Returns:
            Resultado da execução
        """
        try:
            if decisao['decisao'] not in ['comprar', 'vender']:
                return {'status': 'ignorado', 'razao': 'Decisão não é compra/venda'}
            
            symbol = dados_mercado.get('symbol', 'BTCUSDT')
            preco_atual = dados_mercado.get('preco_atual', 0)
            quantidade = self.config.get('trading', {}).get('quantidade_padrao', 0.001)
            
            if preco_atual <= 0:
                return {'status': 'erro', 'razao': 'Preço inválido'}
            
            # Calcular quantidade baseada no capital disponível
            saldo = self.obter_saldo()
            if saldo <= 0:
                return {'status': 'erro', 'razao': 'Saldo insuficiente'}
            
            # Limitar quantidade para não exceder o capital
            valor_maximo = saldo * 0.1  # Máximo 10% do saldo por ordem
            quantidade = min(quantidade, valor_maximo / preco_atual)
            
            # Executar ordem de mercado
            side = "Buy" if decisao['decisao'] == 'comprar' else "Sell"
            
            response = self.client.place_order(
                category="spot",
                symbol=symbol,
                side=side,
                orderType="Market",
                qty=str(quantidade)
            )
            
            if response.get('retCode') == 0:
                order_id = response['result']['orderId']
                logger.info(f"✅ Ordem executada: {side} {quantidade} {symbol} @ {preco_atual}")
                return {
                    'status': 'executada',
                    'order_id': order_id,
                    'side': side,
                    'quantidade': quantidade,
                    'preco': preco_atual
                }
            else:
                logger.error(f"❌ Erro ao executar ordem: {response.get('retMsg')}")
                return {'status': 'erro', 'razao': response.get('retMsg')}
                
        except Exception as e:
            logger.error(f"Erro ao executar ordem: {e}")
            return {'status': 'erro', 'razao': str(e)}
    
    def fechar_ordem(self, order_id: str, symbol: str) -> dict:
        """Fecha uma ordem específica"""
        try:
            response = self.client.cancel_order(
                category="spot",
                symbol=symbol,
                orderId=order_id
            )
            
            if response.get('retCode') == 0:
                logger.info(f"✅ Ordem {order_id} fechada")
                return {'status': 'fechada', 'order_id': order_id}
            else:
                logger.error(f"❌ Erro ao fechar ordem: {response.get('retMsg')}")
                return {'status': 'erro', 'razao': response.get('retMsg')}
                
        except Exception as e:
            logger.error(f"Erro ao fechar ordem: {e}")
            return {'status': 'erro', 'razao': str(e)}
    
    def obter_ordens_ativas(self, symbol: str = None) -> list:
        """Obtém lista de ordens ativas"""
        try:
            params = {"category": "spot"}
            if symbol:
                params["symbol"] = symbol
                
            response = self.client.get_open_orders(**params)
            
            if response.get('retCode') == 0:
                return response['result']['list']
            else:
                logger.error(f"Erro ao obter ordens ativas: {response.get('retMsg')}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter ordens ativas: {e}")
            return [] 