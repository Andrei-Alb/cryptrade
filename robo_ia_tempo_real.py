#!/usr/bin/env python3
"""
Robô de Trading com IA em Tempo Real
Coleta dados da B3 e analisa com IA para decisões precisas
"""

import time
import signal
import sys
from datetime import datetime, time as dt_time
from loguru import logger
import os
import json

# Configurar logging
os.makedirs('logs', exist_ok=True)
logger.add("logs/robo_ia_tempo_real.log", rotation="1 week")

from coletor import Coletor
from armazenamento import Armazenamento
from analisador import AnalisadorIA
from executor import ExecutorOrdensSimuladas
from ia.gestor_ordens import GestorOrdensIA
from ia.sistema_aprendizado import SistemaAprendizado
import config

class RoboIATempoReal:
    def __init__(self):
        """
        Inicializa o robô de IA em tempo real
        """
        self.config = config.load_config()
        self.coletor = Coletor()
        self.armazenamento = Armazenamento()
        self.analisador = AnalisadorIA(self.config)
        self.executor = ExecutorOrdensSimuladas()
        self.gestor_ordens = GestorOrdensIA()
        self.sistema_aprendizado = SistemaAprendizado()
        
        # Configurações de operação
        self.frequencia_coleta = 5  # segundos - coleta de dados da B3 (ajustado para 5 segundos)
        self.frequencia_analise = 15  # segundos - análise com IA
        self.rodando = True
        self.falhas_consecutivas = 0
        self.max_falhas_consecutivas = 5
        
        # Buffer para dados acumulados
        self.dados_buffer = []
        self.ultima_analise = datetime.now()
        
        # Configurações de horário de mercado
        self.horario_inicio = dt_time(9, 0)  # 09:00
        self.horario_fim = dt_time(17, 0)    # 17:00
        self.dias_semana = [0, 1, 2, 3, 4]  # Segunda a Sexta (0=Segunda)
        
        # Métricas
        self.metricas = {
            'inicio': datetime.now(),
            'ciclos': 0,
            'analises_ia': 0,
            'decisoes_compra': 0,
            'decisoes_venda': 0,
            'decisoes_aguardar': 0,
            'ordens_executadas': 0,
            'falhas': 0
        }
        
        # Configura handlers para graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🤖 Robô de IA em Tempo Real inicializado")
    
    def signal_handler(self, signum, frame):
        """
        Handler para graceful shutdown
        """
        logger.info(f"Recebido sinal {signum}. Encerrando robô...")
        self.rodando = False
    
    def esta_horario_mercado(self):
        """
        Verifica se está no horário de mercado
        """
        agora = datetime.now()
        return (
            agora.weekday() in self.dias_semana and
            self.horario_inicio <= agora.time() <= self.horario_fim
        )
    
    def coletar_dados(self):
        """
        Coleta dados da B3 e armazena no buffer
        """
        try:
            # Coletar dados reais da B3
            dados_coletados = self.coletor.coletar_dados()
            
            if not dados_coletados:
                logger.error("❌ NENHUM dado real da B3 foi coletado.")
                self.falhas_consecutivas += 1
                self.metricas['falhas'] += 1
                return False
            
            # Salvar dados no banco e adicionar ao buffer
            for dados in dados_coletados:
                self.armazenamento.salvar_precos(
                    timestamp=dados['timestamp'],
                    preco_atual=dados['preco_atual'],
                    preco_abertura=dados.get('preco_abertura'),
                    preco_minimo=dados.get('preco_minimo'),
                    preco_maximo=dados.get('preco_maximo'),
                    preco_medio=dados.get('preco_medio'),
                    variacao=dados.get('variacao'),
                    volume=dados.get('volume', 0),
                    simbolo=dados['simbolo']
                )
                
                # Adicionar ao buffer para análise posterior
                self.dados_buffer.append(dados)
            
            # Manter apenas os últimos 30 dados no buffer
            if len(self.dados_buffer) > 30:
                self.dados_buffer = self.dados_buffer[-30:]
            
            self.falhas_consecutivas = 0
            return True
            
        except Exception as e:
            self.falhas_consecutivas += 1
            self.metricas['falhas'] += 1
            logger.error(f"❌ Erro na coleta: {e}")
            return False
    
    def analisar_dados_acumulados(self):
        """
        Analisa dados acumulados no buffer com IA
        """
        try:
            if not self.dados_buffer:
                logger.info("📊 Buffer vazio, aguardando dados...")
                return
            
            # Pegar o dado mais recente para análise
            dados_recente = self.dados_buffer[-1]
            
            if not dados_recente['simbolo'].startswith('WIN'):
                return
            
            logger.info(f"🤖 Analisando {dados_recente['simbolo']} com IA (dados acumulados: {len(self.dados_buffer)})")
            
            # Verificar ordens ativas com gestor inteligente
            self.verificar_ordens_ativas_inteligente(dados_recente)
            
            # Verificar se já existe ordem ativa para o símbolo
            ordens_ativas = [o for o in self.gestor_ordens.ordens_ativas.values() if o['simbolo'] == dados_recente['simbolo']]
            ordem_aberta = len(ordens_ativas) > 0
            
            # Analisar com IA
            analise = self.analisador.analisar_com_ia(dados_recente)
            self.metricas['analises_ia'] += 1
            
            # Log da análise
            logger.info(f"📈 {dados_recente['simbolo']}: {dados_recente['preco_atual']} | "
                       f"IA: {analise['decisao'].upper()} | "
                       f"Confiança: {analise['confianca']:.2f}")
            
            # Salvar análise no banco
            self.armazenamento.salvar_analise(
                json.dumps(dados_recente),
                json.dumps(analise),
                float(analise.get('confianca', 0.0))
            )
            
            # Contar decisões
            if analise['decisao'] == 'comprar':
                self.metricas['decisoes_compra'] += 1
            elif analise['decisao'] == 'vender':
                self.metricas['decisoes_venda'] += 1
            else:
                self.metricas['decisoes_aguardar'] += 1
            
            # Obter parâmetros otimizados do sistema de aprendizado
            parametros_otimizados = self.sistema_aprendizado.obter_parametros_otimizados()
            threshold_confianca = parametros_otimizados.get('threshold_confianca', 0.6)
            
            # Executar ordem simulada se decisão for compra/venda e confiança >= threshold otimizado
            if analise['decisao'] in ['comprar', 'vender'] and analise['confianca'] >= threshold_confianca:
                logger.info(f"🚀 Executando ordem simulada: {analise['decisao']} {dados_recente['simbolo']}")
                
                resultado_execucao = self.executor.executar_ordem_simulada(analise, dados_recente)
                
                if resultado_execucao['status'] == 'executada':
                    self.metricas['ordens_executadas'] += 1
                    
                    # Adicionar ordem ao gestor para monitoramento inteligente
                    ordem_completa = {
                        'ordem_id': resultado_execucao['ordem_id'],
                        'timestamp': datetime.now(),
                        'tipo': analise['decisao'],
                        'simbolo': dados_recente['simbolo'],
                        'preco_entrada': dados_recente['preco_atual'],
                        'preco_alvo': resultado_execucao['preco_alvo'],
                        'preco_stop': resultado_execucao['preco_stop'],
                        'confianca_ia': analise['confianca']
                    }
                    self.gestor_ordens.adicionar_ordem_ativa(ordem_completa)
                    
                    logger.success(f"✅ Ordem simulada executada: {analise['decisao']} {dados_recente['simbolo']} "
                                  f"@ {dados_recente['preco_atual']} | Alvo: {resultado_execucao['preco_alvo']:.2f} "
                                  f"| Stop: {resultado_execucao['preco_stop']:.2f}")
                else:
                    logger.warning(f"⚠️ Falha na execução: {resultado_execucao.get('razao', 'Erro desconhecido')}")
            
            # Limpar buffer após análise
            self.dados_buffer = []
            self.ultima_analise = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
    
    def verificar_ordens_ativas_inteligente(self, dados_mercado):
        """
        Verifica ordens ativas usando gestor inteligente
        """
        try:
            # Analisar ordens ativas com gestor
            decisoes_saida = self.gestor_ordens.analisar_ordens_ativas(dados_mercado)
            
            # Processar decisões de saída
            for decisao_saida in decisoes_saida:
                if decisao_saida['decisao'] in ['sair_lucro', 'sair_perda', 'sair_timeout']:
                    # Fechar ordem no executor
                    ordem = decisao_saida['ordem']
                    duracao = (datetime.now() - ordem['timestamp']).total_seconds()
                    
                    # Mapear decisão para resultado
                    if decisao_saida['decisao'] == 'sair_lucro':
                        resultado = 'win'
                    elif decisao_saida['decisao'] == 'sair_perda':
                        resultado = 'loss'
                    else:  # timeout
                        resultado = 'win' if decisao_saida['lucro_percentual'] > 0 else 'loss'
                    
                    # Fechar ordem no executor
                    self.executor.fechar_ordem_simulada(
                        decisao_saida['ordem_id'],
                        resultado,
                        decisao_saida['lucro_percentual'],
                        duracao,
                        decisao_saida['razao']
                    )
                    
                    # Registrar aprendizado no sistema
                    ordem_completa = {
                        'ordem_id': decisao_saida['ordem_id'],
                        'tipo': ordem['tipo'],
                        'confianca_ia': ordem['confianca_ia'],
                        'duracao_segundos': duracao,
                        'razao_fechamento': decisao_saida['razao']
                    }
                    
                    self.sistema_aprendizado.registrar_aprendizado_ordem(
                        ordem_completa,
                        resultado,
                        decisao_saida['lucro_percentual'],
                        dados_mercado
                    )
                    
                    # Registrar aprendizado no gestor
                    self.gestor_ordens.registrar_aprendizado_saida(ordem, decisao_saida)
                    
                    # Remover do gestor
                    self.gestor_ordens.remover_ordem_ativa(decisao_saida['ordem_id'])
                    
                    logger.info(f"🎯 Ordem fechada por gestor inteligente: {decisao_saida['ordem_id']} | "
                               f"Resultado: {resultado} | Lucro: {decisao_saida['lucro_percentual']:.2f}%")
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação inteligente de ordens: {e}")
    
    def ajustar_parametros_automaticamente(self):
        """
        Ajusta parâmetros automaticamente baseado no aprendizado
        """
        try:
            logger.info("🔧 Iniciando ajuste automático de parâmetros...")
            
            # Analisar desempenho e ajustar parâmetros
            resultado = self.sistema_aprendizado.ajustar_parametros_automaticamente()
            
            if 'ajustes_aplicados' in resultado:
                logger.info("✅ Ajustes automáticos aplicados:")
                for parametro, valor in resultado['ajustes_aplicados'].items():
                    logger.info(f"   {parametro}: {valor}")
            else:
                logger.info(f"ℹ️ {resultado.get('mensagem', 'Nenhum ajuste necessário')}")
                
        except Exception as e:
            logger.error(f"❌ Erro no ajuste automático: {e}")
    
    def exibir_status(self):
        """
        Exibe status do robô
        """
        agora = datetime.now()
        tempo_execucao = agora - self.metricas['inicio']
        
        logger.info("=" * 60)
        logger.info("📊 STATUS DO ROBÔ DE IA")
        logger.info("=" * 60)
        logger.info(f"🕐 Tempo de execução: {tempo_execucao}")
        logger.info(f"🔄 Ciclos executados: {self.metricas['ciclos']}")
        logger.info(f"🤖 Análises IA: {self.metricas['analises_ia']}")
        logger.info(f"📈 Decisões compra: {self.metricas['decisoes_compra']}")
        logger.info(f"📉 Decisões venda: {self.metricas['decisoes_venda']}")
        logger.info(f"⏸️ Decisões aguardar: {self.metricas['decisoes_aguardar']}")
        logger.info(f"🚀 Ordens executadas: {self.metricas['ordens_executadas']}")
        logger.info(f"❌ Falhas: {self.metricas['falhas']}")
        
        # Estatísticas da IA
        stats_ia = self.analisador.obter_estatisticas()
        logger.info(f"📊 Confiança média IA: {stats_ia.get('confianca_media', 0):.2f}")
        
        # Estatísticas do executor
        stats_executor = self.executor.obter_estatisticas_aprendizado()
        logger.info(f"📈 Total ordens: {stats_executor.get('total_ordens', 0)}")
        logger.info(f"🟢 Wins: {stats_executor.get('wins', 0)}")
        logger.info(f"🔴 Losses: {stats_executor.get('losses', 0)}")
        logger.info(f"📊 Taxa acerto: {stats_executor.get('taxa_acerto', 0):.1f}%")
        logger.info(f"💰 Lucro total: {stats_executor.get('lucro_total', 0):.2f}%")
        logger.info(f"📋 Ordens ativas: {stats_executor.get('ordens_ativas', 0)}")
        
        # Estatísticas do gestor de ordens
        stats_gestor = self.gestor_ordens.obter_estatisticas_saida()
        logger.info(f"🎯 Total saídas: {stats_gestor.get('total_saidas', 0)}")
        logger.info(f"📊 Taxa acerto saídas: {stats_gestor.get('taxa_acerto_geral', 0):.1f}%")
        logger.info(f"📋 Ordens no gestor: {stats_gestor.get('ordens_ativas', 0)}")
        
        # Estatísticas do sistema de aprendizado
        stats_aprendizado = self.sistema_aprendizado.obter_estatisticas_aprendizado()
        logger.info(f"🧠 Registros aprendizado: {stats_aprendizado.get('total_registros_aprendizado', 0)}")
        logger.info(f"📈 Taxa acerto geral: {stats_aprendizado.get('taxa_acerto_geral', 0):.1f}%")
        logger.info(f"🔧 Ajustes realizados: {stats_aprendizado.get('total_ajustes_realizados', 0)}")
        
        # Threshold atual
        parametros = self.sistema_aprendizado.obter_parametros_otimizados()
        logger.info(f"⚙️ Threshold confiança: {parametros.get('threshold_confianca', 0.6):.2f}")
        
        # Status da conexão
        if self.analisador.testar_conexao():
            logger.info("✅ Conexão com Ollama: OK")
        else:
            logger.warning("⚠️ Conexão com Ollama: PROBLEMA")
        
        logger.info("=" * 60)
    
    def executar(self):
        """
        Executa o robô de IA em tempo real
        """
        logger.info("🚀 Iniciando Robô de IA em Tempo Real")
        logger.info(f"⏰ Coleta de dados: {self.frequencia_coleta} segundo")
        logger.info(f"🤖 Análise IA: {self.frequencia_analise} segundos")
        logger.info(f"🕐 Horário de mercado: {self.horario_inicio} - {self.horario_fim}")
        logger.info(f"📅 Dias úteis: Segunda a Sexta")
        logger.info("=" * 60)
        
        ultimo_status = datetime.now()
        ultimo_ajuste = datetime.now()
        
        while self.rodando:
            try:
                # Verificar se está no horário de mercado
                if not self.esta_horario_mercado():
                    logger.info("⏸️ Fora do horário de mercado. Aguardando...")
                    time.sleep(60)  # Verifica a cada minuto
                    continue
                
                # 1. SEMPRE coletar dados da B3 (1 segundo)
                self.coletar_dados()
                
                # 2. Verificar se é hora de analisar com IA (15 segundos)
                tempo_desde_ultima_analise = (datetime.now() - self.ultima_analise).total_seconds()
                if tempo_desde_ultima_analise >= self.frequencia_analise:
                    self.analisar_dados_acumulados()
                    self.metricas['ciclos'] += 1
                
                # Exibir status a cada 10 minutos
                if (datetime.now() - ultimo_status).seconds >= 600:
                    self.exibir_status()
                    ultimo_status = datetime.now()
                
                # Ajustar parâmetros automaticamente a cada 30 minutos
                if (datetime.now() - ultimo_ajuste).seconds >= 1800:
                    self.ajustar_parametros_automaticamente()
                    ultimo_ajuste = datetime.now()
                
                # Aguardar próxima execução
                if self.rodando:
                    time.sleep(self.frequencia_coleta)
                    
            except KeyboardInterrupt:
                logger.info("⚠️ Interrupção manual detectada")
                break
            except Exception as e:
                logger.error(f"❌ Erro crítico no loop principal: {e}")
                time.sleep(10)  # Pausa breve antes de tentar novamente
        
        # Exibir status final
        self.exibir_status()
        logger.info("👋 Robô de IA encerrado")

def main():
    """
    Função principal
    """
    try:
        robô = RoboIATempoReal()
        robô.executar()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 