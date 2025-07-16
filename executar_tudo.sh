#!/bin/bash

# 🚀 SCRIPT PARA EXECUTAR O ROBÔ COMPLETO
# ========================================

echo "🤖 INICIANDO ROBÔ COMPLETO DE TRADING CRYPTO"
echo "============================================="

# Verificar se estamos no diretório correto
if [ ! -f "robo_completo.py" ]; then
    echo "❌ Erro: Execute este script do diretório robo_trading/"
    exit 1
fi

# Verificar se o ambiente virtual está ativo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ Ambiente virtual não detectado. Tentando ativar..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Ambiente virtual ativado"
    else
        echo "❌ Ambiente virtual não encontrado. Crie um com: python -m venv venv"
        exit 1
    fi
fi

# Verificar dependências
echo "📦 Verificando dependências..."
python -c "import pybit, yaml, loguru, pandas, numpy, sqlite3" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependências faltando. Instale com: pip install -r requirements.txt"
    exit 1
fi
echo "✅ Dependências OK"

# Verificar configuração
if [ ! -f "config.yaml" ]; then
    echo "❌ Arquivo config.yaml não encontrado"
    exit 1
fi

# Verificar credenciais
if [ ! -f "credenciais.py" ]; then
    echo "⚠️ Arquivo credenciais.py não encontrado. Verificando variáveis de ambiente..."
    if [ -z "$BYBIT_API_KEY" ] || [ -z "$BYBIT_API_SECRET" ]; then
        echo "❌ Credenciais não encontradas. Configure BYBIT_API_KEY e BYBIT_API_SECRET"
        exit 1
    fi
    echo "✅ Credenciais encontradas nas variáveis de ambiente"
else
    echo "✅ Arquivo de credenciais encontrado"
fi

# Criar diretórios necessários
mkdir -p dados logs

# Verificar status do modo
echo "📋 Verificando modo atual..."
python alternar_modo.py status

echo ""
echo "🚀 INICIANDO ROBÔ COMPLETO..."
echo "📊 Logs serão salvos em logs/robo_completo.log"
echo "🛑 Para parar: Ctrl+C"
echo ""

# Executar robô completo com log
python robo_completo.py 2>&1 | tee logs/robo_completo.log

echo ""
echo "✅ Robô finalizado" 