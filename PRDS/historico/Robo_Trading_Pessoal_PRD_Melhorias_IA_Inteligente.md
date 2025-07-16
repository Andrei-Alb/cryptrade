# PRD: IA de Trading Inteligente - Gestão Ativa, Trailing Stop e Fechamento Proativo

## Objetivo
Desenvolver uma IA de trading capaz de gerenciar ordens de forma ativa e inteligente, maximizando lucros e minimizando perdas por meio de:
- Fechamento antecipado de ordens ao identificar reversão ou esgotamento do potencial de lucro.
- Ajuste dinâmico do stop loss (trailing stop) para proteger ganhos.
- Análise contínua do contexto do mercado durante a vida da ordem.
- Aprendizado contínuo com cada fechamento inteligente.

---

## Justificativa
A abordagem tradicional de alvo/stop/timeout é limitada e pode desperdiçar oportunidades de lucro ou aumentar perdas. Uma IA proativa, que acompanha cada ordem em tempo real e toma decisões baseadas no contexto, é fundamental para:
- Proteger lucros já conquistados.
- Evitar perdas desnecessárias.
- Aproveitar tendências favoráveis ao máximo.
- Aprender com cada situação para evoluir a estratégia.

---

## Requisitos Funcionais
1. **Gestão Ativa da Ordem**
   - A IA deve monitorar cada ordem aberta em tempo real, reavaliando o cenário a cada novo dado de mercado.
2. **Trailing Stop Dinâmico**
   - Registrar o maior lucro atingido durante a ordem.
   - Se o lucro recuar mais que um threshold (ex: 0.1% ou 30% do pico), fechar a ordem para proteger o ganho.
   - Ajustar o stop loss para o preço de entrada ou para um valor acima do preço de entrada conforme o lucro evolui.
3. **Fechamento Inteligente por Sinais de Reversão**
   - Se indicadores (RSI, médias, volume, etc.) apontarem reversão ou perda de força, fechar a ordem antes do stop.
4. **Aproveitar Tendências**
   - Se o lucro está aumentando e o cenário é favorável, manter a ordem aberta para buscar mais.
5. **Registro e Aprendizado**
   - Registrar no banco e no sistema de aprendizado todos os fechamentos inteligentes, com contexto e justificativa.
   - Aprender padrões de sucesso e fracasso para aprimorar decisões futuras.

---

## Critérios de Sucesso
- A IA fecha ordens de forma proativa, protegendo lucros e evitando perdas maiores.
- O trailing stop é ajustado dinamicamente e funciona na prática.
- O número de ordens fechadas com lucro aumenta e as perdas são reduzidas.
- O sistema de aprendizado registra e utiliza os dados dos fechamentos inteligentes.
- O monitor exibe claramente os fechamentos inteligentes e os ajustes de stop.

---

## TASKS
- [x] Implementar lógica de trailing stop dinâmico no gestor de ordens
- [x] Adicionar fechamento inteligente por sinais de reversão
- [x] Ajustar stop loss dinamicamente conforme o lucro evolui
- [x] Aprimorar análise de contexto e tendência durante a ordem
- [x] Registrar e aprender com cada fechamento inteligente
- [x] Atualizar monitor visual para exibir fechamentos inteligentes
- [~] Monitorar impacto das mudanças e ajustar parâmetros

### Atualização 7
- Monitoramento do impacto das mudanças iniciado: métricas como taxa de acerto, lucro médio, drawdown e quantidade de fechamentos inteligentes serão acompanhadas por pelo menos 1 semana. O sistema de aprendizado irá sugerir ou aplicar ajustes automáticos nos thresholds e critérios conforme o desempenho real. 