#!/usr/bin/env python3
"""
Script para verificar estatísticas de performance da IA
"""

import sqlite3
from datetime import datetime, timedelta

def verificar_estatisticas_ia():
    try:
        conn = sqlite3nect('dados/crypto_trading.db')
        c = conn.cursor()
        
        print('📊 ESTATÍSTICAS DA IA - PREVISÕES E PERFORMANCE)
        print('=' * 60)
        
        # Verificar tabelas existentes
        c.execute("SELECT name FROM sqlite_master WHERE type='table')
        tabelas = [row[0] for row in c.fetchall()]
        print(f📋 Tabelas encontradas: {tabelas}')
        
        # Estatísticas de ordens simuladas
        if ordens_simuladas' in tabelas:
            c.execute('SELECT COUNT(*) FROM ordens_simuladas WHERE status = "fechada"')
            total_ordens = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM ordens_simuladas WHERE status = "fechada" AND resultado = "win"')
            wins = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM ordens_simuladas WHERE status = "fechada" AND resultado = "loss"')
            losses = c.fetchone()[0]
            
            c.execute('SELECT AVG(lucro_percentual) FROM ordens_simuladas WHERE status = "fechada")
            lucro_medio = c.fetchone()[0] or 0
            
            print(fundefinedn🎯 ORDENS SIMULADAS:')
            print(f   Total fechadas: {total_ordens}')
            print(f'   Wins: {wins}')
            print(f'   Losses: {losses}')
            print(f'   Taxa acerto: {(wins/total_ordens*100):.1%' if total_ordens > 0se    Taxa acerto: 0%')
            print(f   Lucro médio: {lucro_medio:.2f}%')
        
        # Estatísticas de previsões da IA
        if analise_previsoes_ia' in tabelas:
            c.execute('SELECT COUNT(*) FROM analise_previsoes_ia')
            total_previsoes = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM analise_previsoes_ia WHERE precisao_target = "acerto"')
            targets_acertos = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM analise_previsoes_ia WHERE precisao_stop = "acerto"')
            stops_acertos = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM analise_previsoes_ia WHERE resultado_real = "win"')
            wins_previsoes = c.fetchone()[0]
            
            print(fn🧠 PREVISÕES DA IA:')
            print(f   Total análises: {total_previsoes}')
            print(f'   Targets acertados: {targets_acertos}')
            print(f'   Stops acertados: {stops_acertos}')
            print(f'   Precisão targets:[object Object](targets_acertos/total_previsoes*1001%' if total_previsoes >0 else '   Precisão targets: 0%')
            print(f   Precisão stops: {(stops_acertos/total_previsoes*1001%' if total_previsoes >0 else    Precisão stops: 0%')
            print(f'   Win rate: {(wins_previsoes/total_previsoes*1001%' if total_previsoes > 0 else '   Win rate: 0%')
        
        # Estatísticas de aprendizado
        if 'aprendizado_ia' in tabelas:
            c.execute('SELECT COUNT(*) FROM aprendizado_ia')
            total_aprendizado = c.fetchone()[0]
            
            c.execute('SELECT AVG(CASE WHEN resultado = "win THEN1ELSE 0.0) FROM aprendizado_ia')
            taxa_acerto_aprendizado = c.fetchone()[0] or 0
            
            print(f'\n📚 APRENDIZADO DA IA:')
            print(f'   Total registros: {total_aprendizado}')
            print(f Taxa acerto: {taxa_acerto_aprendizado*100:.1f}%')
        
        # Últimas decisões da IA
        if 'decisoes_ia' in tabelas:
            c.execute('SELECT decisao, confianca, timestamp FROM decisoes_ia ORDER BY timestamp DESC LIMIT 5)           ultimas_decisoes = c.fetchall()
            
            print(f'\n🤖 ÚLTIMAS DECISÕES DA IA:)         for decisao, confianca, timestamp in ultimas_decisoes:
                print(f[object Object]timestamp}: {decisao} (confiança: {confianca:.2f})')
        
        # Estatísticas de performance da IA
        if 'metricas_ia' in tabelas:
            c.execute('SELECT tempo_medio, cache_hit_rate, timeout_rate, total_inferencias FROM metricas_ia ORDER BY timestamp DESC LIMIT 1')
            metricas = c.fetchone()
            
            if metricas:
                print(f'\n⚡ PERFORMANCE DA IA:)             print(f   Tempo médio: {metricas[0]:.2f}s)             print(f   Cache hit rate: [object Object]metricas[1]*100:.1f}%)             print(f'   Timeout rate: [object Object]metricas[2]*100:.1f}%)             print(f'   Total inferências: {metricas[3]}')
        
        conn.close()
        
    except Exception as e:
        print(f❌ Erro ao consultar banco: {e})if __name__ == "__main__":
    verificar_estatisticas_ia() 