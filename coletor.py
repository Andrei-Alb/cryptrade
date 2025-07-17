import requests
import json
import time
from datetime import datetime
from loguru import logger
import config
import random
from ia.coletor import obter_dados_order_book

# Função para identificar o contrato vigente do mini-índice WIN
# Exemplo: WINQ25 para agosto/2025

def get_win_contract_code(data=None):
    if data is None:
        data = datetime.now()
    ano = data.year
    mes = data.month
    vencimentos = {
        2: 'G',   # Fevereiro
        4: 'J',   # Abril
        6: 'M',   # Junho
        8: 'Q',   # Agosto
        10: 'V',  # Outubro
        12: 'Z',  # Dezembro
    }
    meses_ordenados = sorted(vencimentos.keys())
    for m in meses_ordenados:
        if mes <= m:
            letra = vencimentos[m]
            break
    else:
        ano += 1
        letra = vencimentos[2]
    return f"WIN{letra}{str(ano)[-2:]}"

class Coletor:
    def __init__(self):
        self.config = config.load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def coletar_dados_b3(self, simbolo="IBOV"):
        """
        Coleta dados da API oficial da B3
        """
        try:
            url = f"https://cotacao.b3.com.br/mds/api/v1/instrumentQuotation/{simbolo}"
            logger.info(f"Coletando dados da B3 para {simbolo}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            dados = response.json()
            
            if dados.get('BizSts', {}).get('cd') == 'OK':
                trad = dados.get('Trad', [])
                if trad:
                    scty = trad[0].get('scty', {})
                    scty_qtn = scty.get('SctyQtn', {})
                    
                    return {
                        'simbolo': simbolo,
                        'preco_atual': scty_qtn.get('curPrc'),
                        'preco_abertura': scty_qtn.get('opngPric'),
                        'preco_minimo': scty_qtn.get('minPric'),
                        'preco_maximo': scty_qtn.get('maxPric'),
                        'preco_medio': scty_qtn.get('avrgPric'),
                        'variacao': scty_qtn.get('prcFlcn'),
                        'volume': 0,  # API não retorna volume
                        'timestamp': datetime.now().isoformat(),
                        'fonte': 'B3_API'
                    }
            else:
                logger.warning(f"Erro na API da B3 para {simbolo}: {dados.get('BizSts', {}).get('desc', 'Erro desconhecido')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao coletar dados da B3 para {simbolo}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da B3 para {simbolo}: {e}")
            return None
        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Erro inesperado ao coletar dados da B3 para {simbolo}: {e}")
            return None
    
    def coletar_dados(self):
        """
        Coleta dados APENAS da API oficial da B3
        Retorna None se não conseguir dados reais
        """
        dados_coletados = []
        
        # Coleta IBOV
        dados_b3 = self.coletar_dados_b3("IBOV")
        if dados_b3:
            dados_coletados.append(dados_b3)
            logger.info(f"Dados coletados da B3: {dados_b3['preco_atual']}")
        
        # Coleta contrato vigente do WIN
        contrato_vigente = get_win_contract_code()
        dados_win = self.coletar_dados_b3(contrato_vigente)
        if dados_win:
            dados_coletados.append(dados_win)
            logger.info(f"Dados coletados da B3 para {contrato_vigente}: {dados_win['preco_atual']}")
        else:
            # Fallback para outros contratos WIN (caso o vigente não esteja disponível)
            simbolos_fallback = ["WINZ25", "WINV25", "WINQ25", "WINM25", "WINJ25", "WING25"]
            for simbolo in simbolos_fallback:
                if simbolo == contrato_vigente:
                    continue
                dados_fallback = self.coletar_dados_b3(simbolo)
                if dados_fallback:
                    dados_coletados.append(dados_fallback)
                    logger.info(f"Dados coletados da B3 para {simbolo} (fallback): {dados_fallback['preco_atual']}")
                    break
        
        # Se não conseguiu dados reais da B3, retorna None
        if not dados_coletados:
            logger.error("❌ NENHUM dado real da B3 foi coletado. Sistema deve parar de operar.")
            logger.error("💡 Verifique conectividade com a internet e disponibilidade da API da B3.")
            return None
        
        logger.info(f"✅ {len(dados_coletados)} símbolos coletados com dados reais da B3")
        return dados_coletados
    
    def testar_conexao(self):
        """
        Testa a conexão com a API da B3
        """
        logger.info("Testando conexão com API da B3...")
        
        # Testa API da B3
        try:
            dados = self.coletar_dados_b3("IBOV")
            if dados:
                logger.success("✅ API da B3 funcionando")
                logger.info(f"IBOV: {dados['preco_atual']}")
                return True
            else:
                logger.error("❌ API da B3 não retornou dados")
                return False
        except Exception as e:
            logger.error(f"❌ Erro na API da B3: {e}")
            return False

class ColetorBybit:
    """Coletor específico para dados da Bybit"""
    
    def __init__(self):
        self.config = config.load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://api.bybit.com"
        
    def obter_preco_atual(self, symbol="BTCUSDT"):
        """Obtém o preço atual de um símbolo na Bybit"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            dados = response.json()
            
            if dados.get('retCode') == 0 and dados.get('result', {}).get('list'):
                ticker = dados['result']['list'][0]
                return float(ticker.get('lastPrice', 0))
            else:
                logger.warning(f"Erro na API da Bybit para {symbol}: {dados.get('retMsg', 'Erro desconhecido')}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter preço da Bybit para {symbol}: {e}")
            return None
    
    def coletar_dados_bybit(self, symbol="BTCUSDT"):
        """Coleta dados completos de um símbolo na Bybit"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            dados = response.json()
            
            if dados.get('retCode') == 0 and dados.get('result', {}).get('list'):
                ticker = dados['result']['list'][0]
                
                return {
                    'symbol': symbol,
                    'preco_atual': float(ticker.get('lastPrice', 0)),
                    'preco_abertura': float(ticker.get('openPrice', 0)),
                    'preco_minimo': float(ticker.get('lowPrice24h', 0)),
                    'preco_maximo': float(ticker.get('highPrice24h', 0)),
                    'volume': float(ticker.get('volume24h', 0)),
                    'variacao': float(ticker.get('price24hPcnt', 0)) * 100,
                    'timestamp': datetime.now().isoformat(),
                    'fonte': 'Bybit_API'
                }
            else:
                logger.warning(f"Erro na API da Bybit para {symbol}: {dados.get('retMsg', 'Erro desconhecido')}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao coletar dados da Bybit para {symbol}: {e}")
            return None
    
    def coletar_dados(self):
        """Coleta dados dos pares configurados na Bybit"""
        pares = self.config.get('trading', {}).get('pares', ['BTCUSDT', 'ETHUSDT'])
        dados_coletados = []
        
        for par in pares:
            dados = self.coletar_dados_bybit(par)
            if dados:
                dados_coletados.append(dados)
                logger.info(f"Dados coletados da Bybit para {par}: {dados['preco_atual']}")
        
        if not dados_coletados:
            logger.error("❌ NENHUM dado da Bybit foi coletado.")
            return None
        
        logger.info(f"✅ {len(dados_coletados)} pares coletados da Bybit")
        return dados_coletados
    
    def verificar_conectividade(self):
        """Verifica conectividade com a API da Bybit"""
        try:
            dados = self.coletar_dados_bybit("BTCUSDT")
            if dados:
                logger.success("✅ API da Bybit funcionando")
                logger.info(f"BTCUSDT: {dados['preco_atual']}")
                return True
            else:
                logger.error("❌ API da Bybit não retornou dados")
                return False
        except Exception as e:
            logger.error(f"❌ Erro na API da Bybit: {e}")
            return False

    def obter_dados_rest(self, symbol, *args, **kwargs):
        """Obtém dados de mercado do par solicitado via Bybit (REST) com dados simulados mais realistas"""
        try:
            # Obter preço atual real
            preco_atual = self.obter_preco_atual(symbol)
            if not preco_atual:
                return None
            
            # Simular dados históricos mais realistas
            import pandas as pd
            from datetime import datetime, timedelta
            import random
            
            # Gerar dados históricos simulados com variação realista
            dados_historicos = []
            preco_base = preco_atual
            
            for i in range(100):  # 100 períodos de dados
                # Variação de preço realista (±2% por período)
                variacao = random.uniform(-0.02, 0.02)
                preco = preco_base * (1 + variacao)
                
                # Simular volume
                volume = random.uniform(1000, 10000)
                
                # Timestamp
                timestamp = datetime.now() - timedelta(minutes=100-i)
                
                dados_historicos.append({
                    'timestamp': timestamp,
                    'open': preco * random.uniform(0.995, 1.005),
                    'high': preco * random.uniform(1.001, 1.02),
                    'low': preco * random.uniform(0.98, 0.999),
                    'close': preco,
                    'volume': volume
                })
                
                preco_base = preco
            
            # Converter para DataFrame
            df = pd.DataFrame(dados_historicos)
            
            # Calcular RSI realista
            delta = df['close'].diff().astype(float)
            gain = delta.copy()
            gain[gain < 0] = 0
            gain = gain.rolling(window=14).mean()
            loss = delta.copy()
            loss[loss > 0] = 0
            loss = (-loss).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_atual = float(rsi.iloc[-1])
            
            # Calcular volatilidade realista
            returns = df['close'].pct_change()
            volatilidade = returns.rolling(window=20).std()
            volatilidade_atual = float(volatilidade.iloc[-1])
            
            # Determinar tendência realista
            media_curta = df['close'].tail(5).mean()
            media_longa = df['close'].tail(20).mean()
            
            if media_curta > media_longa * 1.005:
                tendencia = 'alta'
            elif media_curta < media_longa * 0.995:
                tendencia = 'baixa'
            else:
                tendencia = 'lateral'
            
            return {
                'symbol': symbol,
                'preco_atual': preco_atual,
                'preco_abertura': float(df['open'].iloc[-1]),
                'preco_minimo': float(df['low'].iloc[-1]),
                'preco_maximo': float(df['high'].iloc[-1]),
                'volume': float(df['volume'].iloc[-1]),
                'variacao': ((preco_atual - float(df['open'].iloc[-1])) / float(df['open'].iloc[-1])) * 100,
                'rsi': rsi_atual,
                'volatilidade': volatilidade_atual,
                'tendencia': tendencia,
                'timestamp': datetime.now().isoformat(),
                'fonte': 'Bybit_API_Simulada',
                'dados_historicos': df  # DataFrame completo para cálculos
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados rest para {symbol}: {e}")
            return None

def coletar_dados_mercado(par: str) -> dict:
    # Exemplo de coleta real (substitua pelos dados reais do seu sistema)
    dados = {
        'preco_atual': random.uniform(1000, 50000),
        'rsi': random.uniform(10, 90),
        'volatilidade': random.uniform(0.005, 0.05),
        'tendencia': random.choice(['alta', 'baixa', 'lateral']),
        'volume': random.uniform(100, 10000)
    }
    dados_order_book = obter_dados_order_book(par)
    dados.update(dados_order_book)
    return dados

if __name__ == "__main__":
    coletor = Coletor()
    resultado_teste = coletor.testar_conexao()
    
    print("\n" + "="*50)
    print("COLETANDO DADOS REAIS DA B3")
    print("="*50)
    
    dados = coletor.coletar_dados()
    if dados:
        for dado in dados:
            print(f"\nSímbolo: {dado['simbolo']}")
            print(f"Preço Atual: {dado['preco_atual']}")
            print(f"Variação: {dado['variacao']}%")
            print(f"Fonte: {dado['fonte']}")
            print(f"Timestamp: {dado['timestamp']}")
    else:
        print("\n❌ NENHUM dado real foi coletado!")
        print("Sistema deve parar de operar até que dados reais estejam disponíveis.") 