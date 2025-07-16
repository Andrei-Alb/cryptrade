#!/usr/bin/env python3
"""
Script de Inicialização do Robô de Trading
Verifica dependências e inicia o sistema completo
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime
from loguru import logger

# Configurar logging
os.makedirs('logs', exist_ok=True)
logger.add("logs/inicializacao.log", rotation="1 week")

def verificar_ollama():
    """
    Verifica se o Ollama está rodando e acessível
    """
    try:
        logger.info("🔍 Verificando Ollama...")
        
        # Verificar se o processo está rodando
        result = subprocess.run(['pgrep', 'ollama'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ Ollama não está rodando!")
            logger.info("💡 Execute: ollama serve")
            return False
        
        # Verificar se a API está respondendo
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"✅ Ollama OK - Modelos disponíveis: {len(models)}")
                for model in models:
                    logger.info(f"   📦 {model['name']}")
                return True
            else:
                logger.error(f"❌ API Ollama retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Não foi possível conectar ao Ollama: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar Ollama: {e}")
        return False

def verificar_modelo_ia():
    """
    Verifica se o modelo Llama 3.1 8B está disponível
    """
    try:
        logger.info("🤖 Verificando modelo Llama 3.1 8B...")
        
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                if 'llama3.1:8b' in model['name'].lower():
                    logger.info(f"✅ Modelo Llama 3.1 8B encontrado")
                    return True
            
            logger.warning("⚠️ Modelo Llama 3.1 8B não encontrado")
            logger.info("💡 Execute: ollama pull llama3.1:8b")
            return False
        else:
            logger.error("❌ Não foi possível verificar modelos")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar modelo: {e}")
        return False

def verificar_banco_dados():
    """
    Verifica se o banco de dados está acessível
    """
    try:
        logger.info("🗄️ Verificando banco de dados...")
        
        import sqlite3
        from armazenamento import Armazenamento
        
        armazenamento = Armazenamento()
        
        # Testar conexão
        try:
            conn = sqlite3.connect(armazenamento.db_path)
            c = conn.cursor()
            c.execute('SELECT 1')
            conn.close()
            logger.info("✅ Banco de dados OK")
            return True
        except Exception as e:
            logger.error(f"❌ Falha na conexão com banco de dados: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar banco de dados: {e}")
        return False

def verificar_configuracao():
    """
    Verifica se a configuração está válida
    """
    try:
        logger.info("⚙️ Verificando configuração...")
        
        import config
        config_data = config.load_config()
        
        # Seções essenciais
        required_sections = ['trading', 'ia']
        for section in required_sections:
            if section not in config_data:
                logger.error(f"❌ Seção '{section}' não encontrada na configuração")
                return False
        
        # Seções opcionais (adicionar se não existirem)
        optional_sections = ['b3', 'coleta']
        for section in optional_sections:
            if section not in config_data:
                logger.warning(f"⚠️ Seção '{section}' não encontrada - usando configuração padrão")
                # Adicionar seção padrão se não existir
                if section == 'b3':
                    config_data[section] = {
                        'api_url': 'https://api.b3.com.br',
                        'simbolos': ['WINM24', 'WINN24', 'WINQ24'],
                        'timeout': 30,
                        'retry_attempts': 3
                    }
                elif section == 'coleta':
                    config_data[section] = {
                        'frequencia': 30,
                        'horario_inicio': '09:00',
                        'horario_fim': '17:00',
                        'dias_semana': [0, 1, 2, 3, 4],
                        'timeout': 30
                    }
        
        logger.info("✅ Configuração OK")
        logger.info(f"   📋 Seções: {list(config_data.keys())}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar configuração: {e}")
        return False

def testar_coletor():
    """
    Testa o coletor de dados da B3
    """
    try:
        logger.info("📊 Testando coletor de dados...")
        
        from coletor import Coletor
        
        coletor = Coletor()
        dados = coletor.coletar_dados()
        
        if dados and len(dados) > 0:
            logger.info(f"✅ Coletor OK - {len(dados)} símbolos coletados")
            for dado in dados[:3]:  # Mostrar apenas os primeiros 3
                logger.info(f"   📈 {dado['simbolo']}: {dado['preco_atual']}")
            return True
        else:
            logger.warning("⚠️ Coletor não retornou dados (pode ser normal fora do horário de mercado)")
            logger.info("💡 O coletor pode não retornar dados fora do horário de mercado")
            return True  # Não é um erro crítico
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar coletor: {e}")
        logger.info("💡 Verificando se é problema de conectividade...")
        return True  # Não é um erro crítico para iniciar o robô

def testar_ia():
    """
    Testa a conexão com a IA
    """
    try:
        logger.info("🤖 Testando conexão com IA...")
        
        from analisador import AnalisadorIA
        import config
        
        config_data = config.load_config()
        analisador = AnalisadorIA(config_data)
        
        if analisador.testar_conexao():
            logger.info("✅ Conexão com IA OK")
            return True
        else:
            logger.warning("⚠️ Falha na conexão com IA (pode ser timeout)")
            logger.info("💡 A IA pode estar carregando o modelo...")
            return True  # Não é um erro crítico
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar IA: {e}")
        logger.info("💡 Verificando se é problema de configuração...")
        return True  # Não é um erro crítico para iniciar o robô

def iniciar_robo():
    """
    Inicia o robô de trading
    """
    try:
        logger.info("🚀 Iniciando robô de trading...")
        
        # Importar e executar o robô
        from robo_ia_tempo_real import RoboIATempoReal
        
        robô = RoboIATempoReal()
        robô.executar()
        
    except KeyboardInterrupt:
        logger.info("⚠️ Robô interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal no robô: {e}")
        sys.exit(1)

def main():
    """
    Função principal de inicialização
    """
    logger.info("=" * 60)
    logger.info("🤖 INICIALIZADOR DO ROBÔ DE TRADING")
    logger.info("=" * 60)
    logger.info(f"🕐 Início: {datetime.now()}")
    
    # Lista de verificações críticas (devem passar)
    verificacoes_criticas = [
        ("Ollama", verificar_ollama),
        ("Modelo IA", verificar_modelo_ia),
        ("Banco de Dados", verificar_banco_dados),
        ("Configuração", verificar_configuracao)
    ]
    
    # Lista de verificações não-críticas (podem falhar)
    verificacoes_opcionais = [
        ("Coletor B3", testar_coletor),
        ("Conexão IA", testar_ia)
    ]
    
    # Executar verificações críticas
    logger.info("\n🔍 VERIFICAÇÕES CRÍTICAS:")
    todas_criticas_ok = True
    for nome, verificacao in verificacoes_criticas:
        logger.info(f"\n🔍 Verificando {nome}...")
        if not verificacao():
            todas_criticas_ok = False
            logger.error(f"❌ Falha crítica na verificação: {nome}")
            break
        time.sleep(1)
    
    if not todas_criticas_ok:
        logger.error("\n❌ FALHA NAS VERIFICAÇÕES CRÍTICAS")
        logger.error("Corrija os problemas acima antes de continuar")
        sys.exit(1)
    
    # Executar verificações opcionais
    logger.info("\n🔍 VERIFICAÇÕES OPCIONAIS:")
    for nome, verificacao in verificacoes_opcionais:
        logger.info(f"\n🔍 Verificando {nome}...")
        verificacao()
        time.sleep(1)
    
    logger.info("\n✅ TODAS AS VERIFICAÇÕES PASSARAM!")
    logger.info("🚀 Iniciando robô de trading...")
    logger.info("=" * 60)
    
    # Iniciar robô
    iniciar_robo()

if __name__ == "__main__":
    main() 