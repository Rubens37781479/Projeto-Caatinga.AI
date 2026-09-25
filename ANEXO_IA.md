# Anexo — Uso de inteligência artificial

## Ferramentas usadas

- Python 3.12.10 foi usado para executar o programa e gerar os resultados.
- Matplotlib foi usado para criar o gráfico salvo em `resultados/grafico.png`.
- No experimento de tamanhos maiores, cada execução foi encerrada se passasse de 60 segundos.


## Problema encontrado e correção

Na primeira versão da busca local, o programa podia escolher 15 talhões cujo tempo total ultrapassava as seis horas de bateria. Ele tentava corrigir isso removendo somente o último talhão e, em alguns casos, parava com um erro.

A correção verifica cada talhão antes de adicioná-lo. Assim, o grupo escolhido sempre respeita o limite de tempo. Depois da correção, `python src/main.py 24114031` terminou e gerou os arquivos de resultados. Nas 30 execuções registradas, a têmpera simulada aceitou 733 mudanças que diminuíram o valor do resultado; a subida de encosta não aceitou nenhuma.

## O que aprendi

Nos resultados desta execução, a média de utilidade da têmpera simulada foi 14,1039. A média da subida de encosta foi 14,0473. A têmpera pode aceitar uma escolha pior durante a busca e, com isso, tentar encontrar uma opção melhor mais adiante. Os números descrevem este pomar e estas sementes; eles não garantem o mesmo resultado em outras execuções.


## prompts e respostas 

- Estou fazendo a Parte 2 da atividade do Caatinga.AI e implementei o UCS em Python, mas estou tendo um problema: o custo da rota que meu programa encontra não está batendo com o que eu esperava. Você pode analisar a lógica do meu UCS e me explicar o que pode estar errado? O enunciado diz que o custo é a soma dos custos dos talhões em que o agente entra, que "." custa 1 e "~" custa 4, e que o talhão inicial não entra no cálculo. Também preciso contar corretamente os nós expandidos e o tamanho máximo da fronteira. Quero que você me mostre como corrigir a lógica sem alterar o gerador_pomar.py.

-O problema provavelmente está na forma como você está controlando os estados visitados e os custos acumulados no UCS.

No UCS, você não deve considerar apenas se um estado já foi visitado. É necessário guardar o menor custo conhecido para chegar até cada estado. Isso acontece porque um mesmo talhão pode ser alcançado por caminhos diferentes, e um caminho que inicialmente parece mais caro pode depois ser substituído por outro de menor custo.

## A.1 Ferramentas usadas e partes

- **Codex (assistente de IA):** usado nesta conversa para revisar este anexo e comparar os tempos descritos no `RELATORIO.md` com os dados gravados em `resultados/resultados.csv`.
- **Python 3.12 e Matplotlib:** o README e o anexo anterior registram seu uso para executar o projeto e gerar os resultados e o gráfico. Não foram executados novamente nesta revisão do anexo.


