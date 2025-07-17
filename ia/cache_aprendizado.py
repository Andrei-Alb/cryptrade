"""
Sistema de Cache de Aprendizado
Otimiza consultas ao banco de dados e melhora performance do sistema de aprendizado
"""

import json
import hashlib
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import OrderedDict

logger = logging.getLogger(__name__)

class CacheAprendizado:
    """Sistema de cache para recomendações de aprendizado"""
    
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        """
        Inicializa cache de aprendizado
        
        Args:
            ttl: Tempo de vida em segundos (padrão: 5 minutos)
            max_size: Tamanho máximo do cache
        """
        self.ttl = ttl
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        
        logger.info(f"[CACHE] Cache de aprendizado inicializado (TTL: {ttl}s, Max: {max_size})")
    
    def _gerar_chave(self, symbol: str, contexto: Dict[str, Any]) -> str:
        """Gera chave única para o cache"""
        # Normalizar contexto para chave consistente
        contexto_normalizado = {
            'rsi': round(contexto.get('rsi', 50.0), 1),
            'tendencia': contexto.get('tendencia', 'lateral'),
            'volatilidade': round(contexto.get('volatilidade', 0.02), 3),
            'preco': round(contexto.get('preco_atual', 0.0), 2)
        }
        
        dados_chave = {
            'symbol': symbol,
            'contexto': contexto_normalizado
        }
        
        return hashlib.md5(json.dumps(dados_chave, sort_keys=True).encode()).hexdigest()
    
    def obter_recomendacao(self, symbol: str, contexto: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Obtém recomendação do cache ou retorna None se não encontrada
        
        Args:
            symbol: Símbolo do ativo
            contexto: Contexto atual do mercado
            
        Returns:
            Recomendação em cache ou None
        """
        self.stats['total_requests'] += 1
        chave = self._gerar_chave(symbol, contexto)
        
        # Limpar cache expirado
        self._limpar_expirados()
        
        if chave in self.cache:
            timestamp, recomendacao = self.cache[chave]
            if time.time() - timestamp < self.ttl:
                # Mover para o final (LRU)
                self.cache.move_to_end(chave)
                self.stats['hits'] += 1
                logger.debug(f"[CACHE] Hit para {symbol}")
                return recomendacao
            else:
                # Remover expirado
                del self.cache[chave]
        
        self.stats['misses'] += 1
        logger.debug(f"[CACHE] Miss para {symbol}")
        return None
    
    def salvar_recomendacao(self, symbol: str, contexto: Dict[str, Any], 
                          recomendacao: Dict[str, Any]) -> None:
        """
        Salva recomendação no cache
        
        Args:
            symbol: Símbolo do ativo
            contexto: Contexto do mercado
            recomendacao: Recomendação a ser cacheada
        """
        chave = self._gerar_chave(symbol, contexto)
        timestamp = time.time()
        
        # Verificar se cache está cheio
        if len(self.cache) >= self.max_size:
            # Remover item mais antigo (LRU)
            self.cache.popitem(last=False)
            self.stats['evictions'] += 1
        
        # Adicionar nova entrada
        self.cache[chave] = (timestamp, recomendacao)
        logger.debug(f"[CACHE] Recomendação salva para {symbol}")
    
    def _limpar_expirados(self) -> None:
        """Remove entradas expiradas do cache"""
        agora = time.time()
        expirados = []
        
        for chave, (timestamp, _) in self.cache.items():
            if agora - timestamp > self.ttl:
                expirados.append(chave)
        
        for chave in expirados:
            del self.cache[chave]
        
        if expirados:
            logger.debug(f"[CACHE] {len(expirados)} entradas expiradas removidas")
    
    def limpar_cache(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        logger.info("[CACHE] Cache limpo")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        hit_rate = (self.stats['hits'] / max(1, self.stats['total_requests'])) * 100
        
        return {
            'tamanho_atual': len(self.cache),
            'tamanho_maximo': self.max_size,
            'ttl': self.ttl,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'total_requests': self.stats['total_requests'],
            'hit_rate': hit_rate,
            'utilizacao': (len(self.cache) / self.max_size) * 100
        }
    
    def exibir_estatisticas(self) -> None:
        """Exibe estatísticas formatadas"""
        stats = self.obter_estatisticas()
        
        print("\n" + "="*50)
        print("📊 CACHE DE APRENDIZADO - ESTATÍSTICAS")
        print("="*50)
        print(f"📦 Tamanho: {stats['tamanho_atual']}/{stats['tamanho_maximo']} ({stats['utilizacao']:.1f}%)")
        print(f"⏰ TTL: {stats['ttl']}s")
        print(f"🎯 Hit Rate: {stats['hit_rate']:.1f}%")
        print(f"✅ Hits: {stats['hits']}")
        print(f"❌ Misses: {stats['misses']}")
        print(f"🗑️  Evictions: {stats['evictions']}")
        print(f"📈 Total Requests: {stats['total_requests']}")
        print("="*50)
    
    def exportar_cache(self, arquivo: str = "cache_aprendizado.json") -> bool:
        """Exporta cache para arquivo JSON"""
        try:
            dados_export = {
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'ttl': self.ttl,
                    'max_size': self.max_size
                },
                'stats': self.stats,
                'cache': dict()
            }
            
            # Converter cache para formato serializável
            for chave, (timestamp, recomendacao) in self.cache.items():
                dados_export['cache'][str(chave)] = {
                    'timestamp': timestamp,
                    'recomendacao': recomendacao
                }
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_export, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[CACHE] Cache exportado para {arquivo}")
            return True
        except Exception as e:
            logger.error(f"[CACHE] Erro ao exportar cache: {e}")
            return False 