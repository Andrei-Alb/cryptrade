#!/usr/bin/env python3
"""
Script para alternar entre modo simulação e modo real
"""

import yaml
import sys
from loguru import logger

def alternar_modo(modo: str):
    """
    Alterna entre modo simulação e modo real
    
    Args:
        modo: 'simulacao' ou 'real'
    """
    try:
        # Carregar configuração atual
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        if modo.lower() == 'simulacao':
            # Ativar modo simulação
            config['simulacao']['ativo'] = True
            config['treinamento']['ativo'] = True
            config['ia']['modo_treinamento'] = True
            
            logger.info("🎮 ATIVANDO MODO SIMULAÇÃO")
            logger.info("✅ Simulação ativa")
            logger.info("✅ Treinamento ativo")
            logger.info("✅ IA em modo de aprendizado")
            logger.info("⚠️ Ordens serão simuladas (sem dinheiro real)")
            
        elif modo.lower() == 'real':
            # Ativar modo real
            config['simulacao']['ativo'] = False
            config['treinamento']['ativo'] = False
            config['ia']['modo_treinamento'] = False
            
            logger.info("💰 ATIVANDO MODO REAL")
            logger.info("✅ Simulação desativada")
            logger.info("✅ Treinamento desativado")
            logger.info("✅ IA em modo de produção")
            logger.warning("⚠️ ATENÇÃO: Ordens serão executadas com dinheiro real!")
            
        else:
            logger.error("❌ Modo inválido. Use 'simulacao' ou 'real'")
            return False
        
        # Salvar configuração
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False, indent=2)
        
        logger.success(f"✅ Modo alterado para: {modo.upper()}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao alternar modo: {e}")
        return False

def mostrar_status():
    """Mostra o status atual do sistema"""
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        simulacao_ativa = config.get('simulacao', {}).get('ativo', False)
        treinamento_ativo = config.get('treinamento', {}).get('ativo', False)
        modo_treinamento = config.get('ia', {}).get('modo_treinamento', False)
        
        logger.info("📊 STATUS ATUAL DO SISTEMA")
        logger.info("=" * 40)
        logger.info(f"🎮 Simulação: {'ATIVA' if simulacao_ativa else 'INATIVA'}")
        logger.info(f"🧠 Treinamento: {'ATIVO' if treinamento_ativo else 'INATIVO'}")
        logger.info(f"🤖 IA Treinamento: {'ATIVO' if modo_treinamento else 'INATIVO'}")
        
        if simulacao_ativa:
            logger.info("✅ MODO SIMULAÇÃO - Ordens simuladas")
        else:
            logger.info("💰 MODO REAL - Ordens com dinheiro real")
            
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar status: {e}")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        logger.info("📋 USO:")
        logger.info("  python alternar_modo.py simulacao  # Ativar modo simulação")
        logger.info("  python alternar_modo.py real       # Ativar modo real")
        logger.info("  python alternar_modo.py status     # Mostrar status atual")
        return
    
    comando = sys.argv[1].lower()
    
    if comando == 'status':
        mostrar_status()
    elif comando in ['simulacao', 'real']:
        alternar_modo(comando)
    else:
        logger.error("❌ Comando inválido. Use 'simulacao', 'real' ou 'status'")

if __name__ == "__main__":
    main() 