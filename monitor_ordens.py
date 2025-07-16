#!/usr/bin/env python3
"""
Monitor de Ordens em Tempo Real
Mostra ordens ativas, fechadas e estatísticas
"""

import sqlite3
import time
import os
from datetime import datetime
from loguru import logger

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')

def obter_ordens_ativas():
    """Obtém ordens ativas do banco"""
    try:
        conn = sqlite3.connect('dados/trading.db', timeout=30)
        conn.execute("PRAGMA journal_mode=WAL;")
        c = conn.cursor()
        
        c.execute('''
        SELECT ordem_id, tipo, simbolo, preco_entrada, preco_alvo, preco_stop, 
               confianca_ia, timestamp
        FROM ordens_simuladas 
        WHERE status = 'aberta' 
        ORDER BY timestamp DESC
        ''')
        
        ordens = c.fetchall()
        conn.close()
        return ordens
    except Exception as e:
        logger.error(f"Erro ao obter ordens ativas: {e}")
        return []

def obter_ultimas_ordens_fechadas(limite=10):
    """Obtém últimas ordens fechadas"""
    try:
        conn = sqlite3.connect('dados/trading.db', timeout=30)
        conn.execute("PRAGMA journal_mode=WAL;")
        c = conn.cursor()
        
        c.execute('''
        SELECT ordem_id, tipo, simbolo, resultado, lucro_percentual, 
               duracao_segundos, razao_fechamento, timestamp_fechamento
        FROM ordens_simuladas 
        WHERE status = 'fechada' 
        ORDER BY timestamp_fechamento DESC 
        LIMIT ?
        ''', (limite,))
        
        ordens = c.fetchall()
        conn.close()
        return ordens
    except Exception as e:
        logger.error(f"Erro ao obter ordens fechadas: {e}")
        return []

def obter_estatisticas():
    """Obtém estatísticas gerais"""
    try:
        conn = sqlite3.connect('dados/trading.db', timeout=30)
        conn.execute("PRAGMA journal_mode=WAL;")
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
        
        # Ordens ativas
        c.execute('SELECT COUNT(*) FROM ordens_simuladas WHERE status = "aberta"')
        ordens_ativas = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_ordens': total_ordens,
            'wins': wins,
            'losses': losses,
            'taxa_acerto': (wins / total_ordens * 100) if total_ordens > 0 else 0,
            'lucro_total': lucro_total,
            'ordens_ativas': ordens_ativas
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {}

def exibir_ordens_ativas(ordens):
    """Exibe ordens ativas"""
    if not ordens:
        print("📋 Nenhuma ordem ativa no momento")
        return
    
    print("🟡 ORDENS ATIVAS:")
    print("=" * 80)
    print(f"{'ID':<15} {'TIPO':<8} {'SÍMBOLO':<10} {'ENTRADA':<10} {'ALVO':<10} {'STOP':<10} {'CONF':<6} {'DURAÇÃO':<10}")
    print("-" * 80)
    
    for ordem in ordens:
        ordem_id, tipo, simbolo, entrada, alvo, stop, confianca, timestamp = ordem
        duracao = (datetime.now() - datetime.fromisoformat(timestamp)).total_seconds()
        
        print(f"{ordem_id:<15} {tipo.upper():<8} {simbolo:<10} {entrada:<10.2f} {alvo:<10.2f} {stop:<10.2f} {confianca:<6.2f} {duracao:<10.1f}s")

def exibir_ordens_fechadas(ordens):
    """Exibe últimas ordens fechadas"""
    if not ordens:
        print("📋 Nenhuma ordem fechada ainda")
        return
    
    print("📊 ÚLTIMAS ORDENS FECHADAS:")
    print("=" * 100)
    print(f"{'ID':<15} {'TIPO':<8} {'SÍMBOLO':<10} {'RESULTADO':<10} {'LUCRO':<8} {'DURAÇÃO':<10} {'RAZÃO':<30}")
    print("-" * 100)
    
    for ordem in ordens:
        ordem_id, tipo, simbolo, resultado, lucro, duracao, razao, timestamp = ordem
        
        # Emoji para resultado
        emoji = "🟢" if resultado == "win" else "🔴" if resultado == "loss" else "🟡"
        
        # Truncar razão se muito longa
        razao_short = razao[:27] + "..." if len(razao) > 30 else razao
        
        print(f"{ordem_id:<15} {tipo.upper():<8} {simbolo:<10} {emoji} {resultado.upper():<8} {lucro:<8.2f}% {duracao:<10.1f}s {razao_short:<30}")

def exibir_estatisticas(stats):
    """Exibe estatísticas gerais"""
    print("📈 ESTATÍSTICAS GERAIS:")
    print("=" * 50)
    print(f"Total de ordens: {stats.get('total_ordens', 0)}")
    print(f"Wins: {stats.get('wins', 0)}")
    print(f"Losses: {stats.get('losses', 0)}")
    print(f"Taxa de acerto: {stats.get('taxa_acerto', 0):.1f}%")
    print(f"Lucro total: {stats.get('lucro_total', 0):.2f}%")
    print(f"Ordens ativas: {stats.get('ordens_ativas', 0)}")

def monitor_continuo():
    """Monitor contínuo de ordens"""
    print("🎯 MONITOR DE ORDENS EM TEMPO REAL")
    print("Pressione Ctrl+C para sair")
    print("=" * 60)
    
    try:
        while True:
            limpar_tela()
            
            print(f"🕐 {datetime.now().strftime('%H:%M:%S')} - MONITOR DE ORDENS")
            print("=" * 60)
            
            # Obter dados
            ordens_ativas = obter_ordens_ativas()
            ordens_fechadas = obter_ultimas_ordens_fechadas(5)
            stats = obter_estatisticas()
            
            # Exibir dados
            exibir_estatisticas(stats)
            print()
            exibir_ordens_ativas(ordens_ativas)
            print()
            exibir_ordens_fechadas(ordens_fechadas)
            
            print("\n" + "=" * 60)
            print("🔄 Atualizando em 5 segundos... (Ctrl+C para sair)")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n👋 Monitor encerrado")

def exibir_resumo():
    """Exibe resumo único"""
    print("📊 RESUMO DE ORDENS")
    print("=" * 50)
    
    ordens_ativas = obter_ordens_ativas()
    ordens_fechadas = obter_ultimas_ordens_fechadas(10)
    stats = obter_estatisticas()
    
    exibir_estatisticas(stats)
    print()
    exibir_ordens_ativas(ordens_ativas)
    print()
    exibir_ordens_fechadas(ordens_fechadas)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuo":
        monitor_continuo()
    else:
        exibir_resumo() 