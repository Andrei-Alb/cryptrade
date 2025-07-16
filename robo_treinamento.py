#!/usr/bin/env python3
"""
Robô de Treinamento da IA
Treina a IA com ordens simuladas e aprende com os resultados
"""

import os
import sys
import time
import signal
import yaml  # type: ignore
from datetime import datetime, timedelta
from typing import Dict, Any
from loguru import logger

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coletor import ColetorBybit
from executor_simulado import ExecutorSimulado
from armazenamento import ArmazenamentoCrypto
from ia.preparador_dados import PreparadorDadosCrypto
from ia.decisor import DecisorIA
from ia.llama_cpp_client import LlamaCppClient
from ia.sistema_aprendizado_autonomo import SistemaAprendizadoAutonomo

class RoboTreinamento:
    """Robô de treinamento da IA com simulação"""
    
    def __init__(self):
        """Inicializa o robô de treinamento"""
        self.config = self._carregar_config()
        
        # Componentes principais
        self.coletor = ColetorBybit()
        self.executor = ExecutorSimulado(self.config)
        self.armazenamento = ArmazenamentoCrypto()
        self.preparador = PreparadorDadosCrypto()
        self.ia_client = LlamaCppClient()
        self.decisor = DecisorIA(self.config, sistema_aprendizado=self.sistema_aprendizado, ia_client=self.ia_client)
        self.sistema_aprendizado = SistemaAprendizadoAutonomo()
        
        # Controle de execução
        self.executando = False
        self.ultima_analise = {}
        self.contador_ciclos = 0
        self.inicio_execucao = None
        
        # Configurações
        self.frequencia_analise = self.config['coleta']['frequencia']
        self.pares = self.config['trading']['pares']
        self.max_ordens_dia = self.config['trading']['max_ordens_dia']
        
        # Estatísticas de treinamento
        self.estatisticas = {
            'ciclos_executados': 0,
            'analises_realizadas': 0,
            'ordens_simuladas': 0,
            'decisoes_ia': 0,
            'erros': 0,
            'inicio': None
        }
        
        logger.info("🎓 Robô de Treinamento inicializado")
    
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
        logger.info("🛑 Sinal de parada recebido. Finalizando treinamento...")
        self.parar()
    
    def iniciar(self):
        """Inicia o treinamento da IA"""
        try:
            logger.info("🎓 Iniciando Treinamento da IA...")
            
            # Configurar sinais
            self._configurar_sinais()
            
            # Verificar conectividade
            if not self._verificar_conectividade():
                logger.error("❌ Falha na conectividade. Parando treinamento.")
                return False
            
            # Inicializar estatísticas
            self.estatisticas['inicio'] = datetime.now()
            self.inicio_execucao = datetime.now()
            self.executando = True
            
            logger.info("✅ Treinamento iniciado com sucesso!")
            logger.info(f"📊 Pares configurados: {self.pares}")
            logger.info(f"⏱️ Frequência de análise: {self.frequencia_analise}s")
            logger.info(f"🎮 Modo: SIMULAÇÃO (capital: ${self.executor.capital_atual:.2f})")
            
            # Loop principal
            self._loop_principal()
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar treinamento: {e}")
            return False
    
    def _verificar_conectividade(self) -> bool:
        """Verifica conectividade com Bybit"""
        try:
            # Testar coletor
            if not self.coletor.verificar_conectividade():
                logger.error("❌ Falha na conectividade do coletor")
                return False
            
            logger.info(f"✅ Conectividade OK. Capital simulado: ${self.executor.capital_atual:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de conectividade: {e}")
            return False
    
    def _loop_principal(self):
        """Loop principal do treinamento"""
        logger.info("🔄 Iniciando loop de treinamento...")
        
        while self.executando:
            try:
                inicio_ciclo = time.time()
                
                # Executar ciclo de análise
                self._executar_ciclo_treinamento()
                
                # Atualizar estatísticas
                self.contador_ciclos += 1
                self.estatisticas['ciclos_executados'] = self.contador_ciclos
                
                # Exibir estatísticas periodicamente
                if self.contador_ciclos % 10 == 0:
                    self._exibir_estatisticas_treinamento()
                
                # Aguardar próximo ciclo
                tempo_execucao = time.time() - inicio_ciclo
                tempo_espera = max(0, self.frequencia_analise - tempo_execucao)
                
                if tempo_espera > 0:
                    time.sleep(tempo_espera)
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrupção do usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de treinamento: {e}")
                self.estatisticas['erros'] += 1
                time.sleep(5)  # Aguardar antes de continuar
    
    def _executar_ciclo_treinamento(self):
        """Executa um ciclo completo de treinamento"""
        try:
            for par in self.pares:
                # 1. Coletar dados atuais
                dados_atual = self._coletar_dados_par(par)
                if not dados_atual:
                    continue

                # 2. Preparar dados para IA
                dados_ia = self.preparador.preparar_dados_analise_crypto(dados_atual, 50)
                if not dados_ia:
                    continue

                # 3. Analisar com IA
                decisao = self._analisar_com_ia(dados_ia)
                if not decisao:
                    continue

                # 4. Registrar decisão autônoma da IA
                self.sistema_aprendizado.registrar_decisao_autonoma(par.replace("/", ""), decisao, dados_ia['dados_mercado'])
                # Se existir salvar_decisao_ia, chame. Caso contrário, ignore.
                salvar_decisao = getattr(self.executor, 'salvar_decisao_ia', None)
                if callable(salvar_decisao):
                    salvar_decisao(par.replace("/", ""), decisao, dados_ia['dados_mercado'])
                self.estatisticas['decisoes_ia'] += 1

                # 5. Executar decisão (simulada)
                self._executar_decisao_simulada(par, decisao)

                # 6. Atualizar estatísticas
                self.estatisticas['analises_realizadas'] += 1

        except Exception as e:
            logger.error(f"❌ Erro no ciclo de treinamento: {e}")
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
            # Obter decisão da IA
            decisao_ia = self.ia_client.analisar_dados_mercado(dados_ia['dados_mercado'])
            if decisao_ia:
                # Processar decisão com filtros de segurança
                resposta = self.decisor.processar_decisao_ia(decisao_ia, dados_ia['dados_mercado'])
            else:
                resposta = None
            if resposta:
                logger.info(f"🧠 IA: {resposta['decisao']} (confiança: {resposta['confianca']:.2f})")
                return resposta
            return {}
        except Exception as e:
            logger.error(f"❌ Erro na análise com IA: {e}")
            return {}
    
    def _executar_decisao_simulada(self, par: str, decisao: Dict[str, Any]):
        """Executa decisão da IA em modo simulado"""
        try:
            acao = decisao.get('decisao', '').upper()
            confianca = decisao.get('confianca', 0)
            
            # Verificar apenas ruído puro (confiança muito baixa)
            if confianca < 0.2:
                logger.info(f"⚠️ Confiança muito baixa ({confianca:.2f}) para {par}. Aguardando...")
                return
            
            # Verificar limite de ordens
            if self.estatisticas['ordens_simuladas'] >= self.max_ordens_dia:
                logger.warning(f"⚠️ Limite de {self.max_ordens_dia} ordens diárias atingido")
                return
            
            if acao == "COMPRAR":
                self._executar_compra_simulada(par, decisao)
            elif acao == "VENDER":
                self._executar_venda_simulada(par, decisao)
            elif acao == "AGUARDAR":
                logger.info(f"⏳ Aguardando melhor oportunidade para {par}")
            else:
                logger.warning(f"⚠️ Decisão desconhecida: {acao}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar decisão simulada: {e}")
    
    def _executar_compra_simulada(self, par: str, decisao: Dict[str, Any]):
        """Executa ordem de compra simulada"""
        try:
            logger.info(f"🎮 Executando COMPRA simulada para {par}")
            
            # Enviar ordem market simulada
            qty = self.config['trading']['quantidade_padrao']
            resultado = self.executor.enviar_ordem_market(par.replace("/", ""), "Buy", qty=qty)
            
            if resultado:
                self.estatisticas['ordens_simuladas'] += 1
                logger.success(f"✅ Compra simulada executada para {par}")
                logger.info(f"💰 Capital atual: ${resultado['capital_atual']:.2f}")
            else:
                logger.error(f"❌ Falha na execução da compra simulada para {par}")
                
        except Exception as e:
            logger.error(f"❌ Erro na execução da compra simulada: {e}")
    
    def _executar_venda_simulada(self, par: str, decisao: Dict[str, Any]):
        """Executa ordem de venda simulada"""
        try:
            logger.info(f"🎮 Executando VENDA simulada para {par}")
            
            # Verificar se há posição para vender
            # Se existir obter_posicoes, use. Caso contrário, simule lista vazia.
            obter_posicoes = getattr(self.executor, 'obter_posicoes', None)
            if callable(obter_posicoes):
                posicoes = obter_posicoes(par.replace("/", ""))
                if not isinstance(posicoes, list):
                    posicoes = []
            else:
                posicoes = []
            if not posicoes or all(float(pos.get('size', 0)) == 0 for pos in posicoes):
                logger.warning(f"⚠️ Nenhuma posição para vender em {par}")
                return
            
            # Enviar ordem market simulada
            qty = self.config['trading']['quantidade_padrao']
            resultado = self.executor.enviar_ordem_market(par.replace("/", ""), "Sell", qty=qty)
            
            if resultado:
                self.estatisticas['ordens_simuladas'] += 1
                logger.success(f"✅ Venda simulada executada para {par}")
                logger.info(f"💰 Capital atual: ${resultado['capital_atual']:.2f}")
            else:
                logger.error(f"❌ Falha na execução da venda simulada para {par}")
                
        except Exception as e:
            logger.error(f"❌ Erro na execução da venda simulada: {e}")
    
    def _exibir_estatisticas_treinamento(self):
        """Exibe estatísticas do treinamento"""
        # Se existir obter_estatisticas, use. Caso contrário, simule um dicionário padrão.
        obter_estatisticas = getattr(self.executor, 'obter_estatisticas', None)
        if callable(obter_estatisticas):
            stats_executor = obter_estatisticas()
            if not isinstance(stats_executor, dict):
                stats_executor = {
                    'capital_atual': 0.0,
                    'win_rate': 0.0,
                    'profit_factor': 0.0,
                    'total_operacoes': 0
                }
        else:
            stats_executor = {
                'capital_atual': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'total_operacoes': 0
            }
        
        logger.info("📊 ESTATÍSTICAS DE TREINAMENTO")
        logger.info("=" * 50)
        logger.info(f"🔄 Ciclos: {self.estatisticas['ciclos_executados']}")
        logger.info(f"🧠 Análises IA: {self.estatisticas['analises_realizadas']}")
        logger.info(f"📈 Decisões IA: {self.estatisticas['decisoes_ia']}")
        logger.info(f"🎮 Ordens simuladas: {self.estatisticas['ordens_simuladas']}")
        logger.info(f"💰 Capital: ${stats_executor['capital_atual']:.2f}")
        logger.info(f"📊 Win Rate: {stats_executor['win_rate']:.2%}")
        logger.info(f"📈 Profit Factor: {stats_executor['profit_factor']:.2f}")
        logger.info(f"📊 Operações: {stats_executor['total_operacoes']}")
        logger.info(f"❌ Erros: {self.estatisticas['erros']}")
        logger.info("=" * 50)
    
    def parar(self):
        """Para o treinamento"""
        logger.info("🛑 Parando treinamento...")
        self.executando = False
        
        # Parar coletor
        if hasattr(self.coletor, 'parar_websocket'):
            self.coletor.parar_websocket()
        
        # Exibir estatísticas finais
        self._exibir_estatisticas_finais()
        
        logger.info("✅ Treinamento parado com sucesso")
    
    def _exibir_estatisticas_finais(self):
        """Exibe estatísticas finais do treinamento"""
        if self.inicio_execucao:
            duracao = datetime.now() - self.inicio_execucao
            # Se existir obter_estatisticas, use. Caso contrário, simule um dicionário padrão.
            obter_estatisticas = getattr(self.executor, 'obter_estatisticas', None)
            if callable(obter_estatisticas):
                stats_executor = obter_estatisticas()
                if not isinstance(stats_executor, dict):
                    stats_executor = {
                        'capital_atual': 0.0,
                        'win_rate': 0.0,
                        'profit_factor': 0.0,
                        'total_operacoes': 0
                    }
            else:
                stats_executor = {
                    'capital_atual': 0.0,
                    'win_rate': 0.0,
                    'profit_factor': 0.0,
                    'total_operacoes': 0
                }
            
            logger.info("📊 ESTATÍSTICAS FINAIS DO TREINAMENTO")
            logger.info("=" * 60)
            logger.info(f"⏱️ Duração: {duracao}")
            logger.info(f"🔄 Ciclos executados: {self.estatisticas['ciclos_executados']}")
            logger.info(f"🧠 Análises realizadas: {self.estatisticas['analises_realizadas']}")
            logger.info(f"📈 Decisões IA: {self.estatisticas['decisoes_ia']}")
            logger.info(f"🎮 Ordens simuladas: {self.estatisticas['ordens_simuladas']}")
            logger.info(f"❌ Erros: {self.estatisticas['erros']}")
            logger.info("")
            logger.info("💰 RESULTADOS FINANCEIROS:")
            logger.info(f"Capital inicial: ${self.config['simulacao']['capital_inicial']:.2f}")
            logger.info(f"Capital final: ${stats_executor['capital_atual']:.2f}")
            logger.info(f"Resultado: ${stats_executor['capital_atual'] - self.config['simulacao']['capital_inicial']:.2f}")
            logger.info(f"Win Rate: {stats_executor['win_rate']:.2%}")
            logger.info(f"Profit Factor: {stats_executor['profit_factor']:.2f}")
            logger.info(f"Total operações: {stats_executor['total_operacoes']}")
            logger.info("=" * 60)

def main():
    """Função principal"""
    try:
        # Configurar logging
        logger.add("logs/treinamento_{time}.log", rotation="1 day", retention="7 days")
        
        # Criar e iniciar robô
        robo = RoboTreinamento()
        robo.iniciar()
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrupção do usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main() 