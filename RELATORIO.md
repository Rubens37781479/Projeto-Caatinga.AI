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

## Semente e parâmetros usados nos experimentos

Semente informada: **24114031** (matrícula `241.14.031`, lida do endereço
fornecido). A segunda pessoa da dupla ainda não foi identificada. Pomar gerado:
12 × 12, com 144 posições possíveis, das quais 124 são livres. Parâmetros do
sensor: prevalência 0,0236; sensibilidade 0,99; taxa de falso positivo 0,03;
1.200 talhões por semana.

## Parte 2 — Formulação e busca cega

### 2.1 Formulação

- **Estado inicial:** posição (0, 0).
- **Ações:** mover uma célula para Norte, Sul, Oeste ou Leste, se a posição de
  destino estiver dentro da grade e não for bloqueada.
- **Modelo de transição:** a ação move o agente para a célula vizinha escolhida;
  o mapa não muda.
- **Teste de objetivo:** posição atual igual a (11, 11).
- **Custo do caminho:** soma dos custos das células de destino de cada movimento;
  a célula inicial não é cobrada.

O estado de busca é a coordenada do agente. A codificação tem `12 × 12 = 144`
coordenadas possíveis; 20 células bloqueadas não são estados transitáveis, então
há 124 posições livres neste pomar. Os custos 1 e 4 ficam nas transições, não
fazem parte da identidade do estado.

### 2.2 Resultados das buscas cegas

Ordem dos vizinhos em todas as estratégias: **Norte, Sul, Oeste, Leste**. Nós
expandidos contam estados removidos da fronteira e expandidos; o objetivo é
testado na geração do sucessor. A fronteira máxima é o maior tamanho observado
após uma expansão.

| Estratégia | Custo (unid. de custo) | Passos (movimentos) | Nós expandidos | Fronteira máx. (nós) | Ótima em custo? |
|---|---:|---:|---:|---:|---|
| BFS | 49 | 22 | 122 | 10 | Não |
| DFS | 135 | 54 | 63 | 38 | Não |
| UCS | 34 | 22 | 119 | 16 | Sim |

### 2.3 Por que a BFS é mais cara

A BFS devolve 22 movimentos, o menor número possível, mas custa 49 unidades;
a UCS custa 34. Isso não é bug: a BFS minimiza a quantidade de passos e só
minimiza custo quando cada ação tem o mesmo custo. A hipótese de **custo
uniforme por passo** foi violada: entrar em `.` custa 1 e entrar em `~` custa 4.
Por isso, uma rota com o mesmo número de movimentos pode ter custo maior.

### 2.4 Escalabilidade

O experimento isolou cada execução e interrompeu a primeira que excedeu 60 s.
As três estratégias concluíram em `n = 3200`; em `n = 6400`, a BFS excedeu o
limite de 60 s. A fronteira máxima da BFS em `n = 3200` foi 2.873 e ela expandiu
8.177.392 nós em cerca de 19,16 s. Registro completo: `resultados/limites.csv`.

| n | BFS | DFS | UCS |
|---:|---|---|---|
| 12 | concluiu (122 expandidos) | concluiu (63) | concluiu (119) |
| 40 | concluiu (1.289) | concluiu (793) | concluiu (1.287) |
| 100 | concluiu (7.972) | concluiu (3.314) | concluiu (7.968) |
| 200 | concluiu (31.890) | concluiu (16.924) | concluiu (31.890) |
| 400 | concluiu (127.569) | concluiu (69.144) | concluiu (127.570) |
| 800 | concluiu (510.712) | concluiu (256.473) | concluiu (510.710) |
| 1200 | concluiu (1.149.381) | concluiu (582.186) | concluiu (1.149.379) |
| 1600 | concluiu (2.043.695) | concluiu (1.003.532) | concluiu (2.043.696) |
| 3200 | concluiu (8.177.392) | concluiu (4.081.366) | concluiu (8.177.385) |
| 6400 | **BFS: tempo > 60 s** | não executada após a falha | não executada após a falha |

