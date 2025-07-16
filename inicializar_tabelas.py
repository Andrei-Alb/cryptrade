#!/usr/bin/env python3
"""
Script para inicializar tabelas de simulação
"""

import sqlite3
import yaml
from loguru import logger

def inicializar_tabelas():
    """Inicializa todas as tabelas necessárias"""
    try:
        # Carregar configuração
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        # Conectar ao banco
        conn = sqlite3.connect("dados/crypto_trading.db")
        cursor = conn.cursor()
        
        logger.info("🔧 Inicializando tabelas de simulação...")
        
        # Tabela de ordens simuladas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordens_simuladas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                order_id TEXT UNIQUE,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
                timestamp_fechamento DATETIME,
                preco_entrada REAL,
                preco_saida REAL,
                resultado TEXT,
                lucro_prejuizo REAL,
                confianca_ia REAL,
                razao_decisao TEXT,
                dados_mercado TEXT
            )
        """)
        
        # Tabela de decisões da IA
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisoes_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                decisao TEXT NOT NULL,
                confianca REAL NOT NULL,
                razao TEXT,
                dados_entrada TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resultado_operacao TEXT,
                lucro_prejuizo REAL
            )
        """)
        
        # Tabela de performance da IA
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE DEFAULT CURRENT_DATE,
                total_decisoes INTEGER DEFAULT 0,
                decisoes_corretas INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                lucro_total REAL DEFAULT 0.0,
                prejuizo_total REAL DEFAULT 0.0,
                profit_factor REAL DEFAULT 0.0,
                timestamp_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de ordens dinâmicas (usada pelo monitor e gestor)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordens_dinamicas (
                order_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                tipo_ordem TEXT NOT NULL,
                preco_entrada REAL NOT NULL,
                quantidade REAL NOT NULL,
                status TEXT NOT NULL,
                preco_saida REAL,
                timestamp_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
                timestamp_fechamento DATETIME,
                lucro_prejuizo REAL DEFAULT 0.0,
                pnl_percentual REAL DEFAULT 0.0,
                confianca_ia REAL DEFAULT 0.0,
                tempo_operacao REAL DEFAULT 0.0,
                stop_loss_inicial REAL,
                take_profit_inicial REAL,
                stop_loss_atual REAL,
                take_profit_atual REAL,
                tempo_aberta_segundos INTEGER,
                ajustes_stop_loss INTEGER DEFAULT 0,
                ajustes_take_profit INTEGER DEFAULT 0,
                saida_inteligente_utilizada BOOLEAN DEFAULT FALSE,
                razao_saida TEXT,
                dados_mercado_saida TEXT,
                razao_fechamento TEXT
            )
        ''')
        # Garante que todas as colunas críticas existem
        cursor.execute("PRAGMA table_info(ordens_dinamicas);")
        columns = [info[1] for info in cursor.fetchall()]
        colunas_criticas = [
            'stop_loss_inicial', 'take_profit_inicial', 'stop_loss_atual', 'take_profit_atual',
            'tempo_aberta_segundos', 'ajustes_stop_loss', 'ajustes_take_profit',
            'saida_inteligente_utilizada', 'razao_saida', 'dados_mercado_saida',
            'razao_fechamento', 'timestamp_abertura', 'timestamp_fechamento'
        ]
        tipos_colunas = {
            'stop_loss_inicial': 'REAL',
            'take_profit_inicial': 'REAL',
            'stop_loss_atual': 'REAL',
            'take_profit_atual': 'REAL',
            'tempo_aberta_segundos': 'INTEGER',
            'ajustes_stop_loss': 'INTEGER DEFAULT 0',
            'ajustes_take_profit': 'INTEGER DEFAULT 0',
            'saida_inteligente_utilizada': 'BOOLEAN DEFAULT FALSE',
            'razao_saida': 'TEXT',
            'dados_mercado_saida': 'TEXT',
            'razao_fechamento': 'TEXT',
            'timestamp_abertura': 'DATETIME',
            'timestamp_fechamento': 'DATETIME'
        }
        for coluna in colunas_criticas:
            if coluna not in columns:
                cursor.execute(f"ALTER TABLE ordens_dinamicas ADD COLUMN {coluna} {tipos_colunas[coluna]};")
                logger.info(f"✅ Coluna '{coluna}' adicionada à tabela 'ordens_dinamicas'")
        # Tabela de aprendizado_autonomo (completa, conforme sistema_aprendizado_autonomo)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aprendizado_autonomo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                decisao TEXT NOT NULL,
                confianca_ia REAL NOT NULL,
                confianca REAL,
                dados_entrada TEXT,
                contexto_mercado TEXT,
                resultado TEXT,
                lucro_prejuizo REAL,
                aprendizado TEXT,
                sequencia_wins INTEGER DEFAULT 0,
                sequencia_losses INTEGER DEFAULT 0,
                ajuste_confianca REAL DEFAULT 0.0
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.success("✅ Tabelas de simulação criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar tabelas: {e}")
        return False

if __name__ == "__main__":
    inicializar_tabelas() 