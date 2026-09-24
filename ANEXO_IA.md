# Anexo obrigatório — Uso de IA

## A.1 Ferramentas usadas

- Python 3.12 foi usado para executar `src/main.py`, gerar os arquivos de
  resultados e medir as buscas em grades crescentes. O experimento de
  escalabilidade encerrou processos que ultrapassaram 60 segundos.
- Matplotlib foi usado pelo programa para gerar `resultados/grafico.png`.

## A.2 Prompts e respostas recebidas

### Prompt 1

> Precisol da sua ajuda para fazer isso aqui porem nao faça tudo faça em partes pois preciso dar 8 commits

**Resposta recebida:**

> Vou verificar o PDF para separar o que ele pede do que você pediu: fazer a atividade em etapas e chegar a oito commits. Em seguida, vejo o estado atual do projeto e preparo só a primeira parte.

### Prompt 2

> Pronto pode ir fazendo o resto

**Resposta recebida:**

> Vou continuar pelas partes restantes, separando o trabalho em seis commits para completar os oito. O código pode ficar pronto para qualquer matrícula; para preencher identificação e resultados da dupla sem inventar dados, preciso dos nomes e matrículas dos dois integrantes e de saber qual matrícula é da pessoa mais velha. Enquanto isso, vou implementar as buscas e preparar a estrutura executável.

## A.3 Erro encontrado e evidência

Na primeira versão do módulo de busca local, a inicialização gulosa podia montar
um conjunto de 15 talhões que ultrapassava a bateria de seis horas. Ao chegar a
esse conjunto, removia apenas o último talhão e não procurava uma alternativa
viável; a execução terminava com `ValueError` em `_inicializar`. O erro apareceu
ao rodar `python src/main.py 24114031`, antes da geração dos resultados da busca
local.

A inicialização foi corrigida para aceitar uma adição somente quando o conjunto
parcial respeita o limite de duração. Depois da correção, o mesmo comando
concluiu as 30 execuções de cada algoritmo e gravou `resultados/busca_local.csv`
e `resultados/resumo.json`. O CSV mostra 30 rodadas de têmpera simulada com
pioras aceitas (733 no total) e zero para subida de encosta. Esses arquivos são
a evidência usada no relatório.

## A.4 O que aprendi executando

Depois de rodar o programa, vi que a têmpera simulada aceitou pioras em todas as
30 rodadas (733 ao todo), enquanto a subida de encosta não aceitou nenhuma; a
média de utilidade da têmpera foi 14,1039 e a da subida foi 14,0473. A resposta
teórica explica por que aceitar pioras pode ajudar, mas só a execução mostrou
esse comportamento nos dados e sementes deste pomar.
