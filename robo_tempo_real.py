#!/usr/bin/env python3
"""
Robô de Trading Crypto - Tempo Real
Integra coletor, executor, IA e armazenamento para operação 24/7
"""

import os
import sys
import time
import signal
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any
from loguru import logger

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coletor import ColetorBybit
from executor import ExecutorBybit
from armazenamento import ArmazenamentoCrypto
from ia.preparador_dados import PreparadorDadosCrypto
from ia.decisor import DecisorIA
from ia.llama_cpp_client import LlamaCppClient

class RoboCryptoTempoReal:
    """Robô de trading crypto em tempo real"""
    
    def __init__(self):
        """Inicializa o robô crypto"""
        self.config = self._carregar_config()
        
        # Componentes principais
        self.coletor = ColetorBybit()
        self.executor = ExecutorBybit()
        self.armazenamento = ArmazenamentoCrypto()
        self.preparador = PreparadorDadosCrypto()
        self.ia_client = LlamaCppClient()
        self.decisor = DecisorIA(self.config, ia_client=self.ia_client)
        
        # Controle de execução
        self.executando = False
        self.ultima_analise = {}
        self.contador_ciclos = 0
        self.inicio_execucao = None
        
        # Configurações
        self.frequencia_analise = self.config['coleta']['frequencia']
        self.pares = self.config['trading']['pares']
        self.max_ordens_dia = self.config['trading']['max_ordens_dia']
        self.batch_interval = self.config.get('batch_interval', 60)  # segundos
        
        # Estatísticas
        self.estatisticas = {
            'ciclos_executados': 0,
            'analises_realizadas': 0,
            'ordens_enviadas': 0,
            'erros': 0,
            'inicio': None
        }
        
        # Buffers para batching por par
        self.buffers = {par: [] for par in self.pares}
        self.last_batch_time = {par: 0.0 for par in self.pares}
        
        logger.info("🤖 Robô Crypto inicializado")
    
    def _carregar_config(self) -> dict:
        """Carrega configuração"""
        try:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            return {}
    
    def _configurar_sinais(self):
        """Configura handlers para sinais de interrupção"""
        signal.signal(signal.SIGINT, self._handler_parada)
        signal.signal(signal.SIGTERM, self._handler_parada)
    
    def _handler_parada(self, signum, frame):
        """Handler para parada do robô"""
        logger.info("🛑 Sinal de parada recebido. Finalizando robô...")
        self.parar()
    
    def iniciar(self):
        """Inicia o robô crypto"""
        try:
            logger.info("🚀 Iniciando Robô Crypto...")
            
            # Configurar sinais
            self._configurar_sinais()
            
            # Verificar conectividade
            if not self._verificar_conectividade():
                logger.error("❌ Falha na conectividade. Parando robô.")
                return False
            
            # Inicializar estatísticas
            self.estatisticas['inicio'] = datetime.now()
            self.inicio_execucao = datetime.now()
            self.executando = True
            
            logger.info("✅ Robô iniciado com sucesso!")
            logger.info(f"📊 Pares configurados: {self.pares}")
            logger.info(f"⏱️ Frequência de análise: {self.frequencia_analise}s")
            
            # Loop principal
            self._loop_principal()
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar robô: {e}")
            return False
    
    def _verificar_conectividade(self) -> bool:
        """Verifica conectividade com Bybit"""
        try:
            # Testar coletor
            if not self.coletor.verificar_conectividade():
                logger.error("❌ Falha na conectividade do coletor")
                return False
            
            # Testar executor
            saldo = self.executor._verificar_saldo()
            if saldo is None:
                logger.error("❌ Falha na conectividade do executor")
                return False
            
            logger.info(f"✅ Conectividade OK. Saldo: {saldo} USDT")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de conectividade: {e}")
            return False
    
    def _loop_principal(self):
        """Loop principal do robô"""
        logger.info("🔄 Iniciando loop principal...")
        
        while self.executando:
            try:
                inicio_ciclo = time.time()
                
                # Executar ciclo de análise
                self._executar_ciclo_analise()
                
                # Atualizar estatísticas
                self.contador_ciclos += 1
                self.estatisticas['ciclos_executados'] = self.contador_ciclos
                
                # Aguardar próximo ciclo
                tempo_execucao = time.time() - inicio_ciclo
                tempo_espera = max(0, self.frequencia_analise - tempo_execucao)
                
                if tempo_espera > 0:
                    time.sleep(tempo_espera)
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrupção do usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                self.estatisticas['erros'] += 1
                time.sleep(5)  # Aguardar antes de continuar
    
    def _executar_ciclo_analise(self):
        """Executa um ciclo completo de análise com batching de 1 minuto"""
        try:
            now = time.time()
            for par in self.pares:
                dados_ia = None  # Inicializa como None
                # 1. Coletar dados atuais
                dados_atual = self._coletar_dados_par(par)
                if not dados_atual:
                    continue
                # Adicionar ao buffer
                self.buffers[par].append(dados_atual)
                # Checar se passou o intervalo de batch
                if now - self.last_batch_time[par] >= self.batch_interval:
                    # Preparar batch para IA (exemplo: usar o último dado, ou agregar)
                    # Aqui, vamos preparar dados usando o último dado, mas pode ser customizado para enviar o batch inteiro
                    dados_ia = self.preparador.preparar_dados_analise_crypto(self.buffers[par][-1], 50)
                if not dados_ia:
                    self.buffers[par] = []
                    self.last_batch_time[par] = now
                    continue
                # 3. Analisar com IA
                decisao = self._analisar_com_ia(dados_ia)
                if decisao:
                    # 4. Executar decisão
                    self._executar_decisao(par, decisao)
                    self.estatisticas['analises_realizadas'] += 1
                    # Limpar buffer e atualizar tempo
                    self.buffers[par] = []
                    self.last_batch_time[par] = now
        except Exception as e:
            logger.error(f"❌ Erro no ciclo de análise: {e}")
            self.estatisticas['erros'] += 1
    
    def _coletar_dados_par(self, par: str) -> Dict[str, Any]:
        """Coleta dados para um par específico"""
        try:
            # Obter preço atual
            preco_atual = self.coletor.obter_preco_atual(par)
            if not preco_atual:
                return {}
            
            # Obter dados históricos recentes
            dados_historicos = self.coletor.obter_dados_rest(par, "5", 1)
            if dados_historicos is None or dados_historicos.empty:
                return {}
            
            # Estruturar dados
            dados_atual = {
                'symbol': par.replace("/", ""),
                'timestamp': datetime.now().isoformat(),
                'close_price': preco_atual,
                'volume': float(dados_historicos.iloc[0]['volume']),
                'interval': '5m'
            }
            
            # Salvar no banco
            self.armazenamento.salvar_precos_crypto(
                symbol=dados_atual['symbol'],
                timestamp=datetime.now(),
                open_price=float(dados_historicos.iloc[0]['open']),
                high_price=float(dados_historicos.iloc[0]['high']),
                low_price=float(dados_historicos.iloc[0]['low']),
                close_price=preco_atual,
                volume=float(dados_historicos.iloc[0]['volume']),
                interval='5m'
            )
            
            return dados_atual
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados para {par}: {e}")
            return {}
    
    def _analisar_com_ia(self, dados_ia: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa dados com IA"""
        try:
            # Preparar prompt para crypto
            prompt = self._preparar_prompt_crypto(dados_ia)
            
            # Obter decisão da IA - usar dados_ia diretamente
            decisao_ia = self.ia_client.analisar_dados_mercado(dados_ia)
            
            if decisao_ia:
                # Processar decisão com filtros de segurança
                resposta = self.decisor.processar_decisao_ia(decisao_ia, dados_ia)
            else:
                resposta = None
            
            if resposta:
                # Salvar análise
                self.armazenamento.salvar_analise_crypto(
                    symbol=dados_ia.get('symbol', 'BTCUSDT'),
                    dados_entrada=dados_ia,
                    resultado=resposta['decisao'],
                    confianca=resposta.get('confianca')
                )
                return resposta
            return {}
        except Exception as e:
            logger.error(f"❌ Erro na análise com IA: {e}")
            return {}
    
    def _preparar_prompt_crypto(self, dados_ia: Dict[str, Any]) -> str:
        """Prepara prompt específico para crypto"""
        try:
            # A estrutura retornada pelo preparador_dados.py é diferente
            symbol = dados_ia.get('symbol', 'BTCUSDT')
            preco_atual = dados_ia.get('preco_atual', 0.0)
            volume = dados_ia.get('volume', 0.0)
            timestamp = dados_ia.get('timestamp', '')
            rsi = dados_ia.get('rsi', 50.0)
            ma_20 = dados_ia.get('ma_20', 0.0)
            ma_50 = dados_ia.get('ma_50', 0.0)
            volatilidade = dados_ia.get('volatilidade', 0.0)
            tendencia = dados_ia.get('tendencia', 'lateral')
            historico = dados_ia.get('historico', [])
            
            prompt = f"""
            ANÁLISE DE TRADING CRYPTO - {symbol}
            
            DADOS ATUAIS:
            - Preço: ${preco_atual:,.2f}
            - Volume: {volume:,.2f}
            - Timestamp: {timestamp}
            
            INDICADORES TÉCNICOS:
            - RSI: {rsi}
            - MA20: ${ma_20:,.2f}
            - MA50: ${ma_50:,.2f}
            - Volatilidade: {volatilidade:.2f}%
            - Tendência: {tendencia}
            
            HISTÓRICO RECENTE:
            {historico}
            
            CONTEXTO:
            - Mercado: Crypto 24/7
            - Alta volatilidade
            - Liquidez imediata
            - Spread baixo
            
            INSTRUÇÕES:
            Analise os dados acima e forneça uma decisão de trading para {symbol}.
            
            RESPOSTA FORMATO JSON:
            {{
                "decisao": "comprar|vender|aguardar",
                "confianca": 0.0-1.0,
                "razao": "explicação da decisão",
                "quantidade": 1,
                "stop_loss": preco_stop_loss,
                "take_profit": preco_take_profit,
                "acao_ordem": "manter"
            }}
            """
            
            return prompt
            
        except Exception as e:
            logger.error(f"❌ Erro ao preparar prompt: {e}")
            return ""
    
    def _executar_decisao(self, par: str, decisao: Dict[str, Any]):
        """Executa decisão da IA"""
        try:
            acao = decisao.get('decisao', '').upper()
            confianca = decisao.get('confianca')
            if confianca is None:
                confianca = 0.0
            
            # Verificar confiança mínima
            if confianca < 0.7:
                logger.info(f"⚠️ Confiança baixa ({confianca:.2f}) para {par}. Aguardando...")
                return
            
            # Verificar limite de ordens
            if self.estatisticas['ordens_enviadas'] >= self.max_ordens_dia:
                logger.warning(f"⚠️ Limite de {self.max_ordens_dia} ordens diárias atingido")
                return
            
            if acao == "COMPRAR":
                self._executar_compra(par, decisao)
            elif acao == "VENDER":
                self._executar_venda(par, decisao)
            elif acao == "AGUARDAR":
                logger.info(f"⏳ Aguardando melhor oportunidade para {par}")
            else:
                logger.warning(f"⚠️ Decisão desconhecida: {acao}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar decisão: {e}")
    
    def _executar_compra(self, par: str, decisao: Dict[str, Any]):
        """Executa ordem de compra"""
        try:
            logger.info(f"📈 Executando COMPRA para {par}")
            
            # Enviar ordem market
            resultado = self.executor.enviar_ordem_market(par, "Buy")
            
            if resultado:
                # Salvar ordem
                self.armazenamento.salvar_ordem_crypto(
                    symbol=par.replace("/", ""),
                    order_id=resultado.get('orderId', ''),
                    side='Buy',
                    order_type='Market',
                    qty=resultado.get('qty', 0),
                    price=resultado.get('avgPrice', 0),
                    status=resultado.get('orderStatus', 'New')
                )
                
                self.estatisticas['ordens_enviadas'] += 1
                logger.success(f"✅ Compra executada para {par}")
            else:
                logger.error(f"❌ Falha na execução da compra para {par}")
                
        except Exception as e:
            logger.error(f"❌ Erro na execução da compra: {e}")
    
    def _executar_venda(self, par: str, decisao: Dict[str, Any]):
        """Executa ordem de venda"""
        try:
            logger.info(f"📉 Executando VENDA para {par}")
            
            # Verificar se há posição para vender
            posicoes = self.executor.obter_posicoes(par)
            if not posicoes or all(float(pos['size']) == 0 for pos in posicoes):
                logger.warning(f"⚠️ Nenhuma posição para vender em {par}")
                return
            
            # Enviar ordem market
            resultado = self.executor.enviar_ordem_market(par, "Sell")
            
            if resultado:
                # Salvar ordem
                self.armazenamento.salvar_ordem_crypto(
                    symbol=par.replace("/", ""),
                    order_id=resultado.get('orderId', ''),
                    side='Sell',
                    order_type='Market',
                    qty=resultado.get('qty', 0),
                    price=resultado.get('avgPrice', 0),
                    status=resultado.get('orderStatus', 'New')
                )
                
                self.estatisticas['ordens_enviadas'] += 1
                logger.success(f"✅ Venda executada para {par}")
            else:
                logger.error(f"❌ Falha na execução da venda para {par}")
                
        except Exception as e:
            logger.error(f"❌ Erro na execução da venda: {e}")
    
    def parar(self):
        """Para o robô"""
        logger.info("🛑 Parando robô...")
        self.executando = False
        
        # Parar coletor
        if hasattr(self.coletor, 'parar_websocket'):
            self.coletor.parar_websocket()
        
        # Cancelar ordens pendentes
        for par in self.pares:
            try:
                self.executor.cancelar_todas_ordens(par)
            except:
                pass
        
        # Exibir estatísticas finais
        self._exibir_estatisticas_finais()
        
        logger.info("✅ Robô parado com sucesso")
    
    def _exibir_estatisticas_finais(self):
        """Exibe estatísticas finais"""
        if self.inicio_execucao:
            duracao = datetime.now() - self.inicio_execucao
            
            logger.info("📊 ESTATÍSTICAS FINAIS")
            logger.info("=" * 40)
            logger.info(f"⏱️ Duração: {duracao}")
            logger.info(f"🔄 Ciclos executados: {self.estatisticas['ciclos_executados']}")
            logger.info(f"📈 Análises realizadas: {self.estatisticas['analises_realizadas']}")
            logger.info(f"📤 Ordens enviadas: {self.estatisticas['ordens_enviadas']}")
            logger.info(f"❌ Erros: {self.estatisticas['erros']}")
            
            # Calcular métricas por par
            for par in self.pares:
                metricas = self.armazenamento.calcular_metricas_crypto(par.replace("/", ""))
                if metricas:
                    logger.info(f"📊 {par}: Win Rate {metricas.get('win_rate', 0):.1f}%, PnL {metricas.get('total_pnl', 0):.2f}")

def main():
    """Função principal"""
    try:
        robô = RoboCryptoTempoReal()
        robô.iniciar()
        
    except KeyboardInterrupt:
        logger.info("Interrupção do usuário")
    except Exception as e:
        logger.error(f"Erro geral: {e}")

if __name__ == "__main__":
    main() 