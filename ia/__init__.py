"""
Módulo de Inteligência Artificial para Robô de Trading
Implementa análise de dados usando Ollama com modelos locais
"""

from .cursor_ai_client import CursorAITradingClient
from .preparador_dados import PreparadorDadosIA
from .decisor import DecisorIA

__all__ = [
    'CursorAITradingClient',
    'PreparadorDadosIA', 
    'DecisorIA'
] 