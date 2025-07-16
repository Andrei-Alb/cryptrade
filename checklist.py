#!/usr/bin/env python3
"""
Checklist de Integração e Sanidade do Projeto Robo Trading
Testa importação, inicialização, criação de tabelas e integração de todos os módulos, classes e scripts principais.
"""

import importlib
import traceback
import sys
import os
import sqlite3
from pathlib import Path
from typing import Callable

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Utilitário para registrar testes
TESTES = []
def registrar_teste(nome):
    def decorator(func):
        TESTES.append((nome, func))
        return func
    return decorator

def checar_tabela_colunas(db_path, tabela, colunas):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabela})")
        cols = [row[1] for row in cursor.fetchall()]
        conn.close()
        for col in colunas:
            if col not in cols:
                return False, f"Coluna '{col}' não existe na tabela '{tabela}'"
        return True, ""
    except Exception as e:
        return False, str(e)

# Testes de inicialização e criação de tabelas
@registrar_teste('ArmazenamentoCrypto')
def teste_armazenamento():
    from armazenamento import ArmazenamentoCrypto
    arm = ArmazenamentoCrypto()
    if hasattr(arm, 'criar_tabelas'):
        arm.criar_tabelas()
    return True

@registrar_teste('ColetorBybit')
def teste_coletor():
    from coletor import ColetorBybit
    coletor = ColetorBybit()
    return True

@registrar_teste('ExecutorSimulado')
def teste_executor_simulado():
    from executor_simulado import ExecutorSimulado
    from yaml import safe_load  # type: ignore
    with open('config.yaml', 'r') as f:
        config = safe_load(f)
    executor = ExecutorSimulado(config)
    return True

@registrar_teste('GestorOrdensDinamico')
def teste_gestor_ordens():
    from gestor_ordens_dinamico import GestorOrdensDinamico
    gestor = GestorOrdensDinamico()
    if hasattr(gestor, '_criar_tabelas_gestao'):
        gestor._criar_tabelas_gestao()
    return True

@registrar_teste('PreparadorDadosCrypto')
def teste_preparador():
    from ia.preparador_dados import PreparadorDadosCrypto
    preparador = PreparadorDadosCrypto()
    return True

@registrar_teste('DecisorIA')
def teste_decisor():
    from ia.decisor import DecisorIA
    decisor = DecisorIA()
    return True

@registrar_teste('CursorAITradingClient')
def teste_cursor_ai_client():
    from ia.cursor_ai_client import CursorAITradingClient
    client = CursorAITradingClient()
    assert hasattr(client, 'analisar_dados_mercado')
    return True

@registrar_teste('SistemaAprendizadoAutonomo')
def teste_sistema_aprendizado():
    from ia.sistema_aprendizado_autonomo import SistemaAprendizadoAutonomo
    sistema = SistemaAprendizadoAutonomo()
    if hasattr(sistema, '_criar_tabelas_aprendizado'):
        sistema._criar_tabelas_aprendizado()
    return True

@registrar_teste('SistemaAprendizado')
def teste_sistema_aprendizado_legacy():
    from ia.sistema_aprendizado import SistemaAprendizado
    sistema = SistemaAprendizado()
    return True

@registrar_teste('Monitor')
def teste_monitor():
    import monitor
    return True

# Teste de tabelas e colunas críticas
@registrar_teste('Tabelas e Colunas Críticas')
def teste_tabelas_colunas():
    db_path = 'dados/crypto_trading.db'
    tabelas_colunas = {
        'ordens_simuladas': [
            'order_id', 'symbol', 'side', 'order_type', 'qty', 'price', 'status',
            'timestamp_abertura', 'timestamp_fechamento', 'preco_entrada', 'preco_saida',
            'resultado', 'lucro_prejuizo', 'confianca_ia', 'razao_decisao', 'dados_mercado'
        ],
        'decisoes_ia': [
            'symbol', 'decisao', 'confianca', 'razao', 'dados_entrada', 'timestamp',
            'resultado_operacao', 'lucro_prejuizo'
        ],
        'performance_ia': [
            'data', 'total_decisoes', 'decisoes_corretas', 'win_rate', 'lucro_total',
            'prejuizo_total', 'profit_factor', 'timestamp_atualizacao'
        ],
        'ordens_dinamicas': [
            'order_id', 'symbol', 'tipo_ordem', 'preco_entrada', 'quantidade', 'preco_saida',
            'lucro_prejuizo', 'tempo_operacao', 'razao_fechamento', 'timestamp_abertura',
            'timestamp_fechamento', 'status'
        ],
        'aprendizado_autonomo': [
            'id', 'symbol', 'decisao', 'confianca', 'resultado', 'timestamp', 'dados_entrada'
        ]
    }
    for tabela, colunas in tabelas_colunas.items():
        ok, msg = checar_tabela_colunas(db_path, tabela, colunas)
        if not ok:
            raise Exception(f"Tabela/coluna faltando: {tabela}: {msg}")
    return True


