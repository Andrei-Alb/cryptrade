#!/usr/bin/env python3
"""
Teste do Sistema Preditivo de Trading
Testa as funcionalidades de previsão sem depender do modelo de IA
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
import sqlite3

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia.filtros_qualidade import FiltrosQualidade
from ia.decisor import Decisor
from ia.gestor_ordens import GestorOrdens
from ia.sistema_aprendizado import SistemaAprendizado
from armazenamento import Armazenamento
from config import Config

class TesteSistemaPreditivo:
    def __init__(self):
        self.config = Config()
        self.armazenamento = Armazenamento()
        self.filtros = FiltrosQualidade()
        self.decisor = Decisor()
        self.gestor_ordens = GestorOrdens()
        self.sistema_aprendizado = SistemaAprendizado()
        
        # Dados de teste simulados
        self.dados_teste = {
            "PETR4": {
                "preco_atual": 35.50,
                "volume": 1500000,
                "variacao": 0.02,
                "tendencia": "alta",
                "indicadores": {
                    "rsi": 65,
                    "macd": 0.10,
                    "media_movel": 34.80
                }
            },
            "VALE3": {
                "preco_atual": 68.20,
                "volume": 2000000,
                "variacao": -0.01,
                "tendencia": "baixa",
                "indicadores": {
                    "rsi": 45,
                    "macd": -0.05,
                    "media_movel": 69.10
                }
            }
        }
    
    def testar_filtros_qualidade(self):
        print("\n=== Testando Filtros de Qualidade ===")
        
        for ativo, dados in self.dados_teste.items():
            print(f"\nTestando filtros para {ativo}:")
            
            # Simula dados de mercado
            dados_mercado = {
                "ativo": ativo,
                "preco": dados['preco_atual'],
                "volume": dados['volume'],
                "variacao": dados['variacao'],
                "timestamp": datetime.now().isoformat()
            }
            
            # Testa filtros
            qualidade = self.filtros.avaliar_qualidade(dados_mercado)
            print(f"  Qualidade: {qualidade}")
            
            # Testa filtro de tendência
            tendencia_valida = self.filtros.filtrar_tendencia(dados_mercado)
            print(f"  Tendência válida: {tendencia_valida}")
            
            # Testa filtro de volume
            volume_valido = self.filtros.filtrar_volume(dados_mercado)
            print(f"  Volume válido: {volume_valido}")
    
    def testar_decisor_preditivo(self):
        print("\n=== Testando Decisor Preditivo ===")
        
        for ativo, dados in self.dados_teste.items():
            print(f"\nTestando decisão para {ativo}:")
            
            # Simula previsão da IA (sem chamar o modelo real)
            previsao_simulada = {
                "acao": "comprar" if dados['tendencia'] == 'alta' else "vender",
                "confianca": 0.75,
                "preco_alvo": dados['preco_atual'] * (1.05 if dados['tendencia'] == 'alta' else 0.95),
                "stop_loss": dados['preco_atual'] * (0.98 if dados['tendencia'] == 'alta' else 1.02),
                "cenarios": {
                    "otimista": dados['preco_atual'] * 1.08,
                    "realista": dados['preco_atual'] * 1.03,
                    "pessimista": dados['preco_atual'] * 0.97
                },
                "razoes": f"Tendência {dados['tendencia']} com indicadores favoráveis"
            }
            
            # Testa decisão
            decisao = self.decisor.tomar_decisao_preditiva(
                ativo, 
                dados['preco_atual'], 
                previsao_simulada
            )
            
            print(f"Decisão: {decisao['acao']}")
            print(f"  Confiança: {decisao['confianca']:0.2f}")
            print(f"  Preço alvo: R$ {decisao['preco_alvo']:0.2f}")
            print(f"  Stop loss: R$ {decisao['stop_loss']:0.2f}")
    
    def testar_gestor_ordens_preditivo(self):
        print("\n=== Testando Gestor de Ordens Preditivo ===")
        
        for ativo, dados in self.dados_teste.items():
            print(f"\nTestando gestão de ordens para {ativo}:")
            
            # Simula ordem com previsões
            ordem = {
                "ativo": ativo,
                "acao": "comprar" if dados['tendencia'] == 'alta' else "vender",
                "quantidade": 100,
                "preco_entrada": dados['preco_atual'],
                "preco_alvo": dados['preco_atual'] * 1.05,
                "stop_loss": dados['preco_atual'] * 0.98,
                "cenarios": {
                    "otimista": dados['preco_atual'] * 1.08,
                    "realista": dados['preco_atual'] * 1.03,
                    "pessimista": dados['preco_atual'] * 0.97
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Testa criação de ordem
            ordem_id = self.gestor_ordens.criar_ordem_preditiva(ordem)
            print(f"  Ordem criada com ID: {ordem_id}")
            
            # Testa ajuste dinâmico de stop loss
            novo_preco = dados['preco_atual'] * 1.02
            stop_ajustado = self.gestor_ordens.ajustar_stop_loss_dinamico(
                ordem_id, novo_preco, ordem['stop_loss']
            )
            print(f"Stop loss ajustado: R$ {stop_ajustado:0.2f}")
            
            # Testa verificação de cenários
            cenario_ativo = self.gestor_ordens.verificar_cenarios_saida(
                ordem_id, novo_preco, ordem['cenarios']
            )
            print(f"  Cenário ativo: {cenario_ativo}")
    
    def testar_sistema_aprendizado(self):
        print("\n=== Testando Sistema de Aprendizado ===")
        
        # Simula registro de previsão
        previsao = {
            "ativo": "PETR4",
            "preco_atual": 350.5,
            "previsao": {
                "acao": "comprar",
                "preco_alvo": 37.50,
                "stop_loss": 34.80,
                "confianca": 0.75
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Registra previsão
        self.sistema_aprendizado.registrar_previsao(previsao)
        print("  Previsão registrada")
        
        # Simula resultado (após algum tempo)
        resultado = {
            "ativo": "PETR4",
            "preco_realizado": 360.8,
            "acao_realizada": "comprar",
            "lucro_percentual": 30.66,
            "timestamp": datetime.now().isoformat()
        }
        
        # Registra resultado
        self.sistema_aprendizado.registrar_resultado(resultado)
        print("  Resultado registrado")
        
        # Testa análise de performance
        performance = self.sistema_aprendizado.analisar_performance('PETR4')
        print(f"  Performance: {performance}")
    
    def testar_banco_dados(self):
        print("\n=== Testando Estrutura do Banco de Dados ===")
        
        try:
            # Verifica se as tabelas existem
            cursor = self.armazenamento.conn.cursor()
            
            # Lista todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = cursor.fetchall()
            print(f"  Tabelas encontradas: {[t[0] for t in tabelas]}")
            
            # Verifica estrutura da tabela de previsoes
            if 'previsoes' in [t[0] for t in tabelas]:
                cursor.execute("PRAGMA table_info(previsoes);")
                colunas = cursor.fetchall()
                print(f"  Colunas da tabela previsoes: {[c[1] for c in colunas]}")
            
            # Verifica estrutura da tabela de resultados
            if 'resultados_previsoes' in [t[0] for t in tabelas]:
                cursor.execute("PRAGMA table_info(resultados_previsoes);")
                colunas = cursor.fetchall()
                print(f"  Colunas da tabela resultados_previsoes: {[c[1] for c in colunas]}")
            
            cursor.close()
            
        except Exception as e:
            print(f"  Erro ao verificar banco: {e}")
    
    def executar_todos_testes(self):
        print("🚀 Iniciando Testes do Sistema Preditivo")
        print("=" * 50)
        
        try:
            # Testa estrutura do banco primeiro
            self.testar_banco_dados()
            
            # Testa filtros
            self.testar_filtros_qualidade()
            
            # Testa decisor
            self.testar_decisor_preditivo()
            
            # Testa gestor de ordens
            self.testar_gestor_ordens_preditivo()
            
            # Testa sistema de aprendizado
            self.testar_sistema_aprendizado()
            
            print("\n" + "=" * 50)
            print("✅ Todos os testes concluídos com sucesso!")
            
        except Exception as e:
            print(f"\n❌ Erro durante os testes: {e}")
            import traceback
            traceback.print_exc()

def main():
    teste = TesteSistemaPreditivo()
    teste.executar_todos_testes()

if __name__ == "__main__":
    main() 