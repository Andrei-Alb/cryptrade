# PRD: Correção Crítica na Execução da IA de Trading

## Objetivo
Garantir que a IA opere estritamente conforme as regras de risco/retorno, confiança e lógica de decisão dos PRDs, evitando operações aleatórias e prejuízos desnecessários.

---

## Problemas Identificados
- Stop loss maior que o alvo (risco maior que o potencial de ganho).
- Confiança travada em valores intermediários (ex: 0.71).
- Operações aleatórias sem padrão de contexto de mercado.
- Threshold de confiança e regras de drawdown não respeitados.

---

## Tarefas de Correção
- [x] Revisar e corrigir o cálculo de stop e alvo:
  - Para compra: preco_alvo > preco_entrada > preco_stop
  - Para venda: preco_alvo < preco_entrada < preco_stop
  - Distância até o alvo ≥ distância até o stop
- [x] Implementar validação de risco/retorno antes de executar qualquer ordem:
  - Não permitir ordens onde risco > retorno
- [x] Revisar e reforçar lógica de confiança:
  - Confiança só ≥ 0.8 em sinais fortíssimos
  - Corrigir prompt e lógica para evitar valores travados
- [x] Garantir que o threshold de confiança está sendo respeitado no pipeline
- [x] Auditar e reforçar regras de drawdown e aprendizado
- [ ] Testar o sistema com logs detalhados para garantir aderência aos PRDs

---

## Critérios de Aceite
- Nenhuma ordem executada com risco maior que o potencial de ganho
- Confiança variando conforme a força dos sinais
- Operações apenas em sinais realmente fortes
- Aprendizado e drawdown influenciando decisões
- Logs claros e detalhados das decisões e validações 