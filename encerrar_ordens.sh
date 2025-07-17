#!/bin/bash

# 🛑 SCRIPT PARA ENCERRAR TODAS AS ORDENS
# ======================================

echo "🛑 ENCERRAMENTO DE TODAS AS ORDENS"
echo "=================================="

# Verificar se estamos no diretório correto
if [ ! -f "encerrar_ordens.py" ]; then
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

echo ""
echo "🚨 ATENÇÃO: Este script irá encerrar TODAS as ordens ativas!"
echo "   - Ordens simuladas"
echo "   - Ordens dinâmicas" 
echo "   - Ordens reais na Bybit"
echo ""

# Executar script Python
python encerrar_ordens.py

echo ""
echo "✅ Script de encerramento concluído"
echo "📝 Verifique os logs para mais detalhes" 