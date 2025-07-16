import sqlite3
import os
from datetime import datetime
from loguru import logger

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