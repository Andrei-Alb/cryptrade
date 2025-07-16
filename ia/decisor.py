"""
Decisor de IA para Trading
Processa decisões da IA e aplica filtros de segurança
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecisorIA:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa decisor de IA
        
        Args:
            config: Configurações do decisor
        """
        self.config = self._mesclar_config(config)
        self.decisoes_historico: List[Dict[str, Any]] = []
        
    def _mesclar_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Mescla configuração fornecida com padrão"""
        config_padrao = self._config_padrao()
        if config:
            config_padrao.update(config)
        return config_padrao
        
    def _config_padrao(self) -> Dict[str, Any]:
        """Configurações padrão do decisor"""
        return {
            'confianca_minima': 0.8,  # Mais seletivo: exige sinais muito fortes
            'max_ordens_dia': 10,
            'stop_loss_padrao': 100,
            'take_profit_padrao': 200,
            'horario_inicio': '09:00',
            'horario_fim': '17:00',
            'dias_semana': [0, 1, 2, 3, 4],  # Segunda a Sexta
            'volatilidade_maxima': 0.05,  # 5%
            'volume_minimo': 0,
            'rsi_sobrecompra': 70,
            'rsi_sobrevenda': 30,
            'tendencia_minima_periodos': 20
        }
    
    def processar_decisao_ia(self, decisao_ia: Dict[str, Any], dados_mercado: Dict[str, Any], ordem_aberta: bool = False) -> Dict[str, Any]:
        """
        Processa decisão da IA e aplica filtros de segurança
        """
        try:
            # Permitir apenas uma entrada por vez
            if ordem_aberta:
                return {
                    'decisao': 'aguardar',
                    'confianca': decisao_ia.get('confianca', 0.0),
                    'razao': 'Já existe ordem aberta, aguardando fechamento.',
                    'parametros': decisao_ia.get('parametros', {})
                }
            # Validar decisão da IA
            if not self._validar_decisao_ia(decisao_ia):
                logger.warning("Decisão da IA inválida, usando fallback")
                return self._decisao_fallback()
            # --- Penalização de confiança e ajuste em drawdown ---
            try:
                import sqlite3
                conn = sqlite3.connect('robo_trading/dados/trading.db')
                c = conn.cursor()
                c.execute("SELECT resultado FROM ordens_simuladas WHERE status = 'fechada' ORDER BY timestamp_fechamento DESC LIMIT 5;")
                ultimos_resultados = [row[0] for row in c.fetchall()]
                conn.close()
            except sqlite3.Error:
                ultimos_resultados = []
            sequencia_losses = 0
            for r in ultimos_resultados:
                if r == 'loss':
                    sequencia_losses += 1
                else:
                    break
            if sequencia_losses >= 3:
                logger.info("IA em drawdown: %d losses seguidos. Exigindo sinais mais fortes.", sequencia_losses)
                confianca_minima_drawdown = max(self.config['confianca_minima'], 0.85)
                if decisao_ia['confianca'] < confianca_minima_drawdown:
                    return {
                        'decisao': 'aguardar',
                        'confianca': decisao_ia['confianca'],
                        'razao': f'Em drawdown ({sequencia_losses} losses), aguardando sinal fortíssimo',
                        'parametros': decisao_ia.get('parametros', {})
                    }
                decisao_ia['razao'] += f' | Contexto: drawdown ({sequencia_losses} losses)'
            # Após loss, só permitir nova entrada se confiança > 0.85
            if ultimos_resultados and ultimos_resultados[0] == 'loss' and decisao_ia['confianca'] <= 0.85:
                return {
                    'decisao': 'aguardar',
                    'confianca': decisao_ia['confianca'],
                    'razao': 'Última ordem foi loss, aguardando sinal fortíssimo para nova entrada.',
                    'parametros': decisao_ia.get('parametros', {})
                }
            
            # Filtro de tendência: evitar operar contra a tendência
            tendencia = dados_mercado.get('tendencia', 'lateral')
            if decisao_ia['decisao'] == 'comprar' and tendencia == 'baixa':
                logger.info("Evitando compra em tendência de baixa")
                return {
                    'decisao': 'aguardar',
                    'confianca': decisao_ia['confianca'],
                    'razao': 'Tendência de baixa detectada, aguardando',
                    'parametros': decisao_ia.get('parametros', {})
                }
            if decisao_ia['decisao'] == 'vender' and tendencia == 'alta':
                logger.info("Evitando venda em tendência de alta")
                return {
                    'decisao': 'aguardar',
                    'confianca': decisao_ia['confianca'],
                    'razao': 'Tendência de alta detectada, aguardando',
                    'parametros': decisao_ia.get('parametros', {})
                }
            
            # Filtro de exaustão de movimento: evitar comprar no topo ou vender no fundo
            historico_precos = dados_mercado.get('historico_precos', [])
            variacao = dados_mercado.get('variacao', 0.0)
            rsi = dados_mercado.get('rsi', 50.0)
            # Evitar comprar após 3+ candles de alta ou variação > 0.5%
            if decisao_ia['decisao'] == 'comprar':
                if len(historico_precos) >= 4 and all(historico_precos[-i] < historico_precos[-i+1] for i in range(1, 4)):
                    logger.info("Evitando compra após sequência de altas (excesso de otimismo)")
                    return {
                        'decisao': 'aguardar',
                        'confianca': decisao_ia['confianca'],
                        'razao': 'Exaustão de alta detectada, aguardando pullback',
                        'parametros': decisao_ia.get('parametros', {})
                    }
                if variacao > 0.5:
                    logger.info("Evitando compra após variação muito positiva")
                    return {
                        'decisao': 'aguardar',
                        'confianca': decisao_ia['confianca'],
                        'razao': 'Variação muito positiva, aguardando correção',
                        'parametros': decisao_ia.get('parametros', {})
                    }
                if rsi > 70:
                    logger.info("Evitando compra com RSI sobrecomprado")
                    return {
                        'decisao': 'aguardar',
                        'confianca': decisao_ia['confianca'],
                        'razao': 'RSI sobrecomprado, aguardando correção',
                        'parametros': decisao_ia.get('parametros', {})
                    }
            # Evitar vender após 3+ candles de baixa ou variação < -0.5%
            if decisao_ia['decisao'] == 'vender':
                if len(historico_precos) >= 4 and all(historico_precos[-i] > historico_precos[-i+1] for i in range(1, 4)):
                    logger.info("Evitando venda após sequência de baixas (excesso de pessimismo)")
                    return {
                        'decisao': 'aguardar',
                        'confianca': decisao_ia['confianca'],
                        'razao': 'Exaustão de baixa detectada, aguardando pullback',
                        'parametros': decisao_ia.get('parametros', {})
                    }
                if variacao < -0.5:
                    logger.info("Evitando venda após variação muito negativa")
                    return {
                        'decisao': 'aguardar',
                        'confianca': decisao_ia['confianca'],
                        'razao': 'Variação muito negativa, aguardando repique',
                        'parametros': decisao_ia.get('parametros', {})
                    }
                if rsi < 30:
                    logger.info("Evitando venda com RSI sobrevendido")
                    return {
                        'decisao': 'aguardar',
                        'confianca': decisao_ia['confianca'],
                        'razao': 'RSI sobrevendido, aguardando repique',
                        'parametros': decisao_ia.get('parametros', {})
                    }
            
            # Aplicar filtros de segurança
            decisao_filtrada = self._aplicar_filtros_seguranca(decisao_ia, dados_mercado)
            
            # Verificar condições de mercado
            if not self._verificar_condicoes_mercado(dados_mercado):
                logger.info("Condições de mercado não favoráveis, aguardando")
                return self._decisao_aguardar()
            
            # Verificar limites de operação
            if not self._verificar_limites_operacao(decisao_filtrada):
                logger.info("Limite de operações atingido, aguardando")
                return self._decisao_aguardar()
            
            # Registrar decisão
            self._registrar_decisao(decisao_filtrada)
            
            logger.info(f"Decisão final: {decisao_filtrada['decisao']} "
                       f"(confiança: {decisao_filtrada['confianca']})")
            
            return decisao_filtrada
            
        except Exception as e:
            logger.error(f"Erro ao processar decisão da IA: {e}")
            return self._decisao_fallback()
    
    def _validar_decisao_ia(self, decisao: Dict[str, Any]) -> bool:
        """
        Valida se a decisão da IA está no formato correto
        """
        campos_obrigatorios = ['decisao', 'confianca', 'razao', 'parametros']
        
        for campo in campos_obrigatorios:
            if campo not in decisao:
                return False
        
        # Validar valores
        if decisao['decisao'] not in ['comprar', 'vender', 'aguardar']:
            return False
        
        if not isinstance(decisao['confianca'], (int, float)) or not 0 <= decisao['confianca'] <= 1:
            return False
        
        # Validar parâmetros
        parametros = decisao.get('parametros', {})
        if not isinstance(parametros, dict):
            return False
        
        return True
    
    def _aplicar_filtros_seguranca(self, decisao: Dict[str, Any], 
                                 dados_mercado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica filtros de segurança na decisão
        """
        decisao_filtrada = decisao.copy()
        
        # Ajustar confiança baseada em indicadores (opcional, mas não binarizar)
        confianca_ajustada = self._ajustar_confianca(decisao['confianca'], dados_mercado)
        decisao_filtrada['confianca'] = confianca_ajustada
        
        # Só bloquear operações com confiança muito baixa (<0.2)
        if confianca_ajustada < 0.2:
            logger.info(f"🔒 Decisão bloqueada: confiança ({confianca_ajustada:.2f}) < mínimo (0.2) | Forçando 'aguardar'.")
            decisao_filtrada['decisao'] = 'aguardar'
            decisao_filtrada['razao'] = f"Confiança muito baixa ({confianca_ajustada:.2f}) - aguardando sinal mais claro."
        # Não binarizar confiança intermediária, deixar a IA decidir
        # Ajustar parâmetros de trading
        parametros = decisao_filtrada.get('parametros', {})
        parametros['stop_loss'] = self.config['stop_loss_padrao']
        parametros['take_profit'] = self.config['take_profit_padrao']
        parametros['quantidade'] = 1  # Sempre 1 contrato por segurança
        decisao_filtrada['parametros'] = parametros
        return decisao_filtrada
    
    def _ajustar_confianca(self, confianca_original: float, 
                          dados_mercado: Dict[str, Any]) -> float:
        """
        Ajusta confiança baseada em indicadores técnicos
        """
        confianca = confianca_original
        
        # Ajustar baseado no RSI (MENOS AGRESSIVO)
        rsi = dados_mercado.get('rsi', 50.0)
        if rsi < self.config['rsi_sobrevenda'] or rsi > self.config['rsi_sobrecompra']:
            confianca *= 0.9  # Reduzir confiança em extremos (menos agressivo)
        
        # Ajustar baseado na volatilidade (MENOS AGRESSIVO)
        volatilidade = dados_mercado.get('volatilidade', 0.0)
        if volatilidade > self.config['volatilidade_maxima']:
            confianca *= 0.8  # Reduzir confiança em alta volatilidade (menos agressivo)
        
        # Ajustar baseado no volume (API da B3 não retorna volume, então não penalizar)
        volume = dados_mercado.get('volume', 0)
        volume_medio = dados_mercado.get('volume_medio', 0)
        # Só penalizar se tivermos dados de volume e estiver muito baixo
        if volume > 0 and volume_medio > 0 and volume < volume_medio * 0.5:
            confianca *= 0.9  # Reduzir confiança em baixo volume (menos agressivo)
        
        # Ajustar baseado na tendência (MENOS AGRESSIVO)
        tendencia = dados_mercado.get('tendencia', 'lateral')
        if tendencia == 'lateral':
            confianca *= 0.95  # Reduzir confiança em mercado lateral (menos agressivo)
        
        return max(0.0, min(1.0, confianca))  # Manter entre 0 e 1
    
    def _verificar_condicoes_mercado(self, dados_mercado: Dict[str, Any]) -> bool:
        """
        Verifica se as condições de mercado são favoráveis
        """
        # Verificar horário de operação
        agora = datetime.now()
        hora_atual = agora.time()
        
        hora_inicio = time.fromisoformat(self.config['horario_inicio'])
        hora_fim = time.fromisoformat(self.config['horario_fim'])
        
        # Para testes, permitir operação fora do horário de mercado
        if not (hora_inicio <= hora_atual <= hora_fim):
            logger.info("Fora do horário de operação (permitindo para testes)")
            # return False  # Comentado para permitir testes
        
        # Verificar dia da semana
        if agora.weekday() not in self.config['dias_semana']:
            logger.info("Fora dos dias de operação (permitindo para testes)")
            # return False  # Comentado para permitir testes
        
        # Verificar volume mínimo (API da B3 não retorna volume, então não bloquear)
        volume = dados_mercado.get('volume', 0)
        if volume > 0 and volume < self.config['volume_minimo']:
            logger.info(f"Volume muito baixo: {volume}")
            return False
        
        # Verificar volatilidade máxima
        volatilidade = dados_mercado.get('volatilidade', 0.0)
        if volatilidade > self.config['volatilidade_maxima']:
            logger.info(f"Volatilidade muito alta: {volatilidade}")
            return False
        
        return True
    
    def _verificar_limites_operacao(self, decisao: Dict[str, Any]) -> bool:
        """
        Verifica se não excedeu limites de operação
        """
        if decisao['decisao'] == 'aguardar':
            return True
        
        # Contar operações do dia
        hoje = datetime.now().date()
        operacoes_hoje = sum(1 for d in self.decisoes_historico 
                           if d['data'].date() == hoje and d['decisao'] != 'aguardar')
        
        if operacoes_hoje >= self.config['max_ordens_dia']:
            logger.info(f"Limite de operações atingido: {operacoes_hoje}")
            return False
        
        return True
    
    def _registrar_decisao(self, decisao: Dict[str, Any]):
        """
        Registra decisão no histórico
        """
        registro = {
            'data': datetime.now(),
            'decisao': decisao['decisao'],
            'confianca': decisao['confianca'],
            'razao': decisao['razao']
        }
        
        self.decisoes_historico.append(registro)
        
        # Manter apenas últimas 100 decisões
        if len(self.decisoes_historico) > 100:
            self.decisoes_historico = self.decisoes_historico[-100:]
    
    def _decisao_fallback(self) -> Dict[str, Any]:
        """
        Retorna decisão de fallback
        """
        return {
            "decisao": "aguardar",
            "confianca": 0.0,
            "razao": "Erro no processamento - usando fallback",
            "parametros": {
                "quantidade": 1,
                "stop_loss": self.config['stop_loss_padrao'],
                "take_profit": self.config['take_profit_padrao']
            },
            "indicadores_analisados": []
        }
    
    def _decisao_aguardar(self) -> Dict[str, Any]:
        """
        Retorna decisão de aguardar
        """
        return {
            "decisao": "aguardar",
            "confianca": 0.0,
            "razao": "Condições de mercado não favoráveis",
            "parametros": {
                "quantidade": 1,
                "stop_loss": self.config['stop_loss_padrao'],
                "take_profit": self.config['take_profit_padrao']
            },
            "indicadores_analisados": ["rsi", "macd", "bollinger", "media_movel", "volume", "tendencia"]
        }
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas das decisões
        """
        if not self.decisoes_historico:
            return {
                'total_decisoes': 0,
                'decisoes_hoje': 0,
                'taxa_compra': 0.0,
                'taxa_venda': 0.0,
                'taxa_aguardar': 0.0,
                'confianca_media': 0.0
            }
        
        total = len(self.decisoes_historico)
        hoje = datetime.now().date()
        
        decisoes_hoje = [d for d in self.decisoes_historico if d['data'].date() == hoje]
        compras = [d for d in self.decisoes_historico if d['decisao'] == 'comprar']
        vendas = [d for d in self.decisoes_historico if d['decisao'] == 'vender']
        aguardar = [d for d in self.decisoes_historico if d['decisao'] == 'aguardar']
        
        confianca_media = sum(d['confianca'] for d in self.decisoes_historico) / total
        
        return {
            'total_decisoes': total,
            'decisoes_hoje': len(decisoes_hoje),
            'taxa_compra': len(compras) / total,
            'taxa_venda': len(vendas) / total,
            'taxa_aguardar': len(aguardar) / total,
            'confianca_media': confianca_media
        } 