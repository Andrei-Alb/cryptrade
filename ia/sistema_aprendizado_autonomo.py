#!/usr/bin/env python3
"""
Sistema de Aprendizado Autônomo da IA
A IA determina sua própria confiança e aprende com resultados
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
import yaml
import os

class SistemaAprendizadoAutonomo:
    """Sistema onde a IA determina sua própria confiança e aprende autonomamente"""
    
    def __init__(self, db_path: str = "dados/crypto_trading.db"):
        """
        Inicializa sistema de aprendizado autônomo
        
        Args:
            db_path: Caminho para banco de dados
        """
        # Forçar caminho absoluto para o banco de dados na pasta correta
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.path.dirname(__file__), '..', db_path)
            db_path = os.path.abspath(db_path)
        self.db_path = db_path
        self._criar_tabelas_aprendizado()
        
        # Histórico de performance para aprendizado
        self.historico_wins: List[float] = []
        self.historico_losses: List[float] = []
        self.sequencia_atual = 0  # 0 = neutro, >0 = wins, <0 = losses
        self.ultima_decisao: Optional[Dict[str, Any]] = None
        
        logger.info("🧠 Sistema de Aprendizado Autônomo inicializado")
    
    def _criar_tabelas_aprendizado(self):
        """Cria tabelas para aprendizado autônomo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de aprendizado autônomo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aprendizado_autonomo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    decisao TEXT NOT NULL,
                    confianca_ia REAL NOT NULL,
                    contexto_mercado TEXT,
                    resultado TEXT,
                    lucro_prejuizo REAL,
                    aprendizado TEXT,
                    sequencia_wins INTEGER DEFAULT 0,
                    sequencia_losses INTEGER DEFAULT 0,
                    ajuste_confianca REAL DEFAULT 0.0
                )
            """)
            
            # Tabela de padrões aprendidos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS padroes_aprendidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    padrao_tipo TEXT NOT NULL,
                    contexto TEXT,
                    resultado TEXT,
                    confianca_media REAL,
                    sucesso_rate REAL,
                    recomendacao TEXT
                )
            """)
            
            # Tabela de evolução da IA
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evolucao_ia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data DATE DEFAULT CURRENT_DATE,
                    total_decisoes INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0.0,
                    confianca_media REAL DEFAULT 0.0,
                    confianca_evolucao TEXT,
                    aprendizado_dia TEXT,
                    timestamp_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Tabelas de aprendizado autônomo criadas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas de aprendizado: {e}")
    
    def registrar_decisao_autonoma(self, symbol: str, decisao: Dict[str, Any], contexto_mercado: Dict[str, Any]):
        """
        Registra decisão autônoma da IA para aprendizado
        
        Args:
            symbol: Símbolo do ativo
            decisao: Decisão da IA (com confiança)
            contexto_mercado: Contexto do mercado
        """
        try:
            # Usar timeout para evitar database locked
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO aprendizado_autonomo 
                (symbol, decisao, confianca_ia, contexto_mercado, sequencia_wins, sequencia_losses)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                decisao.get('decisao', ''),
                decisao.get('confianca', 0.0),
                json.dumps(contexto_mercado),
                max(0, self.sequencia_atual),
                abs(min(0, self.sequencia_atual))
            ))
            
            conn.commit()
            conn.close()
            
            # Armazenar para análise
            self.ultima_decisao = {
                'symbol': symbol,
                'decisao': decisao.get('decisao', ''),
                'confianca': decisao.get('confianca', 0.0),
                'contexto': contexto_mercado,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar decisão autônoma: {e}")
    
    def registrar_resultado_operacao(self, symbol: str, resultado: str, lucro_prejuizo: float):
        """
        Registra resultado de uma operação para aprendizado
        
        Args:
            symbol: Símbolo do ativo
            resultado: 'win' ou 'loss'
            lucro_prejuizo: Valor do lucro/prejuízo
        """
        try:
            # Atualizar sequência
            if resultado == 'win':
                if self.sequencia_atual >= 0:
                    self.sequencia_atual += 1
                else:
                    self.sequencia_atual = 1  # Reset após loss
                self.historico_wins.append(lucro_prejuizo)
            else:  # loss
                if self.sequencia_atual <= 0:
                    self.sequencia_atual -= 1
                else:
                    self.sequencia_atual = -1  # Reset após win
                self.historico_losses.append(abs(lucro_prejuizo))
            
            # Atualizar banco de dados
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            # Atualizar última decisão com resultado
            cursor.execute("""
                UPDATE aprendizado_autonomo 
                SET resultado = ?, lucro_prejuizo = ?
                WHERE symbol = ? AND resultado IS NULL
                ORDER BY timestamp DESC LIMIT 1
            """, (resultado, lucro_prejuizo, symbol))
            
            # Gerar aprendizado
            aprendizado = self._gerar_aprendizado(resultado, lucro_prejuizo)
            
            # Atualizar com aprendizado
            cursor.execute("""
                UPDATE aprendizado_autonomo 
                SET aprendizado = ?
                WHERE symbol = ? AND resultado = ? AND lucro_prejuizo = ?
                ORDER BY timestamp DESC LIMIT 1
            """, (aprendizado, symbol, resultado, lucro_prejuizo))
            
            conn.commit()
            conn.close()
            
            # Registrar padrão se aplicável (em thread separada para evitar deadlock)
            self._registrar_padrao(resultado, lucro_prejuizo)
            
            logger.info(f"📊 Resultado registrado: {resultado} (${lucro_prejuizo:.2f}) - Sequência: {self.sequencia_atual}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar resultado: {e}")
    
    def _gerar_aprendizado(self, resultado: str, lucro_prejuizo: float) -> str:
        """Gera aprendizado baseado no resultado"""
        if self.ultima_decisao is None:
            return f"{resultado.upper()}: Sem dados de decisão anterior"
            
        confianca = self.ultima_decisao.get('confianca', 0.0)
        
        if resultado == 'win':
            if lucro_prejuizo > 0:
                return f"WIN: Padrão bem-sucedido. Confiança {confianca:.2f} foi adequada. Repetir estratégia similar."
            else:
                return f"WIN PEQUENO: Confiança {confianca:.2f} pode ser otimizada. Buscar sinais mais fortes."
        else:  # loss
            if abs(lucro_prejuizo) > 0:
                return f"LOSS: Evitar padrão similar. Confiança {confianca:.2f} foi insuficiente. Buscar sinais mais claros."
            else:
                return f"LOSS PEQUENO: Padrão pode ser refinado. Confiança {confianca:.2f} precisa ajuste."
    
    def _registrar_padrao(self, resultado: str, lucro_prejuizo: float):
        """Registra padrão para análise futura"""
        try:
            if not self.ultima_decisao:
                return
            
            # Analisar padrão baseado na decisão
            padrao_tipo = f"{self.ultima_decisao['decisao']}_{resultado}"
            contexto = json.dumps({
                'confianca': self.ultima_decisao['confianca'],
                'sequencia': self.sequencia_atual,
                'contexto_mercado': self.ultima_decisao['contexto']
            })
            
            # Calcular recomendação
            if resultado == 'win':
                if lucro_prejuizo > 0.5:  # Win significativo
                    recomendacao = "REPETIR: Padrão muito eficaz"
                else:
                    recomendacao = "REFINAR: Buscar sinais mais fortes"
            else:  # loss
                if abs(lucro_prejuizo) > 0.5:  # Loss significativo
                    recomendacao = "EVITAR: Padrão problemático"
                else:
                    recomendacao = "AJUSTAR: Refinar critérios"
            
            # Usar timeout e retry para evitar database locked
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    conn = sqlite3.connect(self.db_path, timeout=10.0)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO padroes_aprendidos 
                        (padrao_tipo, contexto, resultado, confianca_media, sucesso_rate, recomendacao)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        padrao_tipo,
                        contexto,
                        resultado,
                        self.ultima_decisao['confianca'],
                        1.0 if resultado == 'win' else 0.0,
                        recomendacao
                    ))
                    
                    conn.commit()
                    conn.close()
                    break  # Sucesso, sair do loop
                    
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e) and attempt < max_retries - 1:
                        logger.warning(f"Database locked, tentativa {attempt + 1}/{max_retries}")
                        time.sleep(0.1 * (attempt + 1))  # Backoff exponencial
                        continue
                    else:
                        raise e
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar padrão: {e}")
    
    def obter_recomendacao_confianca(self, symbol: str, contexto_atual: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém recomendação de confiança baseada no aprendizado
        
        Args:
            symbol: Símbolo do ativo
            contexto_atual: Contexto atual do mercado
            
        Returns:
            Recomendação de confiança e ajustes
        """
        try:
            # Analisar histórico recente
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Últimas 10 operações
            cursor.execute("""
                SELECT resultado, confianca_ia, lucro_prejuizo
                FROM aprendizado_autonomo 
                WHERE symbol = ? AND resultado IS NOT NULL
                ORDER BY timestamp DESC 
                LIMIT 10
            """, (symbol,))
            
            operacoes_recentes = cursor.fetchall()
            
            if not operacoes_recentes:
                return {
                    'confianca_recomendada': 0.5,
                    'ajuste': 0.0,
                    'razao': 'Sem histórico suficiente'
                }
            
            # Calcular estatísticas
            wins = sum(1 for op in operacoes_recentes if op[0] == 'win')
            losses = sum(1 for op in operacoes_recentes if op[0] == 'loss')
            win_rate = wins / len(operacoes_recentes) if operacoes_recentes else 0
            
            confianca_media = sum(op[1] for op in operacoes_recentes) / len(operacoes_recentes)
            
            # Ajustar confiança baseado no histórico
            ajuste = 0.0
            razao = ""
            
            if win_rate > 0.7:  # Muito bem-sucedido
                ajuste = 0.1
                razao = f"Win rate alto ({win_rate:.2%}) - aumentar confiança"
            elif win_rate < 0.3:  # Muito mal-sucedido
                ajuste = -0.1
                razao = f"Win rate baixo ({win_rate:.2%}) - reduzir confiança"
            elif self.sequencia_atual < -2:  # Sequência de losses
                ajuste = -0.05
                razao = f"Sequência de {abs(self.sequencia_atual)} losses - ser mais conservador"
            elif self.sequencia_atual > 2:  # Sequência de wins
                ajuste = 0.05
                razao = f"Sequência de {self.sequencia_atual} wins - ser mais agressivo"
            
            confianca_recomendada = max(0.1, min(0.95, confianca_media + ajuste))
            
            conn.close()
            
            return {
                'confianca_recomendada': confianca_recomendada,
                'ajuste': ajuste,
                'razao': razao,
                'win_rate': win_rate,
                'sequencia_atual': self.sequencia_atual
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter recomendação: {e}")
            return {
                'confianca_recomendada': 0.5,
                'ajuste': 0.0,
                'razao': f'Erro: {e}'
            }
    
    def obter_estatisticas_aprendizado(self) -> Dict[str, Any]:
        """Retorna estatísticas do aprendizado autônomo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de decisões
            cursor.execute("SELECT COUNT(*) FROM aprendizado_autonomo")
            total_decisoes = cursor.fetchone()[0]
            
            # Decisões com resultado
            cursor.execute("SELECT COUNT(*) FROM aprendizado_autonomo WHERE resultado IS NOT NULL")
            decisoes_com_resultado = cursor.fetchone()[0]
            
            # Wins e losses
            cursor.execute("SELECT COUNT(*) FROM aprendizado_autonomo WHERE resultado = 'win'")
            total_wins = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM aprendizado_autonomo WHERE resultado = 'loss'")
            total_losses = cursor.fetchone()[0]
            
            # Confiança média
            cursor.execute("SELECT AVG(confianca_ia) FROM aprendizado_autonomo")
            confianca_media = cursor.fetchone()[0] or 0
            
            # Win rate
            win_rate = total_wins / (total_wins + total_losses) if (total_wins + total_losses) > 0 else 0
            
            conn.close()
            
            return {
                'total_decisoes': total_decisoes,
                'decisoes_com_resultado': decisoes_com_resultado,
                'total_wins': total_wins,
                'total_losses': total_losses,
                'win_rate': win_rate,
                'confianca_media': confianca_media,
                'sequencia_atual': self.sequencia_atual
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def atualizar_evolucao_diaria(self):
        """Atualiza evolução diária da IA"""
        try:
            stats = self.obter_estatisticas_aprendizado()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se já existe registro para hoje
            cursor.execute("""
                SELECT id FROM evolucao_ia 
                WHERE data = CURRENT_DATE
            """)
            
            existe_hoje = cursor.fetchone()
            
            if existe_hoje:
                # Atualizar registro existente
                cursor.execute("""
                    UPDATE evolucao_ia SET
                    total_decisoes = ?,
                    wins = ?,
                    losses = ?,
                    win_rate = ?,
                    confianca_media = ?,
                    aprendizado_dia = ?,
                    timestamp_atualizacao = CURRENT_TIMESTAMP
                    WHERE data = CURRENT_DATE
                """, (
                    stats.get('total_decisoes', 0),
                    stats.get('total_wins', 0),
                    stats.get('total_losses', 0),
                    stats.get('win_rate', 0.0),
                    stats.get('confianca_media', 0.0),
                    f"Sequência atual: {stats.get('sequencia_atual', 0)}"
                ))
            else:
                # Criar novo registro
                cursor.execute("""
                    INSERT INTO evolucao_ia 
                    (total_decisoes, wins, losses, win_rate, confianca_media, aprendizado_dia)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    stats.get('total_decisoes', 0),
                    stats.get('total_wins', 0),
                    stats.get('total_losses', 0),
                    stats.get('win_rate', 0.0),
                    stats.get('confianca_media', 0.0),
                    f"Sequência atual: {stats.get('sequencia_atual', 0)}"
                ))
            
            conn.commit()
            conn.close()
            
            logger.info("📈 Evolução diária da IA atualizada")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar evolução diária: {e}")
    
    def obter_evolucao_ia(self, dias: int = 7) -> List[Dict[str, Any]]:
        """
        Obtém evolução da IA nos últimos dias
        
        Args:
            dias: Número de dias para analisar
            
        Returns:
            Lista com evolução da IA
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data, total_decisoes, wins, losses, win_rate, confianca_media, aprendizado_dia
                FROM evolucao_ia 
                WHERE data >= date('now', '-{} days')
                ORDER BY data DESC
            """.format(dias))
            
            evolucao = []
            for row in cursor.fetchall():
                evolucao.append({
                    'data': row[0],
                    'total_decisoes': row[1],
                    'wins': row[2],
                    'losses': row[3],
                    'win_rate': row[4],
                    'confianca_media': row[5],
                    'aprendizado_dia': row[6]
                })
            
            conn.close()
            return evolucao
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter evolução da IA: {e}")
            return []
    
    def obter_padroes_aprendidos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém padrões aprendidos pela IA
        
        Args:
            limit: Limite de padrões a retornar
            
        Returns:
            Lista de padrões aprendidos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT padrao_tipo, contexto, resultado, confianca_media, sucesso_rate, recomendacao, timestamp
                FROM padroes_aprendidos 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            padroes = []
            for row in cursor.fetchall():
                padroes.append({
                    'padrao_tipo': row[0],
                    'contexto': json.loads(row[1]) if row[1] else {},
                    'resultado': row[2],
                    'confianca_media': row[3],
                    'sucesso_rate': row[4],
                    'recomendacao': row[5],
                    'timestamp': row[6]
                })
            
            conn.close()
            return padroes
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter padrões aprendidos: {e}")
            return []
    
    def limpar_historico_antigo(self, dias: int = 30):
        """
        Limpa histórico antigo para otimizar performance
        
        Args:
            dias: Manter apenas dados dos últimos X dias
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Limpar decisões antigas
            cursor.execute("""
                DELETE FROM aprendizado_autonomo 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(dias))
            
            decisoes_removidas = cursor.rowcount
            
            # Limpar padrões antigos
            cursor.execute("""
                DELETE FROM padroes_aprendidos 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(dias))
            
            padroes_removidos = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"🧹 Limpeza concluída: {decisoes_removidas} decisões e {padroes_removidos} padrões removidos")
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar histórico: {e}")
    
    def exportar_aprendizado(self, arquivo: str = "aprendizado_ia.json"):
        """
        Exporta dados de aprendizado para arquivo JSON
        
        Args:
            arquivo: Nome do arquivo de saída
        """
        try:
            dados = {
                'estatisticas': self.obter_estatisticas_aprendizado(),
                'evolucao_7_dias': self.obter_evolucao_ia(7),
                'padroes_recentes': self.obter_padroes_aprendidos(20),
                'timestamp_exportacao': datetime.now().isoformat()
            }
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📤 Aprendizado exportado para {arquivo}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar aprendizado: {e}")
    
    def resetar_aprendizado(self):
        """Reseta todo o aprendizado da IA (cuidado!)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Limpar todas as tabelas de aprendizado
            cursor.execute("DELETE FROM aprendizado_autonomo")
            cursor.execute("DELETE FROM padroes_aprendidos")
            cursor.execute("DELETE FROM evolucao_ia")
            
            # Resetar variáveis internas
            self.historico_wins.clear()
            self.historico_losses.clear()
            self.sequencia_atual = 0
            self.ultima_decisao = None
            
            conn.commit()
            conn.close()
            
            logger.warning("🔄 Aprendizado da IA completamente resetado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao resetar aprendizado: {e}") 