"""
Sistema de Aprendizado Inteligente para IA de Trading - VERSÃO AUTÔNOMA
Analisa resultados e permite que a IA ajuste seus próprios parâmetros
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
import statistics

class SistemaAprendizado:
    def __init__(self, db_path: str = "dados/trading.db"):
        """
        Inicializa sistema de aprendizado AUTÔNOMO
        
        Args:
            db_path: Caminho para banco de dados
        """
        self.db_path = db_path
        
        # PARÂMETROS INICIAIS (TOTALMENTE AUTÔNOMOS)
        self.parametros_atuais = {
            'threshold_confianca': 0.40, # Muito baixo para permitir aprendizado
            'threshold_confianca_alta': 0.60, # Muito baixo para permitir aprendizado
            'tempo_estagnacao': 120, # 2 minutos inicial (IA ajusta dinamicamente)
            'stop_loss_percentual': 0.15,
            'take_profit_percentual': 0.25,
            'max_ordens_consecutivas': 10, # Muito alto para permitir aprendizado
            'balanceamento_compra_venda': True,
            'aprendizado_autonomo': True,  # Habilita ajustes automáticos
            'tempo_expiracao_dinamico': True, # NOVO: IA controla tempo de expiração
            'ajuste_frequente': True  # NOVO: Ajustes mais frequentes
        }
        self.historico_ajustes: List[Dict[str, Any]] = []
        
        logger.info("🧠 Sistema de Aprendizado AUTÔNOMO inicializado")
    
    def analisar_desempenho_recente(self, dias: int = 7) -> Dict[str, Any]:
        """
        Analisa desempenho das últimas ordens
        
        Args:
            dias: Número de dias para analisar
            
        Returns:
            Análise de desempenho
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Data limite
            data_limite = datetime.now() - timedelta(days=dias)
            
            # Buscar ordens recentes
            c.execute('''
            SELECT confianca_ia, resultado, lucro_percentual, duracao_segundos, 
                   razao_fechamento, tipo, timestamp
            FROM ordens_simuladas 
            WHERE status = 'fechada' AND timestamp > ?
            ORDER BY timestamp DESC
            ''', (data_limite,))
            
            ordens = c.fetchall()
            conn.close()
            
            if not ordens:
                return {'total_ordens': 0, 'mensagem': 'Nenhuma ordem recente encontrada'}
            
            # Análise por nível de confiança
            analise_confianca = self._analisar_por_confianca(ordens)
            
            # Análise por tipo de fechamento
            analise_fechamento = self._analisar_por_fechamento(ordens)
            
            # Análise temporal
            analise_temporal = self._analisar_temporal(ordens)
            
            # Análise de lucro/perda
            analise_lucro = self._analisar_lucro(ordens)
            
            return {
                'total_ordens': len(ordens),
                'analise_confianca': analise_confianca,
                'analise_fechamento': analise_fechamento,
                'analise_temporal': analise_temporal,
                'analise_lucro': analise_lucro,
                'recomendacoes': self._gerar_recomendacoes(ordens)
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar desempenho: {e}")
            return {'erro': str(e)}
    
    def _analisar_por_confianca(self, ordens: List[tuple]) -> Dict[str, Any]:
        """Analisa desempenho por nível de confiança"""
        niveis: Dict[str, Dict[str, Any]] = {
            'baixa': {'min': 0.0, 'max': 0.5, 'ordens': []},
            'media': {'min': 0.5, 'max': 0.7, 'ordens': []},
            'alta': {'min': 0.7, 'max': 1.0, 'ordens': []}
        }
        
        for ordem in ordens:
            confianca = ordem[0]
            for nivel, config in niveis.items():
                if config['min'] <= confianca < config['max']:
                    config['ordens'].append(ordem)
                    break
        
        resultado = {}
        for nivel, config in niveis.items():
            if config['ordens']:
                wins = sum(1 for o in config['ordens'] if o[1] == 'win')
                total = len(config['ordens'])
                lucro_medio = statistics.mean([o[2] for o in config['ordens']])
                resultado[nivel] = {
                    'total': total,
                    'wins': wins,
                    'taxa_acerto': (wins / total) * 100,
                    'lucro_medio': lucro_medio
                }
        
        return resultado
    
    def _analisar_por_fechamento(self, ordens: List[tuple]) -> Dict[str, Any]:
        """Analisa desempenho por tipo de fechamento"""
        tipos: Dict[str, List[tuple]] = {}
        
        for ordem in ordens:
            razao = ordem[4]
            if 'alvo' in razao.lower():
                tipo = 'alvo'
            elif 'stop' in razao.lower():
                tipo = 'stop'
            elif 'estagnação' in razao.lower():
                tipo = 'estagnacao'
            elif 'timeout' in razao.lower():
                tipo = 'timeout'
            else:
                tipo = 'outro'
            
            if tipo not in tipos:
                tipos[tipo] = []
            tipos[tipo].append(ordem)
        
        resultado = {}
        for tipo, lista_ordens in tipos.items():
            wins = sum(1 for o in lista_ordens if o[1] == 'win')
            total = len(lista_ordens)
            lucro_medio = statistics.mean([o[2] for o in lista_ordens])
            resultado[tipo] = {
                'total': total,
                'wins': wins,
                'taxa_acerto': (wins / total) * 100,
                'lucro_medio': lucro_medio
            }
        
        return resultado
    
    def _analisar_temporal(self, ordens: List[tuple]) -> Dict[str, Any]:
        """Analisa desempenho temporal"""
        duracoes = [o[3] for o in ordens if o[3] is not None]
        
        if not duracoes:
            return {}
        
        return {
            'duracao_media': statistics.mean(duracoes),
            'duracao_mediana': statistics.median(duracoes),
            'duracao_min': min(duracoes),
            'duracao_max': max(duracoes),
            'ordens_rapidas': sum(1 for d in duracoes if d < 60),  # < 1 minuto
            'ordens_medias': sum(1 for d in duracoes if 60 <= d < 300),  # 1-5 minutos
            'ordens_lentas': sum(1 for d in duracoes if d >= 300)  # > 5 minutos
        }
    
    def _analisar_lucro(self, ordens: List[tuple]) -> Dict[str, Any]:
        """Analisa distribuição de lucros"""
        lucros = [o[2] for o in ordens if o[2] is not None]
        
        if not lucros:
            return {}
        
        wins = [l for l in lucros if l > 0]
        losses = [l for l in lucros if l <= 0]
        
        return {
            'lucro_total': sum(lucros),
            'lucro_medio': statistics.mean(lucros),
            'lucro_mediano': statistics.median(lucros),
            'lucro_max': max(lucros),
            'lucro_min': min(lucros),
            'total_wins': len(wins),
            'total_losses': len(losses),
            'lucro_medio_wins': statistics.mean(wins) if wins else 0,
            'lucro_medio_losses': statistics.mean(losses) if losses else 0,
            'maior_sequencia_losses': self._calcular_maior_sequencia_losses(ordens)
        }
    
    def _calcular_maior_sequencia_losses(self, ordens: List[tuple]) -> int:
        """Calcula maior sequência de losses consecutivos"""
        sequencia_atual = 0
        maior_sequencia = 0
        
        for ordem in ordens:
            if ordem[1] == 'loss':
                sequencia_atual += 1
                maior_sequencia = max(maior_sequencia, sequencia_atual)
            else:
                sequencia_atual = 0
        
        return maior_sequencia
    
    def _gerar_recomendacoes(self, ordens: List[tuple]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recomendacoes = []
        
        # Análise de confiança
        confianca_baixa = [o for o in ordens if o[0] < 0.5]
        confianca_alta = [o for o in ordens if o[0] >= 0.7]
        
        if confianca_baixa:
            wins_baixa = sum(1 for o in confianca_baixa if o[1] == 'win')
            taxa_baixa = (wins_baixa / len(confianca_baixa)) * 100
            if taxa_baixa < 30:
                recomendacoes.append(f"Aumentar threshold de confiança (taxa acerto baixa: {taxa_baixa:.1f}%)")
        
        if confianca_alta:
            wins_alta = sum(1 for o in confianca_alta if o[1] == 'win')
            taxa_alta = (wins_alta / len(confianca_alta)) * 100
            if taxa_alta > 70:
                recomendacoes.append(f"Manter threshold alto (taxa acerto alta: {taxa_alta:.1f}%)")
        
        # Análise de estagnação
        estagnacoes = [o for o in ordens if 'estagnação' in o[4].lower()]
        if estagnacoes:
            wins_estagnacao = sum(1 for o in estagnacoes if o[1] == 'win')
            taxa_estagnacao = (wins_estagnacao / len(estagnacoes)) * 100
            if taxa_estagnacao < 20:
                recomendacoes.append("Aumentar tempo de estagnação (muitas perdas por fechamento rápido)")
        
        # Análise de lucro
        lucros = [o[2] for o in ordens if o[2] is not None]
        if lucros:
            lucro_medio = statistics.mean(lucros)
            if lucro_medio < 0:
                recomendacoes.append("Ajustar stop loss e take profit (lucro médio negativo)")
        
        # Análise de sequência de losses
        maior_sequencia = self._calcular_maior_sequencia_losses(ordens)
        if maior_sequencia >= 5:
            recomendacoes.append(f"Implementar stop de drawdown (sequência de {maior_sequencia} losses)")
        
        return recomendacoes
    
    def ajustar_parametros_automaticamente(self) -> Dict[str, Any]:
        """
        Ajusta parâmetros automaticamente baseado no aprendizado
        """
        try:
            # Analisar desempenho recente
            analise = self.analisar_desempenho_recente(dias=3)
            
            if analise.get('total_ordens', 0) < 5:
                return {'mensagem': 'Poucas ordens para ajuste automático'}
            
            ajustes = {}
            
            # Ajustar threshold de confiança
            analise_confianca = analise.get('analise_confianca', {})
            if 'baixa' in analise_confianca:
                taxa_baixa = analise_confianca['baixa']['taxa_acerto']
                if taxa_baixa < 30:
                    novo_threshold = min(0.6, self.parametros_atuais['threshold_confianca'] + 0.1)
                    ajustes['threshold_confianca'] = novo_threshold
            
            # Ajustar tempo de estagnação
            analise_fechamento = analise.get('analise_fechamento', {})
            if 'estagnacao' in analise_fechamento:
                taxa_estagnacao = analise_fechamento['estagnacao']['taxa_acerto']
                if taxa_estagnacao < 20:
                    novo_tempo = min(600, self.parametros_atuais['tempo_estagnacao'] + 60)
                    ajustes['tempo_estagnacao'] = novo_tempo
            
            # Aplicar ajustes
            if ajustes:
                self._aplicar_ajustes(ajustes)
                return {
                    'ajustes_aplicados': ajustes,
                    'parametros_atuais': self.parametros_atuais.copy()
                }
            else:
                return {'mensagem': 'Nenhum ajuste necessário'}
                
        except Exception as e:
            logger.error(f"Erro ao ajustar parâmetros: {e}")
            return {'erro': str(e)}
    
    def ajustar_parametros_drawdown(self) -> Dict[str, Any]:
        """
        Ajusta thresholds e filtros dinamicamente durante drawdown e aprendizado contínuo.
        - Em drawdown (>=3 losses seguidos): aumenta thresholds, registra contexto.
        - Ao sair do drawdown (>=2 wins seguidos): retorna gradualmente aos thresholds normais.
        - Registra todos os ajustes e contexto no histórico.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            # Buscar últimas 7 ordens fechadas
            c.execute("SELECT resultado FROM ordens_simuladas WHERE status = 'fechada' ORDER BY timestamp_fechamento DESC LIMIT 7;")
            ultimos_resultados = [row[0] for row in c.fetchall()]
            conn.close()
            # Detectar drawdown
            sequencia_losses = 0
            sequencia_wins = 0
            for r in ultimos_resultados:
                if r == 'loss':
                    if sequencia_wins > 0:
                        break
                    sequencia_losses += 1
                elif r == 'win':
                    if sequencia_losses > 0:
                        break
                    sequencia_wins += 1
                else:
                    break
            ajustes = {}
            contexto_drawdown = False
            # Em drawdown: >=3 losses seguidos
            if sequencia_losses >= 3:
                contexto_drawdown = True
                # Thresholds mais rígidos em drawdown
                novo_threshold = 0.85
                novo_threshold_alta = 0.9
                if self.parametros_atuais['threshold_confianca'] < novo_threshold:
                    ajustes['threshold_confianca'] = novo_threshold
                if self.parametros_atuais['threshold_confianca_alta'] < novo_threshold_alta:
                    ajustes['threshold_confianca_alta'] = novo_threshold_alta
                logger.info(f"🔒 Drawdown detectado ({sequencia_losses} losses). Thresholds ajustados: confianca={novo_threshold}, confianca_alta={novo_threshold_alta}")
            # Ao sair do drawdown: >=2 wins seguidos
            elif sequencia_wins >= 2:
                # Retorno gradual aos thresholds normais
                threshold_normal = 0.8
                threshold_alta_normal = 0.85
                if self.parametros_atuais['threshold_confianca'] > threshold_normal:
                    novo_threshold = max(threshold_normal, self.parametros_atuais['threshold_confianca'] - 0.05)
                    ajustes['threshold_confianca'] = novo_threshold
                if self.parametros_atuais['threshold_confianca_alta'] > threshold_alta_normal:
                    novo_threshold_alta = max(threshold_alta_normal, self.parametros_atuais['threshold_confianca_alta'] - 0.05)
                    ajustes['threshold_confianca_alta'] = novo_threshold_alta
                logger.info(f"🟢 Fim do drawdown detectado ({sequencia_wins} wins). Thresholds retornando ao normal: confianca={threshold_normal}, confianca_alta={threshold_alta_normal}")
            # Aplicar ajustes se houver
            if ajustes:
                self._aplicar_ajustes(ajustes, contexto_drawdown=contexto_drawdown)
                return {
                    'ajustes_aplicados': ajustes,
                    'contexto_drawdown': contexto_drawdown,
                    'parametros_atuais': self.parametros_atuais.copy()
                }
            else:
                return {'mensagem': 'Nenhum ajuste necessário', 'contexto_drawdown': contexto_drawdown}
        except Exception as e:
            logger.error(f"Erro ao ajustar parâmetros em drawdown: {e}")
            return {'erro': str(e)}

    def _aplicar_ajustes(self, ajustes: Dict[str, Any], contexto_drawdown: Optional[bool]=None) -> None:
        """Aplica ajustes aos parâmetros e registra contexto de drawdown se fornecido"""
        for parametro, valor in ajustes.items():
            if parametro in self.parametros_atuais:
                valor_anterior = self.parametros_atuais[parametro]
                self.parametros_atuais[parametro] = valor
                # Registrar ajuste
                self.historico_ajustes.append({
                    'timestamp': datetime.now(),
                    'parametro': parametro,
                    'valor_anterior': valor_anterior,
                    'valor_novo': valor,
                    'razao': 'Ajuste dinâmico em drawdown' if contexto_drawdown else 'Ajuste automático baseado em aprendizado',
                    'contexto_drawdown': contexto_drawdown
                })
                logger.info(f"🔧 Ajuste dinâmico: {parametro} {valor_anterior} → {valor} | Drawdown: {contexto_drawdown}")
    
    def obter_parametros_otimizados(self) -> Dict[str, Any]:
        """Retorna parâmetros otimizados para uso na IA"""
        return self.parametros_atuais.copy()
    
    def registrar_aprendizado_ordem(self, ordem: Dict[str, Any], resultado: str, 
                                  lucro_percentual: float, dados_mercado: Dict[str, Any]) -> bool:
        """
        Registra resultado de ordem e ajusta parâmetros automaticamente
        
        Args:
            ordem: Dados da ordem
            resultado: 'win', 'loss' ou 'timeout'
            lucro_percentual: Lucro/prejuízo percentual
            dados_mercado: Dados do mercado no momento da ordem
            
        Returns:
            true se registrado com sucesso
        """
        try:
            # Registrar resultado básico
            self._registrar_resultado_basico(ordem, resultado, lucro_percentual)
            
            # Registrar análise de previsões vs resultado
            self._registrar_previsoes_vs_resultado(ordem, resultado, lucro_percentual, dados_mercado)
            
            # APRENDIZADO AUTÔNOMO - Ajustar parâmetros automaticamente
            if self.parametros_atuais['aprendizado_autonomo']:
                self._ajustar_parametros_autonomo(ordem, resultado, lucro_percentual)
            
            logger.info(f"🧠 Aprendizado registrado: resultado={resultado} (lucro_percentual={lucro_percentual:.2f}%)")
            return True          
        except Exception as e:
            logger.error(f"❌ Erro ao registrar aprendizado: {e}")
            return False
    
    def _ajustar_parametros_autonomo(self, ordem: Dict[str, Any], resultado: str, lucro_percentual: float):
        """Ajusta parâmetros automaticamente baseado no resultado (APRENDIZADO AUTÔNOMO)"""
        try:
            confianca_ia = ordem.get('confianca_ia', 0.5)      
            # Analisar últimas 20 ordens para contexto
            contexto = self._obter_contexto_recente(20)
            
            if resultado == 'win':
                # WIN - Ajustar para ser menos conservador
                if confianca_ia < 0.6:
                    # IA acertou com confiança baixa - pode ser menos conservadora
                    novo_threshold = max(0.35, self.parametros_atuais['threshold_confianca'] - 0.05)
                    self.parametros_atuais['threshold_confianca'] = novo_threshold
                    logger.info(f"🧠 WIN com confiança baixa - Reduzindo threshold para {novo_threshold:.2f}")
                
                # Se sequência de wins, ser ainda menos conservador
                if contexto['sequencia_wins'] >= 3:
                    novo_threshold = max(0.30, self.parametros_atuais['threshold_confianca'] - 0.10)
                    self.parametros_atuais['threshold_confianca'] = novo_threshold
                    logger.info(f"🧠 Sequência de {contexto['sequencia_wins']} wins - Reduzindo threshold para {novo_threshold:.2f}")
            
            elif resultado == 'loss':
                # LOSS - Ajustar para ser mais conservador
                if confianca_ia > 0.7:
                    # IA errou com confiança alta - precisa ser mais conservadora
                    novo_threshold = min(0.95, self.parametros_atuais['threshold_confianca'] + 0.10)
                    self.parametros_atuais['threshold_confianca'] = novo_threshold
                    logger.info(f"🧠 LOSS com confiança alta - Aumentando threshold para {novo_threshold:.2f}")
                
                # Se sequência de losses, ser ainda mais conservador
                if contexto['sequencia_losses'] >= 3:
                    novo_threshold = min(0.95, self.parametros_atuais['threshold_confianca'] + 0.15)
                    self.parametros_atuais['threshold_confianca'] = novo_threshold
                    logger.info(f"🧠 Sequência de {contexto['sequencia_losses']} losses - Aumentando threshold para {novo_threshold:.2f}")
            
            # Ajustar threshold de confiança alta baseado no win rate
            if contexto['win_rate'] < 0.3:  # Win rate baixo
                novo_threshold_alta = min(0.95, self.parametros_atuais['threshold_confianca_alta'] + 0.10)
                self.parametros_atuais['threshold_confianca_alta'] = novo_threshold_alta
                logger.info(f"🧠 Win rate baixo ({contexto['win_rate']:.1%}) - Aumentando threshold alta para {novo_threshold_alta:.2f}")
            
            elif contexto['win_rate'] > 0.7:  # Win rate alto
                novo_threshold_alta = max(0.50, self.parametros_atuais['threshold_confianca_alta'] - 0.10)
                self.parametros_atuais['threshold_confianca_alta'] = novo_threshold_alta
                logger.info(f"🧠 Win rate alto ({contexto['win_rate']:.1%}) - Reduzindo threshold alta para {novo_threshold_alta:.2f}")
            
            # Registrar ajuste
            self._registrar_ajuste_autonomo(ordem, resultado, contexto)
            
        except Exception as e:
            logger.error(f"❌ Erro ao ajustar parâmetros autônomos: {e}")
    
    def _obter_contexto_recente(self, num_ordens: int = 20) -> Dict[str, Any]:
        """Obtém contexto das últimas ordens para ajuste autônomo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT resultado, confianca_ia, timestamp_fechamento
                FROM ordens_dinamicas 
                WHERE status = 'fechada'
                ORDER BY timestamp_fechamento DESC 
                LIMIT ?
            """, (num_ordens,))
            
            resultados = cursor.fetchall()
            conn.close()
            
            if not resultados:
                return {
                    'win_rate': 0,
                    'sequencia_wins': 0,
                    'sequencia_losses': 0,
                    'confianca_media': 0.5,
                    'total_ordens': 0
                }
            
            # Calcular win rate
            wins = sum(1 for r in resultados if r[0] == 'win')
            win_rate = wins / len(resultados)
            
            # Calcular sequências
            sequencia_wins = 0        
            sequencia_losses = 0
            
            for resultado, _, _ in resultados:
                if resultado == 'win':
                    sequencia_wins += 1
                    sequencia_losses = 0             
                else:
                    sequencia_losses += 1
                    sequencia_wins = 0            
                break
            
            # Confiança média
            confiancas = [r[1] for r in resultados if r[1] is not None]
            confianca_media = statistics.mean(confiancas) if confiancas else 0.5      
            return {
                'win_rate': win_rate,
                'sequencia_wins': sequencia_wins,
                'sequencia_losses': sequencia_losses,
                'confianca_media': confianca_media,
                'total_ordens': len(resultados)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter contexto: {e}")
            return {
                'win_rate': 0,
                'sequencia_wins': 0,
                'sequencia_losses': 0,
                'confianca_media': 0.5          
            }
    
    def _registrar_ajuste_autonomo(self, ordem: Dict[str, Any], resultado: str, contexto: Dict[str, Any]):
        """Registra ajuste autônomo realizado"""
        try:
            ajuste = {
                'timestamp': datetime.now(),
                'order_id': ordem.get('order_id', ''),
                'resultado': resultado,
                'confianca_ia': ordem.get('confianca_ia', 0),
                'contexto': contexto,
                'parametros_antes': self.parametros_atuais.copy(),
                'motivo': f"Ajuste autônomo baseado em {resultado}"
            }
            
            self.historico_ajustes.append(ajuste)
            
            # Manter apenas últimos 100 ajustes
            if len(self.historico_ajustes) > 100:
                self.historico_ajustes = self.historico_ajustes[-100:]
            
            logger.info(f"🧠 Ajuste autônomo registrado: {ajuste['motivo']}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar ajuste autônomo: {e}")
    
    def _registrar_resultado_basico(self, ordem: Dict[str, Any], resultado: str, lucro_percentual: float):
        """Registra o resultado básico de uma ordem fechada"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
            INSERT INTO ordens_dinamicas (
                order_id, confianca_ia, resultado, lucro_percentual,
                duracao_segundos, razao_fechamento, dados_mercado, timestamp_fechamento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ordem.get('order_id', ''),
                ordem.get('confianca_ia', 0.0),
                resultado,
                lucro_percentual,
                ordem.get('duracao_segundos', 0),
                ordem.get('razao_fechamento', ''),
                json.dumps(ordem.get('dados_mercado', {})),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📚 Resultado básico registrado para ordem {ordem.get('order_id', '')}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar resultado básico: {e}")
    
    def _registrar_previsoes_vs_resultado(self, ordem: Dict[str, Any], resultado: str, 
                                        lucro_percentual: float, dados_mercado: Dict[str, Any]) -> None:
        """Registra análise de previsões vs resultado real"""
        try:
            previsoes = ordem.get('previsoes_ia', {})
            if not previsoes:
                return
            
            preco_fechamento = dados_mercado.get('preco_atual', 0)
            preco_entrada = ordem.get('preco_entrada', 0)
            
            if preco_fechamento == 0 or preco_entrada == 0:
                return
            
            # Analisar precisão das previsões
            analise_precisao = {
                'order_id': ordem.get('order_id', ''),
                'target_previsto': previsoes.get('target'),
                'stop_previsto': previsoes.get('stop_loss'),
                'preco_entrada': preco_entrada,
                'preco_fechamento': preco_fechamento,
                'resultado_real': resultado,
                'lucro_real': lucro_percentual,
                'precisao_target': None,
                'precisao_stop': None,
                'cenarios_acertados': [],
                'timestamp': datetime.now()
            }
            
            # Verificar precisão do target
            target = previsoes.get('target')
            if target:
                if ordem.get('tipo_ordem') == 'compra':
                    if preco_fechamento >= target:
                        analise_precisao['precisao_target'] = 'acerto'
                    else:
                        analise_precisao['precisao_target'] = 'erro'
                else:  # venda
                    if preco_fechamento <= target:
                        analise_precisao['precisao_target'] = 'acerto'
                    else:
                        analise_precisao['precisao_target'] = 'erro'
            
            # Verificar precisão do stop loss
            stop_loss = previsoes.get('stop_loss')
            if stop_loss:
                if ordem.get('tipo_ordem') == 'compra':
                    if preco_fechamento <= stop_loss:
                        analise_precisao['precisao_stop'] = 'acerto'
                    else:
                        analise_precisao['precisao_stop'] = 'erro'
                else:  # venda
                    if preco_fechamento >= stop_loss:
                        analise_precisao['precisao_stop'] = 'acerto'
                    else:
                        analise_precisao['precisao_stop'] = 'erro'
            
            # Verificar cenários
            cenarios = previsoes.get('cenarios', {})
            if cenarios:
                if resultado == 'win' and cenarios.get('sair_lucro'):
                    analise_precisao['cenarios_acertados'].append('sair_lucro')
                elif resultado == 'loss' and cenarios.get('sair_perda'):
                    analise_precisao['cenarios_acertados'].append('sair_perda')
                elif lucro_percentual > -0.5 and cenarios.get('manter'):
                    analise_precisao['cenarios_acertados'].append('manter')
            
            # Salvar análise no banco
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Criar tabela se não existir
            c.execute('''
            CREATE TABLE IF NOT EXISTS analise_previsoes_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                target_previsto REAL,
                stop_previsto REAL,
                preco_entrada REAL,
                preco_fechamento REAL,
                resultado_real TEXT,
                lucro_real REAL,
                precisao_target TEXT,
                precisao_stop TEXT,
                cenarios_acertados TEXT,
                timestamp DATETIME
            )
            ''')
            
            c.execute('''
            INSERT INTO analise_previsoes_ia (
                order_id, target_previsto, stop_previsto, preco_entrada, preco_fechamento,
                resultado_real, lucro_real, precisao_target, precisao_stop, 
                cenarios_acertados, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analise_precisao['order_id'],
                analise_precisao['target_previsto'],
                analise_precisao['stop_previsto'],
                analise_precisao['preco_entrada'],
                analise_precisao['preco_fechamento'],
                analise_precisao['resultado_real'],
                analise_precisao['lucro_real'],
                analise_precisao['precisao_target'],
                analise_precisao['precisao_stop'],
                json.dumps(analise_precisao['cenarios_acertados']),
                analise_precisao['timestamp']
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🎯 Análise de previsões registrada: Target {analise_precisao['precisao_target']}, Stop {analise_precisao['precisao_stop']}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar análise de previsões: {e}")
    
    def _determinar_acerto(self, ordem: Dict[str, Any], resultado: str, lucro_percentual: float) -> bool:
        """Determina se a ordem foi um acerto"""
        confianca = ordem.get('confianca_ia', 0)
        
        if resultado == 'win':
            return lucro_percentual > 0.1  # Lucro mínimo de 0.1%
        elif resultado == 'loss':
            return lucro_percentual > -0.2  # Perda controlada
        else:  # timeout
            return lucro_percentual > -0.1  # Timeout com perda mínima
    
    def _gerar_aprendizado_especifico(self, ordem: Dict[str, Any], resultado: str, 
                                    lucro_percentual: float, dados_mercado: Dict[str, Any]) -> Dict[str, Any]:
        """Gera aprendizado específico da ordem"""
        confianca = ordem.get('confianca_ia', 0)
        tipo_ordem = ordem.get('tipo', '')
        razao_fechamento = ordem.get('razao_fechamento', '')
        
        aprendizado = {
            'confianca_adequada': confianca >= 0.6,
            'tipo_ordem_eficaz': resultado == 'win',
            'tempo_operacao_adequado': True,  # Será ajustado baseado na duração
            'indicadores_eficazes': [],
            'melhorias_sugeridas': [],
            'padrao_ganho': False,
            'padrao_perda': False
        }
        
        # Análise de confiança
        if confianca < 0.6 and resultado == 'loss':
            aprendizado['melhorias_sugeridas'].append('Aumentar threshold de confiança')
        
        # Análise de tempo
        duracao = ordem.get('duracao_segundos', 0)
        if duracao < 60 and resultado == 'loss':
            aprendizado['melhorias_sugeridas'].append('Aumentar tempo mínimo de operação')
        
        # Análise de fechamento
        if 'estagnação' in razao_fechamento and resultado == 'loss':
            aprendizado['melhorias_sugeridas'].append('Ajustar critério de estagnação')
        
        # Identificação de padrões de ganho
        if resultado == 'win' and confianca >= 0.7 and 'alvo' in razao_fechamento.lower():
            aprendizado['padrao_ganho'] = True
            aprendizado['melhorias_sugeridas'].append('Replicar padrão de ganho: confiança alta + alvo atingido')

        # Identificação de padrões de perda recorrentes
        if resultado == 'loss' and ('estagnação' in razao_fechamento.lower() or 'stop' in razao_fechamento.lower()):
            aprendizado['padrao_perda'] = True
            aprendizado['melhorias_sugeridas'].append('Evitar padrão de perda: estagnação ou stop frequente')
        
        return aprendizado
    
    def obter_estatisticas_aprendizado(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema de aprendizado"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Total de registros de aprendizado
            c.execute('SELECT COUNT(*) FROM aprendizado_ia')
            total_registros = c.fetchone()[0]
            
            # Taxa de acerto geral
            c.execute('SELECT AVG(CASE WHEN resultado = \'win\' THEN 1.0 ELSE 0.0 END) FROM aprendizado_ia')
            taxa_acerto_geral = c.fetchone()[0] or 0.0
            
            # Ajustes realizados
            total_ajustes = len(self.historico_ajustes)
            
            # Últimos ajustes
            ultimos_ajustes = self.historico_ajustes[-5:] if self.historico_ajustes else []
            
            conn.close()
            
            return {
                'total_registros_aprendizado': total_registros,
                'taxa_acerto_geral': taxa_acerto_geral * 100,
                'total_ajustes_realizados': total_ajustes,
                'ultimos_ajustes': ultimos_ajustes,
                'parametros_atuais': self.parametros_atuais.copy()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de aprendizado: {e}")
            return {} 
    
    def obter_estatisticas_previsoes(self, dias: int = 7) -> Dict[str, Any]:
        """Obtém estatísticas de precisão das previsões da IA"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Verificar se tabela existe
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analise_previsoes_ia'")
            if not c.fetchone():
                conn.close()
                return {'mensagem': 'Nenhuma análise de previsões encontrada'}
            
            # Data limite
            data_limite = datetime.now() - timedelta(days=dias)
            
            # Buscar análises recentes
            c.execute('''
            SELECT precisao_target, precisao_stop, resultado_real, lucro_real, cenarios_acertados
            FROM analise_previsoes_ia 
            WHERE timestamp > ?
            ''', (data_limite,))
            
            analises = c.fetchall()
            conn.close()
            
            if not analises:
                return {'total_analises': 0, 'mensagem': 'Nenhuma análise recente encontrada'}
            
            # Calcular estatísticas
            total_analises = len(analises)
            
            # Precisão do target
            targets = [a[0] for a in analises if a[0] is not None]
            precisao_target = (targets.count('acerto') / len(targets) * 100) if targets else 0
            
            # Precisão do stop loss
            stops = [a[1] for a in analises if a[1] is not None]
            precisao_stop = (stops.count('acerto') / len(stops) * 100) if stops else 0
            
            # Resultados gerais
            wins = sum(1 for a in analises if a[2] == 'win')
            win_rate = (wins / total_analises) * 100
            
            # Lucro médio
            lucros = [a[3] for a in analises if a[3] is not None]
            lucro_medio = statistics.mean(lucros) if lucros else 0
            
            # Cenários acertados
            cenarios_totais = 0
            cenarios_acertos = 0
            for analise in analises:
                if analise[4]:
                    cenarios = json.loads(analise[4])
                    cenarios_totais += len(cenarios)
                    cenarios_acertos += len(cenarios)
            
            taxa_cenarios = (cenarios_acertos / cenarios_totais * 100) if cenarios_totais > 0 else 0
            
            return {
                'total_analises': total_analises,
                'precisao_target': precisao_target,
                'precisao_stop': precisao_stop,
                'win_rate': win_rate,
                'lucro_medio': lucro_medio,
                'taxa_cenarios_acertados': taxa_cenarios,
                'recomendacoes': self._gerar_recomendacoes_previsoes(analises)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de previsões: {e}")
            return {'erro': str(e)}
    
    def _gerar_recomendacoes_previsoes(self, analises: List[tuple]) -> List[str]:
        """Gera recomendações baseadas na precisão das previsões"""
        recomendacoes = []
        
        # Analisar precisão do target
        targets = [a[0] for a in analises if a[0] is not None]
        if targets:
            precisao_target = targets.count('acerto') / len(targets)
            if precisao_target < 0.3:
                recomendacoes.append("Precisão do target muito baixa - considerar ajustar prompts da IA")
            elif precisao_target > 0.7:
                recomendacoes.append("Precisão do target alta - manter estratégia atual")
        
        # Analisar precisão do stop loss
        stops = [a[1] for a in analises if a[1] is not None]
        if stops:
            precisao_stop = stops.count('acerto') / len(stops)
            if precisao_stop < 0.5:
                recomendacoes.append("Stop loss pouco preciso - revisar lógica de proteção")
        
        # Analisar resultados gerais
        wins = sum(1 for a in analises if a[2] == 'win')
        win_rate = wins / len(analises)
        if win_rate < 0.3:
            recomendacoes.append("Win rate baixo - revisar critérios de entrada")
        
        return recomendacoes 