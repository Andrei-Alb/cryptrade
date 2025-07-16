# PRD: Melhorias de Desempenho, Autonomia e Uso de Hardware para o Robô de Trading

## Objetivo

Transformar o robô de trading em um sistema 100% autônomo, rápido e capaz de utilizar todo o potencial do hardware disponível (CPU, RAM, GPU AMD RX6600), eliminando gargalos de performance, delays artificiais e tornando o fechamento de ordens e decisões da IA praticamente em tempo real.

---

## 1. Uso de GPU para IA (Ollama/Llama.cpp)
- **Descrição:** Garantir que a IA (Ollama/Llama.cpp) utilize a GPU AMD RX6600 para acelerar as inferências.
- **Ações:**
  - Documentar como rodar Ollama/Llama.cpp com suporte a GPU AMD (ROCm/OpenCL).
  - Adicionar logs no sistema para indicar se a IA está usando GPU.
  - Garantir que o modelo carregado está otimizado para GPU.
- **Critério de Aceitação:** Logs mostram uso de GPU e tempo de inferência da IA cai significativamente.

---

## 2. Paralelismo Total no Processamento de IA
- **Descrição:** Processar cada par de trading em uma thread/processo separado para análise IA, aproveitando múltiplos núcleos e a GPU.
- **Ações:**
  - Refatorar o processamento de IA para que cada par seja analisado em paralelo, sem esperar o batch inteiro.
  - Permitir que múltiplas inferências rodem simultaneamente, limitando apenas pela capacidade do hardware.
- **Critério de Aceitação:** Logs mostram múltiplas análises IA ocorrendo em paralelo, sem bloqueios.

---

## 3. Remoção de Delays Artificiais
- **Descrição:** Eliminar todos os `time.sleep` desnecessários do ciclo de ordens e IA.
- **Ações:**
  - Remover delays do processamento de ordens abertas.
  - Manter apenas delays mínimos para coleta de dados (para não sobrecarregar APIs externas).
- **Critério de Aceitação:** O ciclo de fechamento de ordens e análise IA ocorre o mais rápido possível, limitado apenas por latência real de mercado/modelo.

---

## 4. Tempo Mínimo de Ordem Dinâmico e Inteligente
- **Descrição:** O tempo mínimo de ordem aberta será definido pela IA, limitado entre 5s e 90s (1m30).
- **Ações:**
  - Adicionar campo `tempo_minimo_ordem` na decisão da IA.
  - Usar esse valor no lugar do tempo fixo de 30s.
  - Garantir que a IA pode sugerir tempos diferentes conforme contexto de mercado.
- **Critério de Aceitação:** Logs mostram tempo mínimo de ordem variando conforme decisão da IA, sempre dentro dos limites.

---

## 5. Otimização do Batch Interval
- **Descrição:** Reduzir o `batch_interval` para 5-10s por padrão, permitindo configuração dinâmica.
- **Ações:**
  - Ajustar o valor padrão no `config.yaml`.
  - Permitir ajuste dinâmico sem reiniciar o robô.
- **Critério de Aceitação:** A IA processa lotes de dados a cada 5-10s, sem atrasos perceptíveis.

---

## 6. Paralelização do Processamento de Ordens Abertas
- **Descrição:** Cada ordem aberta será processada em uma thread separada, permitindo fechamento simultâneo.
- **Ações:**
  - Refatorar o processamento de ordens abertas para ser multi-thread.
  - Garantir sincronização e integridade dos dados no banco.
- **Critério de Aceitação:** Logs mostram múltiplas ordens sendo fechadas em paralelo, sem travamentos.

---

## 7. Logs Detalhados e Diagnóstico de Performance
- **Descrição:** Adicionar logs detalhados de tempo de processamento, uso de hardware e status de cada etapa crítica.
- **Ações:**
  - Logar tempo de inferência da IA, tempo de fechamento de ordem, uso de CPU/GPU (se possível).
  - Logar fallback para análise técnica caso a IA trave.
- **Critério de Aceitação:** Logs permitem diagnóstico fácil de gargalos e uso de hardware.

---

## 8. Robustez e Resiliência
- **Descrição:** Garantir que o sistema continue operando mesmo se a IA travar ou o coletor de preços falhar.
- **Ações:**
  - Implementar fallback para análise técnica simples se a IA não responder.
  - Garantir que o coletor de preços sempre tenha dados atualizados (WebSocket + REST).
- **Critério de Aceitação:** O robô nunca para de operar por falha da IA ou do coletor.

---

## 9. Critérios Gerais de Aceitação
- O robô fecha ordens abertas automaticamente e rapidamente, sem delays artificiais.
- A IA toma decisões em tempo real, usando GPU.
- O sistema é 100% autônomo, sem necessidade de intervenção manual.
- Logs detalhados permitem identificar qualquer gargalo de performance.

---

## 10. Observações Técnicas
- O uso de GPU AMD depende do suporte do Ollama/Llama.cpp ao ROCm/OpenCL. Caso não seja possível, considerar alternativas como rodar o modelo via `llama-cpp-python` com OpenCL.
- O paralelismo será limitado apenas pela capacidade do hardware (CPU/GPU/RAM).
- Todas as mudanças serão documentadas e testadas em ambiente controlado antes de produção. 

---

## Tasks

