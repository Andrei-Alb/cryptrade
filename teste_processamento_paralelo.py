#!/usr/bin/env python3
"""
Teste de Processamento Paralelo
Valida a performance do processamento paralelo vs sequencial
"""

import time
import json
import logging
from typing import Dict, Any, List
from ia.analisador_paralelo import AnalisadorParalelo
from ia.decisor import Decisor

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesteProcessamentoParalelo:
    """Teste para validar processamento paralelo"""
    
    def __init__(self):
        self.analisador_paralelo = AnalisadorParalelo(max_workers=3)
        self.decisor_sequencial = Decisor()
        
    def gerar_dados_multiplos_pares(self, num_pares: int = 5) -> Dict[str, Dict[str, Any]]:
        """Gera dados para múltiplos pares"""
        pares = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT']
        dados = {}
        
        for i in range(min(num_pares, len(pares))):
            symbol = pares[i]
            dados[symbol] = {
                'symbol': symbol,
                'rsi': 30 + (i * 10),  # RSI variado
                'tendencia': ['alta', 'baixa', 'lateral'][i % 3],
                'volatilidade': 0.02 + (i * 0.01),
                'preco_atual': 100 + (i * 50),
                'volume_24h': 1000000000 + (i * 500000000),
                'volume_1h': 50000000 + (i * 25000000)
            }
        
        return dados
    
    def teste_sequencial(self, pares_dados: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Testa processamento sequencial"""
        logger.info(f"🔄 Iniciando teste sequencial com {len(pares_dados)} pares")
        
        inicio = time.time()
        resultados = {}
        
        for symbol, dados in pares_dados.items():
            decisao = self.decisor_sequencial.analisar_mercado(dados)
            resultados[symbol] = decisao
            logger.info(f"✅ {symbol}: análise sequencial concluída")
        
        tempo_total = time.time() - inicio
        
        return {
            'tempo_total': tempo_total,
            'resultados': resultados,
            'num_pares': len(pares_dados)
        }
    
    def teste_paralelo(self, pares_dados: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Testa processamento paralelo"""
        logger.info(f"⚡ Iniciando teste paralelo com {len(pares_dados)} pares")
        
        inicio = time.time()
        resultados = self.analisador_paralelo.analisar_pares_simultaneamente(pares_dados)
        tempo_total = time.time() - inicio
        
        return {
            'tempo_total': tempo_total,
            'resultados': resultados,
            'num_pares': len(pares_dados)
        }
    
    async def teste_paralelo_async(self, pares_dados: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Testa processamento paralelo assíncrono"""
        logger.info(f"🚀 Iniciando teste paralelo assíncrono com {len(pares_dados)} pares")
        
        inicio = time.time()
        resultados = await self.analisador_paralelo.analisar_pares_async(pares_dados)
        tempo_total = time.time() - inicio
        
        return {
            'tempo_total': tempo_total,
            'resultados': resultados,
            'num_pares': len(pares_dados)
        }
    
    def comparar_resultados(self, sequencial: Dict[str, Any], paralelo: Dict[str, Any]) -> Dict[str, Any]:
        """Compara resultados dos testes"""
        tempo_sequencial = sequencial['tempo_total']
        tempo_paralelo = paralelo['tempo_total']
        
        melhoria = ((tempo_sequencial - tempo_paralelo) / tempo_sequencial) * 100
        speedup = tempo_sequencial / tempo_paralelo if tempo_paralelo > 0 else 0
        
        return {
            'tempo_sequencial': tempo_sequencial,
            'tempo_paralelo': tempo_paralelo,
            'melhoria_percentual': melhoria,
            'speedup': speedup,
            'num_pares': sequencial['num_pares'],
            'resultados_iguais': self._verificar_resultados_iguais(
                sequencial['resultados'], 
                paralelo['resultados']
            )
        }
    
    def _verificar_resultados_iguais(self, resultados1: Dict[str, Any], resultados2: Dict[str, Any]) -> bool:
        """Verifica se os resultados são iguais"""
        if set(resultados1.keys()) != set(resultados2.keys()):
            return False
        
        for symbol in resultados1:
            if resultados1[symbol] != resultados2[symbol]:
                return False
        
        return True
    
    def exibir_comparacao(self, comparacao: Dict[str, Any]):
        """Exibe comparação formatada"""
        print("\n" + "="*80)
        print("📊 COMPARAÇÃO: SEQUENCIAL vs PARALELO")
        print("="*80)
        print(f"📈 Número de pares: {comparacao['num_pares']}")
        print(f"⏱️  Tempo sequencial: {comparacao['tempo_sequencial']:.2f}s")
        print(f"⚡ Tempo paralelo: {comparacao['tempo_paralelo']:.2f}s")
        print(f"🚀 Melhoria: {comparacao['melhoria_percentual']:+.1f}%")
        print(f"📊 Speedup: {comparacao['speedup']:.1f}x")
        print(f"✅ Resultados iguais: {'Sim' if comparacao['resultados_iguais'] else 'Não'}")
        
        if comparacao['melhoria_percentual'] > 0:
            print("🎉 Processamento paralelo é mais rápido!")
        else:
            print("⚠️  Processamento sequencial foi mais rápido")
        
        print("="*80)
    
    def executar_teste_completo(self, num_pares: int = 5) -> Dict[str, Any]:
        """Executa teste completo de comparação"""
        print("🚀 INICIANDO TESTE DE PROCESSAMENTO PARALELO")
        print("="*60)
        
        # Gerar dados
        pares_dados = self.gerar_dados_multiplos_pares(num_pares)
        
        # Teste sequencial
        resultado_sequencial = self.teste_sequencial(pares_dados)
        
        # Teste paralelo
        resultado_paralelo = self.teste_paralelo(pares_dados)
        
        # Comparar resultados
        comparacao = self.comparar_resultados(resultado_sequencial, resultado_paralelo)
        
        # Exibir resultados
        self.exibir_comparacao(comparacao)
        
        # Exibir métricas
        print("\n📊 MÉTRICAS DO SISTEMA:")
        self.analisador_paralelo.exibir_metricas()
        
        return {
            'sequencial': resultado_sequencial,
            'paralelo': resultado_paralelo,
            'comparacao': comparacao
        }
    
    def salvar_resultados(self, resultados: Dict[str, Any], arquivo: str = "resultados_paralelo.json"):
        """Salva resultados em arquivo JSON"""
        dados_export = {
            'timestamp': time.time(),
            'resultados': resultados
        }
        
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_export, f, indent=2, ensure_ascii=False)
            logger.info(f"📁 Resultados salvos em {arquivo}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {e}")

def main():
    """Função principal do teste"""
    teste = TesteProcessamentoParalelo()
    
    try:
        # Executar teste completo
        resultados = teste.executar_teste_completo(num_pares=5)
        
        # Salvar resultados
        teste.salvar_resultados(resultados)
        
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        raise
    finally:
        # Limpar recursos
        teste.analisador_paralelo.shutdown()

if __name__ == "__main__":
    main() 