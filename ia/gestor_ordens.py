"""
Gestor Inteligente de Ordens
Analisa ordens abertas e decide quando sair baseado em análise técnica e aprendizado
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
import sqlite3

class GestorOrdensIA:
    def __init__(self, db_path: str = "dados/trading.db", parametros_ia: Optional[Dict[str, Any]] = None):
        """
        Inicializa gestor inteligente de ordens
        Args:
            db_path: Caminho para banco de dados
            parametros_ia: Parâmetros dinâmicos da IA (opcional)
        """
        self.db_path = db_path
        self.parametros_ia = parametros_ia if parametros_ia is not None else {}
        self.ordens_ativas: Dict[str, Dict[str, Any]] = {}
        self.historico_aprendizado: List[Dict[str, Any]] = []
        self.carregar_ordens_abertas()
        
    def adicionar_ordem_ativa(self, ordem: Dict[str, Any]) -> None:
        """Adiciona ordem à lista de ordens ativas para monitoramento"""
        self.ordens_ativas[ordem['ordem_id']] = ordem
        logger.info(f"📋 Ordem adicionada ao gestor: {ordem['ordem_id']}")
    
    def remover_ordem_ativa(self, ordem_id: str) -> None:
        """Remove ordem da lista de ordens ativas"""
        if ordem_id in self.ordens_ativas:
            del self.ordens_ativas[ordem_id]
            logger.info(f"📋 Ordem removida do gestor: {ordem_id}")
    
    def analisar_ordens_ativas(self, dados_mercado: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analisa ordens ativas e decide se deve sair usando previsões da IA
        
        Args:
            dados_mercado: Dados atuais do mercado
            
        Returns:
            Lista de decisões de saída
        """
        decisoes_saida = []
        preco_atual = dados_mercado['preco_atual']
        simbolo = dados_mercado.get('simbolo', 'WIN')
        
        for ordem_id, ordem in list(self.ordens_ativas.items()):
            if ordem['simbolo'] != simbolo:
                continue
                
            # Calcular métricas da ordem
            duracao = (datetime.now() - ordem['timestamp']).total_seconds()
            variacao_atual = self.calcular_variacao(ordem['preco_entrada'], preco_atual, ordem['tipo'])
            
            # --- ANÁLISE BASEADA EM PREVISÕES DA IA ---
            decisao_previsao = self._analisar_com_previsoes(ordem, dados_mercado, variacao_atual)
            if decisao_previsao:
                decisao_previsao['ordem_id'] = ordem_id
                decisao_previsao['ordem'] = ordem
                decisoes_saida.append(decisao_previsao)
                logger.info(f"🎯 Decisão baseada em previsões IA: {ordem_id} | {decisao_previsao['decisao']}")
                continue
            
            # --- Trailing Stop Dinâmico ---
            if 'max_lucro' not in ordem:
                ordem['max_lucro'] = variacao_atual
            if variacao_atual > ordem['max_lucro']:
                ordem['max_lucro'] = variacao_atual
            trailing_threshold = max(0.1, ordem['max_lucro'] * 0.3)  # 0.1% ou 30% do pico
            if ordem['max_lucro'] > 0.15 and (ordem['max_lucro'] - variacao_atual) > trailing_threshold:
                return_decisao = {
                    'decisao': 'sair_lucro',
                    'razao': f'Trailing stop: lucro recuou de {ordem["max_lucro"]:.2f}% para {variacao_atual:.2f}%',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'trailing_stop'
                }
                return_decisao['ordem_id'] = ordem_id
                return_decisao['ordem'] = ordem
                decisoes_saida.append(return_decisao)
                logger.info(f"🟢 Trailing stop acionado: {ordem_id} | Lucro máximo: {ordem['max_lucro']:.2f}% | Lucro atual: {variacao_atual:.2f}%")
                continue
                
            # --- Ajuste dinâmico do stop loss ---
            if ordem['max_lucro'] >= 0.15:
                if ordem['tipo'] == 'comprar':
                    novo_stop = ordem['preco_entrada'] * (1 + (ordem['max_lucro'] * 0.5) / 100)
                    if novo_stop > ordem['preco_stop']:
                        logger.info(f"🟡 Ajustando stop para proteger lucro: {ordem_id} | Novo stop: {novo_stop:.2f}")
                        ordem['preco_stop'] = novo_stop
                else:  # vender
                    novo_stop = ordem['preco_entrada'] * (1 - (ordem['max_lucro'] * 0.5) / 100)
                    if novo_stop < ordem['preco_stop']:
                        logger.info(f"🟡 Ajustando stop para proteger lucro: {ordem_id} | Novo stop: {novo_stop:.2f}")
                        ordem['preco_stop'] = novo_stop
                
            # --- Fechamento inteligente por sinais de reversão ---
            indicadores = dados_mercado.get('indicadores', {})
            rsi = indicadores.get('rsi', None)
            media_curta = indicadores.get('media_curta', None)
            media_longa = indicadores.get('media_longa', None)
            # Fechamento por RSI
            if ordem['tipo'] == 'comprar' and rsi is not None and rsi < 65 and rsi > 55 and ordem.get('rsi_pico', 0) > 70:
                return_decisao = {
                    'decisao': 'sair_perda',
                    'razao': f'Reversão detectada: RSI caiu de sobrecompra para {rsi:.1f}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'reversao_rsi'
                }
                return_decisao['ordem_id'] = ordem_id
                return_decisao['ordem'] = ordem
                decisoes_saida.append(return_decisao)
                logger.info(f"🔴 Fechamento por reversão RSI: {ordem_id} | RSI: {rsi:.1f}")
                continue
            if ordem['tipo'] == 'vender' and rsi is not None and rsi > 35 and rsi < 45 and ordem.get('rsi_pico', 100) < 30:
                return_decisao = {
                    'decisao': 'sair_perda',
                    'razao': f'Reversão detectada: RSI subiu de sobrevenda para {rsi:.1f}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'reversao_rsi'
                }
                return_decisao['ordem_id'] = ordem_id
                return_decisao['ordem'] = ordem
                decisoes_saida.append(return_decisao)
                logger.info(f"🔴 Fechamento por reversão RSI: {ordem_id} | RSI: {rsi:.1f}")
                continue
            # Fechamento por cruzamento de médias móveis
            if media_curta is not None and media_longa is not None:
                if ordem['tipo'] == 'comprar' and media_curta < media_longa:
                    return_decisao = {
                        'decisao': 'sair_perda',
                        'razao': f'Reversão: média curta cruzou abaixo da longa',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'reversao_media'
                    }
                    return_decisao['ordem_id'] = ordem_id
                    return_decisao['ordem'] = ordem
                    decisoes_saida.append(return_decisao)
                    logger.info(f"🔴 Fechamento por cruzamento de médias: {ordem_id}")
                    continue
                if ordem['tipo'] == 'vender' and media_curta > media_longa:
                    return_decisao = {
                        'decisao': 'sair_perda',
                        'razao': f'Reversão: média curta cruzou acima da longa',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'reversao_media'
                    }
                    return_decisao['ordem_id'] = ordem_id
                    return_decisao['ordem'] = ordem
                    decisoes_saida.append(return_decisao)
                    logger.info(f"🔴 Fechamento por cruzamento de médias: {ordem_id}")
                    continue
                
            # --- Análise de contexto e tendência ---
            tendencia = indicadores.get('tendencia', None)
            volatilidade = indicadores.get('volatilidade', None)
            volume = indicadores.get('volume', None)
            # Fechamento por reversão de tendência
            if tendencia is not None:
                if ordem['tipo'] == 'comprar' and tendencia == 'baixa':
                    return_decisao = {
                        'decisao': 'sair_perda',
                        'razao': 'Tendência de curto prazo virou para baixa',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'reversao_tendencia'
                    }
                    return_decisao['ordem_id'] = ordem_id
                    return_decisao['ordem'] = ordem
                    decisoes_saida.append(return_decisao)
                    logger.info(f"🔴 Fechamento por reversão de tendência: {ordem_id}")
                    continue
                if ordem['tipo'] == 'vender' and tendencia == 'alta':
                    return_decisao = {
                        'decisao': 'sair_perda',
                        'razao': 'Tendência de curto prazo virou para alta',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'reversao_tendencia'
                    }
                    return_decisao['ordem_id'] = ordem_id
                    return_decisao['ordem'] = ordem
                    decisoes_saida.append(return_decisao)
                    logger.info(f"🔴 Fechamento por reversão de tendência: {ordem_id}")
                    continue
            # Fechamento por volatilidade extrema
            if volatilidade is not None and volatilidade > 2.0:
                return_decisao = {
                    'decisao': 'sair_perda',
                    'razao': f'Volatilidade extrema detectada: {volatilidade:.2f}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'volatilidade_extrema'
                }
                return_decisao['ordem_id'] = ordem_id
                return_decisao['ordem'] = ordem
                decisoes_saida.append(return_decisao)
                logger.info(f"🔴 Fechamento por volatilidade extrema: {ordem_id}")
                continue
            # Fechamento por exaustão de volume
            if volume is not None and volume < 100:
                return_decisao = {
                    'decisao': 'sair_perda',
                    'razao': f'Volume muito baixo detectado: {volume}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'volume_baixo'
                }
                return_decisao['ordem_id'] = ordem_id
                return_decisao['ordem'] = ordem
                decisoes_saida.append(return_decisao)
                logger.info(f"🔴 Fechamento por volume baixo: {ordem_id}")
                continue
                
        return decisoes_saida
    
    def _get_tempo_expiracao_ordem(self, ordem: Dict[str, Any]) -> float:
        """Obtém o tempo de expiração dinâmico da ordem, priorizando o valor salvo na ordem, depois parâmetros globais, depois fallback."""
        # 1. Valor salvo na ordem (preferencial)
        if 'tempo_expiracao' in ordem:
            return float(ordem['tempo_expiracao'])
        if 'tempo_estagnacao' in ordem:
            return float(ordem['tempo_estagnacao'])
        # 2. Parâmetro global da IA (se existir)
        if hasattr(self, 'parametros_ia') and isinstance(self.parametros_ia, dict):
            return float(self.parametros_ia.get('tempo_estagnacao', 300))
        # 3. Fallback permissivo
        return 300.0

    def _analisar_com_previsoes(self, ordem: Dict[str, Any], dados_mercado: Dict[str, Any], variacao_atual: float) -> Optional[Dict[str, Any]]:
        """Analisa ordem usando previsões da IA"""
        try:
            previsoes = ordem.get('previsoes_ia', {})
            if not previsoes:
                return None
            
            preco_atual = dados_mercado['preco_atual']
            preco_entrada = ordem['preco_entrada']
            
            # Verificar se target foi atingido
            target = previsoes.get('target')
            if target:
                if ordem['tipo'] == 'comprar' and preco_atual >= target:
                    return {
                        'decisao': 'sair_lucro',
                        'razao': f'Target da IA atingido: {target}',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'target_ia'
                    }
                elif ordem['tipo'] == 'vender' and preco_atual <= target:
                    return {
                        'decisao': 'sair_lucro',
                        'razao': f'Target da IA atingido: {target}',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'target_ia'
                    }
            
            # Verificar se stop loss foi atingido
            stop_loss = previsoes.get('stop_loss')
            if stop_loss:
                if ordem['tipo'] == 'comprar' and preco_atual <= stop_loss:
                    return {
                        'decisao': 'sair_perda',
                        'razao': f'Stop loss da IA atingido: {stop_loss}',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'stop_ia'
                    }
                elif ordem['tipo'] == 'vender' and preco_atual >= stop_loss:
                    return {
                        'decisao': 'sair_perda',
                        'razao': f'Stop loss da IA atingido: {stop_loss}',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'stop_ia'
                    }
            
            # Verificar cenários da IA
            cenarios = previsoes.get('cenarios', {})
            
            # Cenário de saída por lucro
            if cenarios.get('sair_lucro'):
                # Verificar se condições para saída por lucro foram atendidas
                if variacao_atual >= 1.5:  # Lucro mínimo de 1.5%
                    return {
                        'decisao': 'sair_lucro',
                        'razao': f'Cenário IA: {cenarios["sair_lucro"]}',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'cenario_ia'
                    }
            
            # Cenário de saída por perda
            if cenarios.get('sair_perda'):
                # Verificar se condições para saída por perda foram atendidas
                if variacao_atual <= -1.0:  # Perda mínima de 1%
                    return {
                        'decisao': 'sair_perda',
                        'razao': f'Cenário IA: {cenarios["sair_perda"]}',
                        'lucro_percentual': variacao_atual,
                        'tipo_saida': 'cenario_ia'
                    }
            
            # Verificar timeout dinâmico
            duracao = (datetime.now() - ordem['timestamp']).total_seconds()
            tempo_expiracao = self._get_tempo_expiracao_ordem(ordem)
            if duracao > tempo_expiracao:
                return {
                    'decisao': 'sair_timeout',
                    'razao': f'Timeout: {duracao:.1f}s > {tempo_expiracao:.0f}s',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'timeout'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao analisar com previsões: {e}")
            return None
    
    def analisar_saida_tecnica(self, ordem: Dict[str, Any], dados_mercado: Dict[str, Any], 
                              duracao: float, variacao_atual: float) -> Dict[str, Any]:
        """
        Análise técnica para decidir saída da ordem
        
        Args:
            ordem: Dados da ordem
            dados_mercado: Dados atuais do mercado
            duracao: Duração da ordem em segundos
            variacao_atual: Variação atual em percentual
            
        Returns:
            Decisão de saída
        """
        preco_atual = dados_mercado['preco_atual']
        confianca_entrada = ordem['confianca_ia']
        
        # 1. Verificar alvos e stops automáticos
        if ordem['tipo'] == 'comprar':
            if preco_atual >= ordem['preco_alvo']:
                return {
                    'decisao': 'sair_lucro',
                    'razao': f'Alvo atingido: {preco_atual:.2f} >= {ordem["preco_alvo"]:.2f}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'alvo'
                }
            elif preco_atual <= ordem['preco_stop']:
                return {
                    'decisao': 'sair_perda',
                    'razao': f'Stop atingido: {preco_atual:.2f} <= {ordem["preco_stop"]:.2f}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'stop'
                }
        else:  # vender
            if preco_atual <= ordem['preco_alvo']:
                return {
                    'decisao': 'sair_lucro',
                    'razao': f'Alvo atingido: {preco_atual:.2f} <= {ordem["preco_alvo"]:.2f}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'alvo'
                }
            elif preco_atual >= ordem['preco_stop']:
                return {
                    'decisao': 'sair_perda',
                    'razao': f'Stop atingido: {preco_atual:.2f} >= {ordem["preco_stop"]:.2f}',
                    'lucro_percentual': variacao_atual,
                    'tipo_saida': 'stop'
                }
        
        # 2. Análise de timeout dinâmico
        tempo_expiracao = self._get_tempo_expiracao_ordem(ordem)
        if duracao > tempo_expiracao:
            return {
                'decisao': 'sair_timeout',
                'razao': f'Timeout: {duracao:.1f}s > {tempo_expiracao:.0f}s',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'timeout'
            }
        
        # 3. Análise técnica inteligente para saída antecipada
        decisao_inteligente = self.analisar_saida_inteligente(ordem, dados_mercado, duracao, variacao_atual)
        if decisao_inteligente:
            return decisao_inteligente
        
        # 4. Manter ordem ativa
        return {
            'decisao': 'manter',
            'razao': 'Análise indica manter posição',
            'lucro_percentual': variacao_atual,
            'tipo_saida': 'manter'
        }
    
    def analisar_saida_inteligente(self, ordem: Dict[str, Any], dados_mercado: Dict[str, Any], 
                                  duracao: float, variacao_atual: float) -> Optional[Dict[str, Any]]:
        """
        Análise inteligente para saída antecipada baseada em padrões
        
        Args:
            ordem: Dados da ordem
            dados_mercado: Dados atuais do mercado
            duracao: Duração da ordem
            variacao_atual: Variação atual
            
        Returns:
            Decisão de saída ou None para manter
        """
        # Extrair indicadores do mercado
        indicadores = dados_mercado.get('indicadores', {})
        tendencia = indicadores.get('tendencia', 'lateral')
        rsi = indicadores.get('rsi', 50)
        volume = dados_mercado.get('volume', 0)
        
        # Padrões de saída baseados em aprendizado
        confianca_entrada = ordem['confianca_ia']
        
        # 1. Saída por reversão de tendência
        if ordem['tipo'] == 'comprar' and tendencia == 'baixa' and variacao_atual > 0.1:
            return {
                'decisao': 'sair_lucro',
                'razao': f'Reversão de tendência detectada (baixa) com lucro de {variacao_atual:.2f}%',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'reversao_tendencia'
            }
        elif ordem['tipo'] == 'vender' and tendencia == 'alta' and variacao_atual > 0.1:
            return {
                'decisao': 'sair_lucro',
                'razao': f'Reversão de tendência detectada (alta) com lucro de {variacao_atual:.2f}%',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'reversao_tendencia'
            }
        
        # 2. Saída por RSI extremo
        if rsi > 80 and ordem['tipo'] == 'comprar' and variacao_atual > 0.05:
            return {
                'decisao': 'sair_lucro',
                'razao': f'RSI sobrecomprado ({rsi:.1f}) com lucro de {variacao_atual:.2f}%',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'rsi_extremo'
            }
        elif rsi < 20 and ordem['tipo'] == 'vender' and variacao_atual > 0.05:
            return {
                'decisao': 'sair_lucro',
                'razao': f'RSI sobrevendido ({rsi:.1f}) com lucro de {variacao_atual:.2f}%',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'rsi_extremo'
            }
        
        # 3. Saída por perda controlada (stop inteligente)
        if variacao_atual < -0.15 and duracao > 60:  # Perda de 0.15% após 1 minuto
            return {
                'decisao': 'sair_perda',
                'razao': f'Stop inteligente: perda de {variacao_atual:.2f}% após {duracao:.1f}s',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'stop_inteligente'
            }
        
        # 4. Saída por lucro rápido (take profit inteligente)
        if variacao_atual > 0.25 and duracao < 120:  # Lucro de 0.25% em menos de 2 minutos
            return {
                'decisao': 'sair_lucro',
                'razao': f'Take profit inteligente: lucro de {variacao_atual:.2f}% em {duracao:.1f}s',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'take_profit_inteligente'
            }
        
        # 5. Saída por estagnação (ordem parada)
        if abs(variacao_atual) < 0.03 and duracao > 300:  # Pouca variação após 5 minutos
            return {
                'decisao': 'sair_perda',
                'razao': f'Estagnação: variação de {variacao_atual:.2f}% após {duracao:.1f}s',
                'lucro_percentual': variacao_atual,
                'tipo_saida': 'estagnacao'
            }
        
        return None
    
    def calcular_variacao(self, preco_entrada: float, preco_atual: float, tipo_ordem: str) -> float:
        """Calcula variação percentual da ordem, limitado a [-2, 2]% para evitar outliers"""
        if tipo_ordem == 'comprar':
            variacao = ((preco_atual - preco_entrada) / preco_entrada) * 100
        else:  # vender
            variacao = ((preco_entrada - preco_atual) / preco_entrada) * 100
        # Clamp para evitar outliers
        return max(-2.0, min(2.0, variacao))
    
    def registrar_aprendizado_saida(self, ordem: Dict[str, Any], decisao_saida: Dict[str, Any]) -> None:
        """
        Registra aprendizado sobre decisões de saída
        
        Args:
            ordem: Dados da ordem
            decisao_saida: Decisão de saída tomada
        """
        aprendizado = {
            'timestamp': datetime.now(),
            'ordem_id': ordem['ordem_id'],
            'tipo_ordem': ordem['tipo'],
            'confianca_entrada': ordem['confianca_ia'],
            'duracao': (datetime.now() - ordem['timestamp']).total_seconds(),
            'lucro_percentual': decisao_saida['lucro_percentual'],
            'tipo_saida': decisao_saida['tipo_saida'],
            'razao_saida': decisao_saida['razao'],
            'decisao_saida': decisao_saida['decisao'],
            'acerto': self.avaliar_acerto_saida(decisao_saida)
        }
        
        self.historico_aprendizado.append(aprendizado)
        
        # Salvar no banco
        self.salvar_aprendizado_saida(aprendizado)
        
        logger.info(f"📚 Aprendizado de saída registrado: {decisao_saida['decisao']} | "
                   f"Tipo: {decisao_saida['tipo_saida']} | Acerto: {aprendizado['acerto']}")
    
    def avaliar_acerto_saida(self, decisao_saida: Dict[str, Any]) -> bool:
        """Avalia se a decisão de saída foi acertada"""
        if decisao_saida['decisao'] == 'sair_lucro':
            return decisao_saida['lucro_percentual'] > 0
        elif decisao_saida['decisao'] == 'sair_perda':
            return decisao_saida['lucro_percentual'] > -0.2  # Perda controlada
        else:
            return True  # Timeout é considerado acerto se evitou perda maior
    
    def salvar_aprendizado_saida(self, aprendizado: Dict[str, Any]) -> bool:
        """Salva aprendizado de saída no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Criar tabela se não existir
            c.execute('''
            CREATE TABLE IF NOT EXISTS aprendizado_saida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                ordem_id TEXT,
                tipo_ordem TEXT,
                confianca_entrada DECIMAL(5,2),
                duracao_segundos DECIMAL(10,2),
                lucro_percentual DECIMAL(5,2),
                tipo_saida TEXT,
                razao_saida TEXT,
                decisao_saida TEXT,
                acerto BOOLEAN
            )
            ''')
            
            c.execute('''
            INSERT INTO aprendizado_saida 
            (timestamp, ordem_id, tipo_ordem, confianca_entrada, duracao_segundos,
             lucro_percentual, tipo_saida, razao_saida, decisao_saida, acerto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                aprendizado['timestamp'],
                aprendizado['ordem_id'],
                aprendizado['tipo_ordem'],
                aprendizado['confianca_entrada'],
                aprendizado['duracao'],
                aprendizado['lucro_percentual'],
                aprendizado['tipo_saida'],
                aprendizado['razao_saida'],
                aprendizado['decisao_saida'],
                aprendizado['acerto']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar aprendizado de saída: {e}")
            return False
    
    def obter_estatisticas_saida(self) -> Dict[str, Any]:
        """Obtém estatísticas de decisões de saída"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Total de saídas
            c.execute('SELECT COUNT(*) FROM aprendizado_saida')
            total_saidas = c.fetchone()[0]
            
            # Taxa de acerto por tipo de saída
            c.execute('''
            SELECT tipo_saida, COUNT(*) as total, 
                   SUM(CASE WHEN acerto = 1 THEN 1 ELSE 0 END) as acertos,
                   AVG(lucro_percentual) as lucro_medio
            FROM aprendizado_saida 
            GROUP BY tipo_saida
            ''')
            performance_tipos = {}
            for row in c.fetchall():
                performance_tipos[row[0]] = {
                    'total': row[1],
                    'acertos': row[2],
                    'lucro_medio': row[3] or 0.0
                }
            
            # Taxa de acerto geral
            c.execute('SELECT AVG(CASE WHEN acerto = 1 THEN 1.0 ELSE 0.0 END) FROM aprendizado_saida')
            taxa_acerto_geral = c.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                'total_saidas': total_saidas,
                'taxa_acerto_geral': taxa_acerto_geral * 100,
                'performance_tipos': performance_tipos,
                'ordens_ativas': len(self.ordens_ativas)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de saída: {e}")
            return {} 

    def carregar_ordens_abertas(self) -> None:
        """
        Carrega ordens abertas do banco de dados e adiciona ao monitoramento.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                SELECT ordem_id, tipo, simbolo, preco_entrada, preco_alvo, preco_stop, 
                       confianca_ia, timestamp
                FROM ordens_simuladas 
                WHERE status = 'aberta' 
            ''')
            rows = c.fetchall()
            conn.close()
            for row in rows:
                ordem = self.converter_row_para_ordem(row)
                self.ordens_ativas[ordem['ordem_id']] = ordem
                logger.info(f"♻️ Ordem reimportada para monitoramento: {ordem['ordem_id']}")
        except Exception as e:
            logger.error(f"Erro ao carregar ordens abertas: {e}")

    def converter_row_para_ordem(self, row: tuple) -> Dict[str, Any]:
        """
        Converte uma tupla do banco em dicionário de ordem.
        """
        return {
            'ordem_id': row[0],
            'tipo': row[1],
            'simbolo': row[2],
            'preco_entrada': row[3],
            'preco_alvo': row[4],
            'preco_stop': row[5],
            'confianca_ia': row[6],
            'timestamp': datetime.fromisoformat(row[7]) if isinstance(row[7], str) else row[7],
        } 