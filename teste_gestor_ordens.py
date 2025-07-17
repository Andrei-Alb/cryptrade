#!/usr/bin/env python3
"""
Teste do Gestor de Ordens IA
Testa o sistema completo de gestão inteligente de ordens
"""

import time
import json
from datetime import datetime
from loguru import logger
import os

# Configurar logging
os.makedirs('logs', exist_ok=True)
logger.add("logs/teste_gestor_ordens.log", rotation="1 day")

from executor import ExecutorOrdensSimuladas
from ia.gestor_ordens import GestorOrdensIA
from ia.sistema_aprendizado import SistemaAprendizado

def testar_gestor_ordens():
    """Testa o sistema de gestão de ordens"""
    
    logger.info("🧪 Iniciando teste do Gestor de Ordens IA")
    
    # Inicializar componentes
    executor = ExecutorOrdensSimuladas()
    sistema = SistemaAprendizado()
    gestor = GestorOrdensIA(parametros_ia=sistema.parametros_atuais)
    
    # Simular dados de mercado
    dados_mercado = {
        'preco_atual': 100.0,
        'simbolo': 'WINQ25',
        'indicadores': {
            'tendencia': 'alta',
            'rsi': 65,
            'volume': 1000
        }
    }
    
    # 1. Testar execução de ordem
    logger.info("📝 Testando execução de ordem...")
    
    decisao_compra = {
        'decisao': 'comprar',
        'confianca': 0.75,
        'razao': 'Tendência de alta detectada'
    }
    
    resultado = executor.executar_ordem_simulada(decisao_compra, dados_mercado)
    
    if resultado['status'] == 'executada':
        logger.success(f"✅ Ordem executada: {resultado['ordem_id']}")
        
        # Adicionar ao gestor
        ordem_completa = {
            'ordem_id': resultado['ordem_id'],
            'timestamp': datetime.now(),
            'tipo': 'comprar',
            'simbolo': 'WINQ25',
            'preco_entrada': 100.0,
            'preco_alvo': resultado['preco_alvo'],
            'preco_stop': resultado['preco_stop'],
            'confianca_ia': 0.75
        }
        
        gestor.adicionar_ordem_ativa(ordem_completa)
        logger.info(f"📋 Ordem adicionada ao gestor: {resultado['ordem_id']}")
        
        # 2. Testar análise de ordens ativas
        logger.info("🔍 Testando análise de ordens ativas...")
        
        # Simular diferentes cenários de preço
        cenarios_teste = [
            {'preco': 100.5, 'descricao': 'Preço subindo'},
            {'preco': 101.0, 'descricao': 'Aproximando alvo'},
            {'preco': 101.5, 'descricao': 'Alvo atingido'},
            {'preco': 99.0, 'descricao': 'Stop atingido'},
            {'preco': 100.1, 'descricao': 'Preço estável'}
        ]
        
        for i, cenario in enumerate(cenarios_teste):
            logger.info(f"📊 Teste {i+1}: {cenario['descricao']} - Preço: {cenario['preco']}")
            
            dados_teste = {
                'preco_atual': cenario['preco'],
                'simbolo': 'WINQ25',
                'indicadores': {
                    'tendencia': 'alta' if cenario['preco'] > 100.0 else 'baixa',
                    'rsi': 70 if cenario['preco'] > 100.5 else 50,
                    'volume': 1000
                }
            }
            
            decisoes = gestor.analisar_ordens_ativas(dados_teste)
            
            if decisoes:
                for decisao in decisoes:
                    logger.info(f"🎯 Decisão: {decisao['decisao']} | Razão: {decisao['razao']}")
                    
                    # Simular fechamento da ordem
                    if decisao['decisao'] in ['sair_lucro', 'sair_perda', 'sair_timeout']:
                        duracao = (datetime.now() - ordem_completa['timestamp']).total_seconds()
                        
                        # Mapear para resultado
                        if decisao['decisao'] == 'sair_lucro':
                            resultado_fechamento = 'win'
                        elif decisao['decisao'] == 'sair_perda':
                            resultado_fechamento = 'loss'
                        else:
                            resultado_fechamento = 'timeout'
                        
                        # Fechar ordem
                        executor.fechar_ordem_simulada(
                            decisao['ordem_id'],
                            resultado_fechamento,
                            decisao['lucro_percentual'],
                            duracao,
                            decisao['razao']
                        )
                        
                        # Registrar aprendizado
                        gestor.registrar_aprendizado_saida(ordem_completa, decisao)
                        
                        logger.success(f"✅ Ordem fechada: {resultado_fechamento} | Lucro: {decisao['lucro_percentual']:.2f}%")
                        break
            else:
                logger.info("⏸️ Nenhuma decisão de saída - mantendo ordem")
            
            time.sleep(1)  # Pausa entre testes
        
        # 3. Exibir estatísticas
        logger.info("📊 Exibindo estatísticas...")
        
        stats_executor = executor.obter_estatisticas_aprendizado()
        stats_gestor = gestor.obter_estatisticas_saida()
        
        logger.info("=" * 50)
        logger.info("📈 ESTATÍSTICAS DO EXECUTOR")
        logger.info("=" * 50)
        logger.info(f"Total ordens: {stats_executor.get('total_ordens', 0)}")
        logger.info(f"Wins: {stats_executor.get('wins', 0)}")
        logger.info(f"Losses: {stats_executor.get('losses', 0)}")
        logger.info(f"Taxa acerto: {stats_executor.get('taxa_acerto', 0):.1f}%")
        logger.info(f"Lucro total: {stats_executor.get('lucro_total', 0):.2f}%")
        
        logger.info("=" * 50)
        logger.info("🎯 ESTATÍSTICAS DO GESTOR")
        logger.info("=" * 50)
        logger.info(f"Total saídas: {stats_gestor.get('total_saidas', 0)}")
        logger.info(f"Taxa acerto saídas: {stats_gestor.get('taxa_acerto_geral', 0):.1f}%")
        logger.info(f"Ordens no gestor: {stats_gestor.get('ordens_ativas', 0)}")
        
        if stats_gestor.get('performance_tipos'):
            logger.info("Performance por tipo de saída:")
            for tipo, dados in stats_gestor['performance_tipos'].items():
                logger.info(f"  {tipo}: {dados}")
        
        logger.info("=" * 50)
        
    else:
        logger.error(f"❌ Falha na execução da ordem: {resultado.get('razao', 'Erro desconhecido')}")
    
    logger.info("✅ Teste do Gestor de Ordens concluído")

