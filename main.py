from loguru import logger
from config import load_config
import os
from armazenamento import Armazenamento
from coletor import Coletor
from analisador import analisar_com_ia
from executor import enviar_ordem
import time
from ia.sistema_aprendizado_autonomo import sistema_autonomo, ResultadoTrade
from typing import Dict, Any, Optional
from datetime import datetime
from ia.coletor import coletar_dados_mercado

def iniciar():
    """Inicia o robô de trading"""
    try:
        logger.info("🚀 Iniciando robô de trading...")
        
        # Inicializar sistema de IA autônoma
        sistema_autonomo.carregar_estado()
        logger.info("🧠 Sistema de IA autônoma inicializado")
        
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
        for ciclo in range(3):  # Executa 3 ciclos para demonstração
            logger.info(f"=== CICLO {ciclo + 1} ===")
            
            # Salvar estado da IA autônoma a cada ciclo
            sistema_autonomo.salvar_estado()
            
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
                            _executar_decisao(dados['simbolo'], analise['decisao'], analise['confianca'], dados)
            
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

if __name__ == "__main__":
    iniciar()

def calcular_quantidade_risco(preco: float, confianca: float) -> float:
    """Calcula quantidade baseada na confiança da IA"""
    # Quantidade base ajustada pela confiança
    quantidade_base = 0.0001  # Quantidade mínima
    multiplicador_confianca = 0.5 + (confianca * 0.5)  # 0.5 a 1.0
    
    quantidade = quantidade_base * multiplicador_confianca
    
    # Ajustar para respeitar risco máximo
    risco_maximo = 0.50  # R$ 0.50
    quantidade_maxima = risco_maximo / preco
    
    return min(quantidade, quantidade_maxima)

# Variável global para o gestor
_gestor_ordens = None

def _abrir_ordem_dinamica(par: str, direcao: str, preco: float, quantidade: float, stop_loss: float, take_profit: float) -> Optional[str]:
    """Abre ordem dinâmica usando o gestor de ordens"""
    global _gestor_ordens
    
    try:
        from gestor_ordens_dinamico import GestorOrdensDinamico, TipoOrdem
        
        # Criar gestor se não existir
        if _gestor_ordens is None:
            _gestor_ordens = GestorOrdensDinamico()
        
        # Gerar ID único para a ordem
        order_id = f"ORD_{int(time.time())}_{par}"
        
        # Converter direção para TipoOrdem
        tipo_ordem = TipoOrdem.COMPRA if direcao == "compra" else TipoOrdem.VENDA
        
        # Dados de mercado simulados
        dados_mercado = {
            'preco_atual': preco,
            'rsi': 50.0,
            'volatilidade': 0.01,
            'tendencia': 'lateral'
        }
        
        # Abrir ordem dinâmica
        resultado = _gestor_ordens.abrir_ordem_dinamica(
            order_id, par, tipo_ordem, preco, quantidade, dados_mercado, confianca_ia=0.5
        )
        
        return order_id if resultado else None
        
    except Exception as e:
        logger.error(f"❌ Erro ao abrir ordem dinâmica: {e}")
        return None

def registrar_resultado_trade(par: str, direcao: str, preco_entrada: float, preco_saida: float, 
                            quantidade: float, pnl: float, duracao: float, rsi_entrada: float,
                            volatilidade_entrada: float, tendencia_entrada: str, confianca_entrada: float,
                            stop_loss: float, take_profit: float, motivo_saida: str, indicadores_entrada: Dict[str, Any]):
    """Registra resultado de trade no sistema autônomo"""
    try:
        # Calcular PnL percentual
        pnl_percentual = (pnl / (preco_entrada * quantidade)) * 100
        
        # Determinar sucesso
        sucesso = pnl > 0
        
        # Criar resultado
        resultado = ResultadoTrade(
            timestamp=datetime.now().isoformat(),
            symbol=par,
            direcao=direcao,
            preco_entrada=preco_entrada,
            preco_saida=preco_saida,
            quantidade=quantidade,
            pnl=pnl,
            pnl_percentual=pnl_percentual,
            duracao=duracao,
            rsi_entrada=rsi_entrada,
            volatilidade_entrada=volatilidade_entrada,
            tendencia_entrada=tendencia_entrada,
            confianca_entrada=confianca_entrada,
            stop_loss=stop_loss,
            take_profit=take_profit,
            motivo_saida=motivo_saida,
            indicadores_entrada=indicadores_entrada,
            sucesso=sucesso
        )
        
        # Registrar no sistema autônomo
        sistema_autonomo.registrar_resultado(resultado)
        
        # Registrar fechamento da ordem
        sistema_autonomo.registrar_ordem_fechada(par)
        
        logger.info(f"📊 Resultado registrado: {par} {direcao} - PnL: {pnl:.4f} ({pnl_percentual:.2f}%) - {'✅' if sucesso else '❌'}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar resultado: {e}")

def _executar_decisao(par: str, decisao: str, confianca: float, dados_mercado: Dict[str, Any]):
    """Executa decisão da IA usando sistema autônomo, incluindo contexto do order book"""
    try:
        # Verificar se pode abrir ordem usando IA autônoma
        if not sistema_autonomo.pode_abrir_ordem(par, decisao):
            logger.info(f"⏳ Aguardando melhor oportunidade para {par}")
            return
        
        logger.info(f"🎯 Executando decisão: {decisao} {par} (confiança: {confianca:.3f})")
        
        # Obter parâmetros otimizados da IA
        parametros = sistema_autonomo.obter_parametros_otimizados()
        
        # Coletar contexto do order book
        contexto_order_book = coletar_dados_mercado(par)
        
        if decisao == "comprar":
            sistema_autonomo.registrar_ordem_aberta(par, "compra")
            stop_loss = dados_mercado['preco'] * (1 + parametros['stop_loss_padrao'] / 100)
            take_profit = dados_mercado['preco'] * (1 + parametros['take_profit_padrao'] / 100)
            quantidade = calcular_quantidade_risco(dados_mercado['preco'], confianca)
            ordem_id = _abrir_ordem_dinamica(par, "compra", dados_mercado['preco'], quantidade, stop_loss, take_profit)
            if ordem_id:
                logger.info(f"✅ Ordem de compra aberta: {ordem_id}")
                # Salvar contexto do order book junto com a ordem
                if not isinstance(sistema_autonomo.ultima_analise, dict):
                    sistema_autonomo.ultima_analise = {}
                sistema_autonomo.ultima_analise[par] = contexto_order_book
            else:
                sistema_autonomo.registrar_ordem_fechada(par)
        elif decisao == "venda":
            logger.info(f"⏳ Aguardando melhor oportunidade para {par}")
        else:
            logger.info(f"⏳ Aguardando melhor oportunidade para {par}")
    except Exception as e:
        logger.error(f"❌ Erro ao executar decisão: {e}")
        sistema_autonomo.registrar_ordem_fechada(par) 