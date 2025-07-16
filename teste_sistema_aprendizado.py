#!/usr/bin/env python3
"""
Teste do Sistema de Aprendizado
Verifica se o sistema está aprendendo corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia.sistema_aprendizado import SistemaAprendizado
from loguru import logger
import sqlite3
from datetime import datetime

def testar_sistema_aprendizado():
    """Testa o sistema de aprendizado"""
    
    logger.info("🧠 Testando Sistema de Aprendizado")
    logger.info("=" * 50)
    
    # Inicializar sistema
    sistema = SistemaAprendizado()
    
    # 1. Verificar parâmetros iniciais
    logger.info("📋 Parâmetros iniciais:")
    parametros = sistema.obter_parametros_otimizados()
    for param, valor in parametros.items():
        logger.info(f"   {param}: {valor}")
    
    # 2. Analisar desempenho atual
    logger.info("\n📊 Analisando desempenho atual:")
    analise = sistema.analisar_desempenho_recente(dias=7)
    
    if analise.get('total_ordens', 0) > 0:
        logger.info(f"   Total de ordens: {analise['total_ordens']}")
        
        # Análise por confiança
        analise_confianca = analise.get('analise_confianca', {})
        for nivel, dados in analise_confianca.items():
            logger.info(f"   Confiança {nivel}: {dados['wins']}/{dados['total']} wins "
                       f"({dados['taxa_acerto']:.1f}%) | Lucro médio: {dados['lucro_medio']:.3f}%")
        
        # Análise por fechamento
        analise_fechamento = analise.get('analise_fechamento', {})
        for tipo, dados in analise_fechamento.items():
            logger.info(f"   Fechamento {tipo}: {dados['wins']}/{dados['total']} wins "
                       f"({dados['taxa_acerto']:.1f}%) | Lucro médio: {dados['lucro_medio']:.3f}%")
        
        # Recomendações
        recomendacoes = analise.get('recomendacoes', [])
        if recomendacoes:
            logger.info("\n💡 Recomendações:")
            for rec in recomendacoes:
                logger.info(f"   • {rec}")
        else:
            logger.info("\n✅ Nenhuma recomendação necessária")
    else:
        logger.info("   Nenhuma ordem encontrada para análise")
    
    # 3. Testar ajuste automático
    logger.info("\n🔧 Testando ajuste automático:")
    resultado_ajuste = sistema.ajustar_parametros_automaticamente()
    
    if 'ajustes_aplicados' in resultado_ajuste:
        logger.info("✅ Ajustes aplicados:")
        for param, valor in resultado_ajuste['ajustes_aplicados'].items():
            logger.info(f"   {param}: {valor}")
    else:
        logger.info(f"ℹ️ {resultado_ajuste.get('mensagem', 'Nenhum ajuste')}")
    
    # 4. Verificar estatísticas de aprendizado
    logger.info("\n📈 Estatísticas de aprendizado:")
    stats = sistema.obter_estatisticas_aprendizado()
    
    logger.info(f"   Registros de aprendizado: {stats.get('total_registros_aprendizado', 0)}")
    logger.info(f"   Taxa de acerto geral: {stats.get('taxa_acerto_geral', 0):.1f}%")
    logger.info(f"   Ajustes realizados: {stats.get('total_ajustes_realizados', 0)}")
    
    # 5. Verificar tabelas do banco
    logger.info("\n🗄️ Verificando tabelas do banco:")
    verificar_tabelas_banco()
    
    logger.info("\n✅ Teste do Sistema de Aprendizado concluído")

def verificar_tabelas_banco():
    """Verifica as tabelas do banco de dados"""
    try:
        conn = sqlite3.connect('dados/trading.db')
        c = conn.cursor()
        
        # Verificar tabelas existentes
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in c.fetchall()]
        
        logger.info(f"   Tabelas encontradas: {', '.join(tabelas)}")
        
        # Verificar registros em cada tabela relevante
        tabelas_relevantes = ['ordens_simuladas', 'aprendizado_ia', 'aprendizado_saida', 'aprendizado_detalhado']
        
        for tabela in tabelas_relevantes:
            if tabela in tabelas:
                c.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = c.fetchone()[0]
                logger.info(f"   {tabela}: {count} registros")
            else:
                logger.info(f"   {tabela}: tabela não existe")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar banco: {e}")

def simular_aprendizado():
    """Simula alguns registros de aprendizado para teste"""
    
    logger.info("\n🎯 Simulando registros de aprendizado...")
    
    sistema = SistemaAprendizado()
    
    # Simular algumas ordens para teste
    ordens_teste = [
        {
            'ordem_id': 'teste_001',
            'tipo': 'comprar',
            'confianca_ia': 0.7,
            'duracao_segundos': 120,
            'razao_fechamento': 'Alvo atingido'
        },
        {
            'ordem_id': 'teste_002',
            'tipo': 'comprar',
            'confianca_ia': 0.3,
            'duracao_segundos': 180,
            'razao_fechamento': 'Estagnação'
        },
        {
            'ordem_id': 'teste_003',
            'tipo': 'vender',
            'confianca_ia': 0.8,
            'duracao_segundos': 90,
            'razao_fechamento': 'Alvo atingido'
        }
    ]
    
    dados_mercado_teste = {
        'preco_atual': 136500,
        'simbolo': 'WINQ25',
        'volume': 1000,
        'indicadores': {'rsi': 65, 'tendencia': 'alta'}
    }
    
    for i, ordem in enumerate(ordens_teste):
        resultado = 'win' if i % 2 == 0 else 'loss'
        lucro = 0.5 if resultado == 'win' else -0.2
        
        sucesso = sistema.registrar_aprendizado_ordem(
            ordem, resultado, lucro, dados_mercado_teste
        )
        
        if sucesso:
            logger.info(f"✅ Registro {i+1} simulado com sucesso")
        else:
            logger.error(f"❌ Falha ao simular registro {i+1}")
    
    logger.info("✅ Simulação concluída")

if __name__ == "__main__":
    try:
        # Testar sistema
        testar_sistema_aprendizado()
        
        # Simular aprendizado
        simular_aprendizado()
        
        # Testar novamente após simulação
        logger.info("\n🔄 Testando novamente após simulação:")
        testar_sistema_aprendizado()
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        sys.exit(1) 