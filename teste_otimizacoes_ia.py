#!/usr/bin/env python3
"""
Teste de Validação das Otimizações da IA
Compara performance antes e depois das otimizações
"""

import time
import json
import logging
from typing import Dict, Any, List
from ia.decisor import Decisor
from ia.metricas_ia import MetricasIA

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesteOtimizacoesIA:
    """Teste para validar otimizações da IA"""
    
    def __init__(self):
        self.decisor = Decisor()
        self.metricas = MetricasIA()
        
    def gerar_dados_teste(self) -> List[Dict[str, Any]]:
        """Gera dados de teste variados"""
        dados_teste = []
        
        # Cenários diferentes para testar cache e performance
        cenarios = [
            # RSI baixo - tendência compra
            {
                'symbol': 'BTCUSDT',
                'rsi': 25.5,
                'tendencia': 'alta',
                'volatilidade': 0.025,
                'preco_atual': 45000.0,
                'volume_24h': 2500000000,
                'volume_1h': 150000000
            },
            # RSI alto - tendência venda
            {
                'symbol': 'ETHUSDT',
                'rsi': 78.2,
                'tendencia': 'baixa',
                'volatilidade': 0.035,
                'preco_atual': 2800.0,
                'volume_24h': 1800000000,
                'volume_1h': 95000000
            },
            # RSI neutro - lateral
            {
                'symbol': 'BTCUSDT',
                'rsi': 52.1,
                'tendencia': 'lateral',
                'volatilidade': 0.015,
                'preco_atual': 44500.0,
                'volume_24h': 2200000000,
                'volume_1h': 120000000
            },
            # Cenário extremo - alta volatilidade
            {
                'symbol': 'ETHUSDT',
                'rsi': 35.8,
                'tendencia': 'alta',
                'volatilidade': 0.080,
                'preco_atual': 2750.0,
                'volume_24h': 3000000000,
                'volume_1h': 200000000
            }
        ]
        
        # Repetir cenários para testar cache
        for i in range(3):  # 3 iterações por cenário
            for cenario in cenarios:
                dados_teste.append(cenario.copy())
        
        return dados_teste
    
    def executar_teste_performance(self, num_iteracoes: int = 20) -> Dict[str, Any]:
        """Executa teste de performance"""
        logger.info(f"🚀 Iniciando teste de performance com {num_iteracoes} iterações")
        
        dados_teste = self.gerar_dados_teste()
        resultados = []
        
        # Resetar métricas
        self.metricas.resetar_metricas()
        
        for i in range(num_iteracoes):
            logger.info(f"📊 Iteração {i+1}/{num_iteracoes}")
            
            for dados in dados_teste:
                inicio = time.time()
                
                # Analisar dados
                decisao = self.decisor.analisar_mercado(dados)
                
                tempo_total = time.time() - inicio
                
                resultado = {
                    'iteracao': i + 1,
                    'symbol': dados['symbol'],
                    'tempo': tempo_total,
                    'decisao': decisao,
                    'timestamp': time.time()
                }
                
                resultados.append(resultado)
                
                # Pequena pausa entre análises
                time.sleep(0.1)
        
        # Calcular estatísticas
        tempos = [r['tempo'] for r in resultados if r['decisao'] is not None]
        timeouts = [r for r in resultados if r['decisao'] is None]
        
        estatisticas = {
            'total_analises': len(resultados),
            'analises_sucesso': len(tempos),
            'timeouts': len(timeouts),
            'tempo_medio': sum(tempos) / len(tempos) if tempos else 0,
            'tempo_min': min(tempos) if tempos else 0,
            'tempo_max': max(tempos) if tempos else 0,
            'timeout_rate': len(timeouts) / len(resultados) if resultados else 0,
            'metricas_ia': self.metricas.obter_estatisticas()
        }
        
        return estatisticas
    
    def comparar_com_baseline(self, estatisticas: Dict[str, Any]) -> Dict[str, Any]:
        """Compara com baseline esperado do PRD"""
        baseline = {
            'tempo_medio_esperado': 15.0,  # 15s máximo
            'timeout_rate_esperado': 0.05,  # 5% máximo
            'throughput_esperado': 4.0,     # 4 decisões/min
            'cache_hit_rate_esperado': 0.40  # 40% mínimo
        }
        
        metricas = estatisticas['metricas_ia']
        
        comparacao = {
            'tempo_medio': {
                'atual': metricas['tempo_medio'],
                'esperado': baseline['tempo_medio_esperado'],
                'melhoria': (baseline['tempo_medio_esperado'] - metricas['tempo_medio']) / baseline['tempo_medio_esperado'] * 100,
                'status': '✅' if metricas['tempo_medio'] <= baseline['tempo_medio_esperado'] else '❌'
            },
            'timeout_rate': {
                'atual': metricas['timeout_rate'],
                'esperado': baseline['timeout_rate_esperado'],
                'melhoria': (baseline['timeout_rate_esperado'] - metricas['timeout_rate']) / baseline['timeout_rate_esperado'] * 100,
                'status': '✅' if metricas['timeout_rate'] <= baseline['timeout_rate_esperado'] else '❌'
            },
            'throughput': {
                'atual': metricas['throughput'],
                'esperado': baseline['throughput_esperado'],
                'melhoria': (metricas['throughput'] - baseline['throughput_esperado']) / baseline['throughput_esperado'] * 100,
                'status': '✅' if metricas['throughput'] >= baseline['throughput_esperado'] else '❌'
            },
            'cache_hit_rate': {
                'atual': metricas['cache_hit_rate'],
                'esperado': baseline['cache_hit_rate_esperado'],
                'melhoria': (metricas['cache_hit_rate'] - baseline['cache_hit_rate_esperado']) / baseline['cache_hit_rate_esperado'] * 100,
                'status': '✅' if metricas['cache_hit_rate'] >= baseline['cache_hit_rate_esperado'] else '❌'
            }
        }
        
        return comparacao
    
    def exibir_resultados(self, estatisticas: Dict[str, Any], comparacao: Dict[str, Any]):
        """Exibe resultados formatados"""
        print("\n" + "="*80)
        print("🚀 RESULTADOS DO TESTE DE OTIMIZAÇÃO DA IA")
        print("="*80)
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   Total de análises: {estatisticas['total_analises']}")
        print(f"   Análises com sucesso: {estatisticas['analises_sucesso']}")
        print(f"   Timeouts: {estatisticas['timeouts']}")
        print(f"   Tempo médio: {estatisticas['tempo_medio']:.2f}s")
        print(f"   Tempo mínimo: {estatisticas['tempo_min']:.2f}s")
        print(f"   Tempo máximo: {estatisticas['tempo_max']:.2f}s")
        
        print(f"\n🎯 COMPARAÇÃO COM BASELINE:")
        for metrica, dados in comparacao.items():
            print(f"   {metrica.upper()}:")
            print(f"     Atual: {dados['atual']:.2f}")
            print(f"     Esperado: {dados['esperado']:.2f}")
            print(f"     Melhoria: {dados['melhoria']:+.1f}%")
            print(f"     Status: {dados['status']}")
        
        print(f"\n📈 MÉTRICAS DETALHADAS:")
        metricas = estatisticas['metricas_ia']
        print(f"   Throughput: {metricas['throughput']:.1f} decisões/min")
        print(f"   Cache hit rate: {metricas['cache_hit_rate']:.1%}")
        print(f"   Timeout rate: {metricas['timeout_rate']:.1%}")
        print(f"   Erro rate: {metricas['erro_rate']:.1%}")
        
        # Verificar se atingiu objetivos do PRD
        objetivos_atingidos = sum(1 for dados in comparacao.values() if dados['status'] == '✅')
        total_objetivos = len(comparacao)
        
        print(f"\n🎯 RESUMO:")
        print(f"   Objetivos atingidos: {objetivos_atingidos}/{total_objetivos}")
        
        if objetivos_atingidos == total_objetivos:
            print("   🎉 TODOS OS OBJETIVOS DO PRD FORAM ATINGIDOS!")
        else:
            print("   ⚠️  Alguns objetivos ainda precisam ser ajustados")
        
        print("="*80)
    
    def salvar_resultados(self, estatisticas: Dict[str, Any], comparacao: Dict[str, Any], arquivo: str = "resultados_otimizacao.json"):
        """Salva resultados em arquivo JSON"""
        dados_export = {
            'timestamp': time.time(),
            'estatisticas': estatisticas,
            'comparacao': comparacao
        }
        
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_export, f, indent=2, ensure_ascii=False)
            logger.info(f"📁 Resultados salvos em {arquivo}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {e}")

def main():
    """Função principal do teste"""
    print("🚀 INICIANDO TESTE DE OTIMIZAÇÕES DA IA")
    print("="*50)
    
    teste = TesteOtimizacoesIA()
    
    try:
        # Executar teste de performance
        estatisticas = teste.executar_teste_performance(num_iteracoes=10)
        
        # Comparar com baseline
        comparacao = teste.comparar_com_baseline(estatisticas)
        
        # Exibir resultados
        teste.exibir_resultados(estatisticas, comparacao)
        
        # Salvar resultados
        teste.salvar_resultados(estatisticas, comparacao)
        
        # Exibir métricas finais
        print("\n📊 MÉTRICAS FINAIS DA IA:")
        teste.decisor.exibir_metricas()
        
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        raise

if __name__ == "__main__":
    main() 