Na grade, há `V = n²` posições e até `E ≤ 4n²` transições dirigidas. Na
formulação de busca em grafo, BFS/DFS usam `O(V + E)` tempo e `O(V)` memória;
UCS acrescenta o fator da fila de prioridade, `O((V + E) log V)` no limite
usual. Dobrar n quadruplica V. Nesta implementação, a fila da BFS usa uma lista
Python com `pop(0)`, que desloca os elementos restantes; seu custo real inclui
`Σ |fronteira_t|` e pode chegar a `O(V × W)`, onde W é a largura da fronteira
(até `O(n)` nesta grade). De `n=3200` para `n=6400`, isso pode multiplicar o
trabalho por cerca de oito, além de quadruplicar os estados. A execução medida
da BFS ultrapassou 60 s antes de concluir. O experimento confirma o crescimento
de estados e o limite de tempo, não uma falha de pilha.

## Parte 3 — Busca informada

### 3.1 e 3.2 Heurísticas e admissibilidade

| Heurística | Custo (unid. de custo) | Nós expandidos | Admissível? |
|---|---:|---:|---|
| h1 = 0 | 34 | 119 | Sim; nunca supera o custo restante não negativo. |
| h2 = Manhattan | 34 | 94 | Sim; prova abaixo. |
| h3 = 4 × Manhattan | 40 | 31 | Não; contraexemplo abaixo. |

Uma ação muda uma coordenada em uma unidade e custa no mínimo 1 para entrar no
próximo talhão. Logo, qualquer caminho restante precisa de ao menos a distância
Manhattan em movimentos e custa pelo menos essa distância. Bloqueios podem
alongar a rota, nunca encurtá-la. Portanto `h2(n) ≤ custo_real(n, objetivo)`.

No par concreto `(0, 0)` → `(11, 11)`, a heurística h3 estima
`4 × (11 + 11) = 88`, enquanto a rota de custo mínimo restante medida pela UCS
custa 34. Como `88 > 34`, h3 superestima e não é admissível.

### 3.3 Custo de velocidade

O custo de h3 foi 40, contra 34 da UCS: a perda percentual é
`(40 − 34) / 34 × 100 = 17,65%`. Em troca, h3 expandiu 31 nós, 88 a menos que a
UCS (119), e 63 a menos que h2 (94). Na execução medida, o A* com h3 levou
0,075 ms, contra 0,229 ms da UCS; tempos variam por máquina e carga.

Uma condição verificável para aceitar a troca seria a cooperativa fixar um
limite de custo de rota igual ou superior a 40 e um prazo rígido de planejamento
menor que 0,1 ms por consulta na máquina de produção. Nesta execução, h3 mediu
0,075 ms e h2 0,190 ms; se uma avaliação representativa na máquina de produção
confirmar que h2 não atende esse prazo e h3 atende, a redução de latência pode
justificar a perda de 17,65% neste pomar. Sem esse limite e essa medição, a
solução ótima da UCS/h2 é preferível.

### 3.4 Busca local

Estado: conjunto de 15 talhões livres. Um vizinho troca um talhão selecionado por
outro livre. Para tornar o exercício executável sem rótulos reais de praga, o
valor usa pesos de risco sintéticos uniformes em `[0, 1)`, gerados por sementes
reprodutíveis; o objetivo maximiza a soma desses pesos. A duração estimada é
12 minutos por inspeção mais 3 minutos por passo da rota gulosa entre os
talhões e o ponto de coleta, sujeita ao limite de 360 minutos. Os três minutos
por movimento são uma hipótese explícita do modelo local, pois o enunciado não
fornece duração de deslocamento.

Foram executadas 30 sementes por algoritmo. O desvio é populacional.

| Algoritmo | Média (pontos de utilidade) | Desvio padrão (pontos) | Melhor (pontos) |
|---|---:|---:|---:|
| Subida de encosta | 14,0473 | 0,2825 | 14,5182 |
| Têmpera simulada | 14,1039 | 0,2661 | 14,5182 |

