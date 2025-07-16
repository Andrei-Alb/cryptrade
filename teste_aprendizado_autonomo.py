#!/usr/bin/env python3
"""
Teste do Sistema de Aprendizado Autônomo
Verifica se a IA está aprendendo e ajustando sua confiança
"""

import sys
import os
import time
import json
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia.sistema_aprendizado_autonomo import SistemaAprendizadoAutonomo
from ia.decisor import DecisorIA
from executor_simulado import ExecutorSimulado
import yaml

def carregar_config():
    """Carrega configuração do sistema"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Configuração padrão para teste
        return {
            'simulacao': {
                'capital_inicial': 1000.0,
                'max_operacoes': 50
            },
            'trading': {
                'quantidade_padrao': 0.001,
                'quantidade_eth': 0.01
            }
        }

def simular_operacoes(sistema_aprendizado, decisor, executor, num_operacoes=10):
    """Simula operações para testar o aprendizado"""
    print(f"\n🎮 Simulando {num_operacoes} operações...")
    
    # Dados de mercado simulados
    dados_mercado = {
        'symbol': 'BTCUSDT',
        'preco_atual': 117000.0,
        'volume': 1000000,
        'rsi': 50.0,
        'tendencia': 'lateral',
        'volatilidade': 0.02
    }
    
    for i in range(num_operacoes):
        print(f"\n--- Operação {i+1}/{num_operacoes} ---")
        
        # Simular decisão da IA
        decisao_ia = {
            'decisao': 'comprar' if i % 3 == 0 else 'vender' if i % 3 == 1 else 'aguardar',
            'confianca': 0.6 + (i * 0.02),  # Confiança crescente
            'razao': f'Teste operação {i+1}',
            'parametros': {}
        }
        
        # Processar decisão com aprendizado autônomo
        decisao_processada = decisor.processar_decisao_ia(decisao_ia, dados_mercado)
        
        print(f"Decisão original: {decisao_ia['decisao']} (confiança: {decisao_ia['confianca']:.3f})")
        print(f"Decisão processada: {decisao_processada['decisao']} (confiança: {decisao_processada['confianca']:.3f})")
        
        # Simular execução se não for aguardar
        if decisao_processada['decisao'] != 'aguardar':
            # Conectar executor ao decisor para aprendizado
            executor.decisor_ia = decisor
            
            # Simular ordem
            resultado = executor.enviar_ordem_market(
                'BTCUSDT', 
                'Buy' if decisao_processada['decisao'] == 'comprar' else 'Sell',
                0.001
            )
            
            if resultado:
                print(f"✅ Ordem executada: {resultado['side']} {resultado['qty']} @ ${resultado['avgPrice']:.2f}")
                
                # Simular resultado (win/loss alternado para teste)
                lucro_prejuizo = 5.0 if i % 2 == 0 else -3.0
                resultado_operacao = 'win' if lucro_prejuizo > 0 else 'loss'
                
                print(f"📊 Resultado: {resultado_operacao} (${lucro_prejuizo:.2f})")
                
                # Registrar resultado no aprendizado
                decisor.registrar_resultado_operacao('BTCUSDT', resultado_operacao, lucro_prejuizo)
            else:
                print("❌ Falha na execução da ordem")
        else:
            print("⏳ Aguardando...")
        
        time.sleep(0.5)  # Pequena pausa entre operações

def mostrar_estatisticas(sistema_aprendizado, decisor, executor):
    """Mostra estatísticas do aprendizado"""
    print(f"\n📊 ESTATÍSTICAS DO APRENDIZADO AUTÔNOMO")
    print("=" * 50)
    
    # Estatísticas básicas
    stats = sistema_aprendizado.obter_estatisticas_aprendizado()
    print(f"Total de decisões: {stats.get('total_decisoes', 0)}")
    print(f"Decisões com resultado: {stats.get('decisoes_com_resultado', 0)}")
    print(f"Wins: {stats.get('total_wins', 0)}")
    print(f"Losses: {stats.get('total_losses', 0)}")
    print(f"Win Rate: {stats.get('win_rate', 0):.2%}")
    print(f"Confiança média: {stats.get('confianca_media', 0):.3f}")
    print(f"Sequência atual: {stats.get('sequencia_atual', 0)}")
    
    # Evolução da IA
    print(f"\n📈 EVOLUÇÃO DA IA (últimos 7 dias)")
    print("-" * 30)
    evolucao = sistema_aprendizado.obter_evolucao_ia(7)
    for dia in evolucao:
        print(f"Data: {dia['data']}")
        print(f"  Decisões: {dia['total_decisoes']}")
        print(f"  Win Rate: {dia['win_rate']:.2%}")
        print(f"  Confiança: {dia['confianca_media']:.3f}")
        print(f"  Aprendizado: {dia['aprendizado_dia']}")
    
    # Padrões aprendidos
    print(f"\n🧠 PADRÕES APRENDIDOS (últimos 5)")
    print("-" * 30)
    padroes = sistema_aprendizado.obter_padroes_aprendidos(5)
    for padrao in padroes:
        print(f"Padrão: {padrao['padrao_tipo']}")
        print(f"  Resultado: {padrao['resultado']}")
        print(f"  Confiança: {padrao['confianca_media']:.3f}")
        print(f"  Recomendação: {padrao['recomendacao']}")
        print()
    
    # Estatísticas do executor
    print(f"\n🎮 ESTATÍSTICAS DO EXECUTOR")
    print("-" * 30)
    stats_executor = executor.obter_estatisticas()
    print(f"Capital atual: ${stats_executor.get('capital_atual', 0):.2f}")
    print(f"Operações realizadas: {stats_executor.get('operacoes_realizadas', 0)}")
    print(f"Win Rate: {stats_executor.get('win_rate', 0):.2%}")
    print(f"Profit Factor: {stats_executor.get('profit_factor', 0):.2f}")

def testar_recomendacao_confianca(sistema_aprendizado):
    """Testa o sistema de recomendação de confiança"""
    print(f"\n🧠 TESTE DE RECOMENDAÇÃO DE CONFIANCE")
    print("=" * 40)
    
    dados_mercado = {
        'symbol': 'BTCUSDT',
        'preco_atual': 117000.0,
        'volume': 1000000,
        'rsi': 50.0,
        'tendencia': 'lateral'
    }
    
    recomendacao = sistema_aprendizado.obter_recomendacao_confianca('BTCUSDT', dados_mercado)
    
    print(f"Confiança recomendada: {recomendacao['confianca_recomendada']:.3f}")
    print(f"Ajuste: {recomendacao['ajuste']:.3f}")
    print(f"Razão: {recomendacao['razao']}")
    print(f"Win Rate: {recomendacao.get('win_rate', 0):.2%}")
    print(f"Sequência atual: {recomendacao.get('sequencia_atual', 0)}")

def testar_edge_cases_executor(executor):
    print("\n=== Testando edge cases do Executor Simulado ===")
    symbol = 'BTCUSDT'
    # 1. Venda sem posição (short selling)
    print("\n- Venda sem posição (short selling):")
    resultado_short = executor.enviar_ordem_market(symbol, 'Sell', 0.002)
    print(f"Resultado short: {resultado_short}")
    # 2. Compra para zerar short
    print("\n- Compra para zerar short:")
    resultado_zerar_short = executor.enviar_ordem_market(symbol, 'Buy', 0.002)
    print(f"Resultado zerar short: {resultado_zerar_short}")
    # 3. Fechamento parcial de posição (abrir long, vender metade)
    print("\n- Fechamento parcial de posição:")
    executor.enviar_ordem_market(symbol, 'Buy', 0.004)
    resultado_fechamento_parcial = executor.enviar_ordem_market(symbol, 'Sell', 0.002)
    print(f"Resultado fechamento parcial: {resultado_fechamento_parcial}")
    # 4. Evolução correta do capital simulado
    print("\n- Capital simulado após operações:")
    print(f"Capital atual: {executor.capital_atual}")

def main():
    """Função principal do teste"""
    print("🧠 TESTE DO SISTEMA DE APRENDIZADO AUTÔNOMO")
    print("=" * 50)
    
    # Carregar configuração
    config = carregar_config()
    
    # Inicializar componentes
    print("🔧 Inicializando componentes...")
    sistema_aprendizado = SistemaAprendizadoAutonomo()
    decisor = DecisorIA(config)
    executor = ExecutorSimulado(config)
    
    print("✅ Componentes inicializados")
    
    # Testar recomendação inicial
    testar_recomendacao_confianca(sistema_aprendizado)
    
    # Simular operações
    simular_operacoes(sistema_aprendizado, decisor, executor, num_operacoes=15)
    
    # Mostrar estatísticas finais
    mostrar_estatisticas(sistema_aprendizado, decisor, executor)
    
    # Exportar aprendizado
    print(f"\n📤 Exportando dados de aprendizado...")
    sistema_aprendizado.exportar_aprendizado("teste_aprendizado.json")
    
    # Testar edge cases do executor simulado
    testar_edge_cases_executor(executor)

    print(f"\n✅ Teste concluído!")
    print(f"📁 Dados exportados para: teste_aprendizado.json")

if __name__ == "__main__":
    main() 