def testar_aprendizado_continuo():
    """Testa o sistema de aprendizado contínuo"""
    
    logger.info("🧠 Testando aprendizado contínuo...")
    
    executor = ExecutorOrdensSimuladas()
    sistema = SistemaAprendizado()
    gestor = GestorOrdensIA(parametros_ia=sistema.parametros_atuais)
    
    # Simular múltiplas ordens para testar aprendizado
    for i in range(5):
        logger.info(f"📝 Executando ordem de teste {i+1}/5")
        
        # Variação de preços para simular diferentes cenários
        preco_base = 100.0 + (i * 0.5)
        
        dados_mercado = {
            'preco_atual': preco_base,
            'simbolo': 'WINQ25',
            'indicadores': {
                'tendencia': 'alta' if i % 2 == 0 else 'baixa',
                'rsi': 60 + (i * 5),
                'volume': 1000 + (i * 100)
            }
        }
        
        decisao = {
            'decisao': 'comprar' if i % 2 == 0 else 'vender',
            'confianca': 0.6 + (i * 0.1),
            'razao': f'Teste de aprendizado {i+1}'
        }
        
        resultado = executor.executar_ordem_simulada(decisao, dados_mercado)
        
        if resultado['status'] == 'executada':
            ordem_completa = {
                'ordem_id': resultado['ordem_id'],
                'timestamp': datetime.now(),
                'tipo': decisao['decisao'],
                'simbolo': 'WINQ25',
                'preco_entrada': preco_base,
                'preco_alvo': resultado['preco_alvo'],
                'preco_stop': resultado['preco_stop'],
                'confianca_ia': decisao['confianca']
            }
            
            gestor.adicionar_ordem_ativa(ordem_completa)
            
            # Simular fechamento após alguns segundos
            time.sleep(2)
            
            # Simular preço final (alguns wins, alguns losses)
            preco_final = preco_base + (0.3 if i % 3 == 0 else -0.2)
            
            dados_finais = {
                'preco_atual': preco_final,
                'simbolo': 'WINQ25',
                'indicadores': {
                    'tendencia': 'alta' if preco_final > preco_base else 'baixa',
                    'rsi': 70 if preco_final > preco_base else 30,
                    'volume': 1200
                }
            }
            
            decisoes = gestor.analisar_ordens_ativas(dados_finais)
            
            for decisao_saida in decisoes:
                if decisao_saida['decisao'] in ['sair_lucro', 'sair_perda', 'sair_timeout']:
                    duracao = (datetime.now() - ordem_completa['timestamp']).total_seconds()
                    
                    resultado_fechamento = 'win' if decisao_saida['decisao'] == 'sair_lucro' else 'loss'
                    
                    executor.fechar_ordem_simulada(
                        decisao_saida['ordem_id'],
                        resultado_fechamento,
                        decisao_saida['lucro_percentual'],
                        duracao,
                        decisao_saida['razao']
                    )
                    
                    gestor.registrar_aprendizado_saida(ordem_completa, decisao_saida)
                    
                    logger.info(f"✅ Ordem {i+1} fechada: {resultado_fechamento} | Lucro: {decisao_saida['lucro_percentual']:.2f}%")
                    break
    
    # Exibir estatísticas finais
    stats_executor = executor.obter_estatisticas_aprendizado()
    stats_gestor = gestor.obter_estatisticas_saida()
    
    logger.info("=" * 50)
    logger.info("📊 ESTATÍSTICAS FINAIS DO APRENDIZADO")
    logger.info("=" * 50)
    logger.info(f"Total ordens: {stats_executor.get('total_ordens', 0)}")
    logger.info(f"Taxa acerto: {stats_executor.get('taxa_acerto', 0):.1f}%")
    logger.info(f"Lucro total: {stats_executor.get('lucro_total', 0):.2f}%")
    logger.info(f"Total saídas: {stats_gestor.get('total_saidas', 0)}")
    logger.info(f"Taxa acerto saídas: {stats_gestor.get('taxa_acerto_geral', 0):.1f}%")
    
    logger.info("✅ Teste de aprendizado contínuo concluído")

if __name__ == "__main__":
    try:
        testar_gestor_ordens()
        print("\n" + "="*60)
        testar_aprendizado_continuo()
        logger.info("🎉 Todos os testes concluídos com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro nos testes: {e}") 