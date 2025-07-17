"""
Analisador Paralelo de IA
Processa múltiplos pares de trading simultaneamente para melhor performance
"""

import asyncio
import concurrent.futures
import time
import logging
from typing import Dict, Any, List, Optional
from .decisor import Decisor
from .metricas_ia import MetricasIA

logger = logging.getLogger(__name__)

class AnalisadorParalelo:
    """Sistema de análise paralela para múltiplos pares"""
    
    def __init__(self, max_workers: int = 3):
        """
        Inicializa analisador paralelo
        
        Args:
            max_workers: Número máximo de workers paralelos
        """
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.decisor = Decisor()
        self.metricas = MetricasIA()
        
        logger.info(f"[PARALELO] Analisador paralelo inicializado com {max_workers} workers")
    
    def analisar_pares_simultaneamente(self, pares_dados: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa múltiplos pares simultaneamente
        
        Args:
            pares_dados: Dicionário com {symbol: dados_mercado}
            
        Returns:
            Dicionário com {symbol: decisao}
        """
        inicio_total = time.time()
        resultados = {}
        
        logger.info(f"[PARALELO] Iniciando análise de {len(pares_dados)} pares")
        
        # Criar tasks para cada par
        futures = {}
        for symbol, dados in pares_dados.items():
            future = self.executor.submit(self._analisar_par, symbol, dados)
            futures[future] = symbol
        
        # Coletar resultados
        for future in concurrent.futures.as_completed(futures):
            symbol = futures[future]
            try:
                decisao = future.result()
                resultados[symbol] = decisao
                logger.info(f"[PARALELO] {symbol}: análise concluída")
            except Exception as e:
                logger.error(f"[PARALELO] Erro ao analisar {symbol}: {e}")
                resultados[symbol] = None
        
        tempo_total = time.time() - inicio_total
        logger.info(f"[PARALELO] Análise de {len(pares_dados)} pares concluída em {tempo_total:.2f}s")
        
        return resultados
    
    def _analisar_par(self, symbol: str, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analisa um par específico (método interno para threads)
        
        Args:
            symbol: Símbolo do par
            dados: Dados de mercado
            
        Returns:
            Decisão da IA ou None
        """
        try:
            inicio = time.time()
            
            # Adicionar symbol aos dados se não existir
            if 'symbol' not in dados:
                dados['symbol'] = symbol
            
            # Analisar com decisor
            decisao = self.decisor.analisar_mercado(dados)
            
            tempo = time.time() - inicio
            logger.debug(f"[PARALELO] {symbol}: {tempo:.3f}s")
            
            return decisao
            
        except Exception as e:
            logger.error(f"[PARALELO] Erro ao analisar {symbol}: {e}")
            return None
    
    async def analisar_pares_async(self, pares_dados: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Versão assíncrona da análise paralela
        
        Args:
            pares_dados: Dicionário com {symbol: dados_mercado}
            
        Returns:
            Dicionário com {symbol: decisao}
        """
        inicio_total = time.time()
        
        logger.info(f"[PARALELO] Iniciando análise assíncrona de {len(pares_dados)} pares")
        
        # Criar tasks assíncronas
        tasks = []
        for symbol, dados in pares_dados.items():
            task = asyncio.create_task(self._analisar_par_async(symbol, dados))
            tasks.append((symbol, task))
        
        # Executar todas as tasks
        resultados = {}
        for symbol, task in tasks:
            try:
                decisao = await task
                resultados[symbol] = decisao
                logger.info(f"[PARALELO] {symbol}: análise assíncrona concluída")
            except Exception as e:
                logger.error(f"[PARALELO] Erro na análise assíncrona de {symbol}: {e}")
                resultados[symbol] = None
        
        tempo_total = time.time() - inicio_total
        logger.info(f"[PARALELO] Análise assíncrona de {len(pares_dados)} pares concluída em {tempo_total:.2f}s")
        
        return resultados
    
    async def _analisar_par_async(self, symbol: str, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analisa um par de forma assíncrona
        
        Args:
            symbol: Símbolo do par
            dados: Dados de mercado
            
        Returns:
            Decisão da IA ou None
        """
        try:
            inicio = time.time()
            
            # Adicionar symbol aos dados se não existir
            if 'symbol' not in dados:
                dados['symbol'] = symbol
            
            # Executar análise em thread pool para não bloquear
            loop = asyncio.get_event_loop()
            decisao = await loop.run_in_executor(
                self.executor, 
                self.decisor.analisar_mercado, 
                dados
            )
            
            tempo = time.time() - inicio
            logger.debug(f"[PARALELO] {symbol} (async): {tempo:.3f}s")
            
            return decisao
            
        except Exception as e:
            logger.error(f"[PARALELO] Erro na análise assíncrona de {symbol}: {e}")
            return None
    
    def obter_metricas(self) -> Dict[str, Any]:
        """Retorna métricas do analisador paralelo"""
        return {
            'max_workers': self.max_workers,
            'metricas_ia': self.metricas.obter_estatisticas(),
            'metricas_decisor': self.decisor.obter_metricas()
        }
    
    def exibir_metricas(self) -> None:
        """Exibe métricas formatadas"""
        metricas = self.obter_metricas()
        
        print("\n" + "="*60)
        print("📊 ANALISADOR PARALELO - ESTATÍSTICAS")
        print("="*60)
        print(f"🔧 Workers: {metricas['max_workers']}")
        print(f"📈 Métricas IA:")
        print(f"   Tempo médio: {metricas['metricas_ia']['tempo_medio']:.2f}s")
        print(f"   Throughput: {metricas['metricas_ia']['throughput']:.1f} decisões/min")
        print(f"   Cache hit rate: {metricas['metricas_ia']['cache_hit_rate']:.1%}")
        print("="*60)
    
    def shutdown(self) -> None:
        """Desliga o executor de threads"""
        self.executor.shutdown(wait=True)
        logger.info("[PARALELO] Executor de threads desligado") 