#!/usr/bin/env python3
"""
Teste da IA Aprendendo em Tempo Real
Mostra a IA se adaptando e alterando padrões automaticamente
"""

import sys
import os
import time
import json
import random
from datetime import datetime
import threading

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia.sistema_aprendizado_autonomo import SistemaAprendizadoAutonomo
from ia.decisor import DecisorIA
from executor_simulado import ExecutorSimulado
import yaml

class SimuladorMercado:
    """Simula condições de mercado variáveis para testar adaptação da IA"""
    
    def __init__(self):
        self.tendencia_atual = 'lateral'
        self.volatilidade = 0.02
        self.preco_base = 117000.0
        self.contador_operacoes = 0
        
    def gerar_dados_mercado(self, operacao_num):
        """Gera dados de mercado que mudam ao longo do tempo"""
        # Simular mudanças de tendência
        if operacao_num < 10:
            self.tendencia_atual = 'alta'
            self.volatilidade = 0.015
        elif operacao_num < 20:
            self.tendencia_atual = 'baixa'
            self.volatilidade = 0.025
        elif operacao_num < 30:
            self.tendencia_atual = 'lateral'
            self.volatilidade = 0.02
        else:
            # Mercado volátil
            self.tendencia_atual = random.choice(['alta', 'baixa', 'lateral'])
            self.volatilidade = random.uniform(0.01, 0.04)
        
        # Ajustar preço base
        if self.tendencia_atual == 'alta':
            self.preco_base += random.uniform(-50, 200)
        elif self.tendencia_atual == 'baixa':
            self.preco_base += random.uniform(-200, 50)
        else:
            self.preco_base += random.uniform(-100, 100)
        
        # Gerar RSI baseado na tendência
        if self.tendencia_atual == 'alta':
            rsi = random.uniform(45, 75)
        elif self.tendencia_atual == 'baixa':
            rsi = random.uniform(25, 55)
        else:
            rsi = random.uniform(35, 65)
        
        return {
            'symbol': 'BTCUSDT',
            'preco_atual': self.preco_base,
            'volume': random.uniform(800000, 1200000),
            'rsi': rsi,
            'tendencia': self.tendencia_atual,
            'volatilidade': self.volatilidade,
            'operacao_num': operacao_num
        }

def simular_decisao_ia_adaptativa(operacao_num, dados_mercado, historico_wins):
    """Simula decisão da IA que se adapta ao mercado"""
    
    # Base inicial de confiança
    confianca_base = 0.5
    
    # Ajustar baseado na tendência
    if dados_mercado['tendencia'] == 'alta':
        confianca_base += 0.1
    elif dados_mercado['tendencia'] == 'baixa':
        confianca_base -= 0.1
    
    # Ajustar baseado no RSI
    rsi = dados_mercado['rsi']
    if rsi < 30:  # Sobrevendido
        confianca_base += 0.15
    elif rsi > 70:  # Sobrecomprado
        confianca_base -= 0.15
    
    # Ajustar baseado no histórico de wins
    if historico_wins > 0:
        confianca_base += min(0.2, historico_wins * 0.05)
    
    # Decisão baseada na confiança
    if confianca_base > 0.7:
        decisao = 'comprar' if dados_mercado['tendencia'] != 'baixa' else 'aguardar'
    elif confianca_base > 0.5:
        decisao = 'vender' if dados_mercado['tendencia'] != 'alta' else 'aguardar'
    else:
        decisao = 'aguardar'
    
    return {
        'decisao': decisao,
        'confianca': max(0.1, min(0.95, confianca_base)),
        'razao': f"Tendência: {dados_mercado['tendencia']}, RSI: {rsi:.1f}, Wins: {historico_wins}",
        'parametros': {}
    }

