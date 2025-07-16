#!/usr/bin/env python3
"""
Teste do Sistema Crypto Trading
Valida integração dos componentes: coletor, executor, armazenamento, preparador de dados
"""

import os
import sys
import time
import yaml
from datetime import datetime
from loguru import logger

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coletor import ColetorBybit
from executor import ExecutorBybit
from armazenamento import ArmazenamentoCrypto
from ia.preparador_dados import PreparadorDadosCrypto

class TesteSistemaCrypto:
    def __init__(self):
        """Inicializa teste do sistema crypto"""
        self.config = self._carregar_config()
        self.armazenamento = ArmazenamentoCrypto()
        self.preparador = PreparadorDadosCrypto()
        
        # Inicializar componentes
        self.coletor = ColetorBybit()
        self.executor = ExecutorBybit()
        
        logger.info("Sistema crypto inicializado para testes")
    
    def _carregar_config(self):
        """Carrega configuração da Bybit"""
        try:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            return {}
    
    def teste_conectividade(self):
        """Testa conectividade com Bybit"""
        logger.info("=== TESTE DE CONECTIVIDADE ===")
        
        try:
            # Teste de conectividade básica
            resultado = self.coletor.verificar_conectividade()
            if resultado:
                logger.success("✅ Conectividade com Bybit OK")
            else:
                logger.error("❌ Falha na conectividade com Bybit")
                return False
            
            # Teste de consulta de saldo
            saldo = self.executor._verificar_saldo()
            if saldo:
                logger.success(f"✅ Saldo consultado: {saldo}")
            else:
                logger.warning("⚠️ Não foi possível consultar saldo")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de conectividade: {e}")
            return False
    
    def teste_coleta_dados(self):
        """Testa coleta de dados crypto"""
        logger.info("=== TESTE DE COLETA DE DADOS ===")
        
        try:
            symbol = "BTCUSDT"
            
            # Coletar dados históricos
            dados_historicos = self.coletor.obter_dados_rest(symbol, "5", 10)
            if dados_historicos is not None and not dados_historicos.empty:
                logger.success(f"✅ Dados históricos coletados: {len(dados_historicos)} registros")
                
                # Salvar no banco
                for _, row in dados_historicos.iterrows():
                    self.armazenamento.salvar_precos_crypto(
                        symbol=symbol,
                        timestamp=row['timestamp'],
                        open_price=row['open'],
                        high_price=row['high'],
                        low_price=row['low'],
                        close_price=row['close'],
                        volume=row['volume'],
                        interval='5m'
                    )
                logger.success("✅ Dados salvos no banco crypto")
            else:
                logger.error("❌ Falha na coleta de dados históricos")
                return False
            
            # Coletar preço atual
            preco_atual = self.coletor.obter_preco_atual(symbol)
            if preco_atual:
                logger.success(f"✅ Preço atual {symbol}: {preco_atual}")
            else:
                logger.error("❌ Falha na coleta de preço atual")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de coleta: {e}")
            return False
    
    def teste_preparador_dados(self):
        """Testa preparador de dados crypto"""
        logger.info("=== TESTE DE PREPARADOR DE DADOS ===")
        
        try:
            symbol = "BTCUSDT"
            
            # Dados simulados para teste
            dados_atual = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'close_price': 50000.0,
                'volume': 1000.0,
                'interval': '5m'
            }
            
            # Preparar dados para IA
            dados_ia = self.preparador.preparar_dados_analise_crypto(dados_atual, 50)
            
            if dados_ia:
                logger.success("✅ Dados preparados para IA")
                logger.info(f"   - Indicadores calculados: {len(dados_ia.get('indicadores_tecnicos', {}))}")
                logger.info(f"   - Contexto mercado: {dados_ia.get('contexto_mercado', {})}")
                return True
            else:
                logger.error("❌ Falha na preparação de dados")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de preparador: {e}")
            return False
    
    def teste_executor_ordens(self):
        """Testa executor de ordens (simulado)"""
        logger.info("=== TESTE DE EXECUTOR DE ORDENS ===")
        
        try:
            symbol = "BTCUSDT"
            
            # Teste de consulta de ordens abertas
            ordens_abertas = self.executor.obter_ordens_ativas(symbol)
            logger.info(f"   - Ordens abertas: {len(ordens_abertas) if ordens_abertas else 0}")
            
            # Teste de consulta de posições
            posicoes = self.executor.obter_posicoes(symbol)
            logger.info(f"   - Posições: {len(posicoes) if posicoes else 0}")
            
            # Teste de cálculo de quantidade (sem executar ordem real)
            quantidade = self.executor._obter_quantidade(symbol)  # Quantidade padrão
            logger.info(f"   - Quantidade padrão para {symbol}: {quantidade}")
            
            logger.success("✅ Executor testado (sem execução real)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de executor: {e}")
            return False
    
    def teste_armazenamento(self):
        """Testa funcionalidades do armazenamento"""
        logger.info("=== TESTE DE ARMAZENAMENTO ===")
        
        try:
            symbol = "BTCUSDT"
            
            # Teste de consulta de dados salvos
            ultimos_precos = self.armazenamento.obter_ultimos_precos_crypto(symbol, 10)
            logger.info(f"   - Últimos preços salvos: {len(ultimos_precos)}")
            
            # Teste de estatísticas
            estatisticas = self.armazenamento.obter_estatisticas_crypto()
            logger.info(f"   - Estatísticas: {estatisticas}")
            
            # Teste de métricas
            metricas = self.armazenamento.calcular_metricas_crypto(symbol)
            logger.info(f"   - Métricas calculadas: {len(metricas)}")
            
            logger.success("✅ Armazenamento funcionando")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de armazenamento: {e}")
            return False
    
    def teste_sistema_completo(self):
        """Testa integração completa do sistema"""
        logger.info("=== TESTE DE SISTEMA COMPLETO ===")
        
        try:
            symbol = "BTCUSDT"
            
            # 1. Coletar dados
            dados_historicos = self.coletor.obter_dados_rest(symbol, "5", 5)
            if dados_historicos is None or dados_historicos.empty:
                logger.error("❌ Falha na coleta de dados")
                return False
            
            # 2. Salvar dados
            for _, row in dados_historicos.iterrows():
                self.armazenamento.salvar_precos_crypto(
                    symbol=symbol,
                    timestamp=row['timestamp'],
                    open_price=row['open'],
                    high_price=row['high'],
                    low_price=row['low'],
                    close_price=row['close'],
                    volume=row['volume'],
                    interval='5m'
                )
            
            # 3. Preparar dados para IA
            dados_atual = {
                'symbol': symbol,
                'timestamp': dados_historicos.iloc[0]['timestamp'].isoformat(),
                'close_price': float(dados_historicos.iloc[0]['close']),
                'volume': float(dados_historicos.iloc[0]['volume']),
                'interval': '5m'
            }
            dados_ia = self.preparador.preparar_dados_analise_crypto(dados_atual, 50)
            
            if not dados_ia:
                logger.error("❌ Falha na preparação de dados")
                return False
            
            # 4. Simular análise (sem IA real)
            logger.info("   - Dados preparados para análise de IA")
            logger.info(f"   - Indicadores: RSI={dados_ia['indicadores_tecnicos'].get('rsi', 'N/A')}")
            logger.info(f"   - Tendência: {dados_ia['indicadores_tecnicos'].get('tendencia', 'N/A')}")
            
            # 5. Verificar armazenamento
            ultimos_precos = self.armazenamento.obter_ultimos_precos_crypto(symbol, 5)
            logger.info(f"   - Dados salvos: {len(ultimos_precos)} registros")
            
            logger.success("✅ Sistema completo funcionando")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de sistema completo: {e}")
            return False
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        logger.info("🚀 INICIANDO TESTES DO SISTEMA CRYPTO")
        logger.info("=" * 50)
        
        testes = [
            ("Conectividade", self.teste_conectividade),
            ("Coleta de Dados", self.teste_coleta_dados),
            ("Preparador de Dados", self.teste_preparador_dados),
            ("Executor de Ordens", self.teste_executor_ordens),
            ("Armazenamento", self.teste_armazenamento),
            ("Sistema Completo", self.teste_sistema_completo)
        ]
        
        resultados = {}
        
        for nome, teste in testes:
            logger.info(f"\n📋 Executando: {nome}")
            try:
                resultado = teste()
                resultados[nome] = resultado
                if resultado:
                    logger.success(f"✅ {nome}: PASSOU")
                else:
                    logger.error(f"❌ {nome}: FALHOU")
            except Exception as e:
                logger.error(f"❌ {nome}: ERRO - {e}")
                resultados[nome] = False
        
        # Resumo final
        logger.info("\n" + "=" * 50)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("=" * 50)
        
        total_testes = len(testes)
        testes_passaram = sum(resultados.values())
        
        for nome, resultado in resultados.items():
            status = "✅ PASSOU" if resultado else "❌ FALHOU"
            logger.info(f"   {nome}: {status}")
        
        logger.info(f"\n🎯 RESULTADO: {testes_passaram}/{total_testes} testes passaram")
        
        if testes_passaram == total_testes:
            logger.success("🎉 TODOS OS TESTES PASSARAM! Sistema crypto pronto!")
        else:
            logger.warning("⚠️ Alguns testes falharam. Verificar configurações.")
        
        return resultados

def main():
    """Função principal"""
    try:
        teste = TesteSistemaCrypto()
        resultados = teste.executar_todos_testes()
        
        # Retornar código de saída baseado nos resultados
        if all(resultados.values()):
            sys.exit(0)  # Sucesso
        else:
            sys.exit(1)  # Falha
            
    except KeyboardInterrupt:
        logger.info("Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro geral no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 