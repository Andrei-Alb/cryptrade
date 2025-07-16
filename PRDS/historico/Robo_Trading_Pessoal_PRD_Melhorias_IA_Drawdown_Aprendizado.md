# PRD: Aprimoramento do Aprendizado da IA em Cenários de Drawdown

## Objetivo
Tornar a IA mais resiliente e inteligente em cenários de sequência de perdas (drawdown), ajustando seu comportamento para aprender com os erros, reduzir riscos e aumentar a assertividade das próximas entradas.

---

## Justificativa
Bloquear totalmente as entradas após uma sequência de losses impede o aprendizado real da IA. O ideal é que a IA reconheça o cenário adverso, ajuste sua estratégia (ficando mais cautelosa), mas continue aprendendo e registrando o contexto para evoluir sua tomada de decisão.

---

## Requisitos Funcionais
1. **Penalização de padrões de loss recorrentes**
   - Reduzir a confiança das próximas entradas após sequência de losses.
   - Registrar explicitamente no aprendizado que está em cenário de drawdown.
2. **Ajuste de comportamento em drawdown**
   - Exigir sinais mais fortes (threshold de confiança mais alto) para novas entradas.
   - Priorizar operações a favor da tendência principal.
   - Operar com tamanho reduzido (se aplicável).
   - Continuar aprendendo e registrando o contexto de cada tentativa.
3. **Aprimoramento do sistema de aprendizado**
   - Registrar no banco o contexto de drawdown e os ajustes feitos.
   - Usar o histórico de acertos/erros para ajustar automaticamente thresholds e filtros.
   - Aprender a sair mais rápido de cenários ruins e ser mais agressiva quando o mercado está favorável.

---

## Critérios de Sucesso
- A IA reduz a frequência de losses em sequência.
- O aprendizado é contínuo, mesmo em cenários adversos.
- O sistema registra e utiliza o contexto de drawdown para evoluir a estratégia.
- A assertividade das entradas aumenta após períodos de drawdown.

---

## TASKS
- [x] Implementar penalização de confiança e exigência de sinais mais fortes em sequência de losses
- [x] Registrar contexto de drawdown no aprendizado
- [ ] Ajustar sistema para aprendizado contínuo em drawdown
- [ ] Monitorar impacto das mudanças e ajustar parâmetros

### Atualização 1
- Penalização de confiança e exigência de sinais mais fortes em drawdown implementada: após 3 losses seguidos, a IA só permite novas entradas com confiança mínima de 0.8 e registra o contexto de drawdown na decisão. 

### Atualização 2
- Registro do contexto de drawdown implementado: agora cada ordem registra se foi tomada em cenário de drawdown, permitindo análise e aprendizado mais refinado pela IA. 