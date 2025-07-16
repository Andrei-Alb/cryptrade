import time
import json
import statistics
from datetime import datetime, timedelta
from loguru import logger
import requests
from coletor import Coletor
import pandas as pd
import matplotlib.pyplot as plt
import os

class TestadorFrequencia:
    def __init__(self):
        self.coletor = Coletor()
        self.resultados = {}
        self.config = {
            'frequencias_teste': [0.3, 1, 10],  # segundos (incluindo 0.3s)
            'duracao_teste': 300,  # 5 minutos por frequência (teste rápido)
            'simbolos_teste': ['IBOV', 'WINZ25'],
            'timeout': 10
        }
        
    def testar_frequencia(self, frequencia_segundos):
        """
        Testa uma frequência específica de coleta
        """
        logger.info(f"Iniciando teste para frequência de {frequencia_segundos} segundos")
        
        resultados = {
            'frequencia': frequencia_segundos,
            'inicio': datetime.now(),
            'tentativas': 0,
            'sucessos': 0,
            'falhas': 0,
            'erros_429': 0,
            'timeouts': 0,
            'latencias': [],
            'dados_coletados': []
        }
        
        fim_teste = datetime.now() + timedelta(seconds=self.config['duracao_teste'])
        
        while datetime.now() < fim_teste:
            inicio_request = time.time()
            
            try:
                # Testa coleta para cada símbolo
                for simbolo in self.config['simbolos_teste']:
                    dados = self.coletor.coletar_dados_b3(simbolo)
                    
                    if dados:
                        resultados['sucessos'] += 1
                        resultados['dados_coletados'].append({
                            'timestamp': datetime.now().isoformat(),
                            'simbolo': simbolo,
                            'preco': dados['preco_atual'],
                            'fonte': dados['fonte']
                        })
                    else:
                        resultados['falhas'] += 1
                        
                latencia = time.time() - inicio_request
                resultados['latencias'].append(latencia)
                resultados['tentativas'] += 1
                
                logger.debug(f"Freq {frequencia_segundos}s - Tentativa {resultados['tentativas']} - Latência: {latencia:.3f}s")
                
            except requests.exceptions.Timeout:
                resultados['timeouts'] += 1
                logger.warning(f"Timeout na frequência {frequencia_segundos}s")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    resultados['erros_429'] += 1
                    logger.warning(f"Rate limiting (429) na frequência {frequencia_segundos}s")
                else:
                    resultados['falhas'] += 1
                    logger.error(f"Erro HTTP {e.response.status_code} na frequência {frequencia_segundos}s")
            except Exception as e:
                resultados['falhas'] += 1
                logger.error(f"Erro inesperado na frequência {frequencia_segundos}s: {e}")
            
            # Aguarda até a próxima coleta
            if datetime.now() < fim_teste:
                time.sleep(frequencia_segundos)
        
        resultados['fim'] = datetime.now()
        resultados['duracao_real'] = (resultados['fim'] - resultados['inicio']).total_seconds()
        
        # Calcula estatísticas
        if resultados['latencias']:
            resultados['latencia_media'] = statistics.mean(resultados['latencias'])
            resultados['latencia_mediana'] = statistics.median(resultados['latencias'])
            resultados['latencia_min'] = min(resultados['latencias'])
            resultados['latencia_max'] = max(resultados['latencias'])
        else:
            resultados['latencia_media'] = 0
            resultados['latencia_mediana'] = 0
            resultados['latencia_min'] = 0
            resultados['latencia_max'] = 0
        
        resultados['taxa_sucesso'] = (resultados['sucessos'] / max(resultados['tentativas'], 1)) * 100
        
        logger.info(f"Teste concluído para {frequencia_segundos}s - Taxa de sucesso: {resultados['taxa_sucesso']:.1f}%")
        
        return resultados
    
    def executar_todos_testes(self):
        """
        Executa testes para todas as frequências configuradas
        """
        logger.info("Iniciando bateria de testes de frequência")
        
        for frequencia in self.config['frequencias_teste']:
            logger.info(f"=== TESTANDO FREQUÊNCIA DE {frequencia} SEGUNDOS ===")
            resultado = self.testar_frequencia(frequencia)
            self.resultados[frequencia] = resultado
            
            # Pausa entre testes para não sobrecarregar
            if frequencia != self.config['frequencias_teste'][-1]:
                logger.info("Pausa de 1 minuto entre testes...")
                time.sleep(60)
        
        self.gerar_relatorio()
    
    def gerar_relatorio(self):
        """
        Gera relatório detalhado dos testes
        """
        logger.info("Gerando relatório de testes...")
        
        # Cria pasta de relatórios se não existir
        os.makedirs('relatorios', exist_ok=True)
        
        # Relatório resumido
        resumo = []
        for freq, resultado in self.resultados.items():
            resumo.append({
                'Frequencia (s)': freq,
                'Tentativas': resultado['tentativas'],
                'Sucessos': resultado['sucessos'],
                'Falhas': resultado['falhas'],
                'Taxa Sucesso (%)': round(resultado['taxa_sucesso'], 1),
                'Latencia Media (s)': round(resultado['latencia_media'], 3),
                'Latencia Max (s)': round(resultado['latencia_max'], 3),
                'Erros 429': resultado['erros_429'],
                'Timeouts': resultado['timeouts']
            })
        
        df_resumo = pd.DataFrame(resumo)
        
        # Salva relatório CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_csv = f"relatorios/teste_frequencia_{timestamp}.csv"
        df_resumo.to_csv(arquivo_csv, index=False)
        
        # Salva dados detalhados em JSON
        arquivo_json = f"relatorios/teste_frequencia_detalhado_{timestamp}.json"
        with open(arquivo_json, 'w') as f:
            json.dump(self.resultados, f, default=str, indent=2)
        
        # Gera gráficos
        self.gerar_graficos(timestamp)
        
        # Exibe resumo no console
        logger.info("\n" + "="*80)
        logger.info("RELATÓRIO DE TESTES DE FREQUÊNCIA")
        logger.info("="*80)
        logger.info(df_resumo.to_string(index=False))
        
        # Identifica melhor frequência
        melhor_freq = self.identificar_melhor_frequencia()
        logger.info(f"\n🎯 FREQUÊNCIA RECOMENDADA: {melhor_freq} segundos")
        
        logger.info(f"\n📁 Relatórios salvos em:")
        logger.info(f"   - CSV: {arquivo_csv}")
        logger.info(f"   - JSON: {arquivo_json}")
        logger.info(f"   - Gráficos: relatorios/graficos_{timestamp}/")
    
    def identificar_melhor_frequencia(self):
        """
        Identifica a melhor frequência baseada em critérios
        """
        melhor_freq = None
        melhor_score = 0
        
        for freq, resultado in self.resultados.items():
            # Score baseado em taxa de sucesso, latência e ausência de rate limiting
            score = (
                resultado['taxa_sucesso'] * 0.5 +  # 50% peso para taxa de sucesso
                (1 / (resultado['latencia_media'] + 0.1)) * 0.3 +  # 30% peso para latência
                (100 - resultado['erros_429']) * 0.2  # 20% peso para ausência de rate limiting
            )
            
            if score > melhor_score:
                melhor_score = score
                melhor_freq = freq
        
        return melhor_freq
    
    def gerar_graficos(self, timestamp):
        """
        Gera gráficos de análise dos testes
        """
        try:
            # Cria pasta para gráficos
            pasta_graficos = f"relatorios/graficos_{timestamp}"
            os.makedirs(pasta_graficos, exist_ok=True)
            
            frequencias = list(self.resultados.keys())
            taxas_sucesso = [self.resultados[f]['taxa_sucesso'] for f in frequencias]
            latencias_medias = [self.resultados[f]['latencia_media'] for f in frequencias]
            erros_429 = [self.resultados[f]['erros_429'] for f in frequencias]
            
            # Gráfico 1: Taxa de Sucesso
            plt.figure(figsize=(12, 8))
            plt.subplot(2, 2, 1)
            plt.bar(frequencias, taxas_sucesso, color='green', alpha=0.7)
            plt.title('Taxa de Sucesso por Frequência')
            plt.xlabel('Frequência (segundos)')
            plt.ylabel('Taxa de Sucesso (%)')
            plt.grid(True, alpha=0.3)
            
            # Gráfico 2: Latência Média
            plt.subplot(2, 2, 2)
            plt.bar(frequencias, latencias_medias, color='blue', alpha=0.7)
            plt.title('Latência Média por Frequência')
            plt.xlabel('Frequência (segundos)')
            plt.ylabel('Latência (segundos)')
            plt.grid(True, alpha=0.3)
            
            # Gráfico 3: Erros 429 (Rate Limiting)
            plt.subplot(2, 2, 3)
            plt.bar(frequencias, erros_429, color='red', alpha=0.7)
            plt.title('Erros 429 (Rate Limiting) por Frequência')
            plt.xlabel('Frequência (segundos)')
            plt.ylabel('Quantidade de Erros 429')
            plt.grid(True, alpha=0.3)
            
            # Gráfico 4: Comparação Geral
            plt.subplot(2, 2, 4)
            x = range(len(frequencias))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], taxas_sucesso, width, label='Taxa Sucesso (%)', alpha=0.7)
            plt.bar([i + width/2 for i in x], [l*100 for l in latencias_medias], width, label='Latência (s) * 100', alpha=0.7)
            
            plt.title('Comparação Geral')
            plt.xlabel('Frequências')
            plt.ylabel('Valores')
            plt.xticks(x, frequencias)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{pasta_graficos}/analise_frequencias.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"📊 Gráficos gerados em: {pasta_graficos}/")
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráficos: {e}")

def main():
    """
    Função principal para executar os testes
    """
    logger.info("🚀 Iniciando Testador de Frequência da API B3")
    logger.info("="*60)
    
    # Configura logger para arquivo
    logger.add("logs/teste_frequencia.log", rotation="1 day", retention="7 days")
    
    testador = TestadorFrequencia()
    
    try:
        testador.executar_todos_testes()
        logger.success("✅ Todos os testes concluídos com sucesso!")
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        raise

if __name__ == "__main__":
    main() 