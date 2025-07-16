#!/bin/bash
cd "$(dirname "$0")"

# Script para rodar o robô de trading em background
# Autor: Sistema de Trading IA
# Data: $(date)

echo "🤖 INICIANDO ROBÔ DE TRADING IA"
echo "================================"

# Verificar se estamos no diretório correto
# if [ ! -f "iniciar_robo.py" ]; then
#     echo "❌ Erro: Execute este script no diretório robo_trading/"
#     exit 1
# fi

# Verificar se o ambiente virtual está ativo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ Ambiente virtual não detectado"
    echo "💡 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar se o Ollama está rodando
echo "🔍 Verificando Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "❌ Ollama não está rodando!"
    echo "💡 Execute: ollama serve"
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p logs

# Nome do arquivo de log
LOG_FILE="logs/robo_background.log"
PID_FILE="logs/robo.pid"

# Verificar se já está rodando
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️ Robô já está rodando (PID: $PID)"
        echo "💡 Para parar: ./parar_robo.sh"
        echo "💡 Para ver logs: tail -f $LOG_FILE"
        exit 1
    else
        echo "🧹 Removendo PID file antigo..."
        rm -f "$PID_FILE"
    fi
fi

# Iniciar o robô em background
echo "🚀 Iniciando robô em background..."
nohup python3 iniciar_robo.py > "$LOG_FILE" 2>&1 &
ROBO_PID=$!

# Salvar PID
echo $ROBO_PID > "$PID_FILE"

echo "✅ Robô iniciado com PID: $ROBO_PID"
echo "📋 Logs: $LOG_FILE"
echo "🆔 PID: $PID_FILE"
echo ""
echo "📊 Comandos úteis:"
echo "   Ver logs em tempo real: tail -f $LOG_FILE"
echo "   Verificar status: ps aux | grep $ROBO_PID"
echo "   Parar robô: ./parar_robo.sh"
echo "   Ver métricas: python3 monitor.py"
echo ""
echo "🎯 O robô está rodando e não vai parar!"
echo "   Ele respeita horário de mercado (9h-17h, Seg-Sex)"
echo "   Frequência de análise: 30 segundos"
echo "   Modelo IA: Llama 3.1 8B"
echo ""
echo "📈 Monitorando início..."
sleep 5

# Verificar se iniciou corretamente
if ps -p $ROBO_PID > /dev/null 2>&1; then
    echo "✅ Robô está rodando corretamente!"
    echo "📊 Últimas linhas do log:"
    tail -n 10 "$LOG_FILE"
else
    echo "❌ Erro: Robô não iniciou corretamente"
    echo "📋 Verifique os logs: cat $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi 