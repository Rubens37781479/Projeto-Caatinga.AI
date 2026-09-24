# Relatório — Caatinga.AI, Sprint 1

> Este relatório será preenchido por etapas. As seções de resultados dependem da
> execução do programa com a matrícula-semente da dupla e não devem ser
> preenchidas com valores fictícios.

## Parte 1 — O agente antes do código

### 1.1 Ficha PEAS

| Elemento | Descrição |
|---|---|
| **P — Desempenho** | Maximizar o número de talhões confirmados como infestados e encaminhados para manejo por hora de operação (**talhões confirmados/h**). A avaliação também registra o custo de deslocamento (**unidades de custo**) e os falsos alertas (**talhões**), para que velocidade não esconda desperdício nem erro. |
| **E — Ambiente** | Pomar de manga em grade de 12 × 12; portão em (0, 0); ponto de coleta em (11, 11); terrenos firmes, encharcados e bloqueados; pragas de estado inicialmente desconhecido; agrônomo que recebe os talhões suspeitos. |
| **A — Atuadores** | Mover para norte, sul, leste ou oeste; solicitar/realizar leitura do sensor óptico; registrar um talhão como suspeito e encaminhá-lo para inspeção humana. |
| **S — Sensores** | Posição atual; mapa e tipo/custo de cada talhão; leitura do sensor óptico; parâmetros do sensor derivados da matrícula; confirmação humana de infestação, quando disponível. |

### 1.2 Classificação do ambiente

| Dimensão | Classificação adotada | Evidência do cenário e justificativa |
|---|---|---|
| Observável | Parcialmente observável | O mapa pode ser gerado a partir da matrícula e a posição pode ser acompanhada, mas o agente usa um sensor para apontar pragas e o enunciado descreve sensibilidade e falso positivo. Logo, a leitura não revela perfeitamente se o talhão está infestado. |
| Determinístico | Não determinístico quanto à detecção; determinístico quanto ao deslocamento | As transições de posição e os custos de entrada são definidos pela grade. Já o sensor tem sensibilidade e taxa de falso positivo, indicando resultados de detecção incertos. |
| Episódico | Sequencial | A decisão de movimento altera a posição seguinte e as opções/custos futuros. A rota até (11, 11) é uma sequência de ações cujo custo total importa. |
| Estático | Assumido estático durante uma execução | O enunciado define uma grade e custos de terreno, sem descrever mudanças enquanto o agente se desloca. A hipótese vale para o mapa; a dinâmica biológica das pragas não foi especificada. |
| Discreto | Discreto | O pomar é uma grade finita de talhões, com símbolos discretos, posições inteiras e ações nas quatro direções ortogonais. |
| Agente único | Agente único para a busca e navegação | O problema de busca descreve um agente que percorre a grade. O agrônomo aparece como destinatário dos alertas, sem ações concorrentes modeladas. |

**Dimensões que o enunciado não determina por completo.** A observabilidade depende
do que o agente recebe além da leitura do sensor: se o mapa completo e os estados
reais das pragas fossem fornecidos, seria totalmente observável; se somente leituras
imperfeitas estiverem disponíveis, é parcialmente observável. A informação que
decidiria é a especificação das observações e de como a verdade sobre infestação
fica disponível ao agente. A dimensão estático/dinâmico depende de as pragas
poderem surgir, desaparecer ou se espalhar durante a operação. O enunciado não
informa essa evolução nem sua escala de tempo; sem mudança durante a rota, é
estático, e com mudança relevante, é dinâmico. Para esta entrega, adoto a leitura
conservadora de observabilidade parcial para pragas e mapa fixo durante uma
execução.

### 1.3 Tipo de agente

Escolho um **agente baseado em objetivos**. Ele precisa alcançar um estado-meta
explícito — o ponto de coleta — e escolher ações considerando sequências futuras:
por exemplo, uma rota com menos passos pode custar mais quando atravessa solo
encharcado. Busca de custo uniforme e A* são adequadas para planejar essa rota.
O estado interno também pode guardar leituras e talhões já inspecionados, mas a
decisão central é encontrar um plano que satisfaça a meta, não apenas reagir à
última leitura. Um agente puramente reativo não compara o custo acumulado das
rotas até a meta.

### 1.4 Métrica perversa

Uma métrica aparentemente razoável seria **maximizar alertas emitidos por hora**.
O agente poderia elevar a sensibilidade operacional marcando como suspeito todo
talhão visitado, sem filtrar os resultados do sensor. Isso aumentaria a contagem
imediata, mas sobrecarregaria o agrônomo com falsos positivos. O efeito apareceria
desde os primeiros talhões próximos ao portão, que seriam todos encaminhados,
mesmo sem evidência de infestação.

A correção é medir **infestações confirmadas encaminhadas por hora** e contabilizar
explicitamente falsos positivos por semana, junto do custo de deslocamento. Uma
decisão de alerta deve usar a probabilidade posterior de infestação e um limiar
operacional definido pela cooperativa, em vez de premiar a quantidade bruta de
alertas. Assim, o desempenho reconhece detecções úteis e torna visível o custo
dos alertas incorretos.

## Próximas seções

As Partes 2 a 5 serão adicionadas após a implementação e execução com a
matrícula-semente real. A Parte 6 (anexo de uso de IA) será registrada com os
prompts e respostas efetivamente usados durante o trabalho.