def simular_resultado_operacao(decisao, dados_mercado, operacao_num):
    """Simula resultado realista baseado nas condições de mercado"""
    
    # Probabilidade de win baseada nas condições
    prob_win = 0.5  # Base
    
    # Ajustar baseado na tendência
    if dados_mercado['tendencia'] == 'alta' and decisao == 'comprar':
        prob_win += 0.2
    elif dados_mercado['tendencia'] == 'baixa' and decisao == 'vender':
        prob_win += 0.2
    elif dados_mercado['tendencia'] == 'alta' and decisao == 'vender':
        prob_win -= 0.2
    elif dados_mercado['tendencia'] == 'baixa' and decisao == 'comprar':
        prob_win -= 0.2
    
    # Ajustar baseado no RSI
    rsi = dados_mercado['rsi']
    if rsi < 30 and decisao == 'comprar':
        prob_win += 0.15
    elif rsi > 70 and decisao == 'vender':
        prob_win += 0.15
    
    # Adicionar aleatoriedade do mercado
    prob_win += random.uniform(-0.1, 0.1)
    prob_win = max(0.1, min(0.9, prob_win))
    
    # Determinar resultado
    resultado = 'win' if random.random() < prob_win else 'loss'
    
    # Calcular lucro/prejuízo realista
    if resultado == 'win':
        lucro_prejuizo = random.uniform(2.0, 8.0)
    else:
        lucro_prejuizo = -random.uniform(1.0, 5.0)
    
    return resultado, lucro_prejuizo, prob_win

def mostrar_estatisticas_tempo_real(sistema_aprendizado, decisor, executor, operacao_atual):
    """Mostra estatísticas em tempo real"""
    print(f"\n{'='*60}")
    print(f"📊 ESTATÍSTICAS EM TEMPO REAL - Operação {operacao_atual}")
    print(f"{'='*60}")
    
    # Estatísticas do aprendizado
    stats = sistema_aprendizado.obter_estatisticas_aprendizado()
    print(f"🧠 APRENDIZADO AUTÔNOMO:")
    print(f"   Total de decisões: {stats.get('total_decisoes', 0)}")
    print(f"   Decisões com resultado: {stats.get('decisoes_com_resultado', 0)}")
    print(f"   Wins: {stats.get('total_wins', 0)} | Losses: {stats.get('total_losses', 0)}")
    print(f"   Win Rate: {stats.get('win_rate', 0):.2%}")
    print(f"   Confiança média: {stats.get('confianca_media', 0):.3f}")
    print(f"   Sequência atual: {stats.get('sequencia_atual', 0)}")
    
    # Estatísticas do executor
    stats_exec = executor.obter_estatisticas()
    print(f"\n🎮 EXECUTOR:")
    print(f"   Capital atual: ${stats_exec.get('capital_atual', 0):.2f}")
    print(f"   Operações realizadas: {stats_exec.get('operacoes_realizadas', 0)}")
    print(f"   Win Rate: {stats_exec.get('win_rate', 0):.2%}")
    print(f"   Profit Factor: {stats_exec.get('profit_factor', 0):.2f}")
    
    # Padrões recentes
    padroes = sistema_aprendizado.obter_padroes_aprendidos(3)
    if padroes:
        print(f"\n🧠 PADRÕES RECENTES:")
        for padrao in padroes:
            print(f"   {padrao['padrao_tipo']}: {padrao['recomendacao']}")

