#!/usr/bin/env python3
"""
Monitor do Robô de Trading - Versão Otimizada
Exibe status em tempo real do sistema de forma mais rápida
"""

import os
import time
import sqlite3
import requests
from datetime import datetime, timedelta
from loguru import logger
from executor import ExecutorOrdensSimuladas

def verificar_processo_robo():
    """
    Verifica se o robô está rodando
    """
    try:
        pid_file = "logs/robo.pid"
        if not os.path.exists(pid_file):
            return False, None
        
        with open(pid_file, 'r') as f:
            pid = f.read().strip()
        
        # Verificar se o processo existe
        if os.path.exists(f"/proc/{pid}"):
            return True, pid
        else:
            return False, None
    except:
        return False, None

def verificar_ollama():
    """
    Verifica status do Ollama
    """
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return True, len(models)
        else:
            return False, 0
    except:
        return False, 0

def obter_estatisticas_banco_rapido():
    """
    Obtém estatísticas do banco de dados de forma otimizada
    """
    try:
        db_path = "dados/trading.db"
        if not os.path.exists(db_path):
            return {}
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Obter data de hoje e início da semana
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())  # Segunda-feira
        
        # Consultas otimizadas em batch
        queries = [
            ('total_precos_hoje', f"SELECT COUNT(*) FROM precos WHERE DATE(timestamp) = '{hoje}'"),
            ('total_analises_hoje', f"SELECT COUNT(*) FROM analises WHERE DATE(timestamp) = '{hoje}'"),
            ('total_ordens_hoje', f"SELECT COUNT(*) FROM ordens WHERE DATE(timestamp) = '{hoje}'"),
            ('total_precos_semana', f"SELECT COUNT(*) FROM precos WHERE DATE(timestamp) >= '{inicio_semana}'"),
            ('total_analises_semana', f"SELECT COUNT(*) FROM analises WHERE DATE(timestamp) >= '{inicio_semana}'"),
            ('total_ordens_semana', f"SELECT COUNT(*) FROM ordens WHERE DATE(timestamp) >= '{inicio_semana}'"),
            ('ultimo_preco_ibov', 'SELECT preco_atual, timestamp FROM precos WHERE simbolo = "IBOV" ORDER BY timestamp DESC LIMIT 1'),
            ('ultimo_preco_win', 'SELECT preco_atual, timestamp FROM precos WHERE simbolo LIKE "WIN%" ORDER BY timestamp DESC LIMIT 1'),
            ('ultima_analise', 'SELECT resultado, confianca, timestamp FROM analises ORDER BY timestamp DESC LIMIT 1')
        ]
        
        stats = {}
        for key, query in queries:
            try:
                c.execute(query)
                result = c.fetchone()
                if result:
                    if key.startswith('ultimo_preco_'):
                        stats[key] = {'preco': result[0], 'timestamp': result[1]}
                    elif key == 'ultima_analise':
                        stats[key] = {'resultado': result[0], 'confianca': result[1], 'timestamp': result[2]}
                    else:
                        stats[key] = result[0]
            except Exception as e:
                logger.debug(f"Erro na query {key}: {e}")
        
        conn.close()
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {}

