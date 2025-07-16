from loguru import logger
from config import load_config
import os
from armazenamento import Armazenamento
from coletor import Coletor
from analisador import analisar_com_ia
from executor import enviar_ordem
import time

if __name__ == "__main__":
    # Setup logging
    os.makedirs('logs', exist_ok=True)
    logger.add("logs/robo_trading.log", rotation="1 week")

    # Carregar configuração
    config = load_config()
    logger.info(f"Configuração carregada: {config}")

    # Inicializar componentes
    armazenamento = Armazenamento()
    coletor = Coletor()
    logger.info("Componentes inicializados.")

    # Loop principal com coleta real
    try:
        for ciclo in range(3):  # Executa 3 ciclos para demonstração
            logger.info(f"=== CICLO {ciclo + 1} ===")
            
            # Coletar dados reais (IBOV + contrato vigente WIN)
            dados_coletados = coletor.coletar_dados()
            
            if dados_coletados:
                logger.info(f"Dados coletados: {len(dados_coletados)} símbolos")
                
                # Processar cada símbolo coletado
                for dados in dados_coletados:
                    # Salvar dados no banco
                    armazenamento.salvar_precos(
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
                    
                    # Analisar com IA (apenas para o contrato WIN)
                    if dados['simbolo'].startswith('WIN'):
                        analise = analisar_com_ia(dados)
                        logger.info(f"Resultado da IA para {dados['simbolo']}: {analise}")
                        
                        # Salvar análise no banco
                        armazenamento.salvar_analise(dados, analise['decisao'], analise['confianca'])
                        
                        # Executar ordem se necessário
                        if analise['decisao'] in ['comprar', 'vender']:
                            resposta = enviar_ordem(analise['decisao'], config['trading']['quantidade_padrao'], dados['preco_atual'], dados['simbolo'])
                            armazenamento.salvar_ordem(analise['decisao'], config['trading']['quantidade_padrao'], dados['preco_atual'], 'enviada', resposta)
            
            # Aguardar próximo ciclo
            if ciclo < 2:  # Não aguardar no último ciclo
                time.sleep(config['coleta']['frequencia'])
    
    except KeyboardInterrupt:
        logger.info("Interrupção manual detectada")
    except Exception as e:
        logger.error(f"Erro no loop principal: {e}")

    # Mostrar estatísticas finais
    stats = armazenamento.obter_estatisticas()
    logger.info("=== ESTATÍSTICAS FINAIS ===")
    logger.info(f"Total de preços salvos: {stats.get('total_precos', 0)}")
    logger.info(f"Último preço: {stats.get('ultimo_preco', 'N/A')}")
    logger.info(f"Total de análises: {stats.get('total_analises', 0)}")
    logger.info(f"Total de ordens: {stats.get('total_ordens', 0)}")
    
    logger.info("Robô finalizado.") 