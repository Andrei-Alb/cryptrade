"""
Sistema de Métricas da IA - Monitoramento de Performance
Monitora tempo de inferência, cache hit rate, timeouts e outras métricas
"""

import time
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
from collections import deque

logger = logging.getLogger(__name__)

class MetricasIA:
    """Sistema de métricas em tempo real para monitorar performance da IA"""
    
    def __init__(self, janela_tempo: int = 100):
        """
        Inicializa sistema de métricas
        
        Args:
            janela_tempo: Número de inferências para calcular médias
        """
        self.janela_tempo = janela_tempo
        
        # Métricas de tempo
        self.tempos_inferencia: deque = deque(maxlen=janela_tempo)
        self.tempos_cache: deque = deque(maxlen=janela_tempo)
        
        # Contadores
        self.total_inferencias = 0
        self.timeouts = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.erros = 0
        
        # Histórico de performance
        self.historico_performance: List[Dict[str, Any]] = []
        
        logger.info(f"[MÉTRICAS] Sistema de métricas inicializado (janela: {janela_tempo})")
    
    def registrar_inferencia(self, tempo: float, timeout: bool = False, 
                           cache_hit: bool = False, erro: bool = False):
        """
        Registra uma inferência para métricas
        
        Args:
            tempo: Tempo de inferência em segundos
            timeout: Se houve timeout
            cache_hit: Se foi cache hit
            erro: Se houve erro
        """
        self.total_inferencias += 1
        
        if timeout:
            self.timeouts += 1
            logger.warning(f"[MÉTRICAS] Timeout registrado (total: {self.timeouts})")
        elif erro:
            self.erros += 1
            logger.error(f"[MÉTRICAS] Erro registrado (total: {self.erros})")
        else:
            # Registrar tempo apenas se não foi timeout/erro
            self.tempos_inferencia.append(tempo)
            
            if cache_hit:
                self.cache_hits += 1
                self.tempos_cache.append(0.001)  # Tempo mínimo para cache
            else:
                self.cache_misses += 1
        
        # Registrar no histórico a cada 10 inferências
        if self.total_inferencias % 10 == 0:
            self._registrar_historico()
    
    def _registrar_historico(self):
        """Registra snapshot atual no histórico"""
        snapshot = {
            'timestamp': datetime.now(),
            'total_inferencias': self.total_inferencias,
            'tempo_medio': self.obter_tempo_medio(),
            'timeout_rate': self.obter_timeout_rate(),
            'cache_hit_rate': self.obter_cache_hit_rate(),
            'erro_rate': self.obter_erro_rate(),
            'throughput': self.obter_throughput()
        }
        self.historico_performance.append(snapshot)
        
        # Manter apenas últimos 1000 registros
        if len(self.historico_performance) > 1000:
            self.historico_performance = self.historico_performance[-1000:]
    
    def obter_tempo_medio(self) -> float:
        """Retorna tempo médio de inferência"""
        if not self.tempos_inferencia:
            return 0.0
        return float(np.mean(list(self.tempos_inferencia)))
    
    def obter_tempo_medio_cache(self) -> float:
        """Retorna tempo médio quando usa cache"""
        if not self.tempos_cache:
            return 0.0
        return float(np.mean(list(self.tempos_cache)))
    
    def obter_timeout_rate(self) -> float:
        """Retorna taxa de timeout"""
        if self.total_inferencias == 0:
            return 0.0
        return self.timeouts / self.total_inferencias
    
    def obter_cache_hit_rate(self) -> float:
        """Retorna taxa de cache hit"""
        total_cache = self.cache_hits + self.cache_misses
        if total_cache == 0:
            return 0.0
        return self.cache_hits / total_cache
    
    def obter_erro_rate(self) -> float:
        """Retorna taxa de erro"""
        if self.total_inferencias == 0:
            return 0.0
        return self.erros / self.total_inferencias
    
    def obter_throughput(self) -> float:
        """Retorna throughput (decisões por minuto)"""
        if not self.tempos_inferencia:
            return 0.0
        
        tempo_medio = self.obter_tempo_medio()
        if tempo_medio == 0:
            return 0.0
        
        return 60.0 / tempo_medio  # decisões por minuto
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas completas"""
        return {
            'total_inferencias': self.total_inferencias,
            'tempo_medio': self.obter_tempo_medio(),
            'tempo_medio_cache': self.obter_tempo_medio_cache(),
            'timeout_rate': self.obter_timeout_rate(),
            'cache_hit_rate': self.obter_cache_hit_rate(),
            'erro_rate': self.obter_erro_rate(),
            'throughput': self.obter_throughput(),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'timeouts': self.timeouts,
            'erros': self.erros
        }
    
    def verificar_alertas(self) -> List[str]:
        """Verifica se há alertas baseados nas métricas"""
        alertas = []
        stats = self.obter_estatisticas()
        
        # Alertas baseados no PRD
        if stats['timeout_rate'] > 0.10:  # > 10%
            alertas.append(f"🔴 Timeout rate alto: {stats['timeout_rate']:.1%}")
        
        if stats['tempo_medio'] > 20:  # > 20s
            alertas.append(f"🟡 Tempo médio alto: {stats['tempo_medio']:.1f}s")
        
        if stats['cache_hit_rate'] < 0.30:  # < 30%
            alertas.append(f"🟢 Cache hit rate baixo: {stats['cache_hit_rate']:.1%}")
        
        if stats['erro_rate'] > 0.05:  # > 5%
            alertas.append(f"🔴 Taxa de erro alta: {stats['erro_rate']:.1%}")
        
        return alertas
    
    def exibir_estatisticas(self):
        """Exibe estatísticas formatadas"""
        stats = self.obter_estatisticas()
        alertas = self.verificar_alertas()
        
        print("\n" + "="*60)
        print("📊 MÉTRICAS DE PERFORMANCE DA IA")
        print("="*60)
        print(f"🕐 Tempo médio: {stats['tempo_medio']:.2f}s")
        print(f"⚡ Throughput: {stats['throughput']:.1f} decisões/min")
        print(f"🎯 Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"⏰ Timeout rate: {stats['timeout_rate']:.1%}")
        print(f"❌ Erro rate: {stats['erro_rate']:.1%}")
        print(f"📈 Total inferências: {stats['total_inferencias']}")
        print("-"*60)
        
        if alertas:
            print("🚨 ALERTAS:")
            for alerta in alertas:
                print(f"  {alerta}")
        else:
            print("✅ Todas as métricas estão dentro dos parâmetros normais")
        
        print("="*60)
    
    def resetar_metricas(self):
        """Reseta todas as métricas"""
        self.tempos_inferencia.clear()
        self.tempos_cache.clear()
        self.total_inferencias = 0
        self.timeouts = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.erros = 0
        self.historico_performance.clear()
        logger.info("[MÉTRICAS] Métricas resetadas")
    
    def exportar_historico(self, arquivo: str = "metricas_ia.json"):
        """Exporta histórico de performance para JSON"""
        try:
            import json
            dados_export = []
            for snapshot in self.historico_performance:
                dados_export.append({
                    'timestamp': snapshot['timestamp'].isoformat(),
                    'total_inferencias': snapshot['total_inferencias'],
                    'tempo_medio': snapshot['tempo_medio'],
                    'timeout_rate': snapshot['timeout_rate'],
                    'cache_hit_rate': snapshot['cache_hit_rate'],
                    'erro_rate': snapshot['erro_rate'],
                    'throughput': snapshot['throughput']
                })
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_export, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[MÉTRICAS] Histórico exportado para {arquivo}")
            return True
        except Exception as e:
            logger.error(f"[MÉTRICAS] Erro ao exportar histórico: {e}")
            return False 