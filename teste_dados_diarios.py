#!/usr/bin/env python3
"""
Teste de Dados Diários e Semanais
Verifica se as estatísticas diárias e semanais estão sendo calculadas corretamente
"""

import sqlite3
from datetime import datetime, timedelta

def testar_dados_diarios():
    """Testa cálculo de dados diários"""
    print("📅 TESTE DE DADOS DIÁRIOS E SEMANAIS")
    print("=" * 50)
    
    try:
        db_path = "dados/trading.db"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Obter data de hoje e início da semana
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        print(f"📅 Data de hoje: {hoje}")
        print(f"📅 Início da semana: {inicio_semana}")
        print()
        
        # Testar dados de preços
        print("📊 DADOS DE PREÇOS:")
        c.execute(f"SELECT COUNT(*) FROM precos WHERE DATE(timestamp) = '{hoje}'")
        precos_hoje = c.fetchone()[0]
        print(f"   Hoje: {precos_hoje:,} registros")
        
        c.execute(f"SELECT COUNT(*) FROM precos WHERE DATE(timestamp) >= '{inicio_semana}'")
        precos_semana = c.fetchone()[0]
        print(f"   Semana: {precos_semana:,} registros")
        
        c.execute("SELECT COUNT(*) FROM precos")
        precos_total = c.fetchone()[0]
        print(f"   Total: {precos_total:,} registros")
        print()
        
        # Testar dados de análises
        print("🤖 DADOS DE ANÁLISES:")
        c.execute(f"SELECT COUNT(*) FROM analises WHERE DATE(timestamp) = '{hoje}'")
        analises_hoje = c.fetchone()[0]
        print(f"   Hoje: {analises_hoje:,} registros")
        
        c.execute(f"SELECT COUNT(*) FROM analises WHERE DATE(timestamp) >= '{inicio_semana}'")
        analises_semana = c.fetchone()[0]
        print(f"   Semana: {analises_semana:,} registros")
        
        c.execute("SELECT COUNT(*) FROM analises")
        analises_total = c.fetchone()[0]
        print(f"   Total: {analises_total:,} registros")
        print()
        
        # Testar dados de ordens simuladas
        print("🚀 DADOS DE ORDENS SIMULADAS:")
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) = '{hoje}'")
        ordens_hoje = c.fetchone()[0]
        print(f"   Hoje: {ordens_hoje:,} ordens fechadas")
        
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) >= '{inicio_semana}'")
        ordens_semana = c.fetchone()[0]
        print(f"   Semana: {ordens_semana:,} ordens fechadas")
        
        c.execute("SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada'")
        ordens_total = c.fetchone()[0]
        print(f"   Total: {ordens_total:,} ordens fechadas")
        print()
        
        # Testar performance de hoje
        print("🎯 PERFORMANCE DE HOJE:")
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND resultado = 'win' AND DATE(timestamp_fechamento) = '{hoje}'")
        wins_hoje = c.fetchone()[0]
        
        c.execute(f"SELECT SUM(lucro_percentual) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) = '{hoje}'")
        lucro_hoje = c.fetchone()[0] or 0.0
        
        if ordens_hoje > 0:
            taxa_acerto_hoje = (wins_hoje / ordens_hoje) * 100
            print(f"   ✅ Wins: {wins_hoje}")
            print(f"   ❌ Losses: {ordens_hoje - wins_hoje}")
            print(f"   📈 Taxa de acerto: {taxa_acerto_hoje:.1f}%")
            print(f"   💰 Lucro total: {lucro_hoje:.2f}%")
        else:
            print("   📅 Nenhuma ordem fechada hoje")
        print()
        
        # Testar performance da semana
        print("🎯 PERFORMANCE DA SEMANA:")
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND resultado = 'win' AND DATE(timestamp_fechamento) >= '{inicio_semana}'")
        wins_semana = c.fetchone()[0]
        
        c.execute(f"SELECT SUM(lucro_percentual) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) >= '{inicio_semana}'")
        lucro_semana = c.fetchone()[0] or 0.0
        
        if ordens_semana > 0:
            taxa_acerto_semana = (wins_semana / ordens_semana) * 100
            print(f"   ✅ Wins: {wins_semana}")
            print(f"   ❌ Losses: {ordens_semana - wins_semana}")
            print(f"   📈 Taxa de acerto: {taxa_acerto_semana:.1f}%")
            print(f"   💰 Lucro total: {lucro_semana:.2f}%")
        else:
            print("   📅 Nenhuma ordem fechada esta semana")
        print()
        
        # Verificar dados por dia da semana
        print("📅 DADOS POR DIA DA SEMANA:")
        for i in range(7):
            data = inicio_semana + timedelta(days=i)
            c.execute(f"SELECT COUNT(*) FROM precos WHERE DATE(timestamp) = '{data}'")
            precos_dia = c.fetchone()[0]
            
            c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) = '{data}'")
            ordens_dia = c.fetchone()[0]
            
            if precos_dia > 0 or ordens_dia > 0:
                print(f"   {data.strftime('%A (%d/%m)')}: {precos_dia:,} preços, {ordens_dia} ordens")
        
        conn.close()
        
        print("\n✅ Teste de dados diários concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    testar_dados_diarios() 