import sqlite3
import os
from datetime import datetime
from loguru import logger
from typing import Optional

class Armazenamento:
    def __init__(self, db_path=None):
        self.db_path = db_path or self.get_db_path()
        self.criar_tabelas()

    def get_db_path(self):
        os.makedirs('dados', exist_ok=True)
        return os.path.join('dados', 'trading.db')

    def criar_tabelas(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            preco_atual DECIMAL(10,2),
            bid DECIMAL(10,2),
            ask DECIMAL(10,2),
            volume INTEGER,
            open_price DECIMAL(10,2),
            high_price DECIMAL(10,2),
            low_price DECIMAL(10,2),
            close_price DECIMAL(10,2),
            simbolo TEXT
        );
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS analises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            dados_entrada TEXT,
            resultado TEXT,
            confianca DECIMAL(5,2)
        );
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            tipo TEXT,
            quantidade INTEGER,
            preco DECIMAL(10,2),
            status TEXT,
            resposta_api TEXT
        );
        ''')
        conn.commit()
        conn.close()

    def salvar_precos(self, timestamp, preco_atual, preco_abertura=None, preco_minimo=None, preco_maximo=None, preco_medio=None, variacao=None, volume=None, simbolo=None):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO precos (timestamp, preco_atual, open_price, high_price, low_price, close_price, volume, simbolo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                preco_atual,
                preco_abertura,
                preco_maximo,
                preco_minimo,
                preco_medio,
                volume,
                simbolo
            ))
            conn.commit()
            conn.close()
            logger.info(f"Preço salvo no banco: {preco_atual} ({simbolo})")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar preço: {e}")
            return False

    def salvar_analise(self, dados_entrada, resultado, confianca):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO analises (timestamp, dados_entrada, resultado, confianca)
            VALUES (?, ?, ?, ?)
            ''', (
                datetime.now(),
                str(dados_entrada),
                resultado,
                confianca
            ))
            conn.commit()
            conn.close()
            logger.info(f"Análise salva: {resultado} (confiança: {confianca})")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar análise: {e}")
            return False

    def salvar_ordem(self, tipo, quantidade, preco, status, resposta_api):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO ordens (timestamp, tipo, quantidade, preco, status, resposta_api)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                tipo,
                quantidade,
                preco,
                status,
                str(resposta_api)
            ))
            conn.commit()
            conn.close()
            logger.info(f"Ordem salva: {tipo} {quantidade} @ {preco}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar ordem: {e}")
            return False

    def obter_ultimos_precos(self, limite=100):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            SELECT timestamp, preco_atual, volume, close_price, simbolo
            FROM precos
            WHERE preco_atual IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
            ''', (limite,))
            resultados = c.fetchall()
            conn.close()
            return resultados
        except Exception as e:
            logger.error(f"Erro ao obter preços: {e}")
            return []

    def obter_estatisticas(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM precos')
            total_precos = c.fetchone()[0]
            c.execute('SELECT preco_atual FROM precos WHERE preco_atual IS NOT NULL ORDER BY timestamp DESC LIMIT 1')
            ultimo_preco = c.fetchone()
            ultimo_preco = ultimo_preco[0] if ultimo_preco else None
            c.execute('SELECT COUNT(*) FROM analises')
            total_analises = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM ordens')
            total_ordens = c.fetchone()[0]
            conn.close()
            return {
                'total_precos': total_precos,
                'ultimo_preco': ultimo_preco,
                'total_analises': total_analises,
                'total_ordens': total_ordens
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {} 

class ArmazenamentoCrypto(Armazenamento):
    """Armazenamento específico para dados de crypto"""
    
    def __init__(self, db_path=None):
        super().__init__(db_path)
        self.criar_tabelas_crypto()
    
    def criar_tabelas_crypto(self):
        """Cria tabelas específicas para crypto"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabela de dados crypto
        c.execute('''
        CREATE TABLE IF NOT EXISTS crypto_dados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            symbol TEXT NOT NULL,
            preco_atual DECIMAL(15,8),
            preco_abertura DECIMAL(15,8),
            preco_minimo DECIMAL(15,8),
            preco_maximo DECIMAL(15,8),
            volume DECIMAL(20,8),
            variacao_percentual DECIMAL(10,4),
            rsi DECIMAL(5,2),
            volatilidade DECIMAL(10,6),
            tendencia TEXT,
            fonte TEXT
        );
        ''')
        
        # Tabela de decisões da IA
        c.execute('''
        CREATE TABLE IF NOT EXISTS decisoes_ia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            symbol TEXT NOT NULL,
            decisao TEXT NOT NULL,
            confianca DECIMAL(5,2),
            razao TEXT,
            dados_entrada TEXT,
            resultado TEXT,
            acerto BOOLEAN
        );
        ''')
        
        # Tabela de ordens crypto
        c.execute('''
        CREATE TABLE IF NOT EXISTS ordens_crypto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            order_id TEXT UNIQUE,
            symbol TEXT NOT NULL,
            tipo TEXT NOT NULL,
            quantidade DECIMAL(15,8),
            preco_entrada DECIMAL(15,8),
            preco_atual DECIMAL(15,8),
            status TEXT NOT NULL,
            lucro_prejuizo DECIMAL(15,8),
            pnl_percentual DECIMAL(10,4),
            confianca_ia DECIMAL(5,2),
            dados_mercado TEXT
        );
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Tabelas crypto criadas")
    
    def salvar_dados_crypto(self, dados: dict):
        """Salva dados de crypto no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO crypto_dados (
                timestamp, symbol, preco_atual, preco_abertura, preco_minimo, 
                preco_maximo, volume, variacao_percentual, rsi, volatilidade, 
                tendencia, fonte
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                dados.get('symbol', ''),
                dados.get('preco_atual', 0),
                dados.get('preco_abertura', 0),
                dados.get('preco_minimo', 0),
                dados.get('preco_maximo', 0),
                dados.get('volume', 0),
                dados.get('variacao', 0),
                dados.get('rsi', 50.0),
                dados.get('volatilidade', 0.02),
                dados.get('tendencia', 'lateral'),
                dados.get('fonte', 'Bybit')
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados crypto: {e}")
            return False
    
    def salvar_decisao_ia(self, symbol: str, decisao: dict, dados_entrada: Optional[dict] = None):
        """Salva decisão da IA"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO decisoes_ia (
                timestamp, symbol, decisao, confianca, razao, dados_entrada
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                symbol,
                decisao.get('decisao', 'aguardar'),
                decisao.get('confianca', 0.5),
                decisao.get('razao', ''),
                str(dados_entrada) if dados_entrada else ''
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar decisão IA: {e}")
            return False
    
    def salvar_ordem_crypto(self, ordem: dict):
        """Salva ordem de crypto"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
            INSERT INTO ordens_crypto (
                timestamp, order_id, symbol, tipo, quantidade, preco_entrada,
                preco_atual, status, lucro_prejuizo, pnl_percentual, confianca_ia, dados_mercado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                ordem.get('order_id', ''),
                ordem.get('symbol', ''),
                ordem.get('tipo', ''),
                ordem.get('quantidade', 0),
                ordem.get('preco_entrada', 0),
                ordem.get('preco_atual', 0),
                ordem.get('status', 'aberta'),
                ordem.get('lucro_prejuizo', 0),
                ordem.get('pnl_percentual', 0),
                ordem.get('confianca_ia', 0.5),
                str(ordem.get('dados_mercado', {}))
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar ordem crypto: {e}")
            return False
    
    def obter_estatisticas_crypto(self):
        """Obtém estatísticas dos dados crypto"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Total de dados
            c.execute('SELECT COUNT(*) FROM crypto_dados')
            total_dados = c.fetchone()[0]
            
            # Total de decisões
            c.execute('SELECT COUNT(*) FROM decisoes_ia')
            total_decisoes = c.fetchone()[0]
            
            # Total de ordens
            c.execute('SELECT COUNT(*) FROM ordens_crypto')
            total_ordens = c.fetchone()[0]
            
            # Último preço
            c.execute('''
            SELECT symbol, preco_atual, timestamp 
            FROM crypto_dados 
            ORDER BY timestamp DESC 
            LIMIT 1
            ''')
            ultimo_dado = c.fetchone()
            
            # Taxa de acerto das decisões
            c.execute('''
            SELECT COUNT(*) FROM decisoes_ia 
            WHERE acerto = 1
            ''')
            acertos = c.fetchone()[0]
            
            taxa_acerto = (acertos / total_decisoes * 100) if total_decisoes > 0 else 0
            
            conn.close()
            
            return {
                'total_dados': total_dados,
                'total_decisoes': total_decisoes,
                'total_ordens': total_ordens,
                'ultimo_dado': {
                    'symbol': ultimo_dado[0] if ultimo_dado else None,
                    'preco': ultimo_dado[1] if ultimo_dado else None,
                    'timestamp': ultimo_dado[2] if ultimo_dado else None
                },
                'taxa_acerto': taxa_acerto
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas crypto: {e}")
            return {} 