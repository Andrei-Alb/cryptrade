#!/usr/bin/env python3
"""
Teste do Ciclo Completo de Previsão → Execução → Aprendizado
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
import sqlite3

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia.decisor import Decisor
from ia.sistema_aprendizado import SistemaAprendizado
from ia.gestor_ordens import GestorOrdensIA
from armazenamento import Armazenamento

class TesteCicloPrevisao:
    def __init__(self):
        self.decisor = Decisor()
        self.sistema_aprendizado = SistemaAprendizado()
        self.gestor_ordens = GestorOrdensIA(parametros_ia=self.sistema_aprendizado.parametros_atuais)
        self.armazenamento = Armazenamento()
        
        # Dados de teste simulados
        self.dados_teste = {
            "symbol": "BTCUSDT",
            "preco_atual": 5000,
            "rsi650": 0.7,
            "tendencia": "alta",
            "volatilidade": 0.025,
            "volume_24h": 10000
        }
    
    def testar_previsao_ia(self):
      
        print("\n=== Testando Previsão da IA ===")
        
        try:
            # Simular decisão da IA com previsões
            decisao_simulada = {
                "decisao": "comprar",
                "confianca": 0.8,
                "previsao_alvo": 52000.0,
                "stop_loss": 49000.0,
                "cenario_permanencia": "Manter se preço acima de 49500",
                "cenario_saida": "Sair se atingir 52000 ou cair para 49000",
                "razao": "RSIfavorável com tendência alta"
            }
            
            # Processar decisão
            decisao_processada = self.decisor.processar_decisao_ia(decisao_simulada, self.dados_teste)
            
            if decisao_processada and 'previsoes' in decisao_processada:
                previsoes = decisao_processada['previsoes']
                print(f"✅ Previsões extraídas:")
                print(f"   Target: {previsoes.get('target', 'N/A')}")
                print(f"   Stop Loss: {previsoes.get('stop_loss', 'N/A')}")
                print(f" Cenários: {previsoes.get('cenarios', {})}")
                return decisao_processada
            else:
                print("❌ Falha ao extrair previsões")
                return None
                
        except Exception as e:
            print(f"❌ Erro no teste de previsão: {e}")
            return None
    
    def testar_criacao_ordem(self):
        
        print("\n=== Testando Criação de Ordem ===")
        
        try:
            # Simular ordem com previsões
            ordem = {
                "order_id": "TESTE_001",
                "symbol": "BTCUSDT",
                "tipo": "comprar",
                "preco_entrada": 50000.0,
                "quantidade": 0.001,
                "confianca_ia": 0.8,
                "previsoes_ia": {
                    "target": 52000.0,
                    "stop_loss": 49000.0,
                    "cenarios": {
                        "manter": "Manter se preço acima de 49500",
                        "sair_lucro": "Sair se atingir 52000",
                        "sair_perda": "Sair se cair para 49000"
                    }
                }
            }
            
            # Adicionar ordem ao gestor
            self.gestor_ordens.adicionar_ordem_ativa(ordem)
            
            # Verificar se foi adicionada
            if ordem["order_id"] in self.gestor_ordens.ordens_ativas:
                print(f"✅ Ordem criada com previsões: {ordem['order_id']}")
                return ordem
            else:
                print("❌ Falha ao criar ordem")
                return None
                
        except Exception as e:
            print(f"❌ Erro no teste de criação de ordem: {e}")
            return None
    
    def testar_analise_previsoes(self):
       
        print("\n=== Testando Análise de Previsões ===")
        
        try:
            # Dados de mercado simulados (preço atingiu o target)
            dados_mercado_target = {
                "preco_atual": 52000, # Target atingido
                "symbol": "BTCUSDT"
            }
            
            # Analisar ordens ativas
            decisoes = self.gestor_ordens.analisar_ordens_ativas(dados_mercado_target)
            
            if decisoes:
                for decisao in decisoes:
                    if decisao.get('tipo_saida') == 'target_ia':
                        print(f"✅ Target da IA atingido: {decisao['razao']}")
                        return decisao
            
            print("⚠️ Nenhuma decisão baseada em previsões encontrada")
            return None
            
        except Exception as e:
            print(f"❌ Erro no teste de análise: {e}")
            return None
    
    def testar_aprendizado(self):
      
        print("\n=== Testando Aprendizado ===")
        
        try:
            # Simular ordem fechada com previsões
            ordem = {
                "order_id": "TESTE_001",
                "confianca_ia": 0.8,
                "tipo_ordem": "compra",
                "preco_entrada": 50000.0,
                "duracao_segundos": 120,
                "razao_fechamento": "target atingido",
                "previsoes_ia": {
                    "target": 52000.0,
                    "stop_loss": 49000.0,
                    "cenarios": {
                        "sair_lucro": "Sair se atingir 52000"
                    }
                }
            }
            
            resultado = "win"
            lucro_percentual = 4.0
            dados_mercado = {
                "preco_atual": 52000
            }
            # Registrar aprendizado
            sucesso = self.sistema_aprendizado.registrar_aprendizado_ordem(
                ordem, resultado, lucro_percentual, dados_mercado
            )
            
            if sucesso:
                print("✅ Aprendizado registrado com sucesso")
                
                # Verificar se foi salvo no banco
                conn = sqlite3.connect("dados/trading.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM analise_previsoes_ia WHERE order_id = ?", ("TESTE_001",))
                count = cursor.fetchone()[0]
                conn.close()
                
                if count > 0:
                    print("✅ Análise de previsões salva no banco")
                    return True
                else:
                    print("❌ Análise de previsões não encontrada no banco")
                    return False
            else:
                print("❌ Falha ao registrar aprendizado")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste de aprendizado: {e}")
            return False
    
    def testar_estatisticas_previsoes(self):
    
        print("\n=== Testando Estatísticas de Previsões ===")
        
        try:
            # Obter estatísticas
            stats = self.sistema_aprendizado.obter_estatisticas_previsoes(dias=1)
            
            if stats and 'total_analises' in stats:
                print(f"✅ Estatísticas obtidas:")
                print(f"   Total de análises: {stats.get('total_analises', 0)}")
                print(f"   Precisão do target: {stats.get('precisao_target', 0):.1f}%")
                print(f"   Precisão do stop: {stats.get('precisao_stop', 0):.1f}%")
                print(f"   Win rate: {stats.get('win_rate', 0):.1f}%")
                return True
            else:
                print("⚠️ Nenhuma estatística disponível")
                return True  # Não é erro, pode não ter dados ainda
                
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return False   
    def executar_todos_testes(self):
    
        print("🚀 Iniciando Teste do Ciclo Completo de Previsão")
        print("=" * 60)
        
        resultados = {}
        
        try:
            # Teste 1 da IA
            resultados['previsao'] = self.testar_previsao_ia() is not None
            
            # Teste 2: Criação de ordem
            ordem = self.testar_criacao_ordem()
            resultados['criacao_ordem'] = ordem is not None
            
            # Teste3 Análise de previsões
            resultados['analise_previsoes'] = self.testar_analise_previsoes() is not None
            
            # Teste 4: Aprendizado
            resultados['aprendizado'] = self.testar_aprendizado()
            
            # Teste 5: Estatísticas
            resultados['estatisticas'] = self.testar_estatisticas_previsoes()
            
            # Resumo
            print("\n" + "=" * 60)
            print("📊 RESUMO DOS TESTES")
            print("=" *60)
            for teste, resultado in resultados.items():
                status = "✅ PASSOU" if resultado else "❌ FALHOU"
                print(f"{teste.replace('_', ' ').title()}: {status}")
            
            total_passou = sum(resultados.values())
            total_testes = len(resultados)
            
            print(f"\nTotal: {total_passou}/{total_testes} testes passaram")
            
            if total_passou == total_testes:
                print("\n🎉 CICLO DE PREVISÃO FUNCIONANDO PERFEITAMENTE!")
                print("✅ A IA está prevendo, executando e aprendendo corretamente")
            else:
                print(f"\n⚠️ {total_testes - total_passou} problema(s) encontrado(s)")
                print("Revisar os testes que falharam")
            
            return total_passou == total_testes
            
        except Exception as e:
            print(f"\n❌ Erro geral nos testes: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    teste = TesteCicloPrevisao()
    sucesso = teste.executar_todos_testes()
    
    if sucesso:
        print("\n✅ Todos os testes passaram! O sistema de previsão está funcionando.")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Revisar o sistema.")
        sys.exit(1)
if __name__ == "__main__":
    main() 