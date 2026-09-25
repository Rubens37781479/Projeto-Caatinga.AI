# Anexo — Uso de inteligência artificial

## Ferramentas usadas

- Python 3.12 foi usado para executar o programa e gerar os resultados.
- Matplotlib foi usado para criar o gráfico salvo em `resultados/grafico.png`.
- No experimento de tamanhos maiores, cada execução foi encerrada se passasse de 60 segundos.


## Problema encontrado e correção

Na primeira versão da busca local, o programa podia escolher 15 talhões cujo tempo total ultrapassava as seis horas de bateria. Ele tentava corrigir isso removendo somente o último talhão e, em alguns casos, parava com um erro.

A correção verifica cada talhão antes de adicioná-lo. Assim, o grupo escolhido sempre respeita o limite de tempo. Depois da correção, `python src/main.py 24114031` terminou e gerou os arquivos de resultados. Nas 30 execuções registradas, a têmpera simulada aceitou 733 mudanças que diminuíram o valor do resultado; a subida de encosta não aceitou nenhuma.

## O que aprendi

Nos resultados desta execução, a média de utilidade da têmpera simulada foi 14,1039. A média da subida de encosta foi 14,0473. A têmpera pode aceitar uma escolha pior durante a busca e, com isso, tentar encontrar uma opção melhor mais adiante. Os números descrevem este pomar e estas sementes; eles não garantem o mesmo resultado em outras execuções.