def main():
    """Função principal - IA aprendendo em tempo real"""
    print("🧠 IA APRENDENDO EM TEMPO REAL")
    print("=" * 60)
    print("Acompanhe a IA se adaptando e aprendendo com o mercado!")
    print("=" * 60)
    
    # Carregar configuração
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {
            'simulacao': {
                'capital_inicial': 1000.0,
                'max_operacoes': 100
            },
            'trading': {
                'quantidade_padrao': 0.001,
                'quantidade_eth': 0.01
            }
        }
    
    # Inicializar componentes
    print("🔧 Inicializando sistema de IA autônoma...")
    sistema_aprendizado = SistemaAprendizadoAutonomo()
    decisor = DecisorIA(config)
    executor = ExecutorSimulado(config)
    simulador_mercado = SimuladorMercado()
    
    # Importar e inicializar gestor de ordens dinâmico
    from gestor_ordens_dinamico import GestorOrdensDinamico
    gestor_ordens = GestorOrdensDinamico()
    
    # Conectar componentes
    executor.decisor_ia = decisor
    executor.gestor_ordens = gestor_ordens
    
    print("✅ Sistema inicializado!")
    print("🚀 Iniciando simulação de mercado com IA aprendendo...")
    
    # Contadores para análise
    historico_wins = 0
    total_operacoes = 50  # Mais operações para ver evolução
    
    for operacao_num in range(1, total_operacoes + 1):
        print(f"\n{'='*50}")
        print(f"🎯 OPERAÇÃO {operacao_num}/{total_operacoes}")
        print(f"{'='*50}")
        
        # Gerar dados de mercado
        dados_mercado = simulador_mercado.gerar_dados_mercado(operacao_num)
        
        print(f"📈 MERCADO ATUAL:")
        print(f"   Preço: ${dados_mercado['preco_atual']:.2f}")
        print(f"   Tendência: {dados_mercado['tendencia']}")
        print(f"   RSI: {dados_mercado['rsi']:.1f}")
        print(f"   Volatilidade: {dados_mercado['volatilidade']:.3f}")
        
        # Simular decisão da IA
        decisao_ia = simular_decisao_ia_adaptativa(operacao_num, dados_mercado, historico_wins)
        
        print(f"\n🤖 DECISÃO ORIGINAL DA IA:")
        print(f"   Ação: {decisao_ia['decisao']}")
        print(f"   Confiança: {decisao_ia['confianca']:.3f}")
        print(f"   Razão: {decisao_ia['razao']}")
        
        # Processar com aprendizado autônomo
        decisao_processada = decisor.processar_decisao_ia(decisao_ia, dados_mercado)
        
        print(f"\n🧠 DECISÃO PROCESSADA (com aprendizado):")
        print(f"   Ação: {decisao_processada['decisao']}")
        print(f"   Confiança: {decisao_processada['confianca']:.3f}")
        print(f"   Razão: {decisao_processada.get('razao', 'N/A')}")
        
        # Executar se não for aguardar
        if decisao_processada['decisao'] != 'aguardar':
                        # Simular ordem com gestão dinâmica
            resultado = executor.enviar_ordem_market(
                'BTCUSDT', 
                'Buy' if decisao_processada['decisao'] == 'comprar' else 'Sell',
                0.001,
                dados_mercado,
                decisao_processada['confianca']
            )
            
            if resultado:
                print(f"\n✅ ORDEM EXECUTADA:")
                print(f"   {resultado['side']} {resultado['qty']} @ ${resultado['avgPrice']:.2f}")
                
                # Simular resultado realista
                resultado_operacao, lucro_prejuizo, prob_win = simular_resultado_operacao(
                    decisao_processada['decisao'], dados_mercado, operacao_num
                )
                
                print(f"\n📊 RESULTADO:")
                print(f"   Resultado: {resultado_operacao.upper()}")
                print(f"   Lucro/Prejuízo: ${lucro_prejuizo:.2f}")
                print(f"   Probabilidade de Win: {prob_win:.1%}")
                
                # Atualizar contadores
                if resultado_operacao == 'win':
                    historico_wins += 1
                
                # Registrar no aprendizado
                decisor.registrar_resultado_operacao('BTCUSDT', resultado_operacao, lucro_prejuizo)
                
                print(f"\n🧠 APRENDIZADO REGISTRADO!")
                
            else:
                print("❌ Falha na execução da ordem")
        else:
            print("\n⏳ Aguardando condições melhores...")
        
        # Mostrar estatísticas a cada 5 operações
        if operacao_num % 5 == 0:
            mostrar_estatisticas_tempo_real(sistema_aprendizado, decisor, executor, operacao_num)
        
        # Pausa para acompanhar
        time.sleep(1.5)
    
    # Estatísticas finais
    print(f"\n{'='*60}")
    print(f"🏁 SIMULAÇÃO CONCLUÍDA!")
    print(f"{'='*60}")
    
    mostrar_estatisticas_tempo_real(sistema_aprendizado, decisor, executor, total_operacoes)
    
    # Exportar aprendizado
    print(f"\n📤 Exportando dados de aprendizado...")
    sistema_aprendizado.exportar_aprendizado("ia_aprendendo_tempo_real.json")
    
    print(f"\n🎉 IA completou {total_operacoes} operações!")
    print(f"📁 Dados salvos em: ia_aprendendo_tempo_real.json")
    print(f"🧠 A IA aprendeu e se adaptou ao mercado!")

if __name__ == "__main__":
    main() 