# Teste final: Ordem de Teste pela IA (só executa se todos os anteriores passarem)
def teste_ordem_ia():
    print("\n===== TESTE FINAL: ORDEM DE TESTE PELA IA =====\n")
    from executor_simulado import ExecutorSimulado
    from ia.decisor import DecisorIA
    from ia.preparador_dados import PreparadorDadosCrypto
    from ia.cursor_ai_client import CursorAITradingClient
    from ia.sistema_aprendizado_autonomo import SistemaAprendizadoAutonomo
    from yaml import safe_load  # type: ignore
    import random
    with open('config.yaml', 'r') as f:
        config = safe_load(f)
    executor = ExecutorSimulado(config)
    preparador = PreparadorDadosCrypto()
    decisor = DecisorIA()
    ia_client = CursorAITradingClient()
    sistema = SistemaAprendizadoAutonomo()
    # Simular dados
    dados_mercado = {'preco': random.uniform(100, 200), 'volume': random.uniform(1, 10)}
    dados_ia = preparador.preparar_dados_analise_crypto(dados_mercado, 1)
    print("[IA] Preparando dados para decisão...")
    decisao_ia = ia_client.analisar_dados_mercado(dados_ia['dados_mercado'])
    print(f"[IA] Decisão IA: {decisao_ia}")
    resposta = decisor.processar_decisao_ia(decisao_ia, dados_ia['dados_mercado'])
    print(f"[IA] Decisão processada: {resposta}")
    if resposta.get('decisao') in ['comprar', 'vender']:
        print(f"[ORD] Enviando ordem de teste: {resposta['decisao'].upper()}...")
        resultado = executor.enviar_ordem_market('BTCUSDT', 'Buy' if resposta['decisao']=='comprar' else 'Sell', qty=0.01)
        assert resultado is not None
        print(f"[ORD] Ordem enviada com sucesso: {resultado}")
        order_id = resultado['orderId']
        preco_saida = resultado['avgPrice']  # ou outro preço de saída desejado
        razao_saida = "fechamento_teste"
        dados_mercado_saida = {}  # ou dados_ia['dados_mercado'] se quiser
        executor.gestor_ordens.fechar_ordem_dinamica(order_id, preco_saida, razao_saida, dados_mercado_saida)
        print("[ORD] Ordem de teste fechada.")
    else:
        print("[ORD] Decisão da IA foi 'aguardar'. Nenhuma ordem enviada.")
    sistema.registrar_decisao_autonoma('BTCUSDT', resposta, dados_ia['dados_mercado'])
    print("[IA] Decisão registrada no sistema de aprendizado.")
    print("\n===== FIM DO TESTE FINAL =====\n")
    return True


# Execução dos testes
if __name__ == "__main__":
    print("\n===== CHECKLIST DE INTEGRAÇÃO DO PROJETO ROBO TRADING =====\n")
    total = len(TESTES)
    passed = 0
    for nome, func in TESTES:
        try:
            print(f"Testando: {nome} ... ", end="")
            ok = func()
            if ok:
                print("✅")
                passed += 1
            else:
                print("❌")
        except Exception as e:
            print(f"❌ {e}")
            traceback.print_exc()
    print(f"\nResumo: {passed}/{total} testes passaram.")
    if passed == total:
        print("\n✅ INTEGRAÇÃO COMPLETA: O sistema está pronto para uso!")
        # Só faz ordem de teste se tudo passou
        teste_ordem_ia()
    else:
        print("\n❌ Existem falhas de integração. Corrija antes de rodar o robô em produção!") 