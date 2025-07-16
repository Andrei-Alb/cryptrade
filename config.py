"""Configuration loader and default settings for the trading bot."""
import yaml

DEFAULT_CONFIG = {
    'coleta': {
        'frequencia': 5,  # segundos (ajustado para 5 segundos)
        'horario_inicio': '09:00',
        'horario_fim': '17:00',
        'dias_semana': [1, 2, 3, 4, 5],  # Segunda a Sexta
        'timeout': 30
    },
    'trading': {
        'plataforma': 'profit_pro',
        'quantidade_padrao': 1,
        'stop_loss': 100,
        'take_profit': 200,
        'max_ordens_dia': 10
    },
    'ia': {
        'endpoint': 'http://localhost:8000/analisar',
        'timeout': 10,
        'retry_attempts': 3,
        'confianca_minima': 0.7
    },
    'b3': {
        'api_url': 'https://api.b3.com.br',
        'simbolos': ['WINM24', 'WINN24', 'WINQ24'],
        'timeout': 30,
        'retry_attempts': 3
    }
}

def load_config(path='config.yaml'):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return DEFAULT_CONFIG 