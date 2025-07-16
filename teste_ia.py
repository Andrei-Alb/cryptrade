#!/usr/bin/env python3
"""
Script de teste para o sistema de IA
Testa a integração com Ollama e análise de dados
"""

import sys
import os
import time
from datetime import datetime

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analisador import AnalisadorIA
from ia.cursor_ai_client import CursorAITradingClient
from ia.preparador_dados import PreparadorDadosIA
from ia.decisor import DecisorIA

def testar_ollama():
    """Testa conexão com Ollama"""
    print("🔍 Testando conexão com Ollama...")
    
    try:
        cliente = CursorAITradingClient()
        if cliente.testar_conexao():
            print("✅ Ollama está rodando e acessível")
            return True
        else:
            print("❌ Não foi possível conectar ao Ollama")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar Ollama: {e}")
        return False

def testar_preparador_dados():
    """Testa preparador de dados"""
    print("\n📊 Testando preparador de dados...")
    
    try:
        preparador = PreparadorDadosIA()
        
        # Dados de teste baseados em valores reais do mercado
        dados_teste = {
            'simbolo': 'WINZ25',
            'preco_atual': 143550.0,
            'preco_abertura': 143500.0,
            'preco_minimo': 143200.0,
            'preco_maximo': 143800.0,
            'preco_medio': 143550.0,
            'variacao': 0.35,
            'volume': 5000,
            'timestamp': datetime.now().isoformat(),
            'fonte': 'B3_API'
        }
        
        dados_preparados = preparador.preparar_dados_analise(dados_teste)
        print("✅ Preparador de dados funcionando")
        print(f"   Dados preparados: {len(dados_preparados)} campos")
        return True
        
    except Exception as e:
        print(f"❌ Erro no preparador de dados: {e}")
        return False

def testar_decisor():
    """Testa decisor de IA"""
    print("\n🎯 Testando decisor de IA...")
    
    try:
        decisor = DecisorIA()
        
        # Decisão de teste
        decisao_teste = {
            'decisao': 'comprar',
            'confianca': 0.8,
            'razao': 'Teste de decisão',
            'parametros': {
                'quantidade': 1,
                'stop_loss': 100,
                'take_profit': 200
            }
        }
        
        dados_mercado = {
            'rsi': 45.0,
            'volatilidade': 0.02,
            'volume': 5000,
            'volume_medio': 4000,
            'tendencia': 'alta'
        }
        
        decisao_processada = decisor.processar_decisao_ia(decisao_teste, dados_mercado)
        print("✅ Decisor de IA funcionando")
        print(f"   Decisão: {decisao_processada['decisao']}")
        return True
        
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"❌ Erro no decisor: {e}")
        return False

def testar_analise_completa():
    """Testa análise completa com IA"""
    print("\n🤖 Testando análise completa com IA...")
    
    try:
        analisador = AnalisadorIA()
        
        # Dados de teste baseados em valores reais do mercado
        dados_teste = {
            'simbolo': 'WINZ25',
            'preco_atual': 143550.0,
            'preco_abertura': 143500.0,
            'preco_minimo': 143200.0,
            'preco_maximo': 143800.0,
            'preco_medio': 143550.0,
            'variacao': 0.35,
            'volume': 5000,
            'timestamp': datetime.now().isoformat(),
            'fonte': 'B3_API'
        }
        
        print("   Enviando dados para análise...")
        resultado = analisador.analisar_com_ia(dados_teste)
        
        print("✅ Análise completa funcionando")
        print(f"   Decisão: {resultado['decisao']}")
        print(f"   Confiança: {resultado['confianca']:.2f}")
        print(f"   Razão: {resultado['razao']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise completa: {e}")
        return False

def mostrar_estatisticas():
    """Mostra estatísticas do sistema"""
    print("\n📈 Estatísticas do sistema...")
    
    try:
        analisador = AnalisadorIA()
        stats = analisador.obter_estatisticas()
        
        print(f"   Total de decisões: {stats['total_decisoes']}")
        print(f"   Decisões hoje: {stats['decisoes_hoje']}")
        print(f"   Taxa de compra: {stats['taxa_compra']:.2%}")
        print(f"   Taxa de venda: {stats['taxa_venda']:.2%}")
        print(f"   Taxa de aguardar: {stats['taxa_aguardar']:.2%}")
        print(f"   Confiança média: {stats['confianca_media']:.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema de IA")
    print("=" * 50)
    
    # Testar componentes individuais
    testes = [
        ("Ollama", testar_ollama),
        ("Preparador de Dados", testar_preparador_dados),
        ("Decisor", testar_decisor),
        ("Análise Completa", testar_analise_completa)
    ]
    
    resultados = []
    
    for nome, teste in testes:
        try:
            resultado = teste()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Mostrar resumo
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome:20} {status}")
    
    # Mostrar estatísticas
    mostrar_estatisticas()
    
    # Verificar se todos os testes passaram
    todos_passaram = all(resultado for _, resultado in resultados)
    
    if todos_passaram:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O sistema de IA está funcionando corretamente.")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima e corrija antes de usar o sistema.")
    
    return todos_passaram

if __name__ == "__main__":
    main() 