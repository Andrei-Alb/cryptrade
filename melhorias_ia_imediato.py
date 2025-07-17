#!/usr/bin/env python3
"""
Melhorias Imediatas para IA - Baseado na Análise de Performance
Implementa correções urgentes identificadas na análise
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MelhoriasIA:
    """Implementa melhorias imediatas na IA baseado na análise"""
    
    def __init__(self, db_path: str = "dados/trading.db"):
        self.db_path = db_path
    
    def analisar_problemas(self) -> Dict[str, Any]:
        """Analisa problemas atuais da IA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estatísticas gerais
            cursor.execute("""
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'fechada' THEN 1 ELSE 0 END) as fechadas,
                       SUM(CASE WHEN lucro_prejuizo > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN lucro_prejuizo < 0 THEN 1 ELSE 0 END) as losses,
                       AVG(lucro_prejuizo) as pnl_medio
                FROM ordens_dinamicas 
                WHERE status = 'fechada'
            """)
            
            stats = cursor.fetchone()
            
            # Análise por par
            cursor.execute("""
                SELECT symbol, 
                       COUNT(*) as total,
                       SUM(CASE WHEN lucro_prejuizo > 0 THEN 1 ELSE 0 END) as wins,
                       AVG(lucro_prejuizo) as pnl_medio
                FROM ordens_dinamicas 
                WHERE status = 'fechada'
                GROUP BY symbol
            """)
            
            stats_por_par = cursor.fetchall()
            
            # Análise de confiança
            cursor.execute("""
                SELECT AVG(confianca_ia) as confianca_media,
                       COUNT(*) as total_decisoes
                FROM aprendizado_autonomo
            """)
            
            confianca_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_ordens': stats[0],
                'ordens_fechadas': stats[1],
                'wins': stats[2],
                'losses': stats[3],
                'pnl_medio': stats[4],
                'win_rate': stats[2] / stats[1] if stats[1] > 0 else 0,
                'stats_por_par': stats_por_par,
                'confianca_media': confianca_stats[0],
                'total_decisoes': confianca_stats[1]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar problemas: {e}")
            return {}
    
    def implementar_melhorias(self):
        """Implementa melhorias baseadas na análise"""
        try:
            problemas = self.analisar_problemas()
            
            logger.info("🔧 IMPLEMENTANDO MELHORIAS IMEDIATAS")
            logger.info("=" * 50)
            
            # 1. Ajustar parâmetros baseado na performance
            win_rate = problemas.get('win_rate', 0)
            pnl_medio = problemas.get('pnl_medio', 0)
            
            logger.info(f"📊 Performance Atual:")
            logger.info(f"   Win Rate: {win_rate:.1%}")
            logger.info(f"   PnL Médio: {pnl_medio:.4f}")
            logger.info(f"   Confiança Média: {problemas.get('confianca_media', 0):.3f}")
            
            # 2. Ajustar configurações baseado na performance
            self._ajustar_configuracoes(win_rate, pnl_medio)
            
            # 3. Implementar filtros de qualidade
            self._implementar_filtros_qualidade()
            
            # 4. Melhorar gestão de risco
            self._melhorar_gestao_risco()
            
            # 5. Implementar pausa inteligente
            self._implementar_pausa_inteligente()
            
            logger.info("✅ Melhorias implementadas com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao implementar melhorias: {e}")
    
    def _ajustar_configuracoes(self, win_rate: float, pnl_medio: float):
        """Ajusta configurações baseado na performance"""
        try:
            # Se win rate muito baixo, ser mais conservador
            if win_rate < 0.2:
                logger.info("🎯 Ajustando para modo conservador (win rate < 20%)")
                
                # Reduzir quantidade
                self._atualizar_config('quantidade_padrao', 0.0005)  # Reduzir pela metade
                
                # Aumentar confiança mínima
                self._atualizar_config('confianca_minima', 0.7)
                
                # Reduzir stop loss
                self._atualizar_config('stop_loss_padrao', -1.5)
                
                # Aumentar take profit
                self._atualizar_config('take_profit_padrao', 4.0)
            
            # Se PnL negativo, reduzir exposição
            if pnl_medio < 0:
                logger.info("⚠️ Reduzindo exposição (PnL negativo)")
                
                # Reduzir máximo de ordens simultâneas
                self._atualizar_config('max_ordens_simultaneas', 2)
                
                # Aumentar tempo entre ordens
                self._atualizar_config('tempo_minimo_entre_ordens', 30)
            
        except Exception as e:
            logger.error(f"❌ Erro ao ajustar configurações: {e}")
    
    def _implementar_filtros_qualidade(self):
        """Implementa filtros de qualidade de sinal"""
        try:
            logger.info("🔍 Implementando filtros de qualidade")
            
            # Criar tabela de filtros
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS filtros_qualidade (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    filtro_tipo TEXT NOT NULL,
                    parametros TEXT NOT NULL,
                    ativo BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Inserir filtros básicos
            filtros = [
                ('confianca_minima', '0.6'),
                ('rsi_minimo', '20'),
                ('rsi_maximo', '80'),
                ('volatilidade_maxima', '0.05'),
                ('tendencia_requerida', 'alta,baixa')
            ]
            
            for filtro_tipo, parametros in filtros:
                cursor.execute("""
                    INSERT OR REPLACE INTO filtros_qualidade (filtro_tipo, parametros)
                    VALUES (?, ?)
                """, (filtro_tipo, parametros))
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Filtros de qualidade implementados")
            
        except Exception as e:
            logger.error(f"❌ Erro ao implementar filtros: {e}")
    
    def _melhorar_gestao_risco(self):
        """Melhora a gestão de risco"""
        try:
            logger.info("🛡️ Melhorando gestão de risco")
            
            # Criar tabela de gestão de risco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gestao_risco (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    max_drawdown_diario REAL DEFAULT 0.05,
                    max_exposicao_par REAL DEFAULT 0.3,
                    stop_loss_dinamico BOOLEAN DEFAULT TRUE,
                    take_profit_dinamico BOOLEAN DEFAULT TRUE,
                    pausa_apos_losses INTEGER DEFAULT 3
                )
            """)
            
            # Inserir configurações de risco
            cursor.execute("""
                INSERT OR REPLACE INTO gestao_risco 
                (max_drawdown_diario, max_exposicao_par, pausa_apos_losses)
                VALUES (0.03, 0.2, 5)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Gestão de risco melhorada")
            
        except Exception as e:
            logger.error(f"❌ Erro ao melhorar gestão de risco: {e}")
    
    def _implementar_pausa_inteligente(self):
        """Implementa pausa inteligente baseada na performance"""
        try:
            logger.info("⏸️ Implementando pausa inteligente")
            
            # Criar tabela de pausas
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pausas_inteligentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    par TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    duracao_minutos INTEGER DEFAULT 30,
                    ativa BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Pausa inteligente implementada")
            
        except Exception as e:
            logger.error(f"❌ Erro ao implementar pausa inteligente: {e}")
    
    def _atualizar_config(self, chave: str, valor: Any):
        """Atualiza configuração no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabela se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes_ajustadas (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                INSERT OR REPLACE INTO configuracoes_ajustadas 
                (chave, valor, timestamp) VALUES (?, ?, ?)
            """, (chave, str(valor), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"⚙️ Configuração atualizada: {chave} = {valor}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar configuração: {e}")

def main():
    """Função principal"""
    try:
        logger.info("🚀 INICIANDO MELHORIAS IMEDIATAS DA IA")
        
        melhorias = MelhoriasIA()
        
        # Analisar problemas
        problemas = melhorias.analisar_problemas()
        
        logger.info("📊 ANÁLISE ATUAL:")
        logger.info(f"   Total de ordens: {problemas.get('total_ordens', 0)}")
        logger.info(f"   Win Rate: {problemas.get('win_rate', 0):.1%}")
        logger.info(f"   PnL Médio: {problemas.get('pnl_medio', 0):.4f}")
        logger.info(f"   Confiança Média: {problemas.get('confianca_media', 0):.3f}")
        
        # Implementar melhorias
        melhorias.implementar_melhorias()
        
        logger.info("🎉 Melhorias concluídas!")
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main() 