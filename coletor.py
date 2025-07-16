import requests
import json
import time
from datetime import datetime
from loguru import logger
import config

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