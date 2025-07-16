# PRD: Melhorias na IA de Trading - Estagnação, Seletividade e Aprendizado

## Objetivo
Tornar a confiança da IA mais seletiva, volátil e preditiva, reduzindo entradas em sinais medianos e melhorando o aprendizado após losses.

---

## 1. Confiança Dinâmica e Binária
- **Problema:** Confiança quase sempre em 0.7125, sem volatilidade.
- **Melhoria:**
  - Ajustar o cálculo/prompt para só dar confiança ≥ 0.8 quando houver múltiplos sinais fortíssimos.
  - Para sinais medianos, confiança < 0.6.
  - Aumentar o threshold de entrada para ≥ 0.8.
  - Corrigir possíveis bugs/lógicas que fixam a confiança.

## 2. Seletividade e Gestão de Entradas
- **Problema:** Robô opera quase sempre, mesmo após loss.
- **Melhoria:**
  - Permitir apenas uma entrada por vez.
  - Após loss, só liberar nova entrada se a confiança for significativamente maior que o mínimo (ex: >0.85).
  - Registrar contexto de drawdown e exigir sinais ainda mais fortes após sequência de losses.

## 3. Aprendizado e Feedback
- **Problema:** O aprendizado não está sendo usado para ajustar a seletividade.
- **Melhoria:**
  - Registrar padrões de loss/win e ajustar thresholds dinamicamente.
  - Aprender com padrões de loss para evitar repetições.

## 4. Outliers e Cálculo de Lucro
- **Problema:** Existem valores extremos de lucro/perda.
- **Melhoria:**
  - Corrigir o cálculo de lucro/perda para evitar outliers irreais.

---

## Critérios de Aceite
- Distribuição de confiança mais variada (poucas ordens com confiança intermediária, maioria em extremos).
- Redução do número de operações em sinais medianos.
- Bloqueio de novas entradas após loss, exigindo sinais mais fortes para nova tentativa.
- Aprendizado contínuo e ajuste dinâmico dos thresholds.
- Cálculo de lucro/perda sem outliers irreais.

---

## TASKS

- [x] Ajustar prompt e lógica de confiança para maior seletividade e volatilidade
- [x] Aumentar threshold de entrada para ≥ 0.8
- [x] Permitir apenas uma entrada por vez
- [x] Implementar bloqueio e seletividade extra após loss/drawdown
- [x] Corrigir cálculo de lucro/perda para evitar outliers
- [x] Aprimorar registro e uso do aprendizado para ajuste dinâmico
- [ ] Monitorar impacto das mudanças e ajustar conforme necessário 

## Observação
O sistema de aprendizado dinâmico já está implementado: ajusta thresholds de confiança e tempo de estagnação automaticamente, registra contexto de drawdown, recomenda ajustes e registra aprendizado detalhado de cada ordem. O monitoramento contínuo dos resultados deve ser mantido para ajustes futuros finos. 