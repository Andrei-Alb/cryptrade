import sqlite3
import os
import time
import requests
from tabulate import tabulate
from datetime import datetime

DB_PATH = 'dados/crypto_trading.db'

# Garante que o diretório do banco existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_current_prices():
    """Obtém preços atuais de todos os ativos de uma vez só"""
    try:
        # Buscar todos os pares de uma vez
        url = "https://api.bybit.com/v5/market/tickers?category=linear"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0 and data.get('result', {}).get('list'):
                prices = {}
                for ticker in data['result']['list']:
                    symbol = ticker['symbol']
                    prices[symbol] = float(ticker['lastPrice'])
                return prices
        return {}
    except Exception as e:
        print(f"Erro ao obter preços: {e}")
        return {}

def get_open_orders():
    """Busca apenas ordens abertas do banco"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, symbol, tipo_ordem, preco_entrada, quantidade, 
               stop_loss_atual, take_profit_atual, timestamp_abertura
        FROM ordens_dinamicas
        WHERE status = 'aberta'
        ORDER BY timestamp_abertura DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def calculate_pnl(ordem_data, current_prices):
    """Calcula PnL em memória para uma ordem"""
    order_id, symbol, tipo_ordem, preco_entrada, quantidade, stop_loss, take_profit, timestamp_abertura = ordem_data
    
    current_price = current_prices.get(symbol, preco_entrada)
    
    # Calcular PnL
    if tipo_ordem == 'compra':
        pnl_value = (current_price - preco_entrada) * quantidade
        pnl_percent = ((current_price - preco_entrada) / preco_entrada) * 100
    else:  # venda
        pnl_value = (preco_entrada - current_price) * quantidade
        pnl_percent = ((preco_entrada - current_price) / preco_entrada) * 100
    
    return {
        'order_id': order_id,
        'symbol': symbol,
        'tipo_ordem': tipo_ordem,
        'preco_entrada': preco_entrada,
        'quantidade': quantidade,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'data_abertura': timestamp_abertura,
        'confianca_ia': 0.5,  # Valor padrão
        'preco_atual': current_price,
        'pnl_value': pnl_value,
        'pnl_percent': pnl_percent
    }

def get_closed_orders_summary():
    """Busca resumo rápido das ordens fechadas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN lucro_prejuizo > 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN lucro_prejuizo <= 0 THEN 1 ELSE 0 END) as losses,
               SUM(lucro_prejuizo) as pnl_total
        FROM ordens_dinamicas
        WHERE status = 'fechada'
    """)
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] > 0:
        total, wins, losses, pnl_total = result
        win_rate = (wins / total) * 100 if total > 0 else 0
        return {
            'total': total,
            'wins': wins or 0,
            'losses': losses or 0,
            'pnl_total': pnl_total or 0.0,
            'win_rate': win_rate
        }
    return {'total': 0, 'wins': 0, 'losses': 0, 'pnl_total': 0.0, 'win_rate': 0.0}

def main():
    """Monitor otimizado e rápido"""
    print("🎮 MONITOR SIMULADOR - VERSÃO OTIMIZADA")
    print("=" * 60)
    
    while True:
        try:
            # Obter preços atuais uma única vez
            current_prices = get_current_prices()
            
            # Buscar ordens abertas
            open_orders = get_open_orders()
            
            if not open_orders:
                print("📊 Nenhuma ordem aberta encontrada")
                print(f"⏰ Última atualização: {datetime.now().strftime('%H:%M:%S')}")
                time.sleep(5)
                continue
            
            # Calcular PnL para todas as ordens
            orders_with_pnl = []
            total_pnl = 0.0
            
            for ordem in open_orders:
                pnl_data = calculate_pnl(ordem, current_prices)
                orders_with_pnl.append(pnl_data)
                total_pnl += pnl_data['pnl_value']
            
            # Preparar dados para tabela
            table_data = []
            for ordem in orders_with_pnl:
                table_data.append([
                    ordem['order_id'][:20] + "...",
                    ordem['symbol'],
                    ordem['tipo_ordem'],
                    f"${ordem['preco_entrada']:.2f}",
                    f"{ordem['quantidade']:.6f}",
                    f"${ordem['preco_atual']:.2f}",
                    f"${ordem['pnl_value']:.4f}",
                    f"{ordem['pnl_percent']:+.2f}%",
                    ordem['data_abertura'][:16] if ordem['data_abertura'] else "N/A"
                ])
            
            # Exibir tabela
            print("\n📈 ORDENS ABERTAS (PnL em Tempo Real)")
            print(tabulate(table_data, headers=[
                "Order ID", "Symbol", "Tipo", "Preço Entrada", "Qtd", 
                "Preço Atual", "PnL ($)", "PnL (%)", "Data Abertura"
            ], tablefmt="grid"))
            
            print(f"\n💰 PnL Total das Ordens Abertas: ${total_pnl:.4f}")
            
            # Resumo de ordens fechadas
            closed_summary = get_closed_orders_summary()
            print(f"\n📊 RESUMO ORDENS FECHADAS:")
            print(f"   Total: {closed_summary['total']}")
            print(f"   Wins: {closed_summary['wins']} | Losses: {closed_summary['losses']}")
            print(f"   Win Rate: {closed_summary['win_rate']:.1f}%")
            print(f"   PnL Total: ${closed_summary['pnl_total']:.4f}")
            
            print(f"\n⏰ Última atualização: {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
            # Atualizar a cada 3 segundos (mais rápido)
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main() 