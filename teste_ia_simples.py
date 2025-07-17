#!/usr/bin/env python3

from ia.decisor import Decisor

def testar_ia():
    print("🧠 Testando IA...")
    
    # Inicializar decisor
    decisor = Decisor()
    
    # Dados de teste
    dados = {
        'symbol': 'BTCUSDT',
        'preco_atual': 5000,
        'rsi': 65,
        'tendencia': 'alta',
        'volatilidade': 0.02
    }
    
    print(f"📊 Dados de teste: {dados}")   
    # Analisar mercado
    resultado = decisor.analisar_mercado(dados)
    
    print(f"🤖 Resultado da IA: {resultado}")
    
    if resultado:
        # Processar decisão
        decisao_processada = decisor.processar_decisao_ia(resultado, dados)
        print(f"✅ Decisão processada: {decisao_processada}")
    else:
        print("❌ IA não retornou resultado")

if __name__ == "__main__":
    testar_ia() 