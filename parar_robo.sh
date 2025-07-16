#!/bin/bash
cd "$(dirname "$0")"

# Script para parar o robô de trading
# Autor: Sistema de Trading IA

echo "🛑 PARANDO ROBÔ DE TRADING IA"
echo "=============================="

PID_FILE="logs/robo.pid"

# Verificar se existe arquivo PID
if [ ! -f "$PID_FILE" ]; then
    echo "❌ Arquivo PID não encontrado"
    echo "💡 O robô pode não estar rodando"
    exit 1
fi

# Ler PID
ROBO_PID=$(cat "$PID_FILE")

# Verificar se o processo está rodando
if ! ps -p $ROBO_PID > /dev/null 2>&1; then
    echo "⚠️ Processo $ROBO_PID não está rodando"
    echo "🧹 Removendo arquivo PID..."
    rm -f "$PID_FILE"
    exit 0
fi

echo "🔍 Encontrado processo: $ROBO_PID"

# Tentar parada graciosa primeiro
echo "🔄 Enviando sinal de parada graciosa..."
kill -TERM $ROBO_PID

# Aguardar até 10 segundos
for i in {1..10}; do
    if ! ps -p $ROBO_PID > /dev/null 2>&1; then
        echo "✅ Robô parado graciosamente"
        rm -f "$PID_FILE"
        exit 0
    fi
    echo "⏳ Aguardando parada... ($i/10)"
    sleep 1
done

# Se não parou, forçar parada
echo "⚠️ Robô não parou graciosamente"
echo "🔄 Forçando parada..."
kill -KILL $ROBO_PID

# Verificar se parou
sleep 2
if ! ps -p $ROBO_PID > /dev/null 2>&1; then
    echo "✅ Robô parado forçadamente"
    rm -f "$PID_FILE"
else
    echo "❌ Erro: Não foi possível parar o robô"
    echo "💡 PID: $ROBO_PID"
    exit 1
fi

echo ""
echo "📊 Status final:"
echo "   PID removido: $PID_FILE"
echo "   Logs disponíveis em: logs/"
echo "   Para ver logs: tail -f logs/robo_background.log" 