A têmpera aceitou uma troca que reduzia temporariamente o valor em todas as
30 execuções: 733 pioras aceitas ao todo (média de 24,43 por rodada). A subida
de encosta aceitou zero. Os contadores por rodada estão em
`resultados/busca_local.csv`. Aceitar piora permite sair de máximos locais; nos
resultados, a têmpera teve média maior, embora os dois métodos tenham encontrado
o mesmo melhor valor. Os pesos são uma simulação para comparar algoritmos, não
medições de infestação real.

### Bônus — Liga de IA: contraexemplo para DFS

Pomar construído manualmente (8 × 8), com a mesma ordem de vizinhos. `#` é
bloqueado, `~` custa 4 e `.` custa 1:

```text
........
~######.
~~~~~~#.
#####~#.
~~~~~~#.
~######.
~~~~~~#.
#####~~.
```

DFS retornou o caminho
`(0,0)→(1,0)→(2,0)→(2,1)→(2,2)→(2,3)→(2,4)→(2,5)→(3,5)→(4,5)→(4,4)→(4,3)→(4,2)→(4,1)→(4,0)→(5,0)→(6,0)→(6,1)→(6,2)→(6,3)→(6,4)→(6,5)→(7,5)→(7,6)→(7,7)`, com 24 movimentos e custo **93**. UCS encontrou a rota pelo topo e pela coluna da direita, com 14 movimentos e custo ótimo **14**. A rota da DFS custa mais de seis vezes o ótimo (`93 / 14 ≈ 6,64`).

## Partes 4 e 5

### Parte 4 — Regras e incerteza

Parâmetros da matrícula-semente: prevalência `0,0236`, sensibilidade `0,99`,
taxa de falso positivo `0,03` e 1.200 talhões por semana.

#### 4.1 Mini sistema especialista

As regras implementadas são:

1. SE `sensor_positivo` E `risco_alto`, ENTÃO `inspecionar_prioridade_alta` (R1).
2. SE `sensor_positivo` E `umidade_alta` E `pulverizacao_antiga`, ENTÃO `risco_alto` (R2).
3. SE `armadilha_positiva` E `fruto_danificado`, ENTÃO `risco_alto` (R3).
4. SE `sensor_positivo` E `umidade_alta`, ENTÃO `inspecionar_prioridade_media` (R4).
5. SE `sensor_negativo` E `fruto_saudavel`, ENTÃO `monitorar_rotina` (R5).
6. SE `pulverizacao_recente` E `sensor_positivo`, ENTÃO `revisar_alerta` (R6).
7. SE `infestacao_confirmada`, ENTÃO `manejo_conforme_protocolo` (R7).

Com os fatos `sensor_positivo`, `umidade_alta` e `pulverizacao_antiga`, o
encadeamento para trás prova a prioridade alta pela cadeia **R2 → R1**. O
programa grava os fatos consultados e as regras usadas em `resultados/resumo.json`
e imprime a cadeia no terminal.

#### 4.2 Caso que quebra a base e correção

Caso: o sensor dá positivo logo após uma pulverização recente, enquanto a
umidade está alta. Sem tratamento de conflito, R4 prova
`inspecionar_prioridade_media` usando apenas `sensor_positivo` e `umidade_alta`,
ignorando que o resíduo da pulverização pode explicar o sinal. O traço da base
sem prioridade é `sensor_positivo`, `umidade_alta` → **R4** → inspeção média.

A correção dá precedência à R6: quando há `pulverizacao_recente` e
`sensor_positivo`, a decisão passa a `revisar_alerta`; o traço é
`pulverizacao_recente`, `sensor_positivo` → **R6** → revisão. A regra R4 continua
válida para o caso sem pulverização recente, portanto a exceção não contradiz a
base; `decidir_manejo` explicita essa prioridade.

#### 4.3 Cálculos de Bayes

**(a)** Pelo teorema de Bayes:

```text
P(infestado | positivo)
 = (0,0236 × 0,99) / [(0,0236 × 0,99) + (1 − 0,0236) × 0,03]
 = 0,023364 / (0,023364 + 0,029292)
 = 0,44371 ≈ 44,37%
```

**(b)** A cada 100 alertas positivos, cerca de **55,63** são falsos
(`100 × (1 − 0,44371)`).

**(c)** Em 1.200 testes por semana, alertas falsos esperados:
`1200 × (1 − 0,0236) × 0,03 = 35,1504`. A 12 minutos por inspeção, são
`35,1504 × 12 / 60 = 7,03008 horas` por semana.

**(d)** Elevando a sensibilidade para `0,999` e mantendo a taxa de falso positivo:

```text
VPP = (0,0236 × 0,999) / [(0,0236 × 0,999) + (1 − 0,0236) × 0,03]
    = 0,445945 ≈ 44,59%
```

O ganho é só cerca de **0,22 ponto percentual** frente a 44,37%. Para melhorar
de fato a proporção de alertas corretos, a cooperativa deve reduzir a taxa de
falso positivo: com prevalência baixa, os falsos positivos de uma população
grande de talhões não infestados dominam o denominador.

#### 4.4 Regra explícita

A aplicação de defensivo deve exigir confirmação e protocolo aprovados por um
agrônomo responsável. Essa decisão deve ser uma regra explícita e auditável:
um modelo aprendido não deve autorizar sozinho uma ação química com impacto
ambiental, econômico e de responsabilidade profissional.

### Parte 5 — Auditoria do laudo do fornecedor

| Afirmação | Veredito | Fundamentação e evidência medida |
|---|---|---|
| 1. A* com Manhattan × 4 é sempre ótimo. | **Incorreta** | h3 não é admissível: no par `(0,0)` → `(11,11)`, estima 88 para um custo restante ótimo de 34. No pomar da dupla, o A* h3 devolveu custo 40; a UCS encontrou 34. Ser A* não garante otimalidade para qualquer heurística. |
| 2. BFS → A* reduziu custo em 38%, provando que a heurística melhora a solução. | **Parcialmente correta** | Neste pomar, BFS custa 49 e A* h2 custa 34, queda de `(49−34)/49 = 30,61%`, não 38%. A* h2 expandiu 94 nós, contra 122 da BFS. A rota melhorou em custo neste exemplo, mas isso não prova que qualquer heurística melhora a qualidade; h3 expandiu só 31 nós e devolveu custo 40. |
| 3. Sensibilidade de 99% significa que 99% dos alertas estão infestados. | **Incorreta** | Confunde sensibilidade com valor preditivo positivo. Com os parâmetros da dupla, o VPP é 44,37%; aproximadamente 55,63 de cada 100 alertas são falsos. |
| 4. Dois positivos fazem a confiança passar de 99%. | **Incorreta** | Mesmo assumindo independência condicional dos dois testes, o VPP calculado é 96,34%, abaixo de 99%. O enunciado do fornecedor também não demonstra essa independência; testes repetidos podem compartilhar as mesmas condições de erro. |
| 5. DFS usa menos memória e basta porque o pomar é estático e totalmente observável. | **Parcialmente correta** | DFS pode usar menos memória de fronteira que BFS em certas árvores, mas neste pomar a fronteira máxima da DFS foi 38 e a da BFS 10; DFS devolveu custo 135 contra 34 da UCS. Além disso, estático/observável não implica solução ótima, os custos de entrada não são uniformes e o estado real das pragas não é revelado perfeitamente pelo sensor. |

**Recomendação à diretoria:** recusar o laudo como está. A proposta usa uma
heurística que perdeu 17,65% de custo neste pomar e interpreta sensibilidade
como precisão dos alertas. Reavaliar a contratação se o fornecedor demonstrar,
com a prevalência local e testes independentes, um VPP e uma taxa de falsos
positivos compatíveis com a capacidade semanal dos agrônomos, e se oferecer um
planejador com limite de custo verificável.
