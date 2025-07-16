#!/usr/bin/env python3
"""
Script para testar conectividade com a Bybit
Autor: Sistema de Trading Crypto
Data: Julho 2025
"""

import os
import sys
import yaml
from pybit.unified_trading import HTTP
from loguru import logger

def carregar_config():
    """Carrega configurações do arquivo YAML"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        logger.error("Arquivo config.yaml não encontrado!")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        return None

def carregar_credenciais():
    """Carrega credenciais da Bybit"""
    try:
        # Tenta carregar do arquivo credenciais.py
        from credenciais import BYBIT_API_KEY, BYBIT_API_SECRET
        return BYBIT_API_KEY, BYBIT_API_SECRET
    except ImportError:
        # Tenta carregar de variáveis de ambiente
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not api_key or not api_secret:
            logger.error("Credenciais não encontradas!")
            logger.info("Crie um arquivo credenciais.py ou configure as variáveis de ambiente:")
            logger.info("BYBIT_API_KEY=sua_api_key")
            logger.info("BYBIT_API_SECRET=sua_api_secret")
            return None, None
        
        return api_key, api_secret

def testar_conectividade_basica():
    """Testa conectividade básica com a Bybit"""
    logger.info("🔗 Testando conectividade básica com Bybit...")
    
    try:
        # Teste sem autenticação
        session = HTTP()
        
        # Teste de servidor
        server_time = session.get_server_time()
        logger.success(f"✅ Servidor Bybit acessível - Tempo: {server_time}")
        
        # Teste de informações da exchange
        exchange_info = session.get_instruments_info(category="linear")
        logger.success(f"✅ Informações da exchange obtidas - {len(exchange_info['result']['list'])} instrumentos")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na conectividade básica: {e}")
        return False

def testar_autenticacao(api_key, api_secret, testnet=False):
    """Testa autenticação com a Bybit"""
    logger.info("🔐 Testando autenticação com Bybit...")
    
    try:
        # Configurar sessão autenticada
        session = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        
        # Teste de wallet
        wallet_info = session.get_wallet_balance(accountType="UNIFIED")
        logger.success("✅ Autenticação bem-sucedida!")
        logger.info(f"💰 Saldo disponível: {wallet_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na autenticação: {e}")
        return False

def testar_permissoes_trading(api_key, api_secret, testnet=False):
    """Testa permissões de trading"""
    logger.info("📊 Testando permissões de trading...")
    
    try:
        session = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        
        # Teste de posições
        positions = session.get_positions(category="linear")
        logger.success("✅ Permissões de trading válidas!")
        logger.info(f"📈 Posições atuais: {len(positions['result']['list'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nas permissões de trading: {e}")
        return False

def testar_pares_trading(config):
    """Testa disponibilidade dos pares de trading"""
    logger.info("🔄 Testando pares de trading...")
    
    try:
        session = HTTP()
        pares = config['trading']['pares']
        
        for par in pares:
            # Teste de informações do instrumento
            instrument_info = session.get_instruments_info(
                category="linear",
                symbol=par
            )
            
            if instrument_info['result']['list']:
                logger.success(f"✅ Par {par} disponível")
            else:
                logger.warning(f"⚠️ Par {par} não encontrado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar pares: {e}")
        return False

def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes de conectividade com Bybit")
    
    # Carregar configurações
    config = carregar_config()
    if not config:
        return False
    
    # Carregar credenciais
    api_key, api_secret = carregar_credenciais()
    if not api_key or not api_secret:
        return False
    
    # Testes
    testes = [
        ("Conectividade Básica", lambda: testar_conectividade_basica()),
        ("Autenticação", lambda: testar_autenticacao(api_key, api_secret, config['bybit']['testnet'])),
        ("Permissões Trading", lambda: testar_permissoes_trading(api_key, api_secret, config['bybit']['testnet'])),
        ("Pares Trading", lambda: testar_pares_trading(config))
    ]
    
    resultados = []
    for nome, teste in testes:
        logger.info(f"\n{'='*50}")
        logger.info(f"Teste: {nome}")
        logger.info(f"{'='*50}")
        
        try:
            resultado = teste()
            resultados.append((nome, resultado))
        except Exception as e:
            logger.error(f"❌ Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RESUMO DOS TESTES")
    logger.info(f"{'='*50}")
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        logger.info(f"{nome}: {status}")
        if resultado:
            sucessos += 1
    
    logger.info(f"\n🎯 Resultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        logger.success("🎉 Todos os testes passaram! Sistema pronto para uso.")
        return True
    else:
        logger.error("⚠️ Alguns testes falharam. Verifique as configurações.")
        return False

if __name__ == "__main__":
    # Configurar logger
    logger.remove()
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    success = main()
    sys.exit(0 if success else 1) 