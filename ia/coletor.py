import random

def obter_dados_order_book(par: str) -> dict:
    """Coleta features do livro de ordens para o par"""
    # Simulação: valores aleatórios para exemplo
    return {
        'bid_ask_imbalance': round(random.uniform(-1, 1), 2),
        'max_bid_size': round(random.uniform(1, 10), 2),
        'max_ask_size': round(random.uniform(1, 10), 2),
        'liquidity_clusters': random.randint(0, 3)
    }

# No método de coleta de dados de mercado:
def coletar_dados_mercado(par: str) -> dict:
    dados = {}  # coleta normal
    dados_order_book = obter_dados_order_book(par)
    dados.update(dados_order_book)
    return dados 