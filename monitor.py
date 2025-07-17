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

def obter_estatisticas_previsoes_rapido():
    """
    Obtém estatísticas de previsões da IA de forma otimizada
    """
    try:
        db_path = "dados/trading.db"
        if not os.path.exists(db_path):
            return {}
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar se tabela existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analise_previsoes_ia'")
        if not c.fetchone():
            conn.close()
            return {'mensagem': 'Nenhuma análise de previsões encontrada'}
        
        # Obter data de hoje e início da semana
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        # Estatísticas de hoje
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE DATE(timestamp) = '{hoje}'")
        total_analises_hoje = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE precisao_target = 'acerto' AND DATE(timestamp) = '{hoje}'")
        targets_acertos_hoje = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE precisao_stop = 'acerto' AND DATE(timestamp) = '{hoje}'")
        stops_acertos_hoje = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE resultado_real = 'win' AND DATE(timestamp) = '{hoje}'")
        wins_hoje = c.fetchone()[0]
        
        # Estatísticas da semana
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE DATE(timestamp) >= '{inicio_semana}'")
        total_analises_semana = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE precisao_target = 'acerto' AND DATE(timestamp) >= '{inicio_semana}'")
        targets_acertos_semana = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE precisao_stop = 'acerto' AND DATE(timestamp) >= '{inicio_semana}'")
        stops_acertos_semana = c.fetchone()[0]
        
        c.execute(f"SELECT COUNT(*) FROM analise_previsoes_ia WHERE resultado_real = 'win' AND DATE(timestamp) >= '{inicio_semana}'")
        wins_semana = c.fetchone()[0]
        
        conn.close()
        
        # Calcular taxas de precisão
        precisao_target_hoje = (targets_acertos_hoje / total_analises_hoje * 100) if total_analises_hoje > 0 else 0
        precisao_stop_hoje = (stops_acertos_hoje / total_analises_hoje * 100) if total_analises_hoje > 0 else 0
        win_rate_hoje = (wins_hoje / total_analises_hoje * 100) if total_analises_hoje > 0 else 0
        
        precisao_target_semana = (targets_acertos_semana / total_analises_semana * 100) if total_analises_semana > 0 else 0
        precisao_stop_semana = (stops_acertos_semana / total_analises_semana * 100) if total_analises_semana > 0 else 0
        win_rate_semana = (wins_semana / total_analises_semana * 100) if total_analises_semana > 0 else 0
        
        return {
            'hoje': {
                'total_analises': total_analises_hoje,
                'precisao_target': precisao_target_hoje,
                'precisao_stop': precisao_stop_hoje,
                'win_rate': win_rate_hoje
            },
            'semana': {
                'total_analises': total_analises_semana,
                'precisao_target': precisao_target_semana,
                'precisao_stop': precisao_stop_semana,
                'win_rate': win_rate_semana
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de previsões: {e}")
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
                    print("📈 ESTATÍSTICAS BÁSICAS:")
                    print(f"   📊 Preços hoje: {stats_banco.get('total_precos_hoje', 0)}")
                    print(f"   🧠 Análises hoje: {stats_banco.get('total_analises_hoje', 0)}")
                    print(f"   📋 Ordens hoje: {stats_banco.get('total_ordens_hoje', 0)}")
                    
                    # Último preço IBOV
                    ultimo_ibov = stats_banco.get('ultimo_preco_ibov')
                    if ultimo_ibov:
                        print(f"   📊 IBOV: {ultimo_ibov['preco']:.2f} ({ultimo_ibov['timestamp']})")
                    
                    # Última análise
                    ultima_analise = stats_banco.get('ultima_analise')
                    if ultima_analise:
                        print(f"   🧠 Última análise: {ultima_analise['resultado']} (conf: {ultima_analise['confianca']:.2f})")
                
                print()
                
                # Estatísticas de aprendizado
                stats_aprendizado = obter_estatisticas_aprendizado_rapido()
                
                if stats_aprendizado:
                    print("🎯 ESTATÍSTICAS DE APRENDIZADO:")
                    
                    hoje = stats_aprendizado.get('hoje', {})
                    if hoje.get('total_ordens', 0) > 0:
                        print(f"   📅 HOJE: {hoje['total_ordens']} ordens | {hoje['taxa_acerto']:.1f}% acerto | {hoje['lucro_total']:+.2f}%")
                    
                    semana = stats_aprendizado.get('semana', {})
                    if semana.get('total_ordens', 0) > 0:
                        print(f"   📅 SEMANA: {semana['total_ordens']} ordens | {semana['taxa_acerto']:.1f}% acerto | {semana['lucro_total']:+.2f}%")
                    
                    ordens_ativas = stats_aprendizado.get('ordens_ativas', 0)
                    if ordens_ativas > 0:
                        print(f"   🔄 Ordens ativas: {ordens_ativas}")
                
                print()
                
                # Estatísticas de previsões da IA
                stats_previsoes = obter_estatisticas_previsoes_rapido()
                
                if isinstance(stats_previsoes, dict) and 'mensagem' not in stats_previsoes:
                    print("🎯 ESTATÍSTICAS DE PREVISÕES IA:")
                    
                    hoje = stats_previsoes.get('hoje', {})
                    if isinstance(hoje, dict) and hoje.get('total_analises', 0) > 0:
                        print(f"   📅 HOJE: {hoje.get('total_analises', 0)} análises")
                        print(f"      🎯 Target: {hoje.get('precisao_target', 0):.1f}% | 🛑 Stop: {hoje.get('precisao_stop', 0):.1f}% | 📊 Win Rate: {hoje.get('win_rate', 0):.1f}%")
                    
                    semana = stats_previsoes.get('semana', {})
                    if isinstance(semana, dict) and semana.get('total_analises', 0) > 0:
                        print(f"   📅 SEMANA: {semana.get('total_analises', 0)} análises")
                        print(f"      🎯 Target: {semana.get('precisao_target', 0):.1f}% | 🛑 Stop: {semana.get('precisao_stop', 0):.1f}% | 📊 Win Rate: {semana.get('win_rate', 0):.1f}%")
                elif isinstance(stats_previsoes, dict) and 'mensagem' in stats_previsoes:
                    print("🎯 PREVISÕES IA:")
                    print(f"   ℹ️  {stats_previsoes.get('mensagem', '')}")
                
                print()
                
            except Exception as e:
                print(f"❌ Erro ao obter estatísticas: {e}")
                print()
            
            # Comandos disponíveis
            print("🔧 COMANDOS DISPONÍVEIS:")
            print("   🚀 ./executar_robo.sh - Iniciar robô")
            print("   🛑 ./parar_robo.sh - Parar robô")
            print("   ❌ ./encerrar_ordens.sh - Fechar todas as ordens")
            print("   📊 ./monitor.py - Atualizar monitor")
            print("   🔄 Ctrl+C - Sair do monitor")
            print()
            
            # Aguardar próximo update
            print("⏳ Atualizando em 5 segundos... (Ctrl+C para sair)")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n👋 Monitor encerrado!")
            break
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
            time.sleep(5)

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