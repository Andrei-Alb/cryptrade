import json
import logging
import subprocess
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LlamaCppClient:
    def __init__(self, model_path: str = "llama3.1:8b"):
        """
        Inicializa cliente Llama usando Ollama
        """
        self.model_name = model_path
        logger.info(f"[IA] Cliente Llama inicializado com modelo: {self.model_name}")
    
    def _criar_prompt_trading(self, dados: Dict[str, Any]) -> str:
        import json
        dados_json = json.dumps(dados, ensure_ascii=False)
        return (
            "Responda apenas com um JSON real de decisão de trading, sem comentários, sem explicações, sem repetir os dados de entrada. "
            "A resposta deve começar diretamente com { e terminar com }. Não inclua nada além do JSON. "
            "Formato esperado:\n"
            "{\n"
            "  \"decisao\": \"comprar\" ou \"vender\" ou \"aguardar\" ou \"fechar_ordem\",\n"
            "  \"confianca\": 0.0 a 1.0,\n"
            "  \"razao\": \"justificativa\",\n"
            "  \"quantidade\": 1,\n"
            "  \"stop_loss\": valor,\n"
            "  \"take_profit\": valor,\n"
            "  \"acao_ordem\": \"manter\" ou \"fechar_antecipado\" ou \"ajustar_stop\"\n"
            "}\n"
            "Responda apenas com o JSON de decisão, sem repetir os dados de entrada."
        )

    def _processar_resposta(self, resposta_bruta: str) -> Optional[Dict[str, Any]]:
        """
        Processa resposta do modelo e extrai JSON válido
        """
        if not resposta_bruta or not resposta_bruta.strip():
            logger.error("[IA] Resposta vazia do modelo")
            return None
        
        # Limpar resposta
        resposta_limpa = resposta_bruta.strip()
        
        # Procurar por JSON válido
        try:
            # Tentar encontrar JSON entre { e }
            inicio = resposta_limpa.find('{')
            fim = resposta_limpa.rfind('}')
            
            if inicio != -1 and fim != -1 and fim > inicio:
                json_str = resposta_limpa[inicio:fim+1]
                resultado = json.loads(json_str)
                logger.info(f"[IA] JSON extraído com sucesso: {resultado}")
                return resultado
            else:
                logger.error(f"[IA] Nenhum JSON válido encontrado na resposta: {resposta_limpa}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"[IA] Erro ao decodificar JSON: {e}")
            logger.error(f"[IA] Resposta problemática: {resposta_limpa}")
            return None
        except Exception as e:
            logger.error(f"[IA] Erro inesperado ao processar resposta: {e}")
            return None

    def _converter_para_serializavel(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Converte dados para formato serializável em JSON"""
        try:
            dados_serializaveis = {}
            for key, value in dados.items():
                if hasattr(value, 'to_dict'):
                    dados_serializaveis[key] = value.to_dict()
                elif isinstance(value, (dict, list, str, int, float, bool)):
                    dados_serializaveis[key] = value
                else:
                    dados_serializaveis[key] = str(value)
            return dados_serializaveis
        except Exception as e:
            logger.error(f"[IA] Erro ao converter dados: {e}")
            return dados

    def _extrair_json(self, texto: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON válido do texto de resposta"""
        try:
            # Procurar por JSON no texto
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, texto)
            
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"[IA] Erro ao extrair JSON: {e}")
            return None

    def _validar_e_normalizar_decisao(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e normaliza os valores da decisão da IA"""
        try:
            # Normalizar confiança
            confianca = decisao.get('confianca', 0.5)
            confianca = max(0.1, min(1.0, float(confianca)))
            
            # Normalizar quantidade
            quantidade = decisao.get('quantidade', 1)
            quantidade = max(1, min(10, int(quantidade)))
            
            # Normalizar stop loss (entre -5% e -1%)
            stop_loss = decisao.get('stop_loss', -2.0)
            stop_loss = max(-5.0, min(-1.0, float(stop_loss)))
            
            # Normalizar take profit (entre +1% e +10%)
            take_profit = decisao.get('take_profit', 3.0)
            take_profit = max(1.0, min(10.0, float(take_profit)))
            
            return {
                'decisao': decisao.get('decisao', 'aguardar'),
                'confianca': confianca,
                'razao': decisao.get('razao', 'Análise técnica'),
                'quantidade': quantidade,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'acao_ordem': decisao.get('acao_ordem', 'manter')
            }
        except Exception as e:
            logger.error(f"[IA] Erro ao validar decisão: {e}")
            return {
                'decisao': 'aguardar',
                'confianca': 0.5,
                'razao': 'Erro na validação',
                'quantidade': 1,
                'stop_loss': -2.0,
                'take_profit': 3.0,
                'acao_ordem': 'manter'
            }

    def analisar_dados_mercado(self, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analisa dados de mercado e retorna decisão da IA"""
        try:
            # Converter dados para formato serializável
            dados_serializaveis = self._converter_para_serializavel(dados)
            
            prompt = f"""
Você é um trader especializado em criptomoedas. Analise os dados de mercado fornecidos e tome uma decisão de trading.

DADOS DE MERCADO:
{json.dumps(dados_serializaveis, ensure_ascii=False, indent=2)}

INSTRUÇÕES IMPORTANTES:
1. Analise tendências, indicadores técnicos e volume
2. Tome decisão: "comprar", "vender" ou "aguardar"
3. Confiança deve ser entre 0.1 e 1.0
4. Quantidade deve ser entre 1 e 10
5. Stop Loss deve ser entre -5% e -1% do preço atual (valores negativos)
6. Take Profit deve ser entre +1% e +10% do preço atual (valores positivos)
7. Ação para ordens abertas: "manter", "fechar" ou "ajustar"

EXEMPLO DE RESPOSTA VÁLIDA:
{{
  "decisao": "comprar",
  "confianca": 0.85,
  "razao": "Tendência ascendente e indicadores técnicos favoráveis",
  "quantidade": 2,
  "stop_loss": -2.5,
  "take_profit": 5.0,
  "acao_ordem": "manter"
}}

RESPONDA APENAS COM JSON VÁLIDO, SEM TEXTO ADICIONAL:
"""
            
            logger.info(f"[IA] Enviando prompt para modelo {self.model_name}")
            
            # Executar comando ollama com timeout aumentado
            resultado = subprocess.run(
                ['ollama', 'run', self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=60  # 60 segundos timeout
            )
            
            if resultado.returncode != 0:
                logger.error(f"[IA] Erro ao executar Ollama: {resultado.stderr}")
                return None
                
            resposta_bruta = resultado.stdout.strip()
            logger.info(f"[IA] Resposta bruta do modelo: {resposta_bruta}")
            
            # Extrair JSON da resposta
            json_extraido = self._extrair_json(resposta_bruta)
            
            if json_extraido:
                logger.info(f"[IA] JSON extraído com sucesso: {json_extraido}")
                
                # Validar e normalizar valores
                json_extraido = self._validar_e_normalizar_decisao(json_extraido)
                
                return json_extraido
            else:
                logger.error("[IA] Falha ao extrair JSON válido da resposta")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("[IA] Timeout ao executar modelo")
            return None
        except Exception as e:
            logger.error(f"[IA] Erro ao analisar dados: {e}")
            return None 