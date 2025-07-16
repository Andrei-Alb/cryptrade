import time
import signal
import sys
from datetime import datetime, time as dt_time
from loguru import logger
from coletor import Coletor
from armazenamento import Armazenamento
import config

class ColetaContinua:
    def __init__(self):
        self.coletor = Coletor()
        self.armazenamento = Armazenamento()
        self.config = config.load_config()
        self.rodando = True
        self.frequencia = 10  # segundos (será otimizada pelos testes)
        self.falhas_consecutivas = 0
        self.max_falhas_consecutivas = 5
        
        # Configurações de horário de mercado
        self.horario_inicio = dt_time(9, 0)  # 09:00
        self.horario_fim = dt_time(17, 0)    # 17:00
        self.dias_semana = [0, 1, 2, 3, 4]  # Segunda a Sexta (0=Segunda)
        
        # Configurações de backoff
        self.backoff_inicial = 5
        self.backoff_maximo = 300
        self.backoff_atual = self.backoff_inicial
        
        # Métricas
        self.metricas = {
            'inicio': datetime.now(),
            'tentativas': 0,
            'sucessos': 0,
            'falhas': 0,
            'erros_429': 0,
            'timeouts': 0,
            'latencias': []
        }
        
        # Configura handlers para graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """
        Handler para graceful shutdown
        """
        logger.info(f"Recebido sinal {signum}. Encerrando coleta...")
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
    
    def aplicar_backoff(self):
        """
        Aplica backoff exponencial em caso de falhas
        """
        if self.falhas_consecutivas > 0:
            self.backoff_atual = min(
                self.backoff_inicial * (2 ** (self.falhas_consecutivas - 1)),
                self.backoff_maximo
            )
            logger.warning(f"Backoff aplicado: {self.backoff_atual}s (falhas consecutivas: {self.falhas_consecutivas})")
            time.sleep(self.backoff_atual)
        else:
            self.backoff_atual = self.backoff_inicial
    
    def coletar_dados_ciclo(self):
        """
        Executa um ciclo de coleta de dados
        """
        inicio_request = time.time()
        
        try:
            # Coleta dados
            dados_coletados = self.coletor.coletar_dados()
            
            if dados_coletados:
                # Salva dados no banco
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
                
                # Reset falhas consecutivas
                self.falhas_consecutivas = 0
                self.metricas['sucessos'] += 1
                
                latencia = time.time() - inicio_request
                self.metricas['latencias'].append(latencia)
                
                logger.info(f"✅ Dados coletados - {len(dados_coletados)} símbolos - Latência: {latencia:.3f}s")
                
                # Log dos dados coletados
                for dados in dados_coletados:
                    logger.debug(f"  {dados['simbolo']}: {dados['preco_atual']} ({dados['fonte']})")
                
            else:
                self.falhas_consecutivas += 1
                self.metricas['falhas'] += 1
                logger.error("❌ Falha na coleta de dados")
                
        except Exception as e:
            self.falhas_consecutivas += 1
            self.metricas['falhas'] += 1
            logger.error(f"❌ Erro durante coleta: {e}")
        
        self.metricas['tentativas'] += 1
        
        # Verifica se precisa aplicar backoff
        if self.falhas_consecutivas > 0:
            self.aplicar_backoff()
        
        # Alerta se muitas falhas consecutivas
        if self.falhas_consecutivas >= self.max_falhas_consecutivas:
            logger.critical(f"🚨 Muitas falhas consecutivas ({self.falhas_consecutivas})! Verificar sistema.")
    
    def exibir_status(self):
        """
        Exibe status atual do sistema
        """
        agora = datetime.now()
        duracao = agora - self.metricas['inicio']
        
        if self.metricas['latencias']:
            latencia_media = sum(self.metricas['latencias']) / len(self.metricas['latencias'])
        else:
            latencia_media = 0
        
        taxa_sucesso = (self.metricas['sucessos'] / max(self.metricas['tentativas'], 1)) * 100
        
        logger.info("\n" + "="*60)
        logger.info("📊 STATUS DA COLETA CONTÍNUA")
        logger.info("="*60)
        logger.info(f"⏱️  Tempo de execução: {duracao}")
        logger.info(f"🔄 Tentativas: {self.metricas['tentativas']}")
        logger.info(f"✅ Sucessos: {self.metricas['sucessos']}")
        logger.info(f"❌ Falhas: {self.metricas['falhas']}")
        logger.info(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        logger.info(f"⚡ Latência média: {latencia_media:.3f}s")
        logger.info(f"🚨 Falhas consecutivas: {self.falhas_consecutivas}")
        logger.info(f"⏰ Horário de mercado: {'SIM' if self.esta_horario_mercado() else 'NÃO'}")
        logger.info("="*60)
    
    def executar(self):
        """
        Executa a coleta contínua
        """
        logger.info("🚀 Iniciando Coleta Contínua de Dados")
        logger.info(f"⏰ Frequência: {self.frequencia} segundos")
        logger.info(f"🕐 Horário de mercado: {self.horario_inicio} - {self.horario_fim}")
        logger.info(f"📅 Dias úteis: Segunda a Sexta")
        logger.info("="*60)
        
        ultimo_status = datetime.now()
        
        while self.rodando:
            try:
                # Verifica se está no horário de mercado
                if not self.esta_horario_mercado():
                    logger.info("⏸️  Fora do horário de mercado. Aguardando...")
                    time.sleep(60)  # Verifica a cada minuto
                    continue
                
                # Executa ciclo de coleta
                self.coletar_dados_ciclo()
                
                # Exibe status a cada 10 minutos
                if (datetime.now() - ultimo_status).seconds >= 600:
                    self.exibir_status()
                    ultimo_status = datetime.now()
                
                # Aguarda próxima coleta
                if self.rodando:
                    time.sleep(self.frequencia)
                    
            except KeyboardInterrupt:
                logger.info("⚠️  Interrupção manual detectada")
                break
            except Exception as e:
                logger.error(f"❌ Erro crítico no loop principal: {e}")
                time.sleep(10)  # Pausa breve antes de tentar novamente
        
        # Exibe status final
        self.exibir_status()
        logger.info("👋 Coleta contínua encerrada")

def main():
    """
    Função principal
    """
    # Configura logger
    logger.add("logs/coleta_continua.log", rotation="1 day", retention="7 days")
    
    coleta = ColetaContinua()
    
    try:
        coleta.executar()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 