def obter_estatisticas_aprendizado_rapido():
    """
    Obtém estatísticas de aprendizado de forma otimizada (hoje e semana)
    """
    try:
        executor = ExecutorOrdensSimuladas()
        stats = executor.obter_estatisticas_aprendizado()
        
        # Obter data de hoje e início da semana
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        # Conectar ao banco para obter dados diários e semanais
        conn = sqlite3.connect(executor.db_path)
        c = conn.cursor()
        
        # Estatísticas de hoje
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) = '{hoje}'")
        total_ordens_hoje = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND resultado = 'win' AND DATE(timestamp_fechamento) = '{hoje}'")
        wins_hoje = c.fetchone()[0]
        
        c.execute(f"SELECT SUM(lucro_percentual) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) = '{hoje}'")
        lucro_hoje = c.fetchone()[0] or 0.0
        
        # Estatísticas da semana
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) >= '{inicio_semana}'")
        total_ordens_semana = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM ordens_simuladas WHERE status = 'fechada' AND resultado = 'win' AND DATE(timestamp_fechamento) >= '{inicio_semana}'")
        wins_semana = c.fetchone()[0]
        
        c.execute(f"SELECT SUM(lucro_percentual) FROM ordens_simuladas WHERE status = 'fechada' AND DATE(timestamp_fechamento) >= '{inicio_semana}'")
        lucro_semana = c.fetchone()[0] or 0.0
        
        conn.close()
        
        # Calcular taxas de acerto
        taxa_acerto_hoje = (wins_hoje / total_ordens_hoje * 100) if total_ordens_hoje > 0 else 0
        taxa_acerto_semana = (wins_semana / total_ordens_semana * 100) if total_ordens_semana > 0 else 0
        
        return {
            'hoje': {
                'total_ordens': total_ordens_hoje,
                'wins': wins_hoje,
                'losses': total_ordens_hoje - wins_hoje,
                'taxa_acerto': taxa_acerto_hoje,
                'lucro_total': lucro_hoje
            },
            'semana': {
                'total_ordens': total_ordens_semana,
                'wins': wins_semana,
                'losses': total_ordens_semana - wins_semana,
                'taxa_acerto': taxa_acerto_semana,
                'lucro_total': lucro_semana
            },
            'ordens_ativas': len(executor.ordens_ativas)
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de aprendizado: {e}")
        return {}

def exibir_monitor_otimizado():
    """
    Exibe monitor otimizado e rápido
    """
    while True:
        try:
            # Limpar tela
            os.system('clear')
            
            # Verificar se robô está rodando
            robo_rodando, pid = verificar_processo_robo()
            
            # Exibir cabeçalho
            print("=" * 60)
            print("🤖 MONITOR DO ROBÔ DE TRADING IA (OTIMIZADO)")
            print("=" * 60)
            print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print()
            
            # Status do sistema
            print("📊 STATUS DO SISTEMA:")
            if robo_rodando:
                print(f"   ✅ Robô: RODANDO (PID: {pid})")
            else:
                print("   ❌ Robô: PARADO")
            
            # Verificar Ollama
            ollama_ok, num_models = verificar_ollama()
            if ollama_ok:
                print(f"   ✅ Ollama: OK ({num_models} modelos)")
            else:
                print("   ❌ Ollama: OFFLINE")
            
            print()
            
            # Estatísticas básicas otimizadas
            try:
                stats_banco = obter_estatisticas_banco_rapido()
                if stats_banco:
                    print("📈 ESTATÍSTICAS DE HOJE:")
                    print(f"   📊 Preços coletados: {stats_banco.get('total_precos_hoje', 0):,}")
                    print(f"   🤖 Análises realizadas: {stats_banco.get('total_analises_hoje', 0):,}")
                    print(f"   🚀 Ordens executadas: {stats_banco.get('total_ordens_hoje', 0):,}")
                    
                    print("\n📈 ESTATÍSTICAS DA SEMANA:")
                    print(f"   📊 Preços coletados: {stats_banco.get('total_precos_semana', 0):,}")
                    print(f"   🤖 Análises realizadas: {stats_banco.get('total_analises_semana', 0):,}")
                    print(f"   🚀 Ordens executadas: {stats_banco.get('total_ordens_semana', 0):,}")
                    
                    # Preços em tempo real
                    print("\n💰 PREÇOS EM TEMPO REAL:")
                    if 'ultimo_preco_ibov' in stats_banco:
                        ibov = stats_banco['ultimo_preco_ibov']
                        tempo_atras = datetime.now() - datetime.fromisoformat(ibov['timestamp'])
                        emoji = "🟢" if tempo_atras.seconds <= 5 else "🟡" if tempo_atras.seconds <= 15 else "🔴"
                        print(f"   {emoji} IBOV: {ibov['preco']:,.2f} ({tempo_atras.seconds}s atrás)")
                    
                    if 'ultimo_preco_win' in stats_banco:
                        win = stats_banco['ultimo_preco_win']
                        tempo_atras = datetime.now() - datetime.fromisoformat(win['timestamp'])
                        emoji = "🟢" if tempo_atras.seconds <= 5 else "🟡" if tempo_atras.seconds <= 15 else "🔴"
                        print(f"   {emoji} WIN: {win['preco']:,.2f} ({tempo_atras.seconds}s atrás)")
                    
                    # Última análise
                    if 'ultima_analise' in stats_banco:
                        analise = stats_banco['ultima_analise']
                        tempo_atras = datetime.now() - datetime.fromisoformat(analise['timestamp'])
                        resultado = analise['resultado'].upper() if analise['resultado'] else 'N/A'
                        emoji = "⏳" if 'aguardar' in resultado.lower() else "📈" if 'comprar' in resultado.lower() else "📉"
                        print(f"   🔍 Última análise: {emoji} {resultado} | Confiança: {analise['confianca']:.2f} ({tempo_atras.seconds}s atrás)")
                    
                    print()
            except Exception as e:
                print("   ⚠️ Erro ao carregar estatísticas")
                print()
            
            # Performance de aprendizado otimizada
            try:
                stats_aprendizado = obter_estatisticas_aprendizado_rapido()
                if stats_aprendizado:
                    print("🎯 PERFORMANCE DE APRENDIZADO:")
                    
                    # Dados de hoje
                    hoje = stats_aprendizado.get('hoje', {})
                    if hoje.get('total_ordens', 0) > 0:
                        print("   📅 HOJE:")
                        print(f"      ✅ Wins: {hoje.get('wins', 0)} | ❌ Losses: {hoje.get('losses', 0)}")
                        print(f"      📈 Taxa de acerto: {hoje.get('taxa_acerto', 0):.1f}%")
                        print(f"      💰 Lucro total: {hoje.get('lucro_total', 0):.2f}%")
                    
                    # Dados da semana
                    semana = stats_aprendizado.get('semana', {})
                    if semana.get('total_ordens', 0) > 0:
                        print("   📅 SEMANA:")
                        print(f"      ✅ Wins: {semana.get('wins', 0)} | ❌ Losses: {semana.get('losses', 0)}")
                        print(f"      📈 Taxa de acerto: {semana.get('taxa_acerto', 0):.1f}%")
                        print(f"      💰 Lucro total: {semana.get('lucro_total', 0):.2f}%")
                    
                    # Ordens ativas
                    ordens_ativas = stats_aprendizado.get('ordens_ativas', 0)
                    if ordens_ativas > 0:
                        print(f"   🔄 Ordens ativas: {ordens_ativas}")
                    
                    if hoje.get('total_ordens', 0) == 0 and semana.get('total_ordens', 0) == 0:
                        print("   📅 Nenhuma ordem simulada hoje ou esta semana")
                    
                    print()
                else:
                    print("🎯 APRENDIZADO: Nenhuma ordem simulada ainda")
                    print()
            except Exception as e:
                print("   ⚠️ Erro ao carregar aprendizado")
                print()
            
            print("=" * 60)
            print("💡 Ctrl+C para sair | ./parar_robo.sh para parar")
            print("=" * 60)
            
            # Aguardar 0.5 segundos (mais rápido)
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n👋 Monitor encerrado")
            break
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
            time.sleep(2)

def main():
    """
    Função principal do monitor
    """
    print("🤖 MONITOR DO ROBÔ DE TRADING IA")
    print("=" * 50)
    print("1. Status básico")
    print("2. Monitor otimizado (recomendado)")
    print("3. Sair")
    
    try:
        opcao = input("\nEscolha uma opção (1-3): ").strip()
        
        if opcao == "1":
            # Status básico (mantido para compatibilidade)
            stats = obter_estatisticas_banco_rapido()
            print(f"📊 Preços hoje: {stats.get('total_precos_hoje', 0):,}")
            print(f"🤖 Análises hoje: {stats.get('total_analises_hoje', 0):,}")
            print(f"🚀 Ordens hoje: {stats.get('total_ordens_hoje', 0):,}")
        elif opcao == "2":
            exibir_monitor_otimizado()
        elif opcao == "3":
            print("👋 Saindo...")
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n👋 Monitor encerrado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 