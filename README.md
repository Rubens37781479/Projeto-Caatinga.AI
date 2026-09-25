# Caatinga.AI — Sprint 1

## Prompts 

-Codex: auxílio na compreensão do enunciado, formulação das buscas BFS/DFS/UCS/A*, auxilio na correção de erros dentro do codigo. 

## Identificação

- Disciplina: Inteligência Artificial — UniRios — 2026.2
- Integrante 1: Rubens Alves (Rubens Alves de Barros) — matrícula: 241.14.031
- Integrante 2: Paloma Graziela (Paloma Graziela Bertoleza Martins) - 241.14.078
- Matrícula-semente (Rubens Alves de Barros): 241.14.031 (`24114031` no comando)

## O que este projeto faz

O Caatinga.AI navega em um pomar de manga gerado a partir da matrícula-semente.
O programa compara BFS, DFS, UCS e A* com três heurísticas, registrando custo,
passos, nós expandidos, fronteira máxima e tempo. Também executa busca local,
regras explicáveis e cálculos bayesianos para interpretar alertas do sensor.

## Como rodar

Requer Python 3.11 ou superior. No Windows PowerShell, a partir da raiz do
repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py 24114031
```

O último comando gera `resultados.csv`, `grafico.png`, `pomar.txt`,
`busca_local.csv` e `resumo.json` dentro de `resultados/`. Para reproduzir o
experimento de escalabilidade da seção 2.4 do relatório, rode também:

```powershell
python src/experimentos.py 24114031
```

Esse experimento interrompe cada processo que ultrapassa 60 segundos e grava
`resultados/limites.csv`.

## Resultados da semente 24114031

| Estratégia | Heurística | Custo (unid. de custo) | Passos (movimentos) | Nós expandidos | Fronteira máx. (nós) |
|---|---|---:|---:|---:|---:|
| BFS | — | 49 | 22 | 122 | 10 |
| DFS | — | 135 | 54 | 63 | 38 |
| UCS | — | 34 | 22 | 119 | 16 |
| A* | h1 = 0 | 34 | 22 | 119 | 16 |
| A* | h2 = Manhattan | 34 | 22 | 94 | 32 |
| A* | h3 = 4 × Manhattan | 40 | 22 | 31 | 27 |

Resultados detalhados, incluindo tempos medidos e busca local, estão em
[`resultados/`](resultados/). A análise completa das Partes 1 a 5 está em
[`RELATORIO.md`](RELATORIO.md).

## Busca e escolhas de implementação

- Ordem de expansão dos vizinhos, igual em todas as buscas: **Norte, Sul, Oeste,
  Leste**.
- UCS e A* reabrem estados quando encontram um caminho com custo `g` menor; a
  fila descarta entradas antigas.
- O A* com h3 não garante otimalidade. Nesta semente, custou 40 contra 34 da UCS.
- O tempo de movimento usado na busca local (3 minutos por passo) é uma hipótese
  do modelo; a atividade fornece apenas os 12 minutos por inspeção.

## Mapa do repositório

- [`src/gerador_pomar.py`](src/gerador_pomar.py) — gerador fornecido no enunciado,
  mantido intacto.
- [`src/buscas.py`](src/buscas.py) — BFS, DFS, UCS, A*, heurísticas e contadores.
- [`src/busca_local.py`](src/busca_local.py) — subida de encosta, têmpera simulada
  e resumo de 30 execuções.
- [`src/especialista.py`](src/especialista.py) — regras de manejo, encadeamento
  para trás e decisão de exceção.
- [`src/bayes.py`](src/bayes.py) — VPP, alertas falsos e teste duplo.
- [`src/experimentos.py`](src/experimentos.py) — medição de escalabilidade com
  timeout por processo.
- [`src/main.py`](src/main.py) — comando principal que gera os resultados.
- [`RELATORIO.md`](RELATORIO.md) — relatório completo das Partes 1 a 5.
- [`ANEXO_IA.md`](ANEXO_IA.md) — prompts, respostas e registro de uso de IA.
- [`requirements.txt`](requirements.txt) — dependência Matplotlib para o gráfico.
- [`resultados/resultados.csv`](resultados/resultados.csv) — métricas das buscas.
- [`resultados/grafico.png`](resultados/grafico.png) — gráfico de nós expandidos.
- [`resultados/pomar.txt`](resultados/pomar.txt) — grade e matrícula-semente.
- [`resultados/busca_local.csv`](resultados/busca_local.csv) — 60 execuções locais.
- [`resultados/limites.csv`](resultados/limites.csv) — experimento de escalabilidade.
- [`resultados/resumo.json`](resultados/resumo.json) — parâmetros, cálculos e rotas.

## Limitações conhecidas

- Falta confirmar o nome completo e a matrícula do segundo integrante antes da
  entrega.
- A busca local usa pesos de risco sintéticos, pois não há rótulos de infestação
  no gerador; os valores comparam algoritmos, não medem pragas reais.
- A duração de deslocamento não é fornecida pelo enunciado; o modelo local assume
  3 minutos por movimento e explicita essa hipótese no relatório.
- A execução de escalabilidade encontrou o limite de 60 segundos para a BFS em
  `n=6400`; DFS e UCS nesse tamanho não foram executadas depois da primeira falha.
- A detecção real de pragas precisa de observações e confirmações de campo; as
  probabilidades fornecidas não substituem a validação agronômica.