- [x] **Documentar como rodar Ollama/Llama.cpp com GPU AMD (ROCm/OpenCL) e garantir uso da GPU RX6600**
- [x] Adicionar logs para indicar uso de GPU e tempo de inferência da IA (parcial, logs de tempo de inferência já implementados)
- [x] Refatorar processamento de IA para paralelizar por par (thread/processo por par)
- [x] Remover todos os `time.sleep` desnecessários do ciclo de ordens e IA
- [x] Tornar o tempo mínimo de ordem dinâmica, definido pela IA (campo `tempo_minimo_ordem`), limitado entre 5s e 90s
- [x] Ajustar o batch_interval padrão para 5-10s e permitir ajuste dinâmico
- [x] Refatorar processamento de ordens abertas para ser multi-thread, garantindo integridade dos dados
- [ ] Adicionar logs detalhados de tempo de processamento, uso de hardware e status de cada etapa crítica
- [x] Implementar fallback para análise técnica simples caso a IA trave (com log explícito)
- [x] Garantir que o coletor de preços sempre tenha dados atualizados (WebSocket + REST, fallback automático e log)
- [ ] Testar todas as mudanças em ambiente controlado antes de produção
- [ ] Atualizar documentação do projeto com as novas instruções e requisitos 

---

## 11. Fallback Automático para GPU AMD (LlamaCppClient)
- **Descrição:** Se Ollama não suportar GPU AMD ou estiver indisponível, o sistema usa automaticamente o backend Python `llama-cpp-python` (LlamaCppClient) com OpenCL/ROCm para inferência acelerada por GPU AMD.
- **Ações:**
  - Implementar client Python com `llama-cpp-python` e `use_opencl=True`.
  - Integrar fallback automático no client IA principal.
  - Logar explicitamente qual backend foi usado (Ollama/NVIDIA ou LlamaCpp/AMD).
  - Logar tempo de inferência e se GPU foi utilizada.
- **Critério de Aceitação:** Logs mostram claramente qual backend foi usado e o tempo de inferência, e o sistema funciona com GPU AMD sem intervenção manual.

---

## Exemplo de Logs Esperados

```
[IA] Inferência via Ollama concluída em 2.13s (backend: Ollama, GPU: NVIDIA apenas)
[IA] Ollama indisponível ou lento: ...
[IA] Tentando fallback para LlamaCppClient (GPU AMD/OpenCL)...
[IA] Llama.cpp inicializado com GPU AMD (OpenCL)!
[IA] Inferência via LlamaCppClient concluída em 1.45s (backend: LlamaCpp, GPU: AMD)
```

---

## Checklist de Validação
- [x] Fallback automático para GPU AMD implementado
- [x] Logs detalhados de backend e tempo de inferência
- [ ] Validar em ambiente real com GPU AMD RX6600
- [ ] Atualizar README com instruções de uso do backend Python

---

## Apêndice: Guia de Uso de GPU AMD com Ollama/Llama.cpp

### 1. Introdução
Este guia mostra como rodar modelos Llama (Ollama/Llama.cpp) usando sua GPU AMD RX6600 para acelerar a IA do robô de trading.

### 2. Ollama: Suporte a GPU AMD
- **Ollama** oficialmente suporta apenas CUDA (NVIDIA) até o momento.
- Para AMD, é necessário usar builds experimentais do Llama.cpp com suporte a ROCm (Linux) ou OpenCL.
- Alternativa: usar `llama-cpp-python` com OpenCL.

### 3. Usando Llama.cpp com GPU AMD (ROCm/OpenCL)

a) Instale dependências ROCm (Linux)
- Siga o guia oficial ROCm para sua distribuição: https://rocm.docs.amd.com/en/latest/
- Verifique se sua GPU aparece em `rocminfo` ou `clinfo`.

b) Compile o Llama.cpp com OpenCL
```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make LLAMA_OPENCL=1
```

c) Rode o modelo com OpenCL
```bash
./main -m ./models/llama-2-7b-chat.Q4_K_M.gguf --gpu 0 --n-gpu-layers 99 --use-opencl
```
- Ajuste o caminho do modelo conforme necessário.
- O parâmetro `--use-opencl` força uso da GPU AMD.

d) Usando com Python
```bash
pip install llama-cpp-python
```
```python
from llama_cpp import Llama
llm = Llama(model_path="./models/llama-2-7b-chat.Q4_K_M.gguf", n_gpu_layers=99, use_opencl=True)
```

### 4. Diagnóstico: Como saber se está usando a GPU?
- Monitore o uso da GPU com `watch -n 1 rocm-smi` ou `radeontop`.
- O tempo de inferência deve cair drasticamente (respostas em 1-3s para prompts pequenos).
- Logs do Llama.cpp/Python devem indicar uso de OpenCL.

### 5. Integrando com o Robô
- Se usar Ollama, aponte para o endpoint HTTP normalmente (mas só terá GPU se for NVIDIA).
- Para AMD, prefira rodar o Llama.cpp como serviço local (REST ou via Python) e adaptar o client Python para usar `llama-cpp-python`.
- Ajuste o client IA do robô para usar o endpoint local do Llama.cpp ou a API Python.

### 6. Alternativas
- Se não conseguir rodar com GPU AMD, use instâncias cloud com GPU NVIDIA ou CPUs potentes.
- Fique atento a atualizações do Ollama para suporte oficial a AMD/ROCm.

### 7. Referências
- [Llama.cpp](https://github.com/ggerganov/llama.cpp)
- [ROCm AMD](https://rocm.docs.amd.com/en/latest/)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [Ollama](https://ollama.com/)

**Dúvidas? Consulte o README do projeto ou abra um PRD de suporte!** 