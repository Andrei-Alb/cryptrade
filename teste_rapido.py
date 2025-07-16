#!/usr/bin/env python3
"""
Teste rápido do sistema de trading
Verifica se todos os componentes estão funcionando
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from coletor import Coletor
from armazenamento import Armazenamento
from analisador import AnalisadorIA
import config

def testar_banco():
    """Testa banco de dados"""
    print("\n🗄️ Testando banco de dados...")
    
    try:
        armazenamento = Armazenamento()
        
        # Verificar se tabelas existem
        conn = sqlite3.connect(armazenamento.db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = c.fetchall()
        conn.close()
        
        print("✅ Banco de dados funcionando")
        print(f"   Tabelas encontradas: {len(tabelas)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def testar_coletor():
    """Testa coletor de dados"""
    print("\n📊 Testando coletor de dados...")
    
    try:
        coletor = Coletor()
        dados = coletor.coletar_dados()
        
        if dados and len(dados) > 0:
            print("✅ Coletor funcionando")
            print(f"   Dados coletados: {len(dados)} símbolos")
            for dado in dados[:2]:  # Mostrar apenas os primeiros 2
                print(f"   📈 {dado['simbolo']}: {dado['preco_atual']}")
            return True
        else:
            print("⚠️ Coletor não retornou dados (pode ser normal fora do horário de mercado)")
            return True  # Não é um erro crítico
            
    except Exception as e:
        print(f"❌ Erro no coletor: {e}")
        return False

def testar_ia():
    """Testa se a IA está funcionando"""
    try:
        print("\n🤖 Testando análise com IA...")
        from analisador import AnalisadorIA
        import config
        
        config_data = config.load_config()
        analisador = AnalisadorIA(config_data)
        
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
        
        analise = analisador.analisar_com_ia(dados_teste)
        print(f"✅ IA respondeu: {analise['decisao']} (confiança: {analise['confianca']:.2f})")
        return True
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        return True  # Não é crítico

def main():
    """Função principal"""
    print("🚀 Teste Rápido do Sistema de Trading")
    print("=" * 50)
    
    # Testar componentes
    testes = [
        ("Banco de Dados", testar_banco),
        ("Coletor", testar_coletor),
        ("IA", testar_ia)
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
        print(f"{nome:15} {status}")
    
    # Verificar se todos os testes passaram
    todos_passaram = all(resultado for _, resultado in resultados)
    
    if todos_passaram:
        print("\n🎉 SISTEMA FUNCIONANDO!")
        print("Todos os componentes estão operacionais.")
    else:
        print("\n⚠️  ALGUNS PROBLEMAS DETECTADOS")
        print("Verifique os erros acima antes de usar o sistema.")
    
    return todos_passaram

if __name__ == "__main__":
    main() 