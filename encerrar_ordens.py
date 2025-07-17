#!/usr/bin/env python3
"""
Script para encerrar todas as ordens ativas do robô de trading
"""

import os
import sys
import sqlite3
import signal
import time
from datetime import datetime
from loguru import logger
from executor import ExecutorOrdensSimuladas
from gestor_ordens_dinamico import GestorOrdensDinamico

def encerrar_ordens_simuladas():
    """Encerra todas as ordens simuladas ativas"""
    try:
        executor = ExecutorOrdensSimuladas()
        ordens_ativas = list(executor.ordens_ativas.items())
        
        if not ordens_ativas:
            print("✅ Nenhuma ordem simulada ativa para encerrar")
            return
        
        print(f"🔄 Encerrando {len(ordens_ativas)} ordens simuladas...")
        
        for ordem_id, ordem in ordens_ativas:
            try:
                symbol = ordem['simbolo']
                tipo = ordem['tipo']
                preco_entrada = ordem['preco_entrada']
                
                # Obter preço atual para calcular resultado
                from coletor import ColetorBybit
                coletor = ColetorBybit()
                preco_atual = coletor.obter_preco_atual(symbol)
                if preco_atual is None:
                    preco_atual = preco_entrada  # Usar preço de entrada como fallback
                
                # Calcular resultado
                if tipo == 'comprar':
                    lucro_percentual = ((preco_atual - preco_entrada) / preco_entrada) * 100
                else:
                    lucro_percentual = ((preco_entrada - preco_atual) / preco_entrada) * 100
                
                resultado = 'win' if lucro_percentual > 0 else 'loss'
                duracao = (datetime.now() - ordem['timestamp']).total_seconds()
                
                # Fechar ordem
                executor.fechar_ordem_simulada(
                    ordem_id, 
                    resultado, 
                    lucro_percentual, 
                    duracao, 
                    "Encerramento forçado pelo usuário"
                )
                
                emoji = "🟢" if resultado == 'win' else "🔴"
                print(f"   {emoji} {ordem_id}: {tipo.upper()} {symbol} | {resultado.upper()} | {lucro_percentual:.2f}%")
                
            except Exception as e:
                print(f"   ❌ Erro ao encerrar ordem {ordem_id}: {e}")
        
        print("✅ Todas as ordens simuladas foram encerradas")
        
    except Exception as e:
        print(f"❌ Erro ao encerrar ordens simuladas: {e}")

def encerrar_ordens_dinamicas():
    """Encerra todas as ordens dinâmicas ativas"""
    try:
        gestor = GestorOrdensDinamico()
        ordens_ativas = list(gestor.ordens_ativas.items())
        
        if not ordens_ativas:
            print("✅ Nenhuma ordem dinâmica ativa para encerrar")
            return
        
        print(f"🔄 Encerrando {len(ordens_ativas)} ordens dinâmicas...")
        
        for order_id, ordem in ordens_ativas:
            try:
                symbol = ordem['symbol']
                tipo_ordem = ordem['tipo_ordem']
                preco_entrada = ordem['preco_entrada']
                
                # Obter preço atual
                from coletor import ColetorBybit
                coletor = ColetorBybit()
                preco_atual = coletor.obter_preco_atual(symbol)
                if preco_atual is None:
                    preco_atual = preco_entrada
                
                # Fechar ordem
                gestor.fechar_ordem_dinamica(
                    order_id,
                    preco_atual,
                    "Encerramento forçado pelo usuário",
                    {'preco_atual': preco_atual}
                )
                
                print(f"   ✅ {order_id}: {tipo_ordem.upper()} {symbol} | Preço: {preco_atual:.2f}")
                
            except Exception as e:
                print(f"   ❌ Erro ao encerrar ordem {order_id}: {e}")
        
        print("✅ Todas as ordens dinâmicas foram encerradas")
        
    except Exception as e:
        print(f"❌ Erro ao encerrar ordens dinâmicas: {e}")

def encerrar_ordens_bybit():
    """Encerra todas as ordens reais na Bybit"""
    try:
        from executor import ExecutorBybit
        executor = ExecutorBybit()
        
        # Obter ordens ativas
        ordens_ativas = executor.obter_ordens_ativas()
        
        if not ordens_ativas:
            print("✅ Nenhuma ordem real ativa na Bybit")
            return
        
        print(f"🔄 Encerrando {len(ordens_ativas)} ordens reais na Bybit...")
        
        for ordem in ordens_ativas:
            try:
                order_id = ordem['orderId']
                symbol = ordem['symbol']
                
                # Cancelar ordem
                resultado = executor.fechar_ordem(order_id, symbol)
                
                if resultado['status'] == 'fechada':
                    print(f"   ✅ {order_id}: {symbol} | Cancelada")
                else:
                    print(f"   ❌ {order_id}: {symbol} | Erro: {resultado.get('razao', 'Desconhecido')}")
                
            except Exception as e:
                print(f"   ❌ Erro ao cancelar ordem {ordem.get('orderId', 'N/A')}: {e}")
        
        print("✅ Todas as ordens reais foram canceladas")
        
    except Exception as e:
        print(f"❌ Erro ao encerrar ordens reais: {e}")

def verificar_ordens_restantes():
    """Verifica se ainda existem ordens ativas"""
    try:
        # Verificar ordens simuladas
        executor = ExecutorOrdensSimuladas()
        ordens_simuladas = len(executor.ordens_ativas)
        
        # Verificar ordens dinâmicas
        gestor = GestorOrdensDinamico()
        ordens_dinamicas = len(gestor.ordens_ativas)
        
        # Verificar ordens reais
        try:
            from executor import ExecutorBybit
            executor_real = ExecutorBybit()
            ordens_reais = len(executor_real.obter_ordens_ativas())
        except:
            ordens_reais = 0
        
        total = ordens_simuladas + ordens_dinamicas + ordens_reais
        
        print(f"\n📊 RESUMO DE ORDENS RESTANTES:")
        print(f"   🎮 Simuladas: {ordens_simuladas}")
        print(f"   🔄 Dinâmicas: {ordens_dinamicas}")
        print(f"   💰 Reais: {ordens_reais}")
        print(f"   📈 TOTAL: {total}")
        
        return total == 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar ordens restantes: {e}")
        return False

def main():
    """Função principal"""
    print("🛑 ENCERRAMENTO DE TODAS AS ORDENS")
    print("=" * 50)
    print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verificar se o usuário confirma
    try:
        confirmacao = input("⚠️ Tem certeza que deseja encerrar TODAS as ordens? (s/N): ").strip().lower()
        if confirmacao not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada pelo usuário")
            return
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
        return
    
    print()
    
    # Encerrar ordens simuladas
    print("🎮 ENCERRANDO ORDENS SIMULADAS...")
    encerrar_ordens_simuladas()
    print()
    
    # Encerrar ordens dinâmicas
    print("🔄 ENCERRANDO ORDENS DINÂMICAS...")
    encerrar_ordens_dinamicas()
    print()
    
    # Encerrar ordens reais
    print("💰 ENCERRANDO ORDENS REAIS...")
    encerrar_ordens_bybit()
    print()
    
    # Verificar resultado
    print("🔍 VERIFICANDO RESULTADO...")
    todas_encerradas = verificar_ordens_restantes()
    
    if todas_encerradas:
        print("\n✅ SUCESSO: Todas as ordens foram encerradas!")
    else:
        print("\n⚠️ ATENÇÃO: Algumas ordens podem ainda estar ativas")
    
    print("\n📝 Logs detalhados disponíveis em: logs/")

if __name__ == "__main__":
    main() 