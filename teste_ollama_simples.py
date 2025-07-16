#!/usr/bin/env python3
"""
Teste simples do Ollama para verificar se consegue responder
"""

import requests
import json
from loguru import logger

def testar_ollama_simples():
    """Testa Ollama com prompt simples"""
    
    # Prompt simples para teste
    prompt_simples = """Você é um assistente útil. Responda apenas com "OK" se você entendeu esta mensagem."""

    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt_simples,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 50
        }
    }
    
    try:
        print("🔍 Testando Ollama com prompt simples...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ Ollama respondeu: {resultado['response']}")
            return True
        else:
            print(f"❌ Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_ollama_trading_simples():
    """Testa Ollama com prompt de trading simples"""
    
    prompt_trading = """Analise: Preço=120000, RSI=45, Tendência=alta. Decisão: comprar, vender ou aguardar? Responda apenas com uma palavra."""

    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt_trading,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 20
        }
    }
    
    try:
        print("\n🔍 Testando Ollama com prompt de trading simples...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ Ollama respondeu: {resultado['response']}")
            return True
        else:
            print(f"❌ Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testando Ollama com prompts simples")
    print("=" * 50)
    
    # Teste 1: Prompt básico
    sucesso1 = testar_ollama_simples()
    
    # Teste 2: Prompt de trading simples
    sucesso2 = testar_ollama_trading_simples()
    
    print("\n" + "=" * 50)
    print("📋 RESULTADOS")
    print("=" * 50)
    print(f"Prompt básico: {'✅ PASSOU' if sucesso1 else '❌ FALHOU'}")
    print(f"Prompt trading: {'✅ PASSOU' if sucesso2 else '❌ FALHOU'}")
    
    if sucesso1 and sucesso2:
        print("\n🎉 Ollama está funcionando corretamente!")
    else:
        print("\n⚠️ Ollama pode ter problemas com prompts complexos.") 