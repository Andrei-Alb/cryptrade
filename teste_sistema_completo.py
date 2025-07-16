#!/usr/bin/env python3
"""
Teste Completo do Sistema de Trading IA
Verifica todos os componentes: banco, coleta, IA, execução simulada
"""

import sys
import os
import time
import sqlite3
from datetime import datetime
from loguru import logger

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coletor import Coletor
from armazenamento import Armazenamento
from analisador import AnalisadorIA
from executor import ExecutorOrdensSimuladas

def testar_banco_dados():
    """Testa banco de dados"""
    print("🗄️ Testando banco de dados...")
    
    try:
        db_path = "dados/trading.db"
        if not os.path.exists(db_path):
            print("❌ Banco não encontrado")
            return False
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar tabelas
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in c.fetchall()]
        
        tabelas_esperadas = ['precos', 'analises', 'ordens', 'ordens_simuladas', 'aprendizado_ia']
        tabelas_ok = all(tabela in tabelas for tabela in tabelas_esperadas)
        
        if tabelas_ok:
            print("✅ Banco de dados OK")
            print(f"   Tabelas encontradas: {len(tabelas)}")
            
            # Contar registros
            for tabela in tabelas_esperadas:
                if tabela in tabelas:
                    c.execute(f"SELECT COUNT(*) FROM {tabela}")
                    count = c.fetchone()[0]
                    print(f"   📊 {tabela}: {count:,} registros")
            
            # Verificar dados recentes
            c.execute("SELECT COUNT(*) FROM precos WHERE timestamp > datetime('now', '-1 hour')")
            recentes = c.fetchone()[0]
            print(f"   🕐 Dados da última hora: {recentes}")
            
            conn.close()
            return True
        else:
            print("❌ Tabelas essenciais não encontradas")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

def testar_coletor():
    """Testa coletor de dados"""
    print("\n📡 Testando coletor de dados...")
    
    try:
        coletor = Coletor()
        
        # Testar conexão
        if coletor.testar_conexao():
            print("✅ Conexão com API B3 OK")
            
            # Coletar dados
            dados = coletor.coletar_dados()
            if dados and len(dados) > 0:
                print(f"✅ Dados coletados: {len(dados)} símbolos")
                for dado in dados:
                    print(f"   📈 {dado['simbolo']}: {dado['preco_atual']:,.2f}")
                return True
            else:
                print("❌ Nenhum dado coletado")
                return False
        else:
            print("❌ Falha na conexão com API B3")
            return False
            
    except Exception as e:
        print(f"❌ Erro no coletor: {e}")
        return False

def testar_armazenamento():
    """Testa armazenamento"""
    print("\n💾 Testando armazenamento...")
    
    try:
        armazenamento = Armazenamento()
        
        # Dados de teste
        dados_teste = {
            'simbolo': 'TESTE',
            'preco_atual': 100.0,
            'preco_abertura': 99.0,
            'preco_minimo': 98.0,
            'preco_maximo': 101.0,
            'preco_medio': 100.0,
            'variacao': 1.0,
            'volume': 1000,
            'timestamp': datetime.now().isoformat(),
            'fonte': 'TESTE'
        }
        
        # Salvar preço
        sucesso = armazenamento.salvar_precos(
            timestamp=dados_teste['timestamp'],
            preco_atual=dados_teste['preco_atual'],
            preco_abertura=dados_teste['preco_abertura'],
            preco_minimo=dados_teste['preco_minimo'],
            preco_maximo=dados_teste['preco_maximo'],
            preco_medio=dados_teste['preco_medio'],
            variacao=dados_teste['variacao'],
            volume=dados_teste['volume'],
            simbolo=dados_teste['simbolo']
        )
        
        if sucesso:
            print("✅ Armazenamento OK")
            print("   Preço de teste salvo")
            
            # Verificar se foi salvo
            stats = armazenamento.obter_estatisticas()
            print(f"   Total de preços: {stats.get('total_precos', 0):,}")
            return True
        else:
            print("❌ Falha ao salvar dados")
            return False
            
    except Exception as e:
        print(f"❌ Erro no armazenamento: {e}")
        return False

def testar_ia():
    """Testa sistema de IA"""
    print("\n🤖 Testando sistema de IA...")
    
    try:
        analisador = AnalisadorIA()
        
        # Dados de teste
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
        
        # Testar análise
        resultado = analisador.analisar_com_ia(dados_teste)
        
        if resultado and 'decisao' in resultado:
            print("✅ Sistema de IA OK")
            print(f"   Decisão: {resultado['decisao']}")
            print(f"   Confiança: {resultado['confianca']:.2f}")
            print(f"   Razão: {resultado['razao']}")
            return True
        else:
            print("❌ Falha na análise de IA")
            return False
            
    except Exception as e:
        print(f"❌ Erro no sistema de IA: {e}")
        return False

def testar_execucao_simulada():
    """Testa execução simulada"""
    print("\n🚀 Testando execução simulada...")
    
    try:
        executor = ExecutorOrdensSimuladas()
        
        # Decisão de teste
        decisao_teste = {
            'decisao': 'comprar',
            'confianca': 0.75,
            'razao': 'Teste de execução',
            'parametros': {
                'quantidade': 1,
                'stop_loss': 100,
                'take_profit': 200
            }
        }
        
        dados_mercado = {
            'simbolo': 'WINZ25',
            'preco_atual': 143550.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Executar ordem simulada
        resultado = executor.executar_ordem_simulada(decisao_teste, dados_mercado)
        
        if resultado and resultado.get('status') == 'executada':
            print("✅ Execução simulada OK")
            print(f"   Ordem ID: {resultado.get('ordem_id', 'N/A')}")
            print(f"   Preço entrada: {resultado.get('preco_entrada', 0):,.2f}")
            print(f"   Preço alvo: {resultado.get('preco_alvo', 0):,.2f}")
            print(f"   Preço stop: {resultado.get('preco_stop', 0):,.2f}")
            
            # Verificar ordens ativas
            ordens_ativas = len(executor.ordens_ativas)
            print(f"   Ordens ativas: {ordens_ativas}")
            
            return True
        else:
            print("❌ Falha na execução simulada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na execução simulada: {e}")
        return False

def testar_pipeline_completo():
    """Testa pipeline completo: coleta -> armazena -> analisa -> executa"""
    print("\n🔄 Testando pipeline completo...")
    
    try:
        # 1. Coletar dados
        coletor = Coletor()
        dados = coletor.coletar_dados()
        
        if not dados:
            print("❌ Falha na coleta de dados")
            return False
        
        print("✅ Dados coletados")
        
        # 2. Armazenar dados
        armazenamento = Armazenamento()
        for dado in dados:
            armazenamento.salvar_precos(
                timestamp=dado['timestamp'],
                preco_atual=dado['preco_atual'],
                preco_abertura=dado.get('preco_abertura'),
                preco_minimo=dado.get('preco_minimo'),
                preco_maximo=dado.get('preco_maximo'),
                preco_medio=dado.get('preco_medio'),
                variacao=dado.get('variacao'),
                volume=dado.get('volume', 0),
                simbolo=dado['simbolo']
            )
        
        print("✅ Dados armazenados")
        
        # 3. Analisar com IA (apenas para WIN)
        analisador = AnalisadorIA()
        for dado in dados:
            if dado['simbolo'].startswith('WIN'):
                analise = analisador.analisar_com_ia(dado)
                print(f"✅ Análise IA: {analise['decisao']} (confiança: {analise['confianca']:.2f})")
                
                # 4. Executar ordem simulada se necessário
                if analise['decisao'] in ['comprar', 'vender']:
                    executor = ExecutorOrdensSimuladas()
                    resultado = executor.executar_ordem_simulada(analise, dado)
                    if resultado.get('status') == 'executada':
                        print(f"✅ Ordem simulada executada: {resultado['ordem_id']}")
                    else:
                        print(f"⚠️ Ordem não executada: {resultado.get('razao', 'N/A')}")
                break
        
        print("✅ Pipeline completo funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro no pipeline: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE COMPLETO DO SISTEMA DE TRADING IA")
    print("=" * 60)
    
    # Lista de testes
    testes = [
        ("Banco de Dados", testar_banco_dados),
        ("Coletor", testar_coletor),
        ("Armazenamento", testar_armazenamento),
        ("Sistema de IA", testar_ia),
        ("Execução Simulada", testar_execucao_simulada),
        ("Pipeline Completo", testar_pipeline_completo)
    ]
    
    resultados = []
    
    for nome, teste in testes:
        try:
            resultado = teste()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome:20} {status}")
    
    # Verificar se todos passaram
    todos_passaram = all(resultado for _, resultado in resultados)
    
    if todos_passaram:
        print("\n🎉 SISTEMA 100% FUNCIONAL!")
        print("Todos os componentes estão operacionais.")
        print("✅ Banco de dados: OK")
        print("✅ Coleta de dados: OK")
        print("✅ Sistema de IA: OK")
        print("✅ Execução simulada: OK")
        print("✅ Pipeline completo: OK")
    else:
        print("\n⚠️  ALGUNS COMPONENTES COM PROBLEMAS")
        print("Verifique os erros acima antes de usar o sistema.")
    
    return todos_passaram

if __name__ == "__main__":
    main() 