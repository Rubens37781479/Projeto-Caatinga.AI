"""Busca de rotas no pomar, com contadores reproduzíveis."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from time import perf_counter
from typing import Callable

from src.gerador_pomar import BLOQUEADO, CUSTO

Estado = tuple[int, int]
Grade = list[list[str]]
Heuristica = Callable[[Estado, Estado], float]

# A mesma ordem é usada por BFS, DFS, UCS e A* e será declarada no relatório.
ORDEM_VIZINHOS: tuple[tuple[int, int], ...] = (
    (-1, 0),  # Norte
    (1, 0),  # Sul
    (0, -1),  # Oeste
    (0, 1),  # Leste
)


@dataclass(frozen=True)
class ResultadoBusca:
    estrategia: str
    caminho: tuple[Estado, ...]
    custo: int
    passos: int
    nos_expandidos: int
    fronteira_max: int
    tempo_ms: float


def manhattan(estado: Estado, objetivo: Estado) -> int:
    return abs(estado[0] - objetivo[0]) + abs(estado[1] - objetivo[1])


def _validar(grade: Grade, inicio: Estado, objetivo: Estado) -> None:
    if not grade or not grade[0] or any(len(linha) != len(grade[0]) for linha in grade):
        raise ValueError("A grade precisa ser retangular e não vazia.")
    linhas, colunas = len(grade), len(grade[0])
    for nome, (i, j) in (("início", inicio), ("objetivo", objetivo)):
        if not (0 <= i < linhas and 0 <= j < colunas):
            raise ValueError(f"O {nome} está fora da grade: {(i, j)}.")
        if grade[i][j] == BLOQUEADO:
            raise ValueError(f"O {nome} está em um talhão bloqueado: {(i, j)}.")


def _vizinhos(grade: Grade, estado: Estado):
    linhas, colunas = len(grade), len(grade[0])
    i, j = estado
    for di, dj in ORDEM_VIZINHOS:
        ni, nj = i + di, j + dj
        if 0 <= ni < linhas and 0 <= nj < colunas and grade[ni][nj] != BLOQUEADO:
            yield (ni, nj)


def _resultado(
    nome: str,
    caminho: list[Estado],
    grade: Grade,
    expandidos: int,
    fronteira_max: int,
    inicio_tempo: float,
) -> ResultadoBusca:
    custo = sum(CUSTO[grade[i][j]] for i, j in caminho[1:])
    return ResultadoBusca(
        estrategia=nome,
        caminho=tuple(caminho),
        custo=custo,
        passos=len(caminho) - 1,
        nos_expandidos=expandidos,
        fronteira_max=fronteira_max,
        tempo_ms=(perf_counter() - inicio_tempo) * 1000,
    )


def _reconstruir(pais: dict[Estado, Estado | None], estado: Estado) -> list[Estado]:
    caminho = []
    while estado is not None:
        caminho.append(estado)
        estado = pais[estado]  # type: ignore[assignment]
    caminho.reverse()
    return caminho


def bfs(grade: Grade, inicio: Estado = (0, 0), objetivo: Estado | None = None) -> ResultadoBusca:
    """Retorna a rota com menos passos, sem garantir custo mínimo ponderado."""
    _validar(grade, inicio, objetivo or (len(grade) - 1, len(grade[0]) - 1))
    objetivo = objetivo or (len(grade) - 1, len(grade[0]) - 1)
    inicio_tempo = perf_counter()
    fronteira = [inicio]
    pais: dict[Estado, Estado | None] = {inicio: None}
    max_fronteira = 1
    expandidos = 0
    if inicio == objetivo:
        return _resultado("BFS", [inicio], grade, 0, 1, inicio_tempo)
    while fronteira:
        atual = fronteira.pop(0)
        expandidos += 1
        for proximo in _vizinhos(grade, atual):
            if proximo in pais:
                continue
            pais[proximo] = atual
            if proximo == objetivo:  # teste na geração do sucessor
                max_fronteira = max(max_fronteira, len(fronteira))
                return _resultado("BFS", _reconstruir(pais, proximo), grade, expandidos, max_fronteira, inicio_tempo)
            fronteira.append(proximo)
        max_fronteira = max(max_fronteira, len(fronteira))
    raise ValueError("Não existe caminho até o objetivo.")


def dfs(grade: Grade, inicio: Estado = (0, 0), objetivo: Estado | None = None) -> ResultadoBusca:
    """Busca em profundidade iterativa, com estados descobertos para evitar ciclos."""
    objetivo = objetivo or (len(grade) - 1, len(grade[0]) - 1)
    _validar(grade, inicio, objetivo)
    inicio_tempo = perf_counter()
    fronteira = [inicio]
    pais: dict[Estado, Estado | None] = {inicio: None}
    max_fronteira = 1
    expandidos = 0
    if inicio == objetivo:
        return _resultado("DFS", [inicio], grade, 0, 1, inicio_tempo)
    while fronteira:
        atual = fronteira.pop()
        expandidos += 1
        # Push em ordem inversa para que Norte seja o primeiro vizinho removido.
        for proximo in reversed(list(_vizinhos(grade, atual))):
            if proximo in pais:
                continue
            pais[proximo] = atual
            if proximo == objetivo:
                max_fronteira = max(max_fronteira, len(fronteira))
                return _resultado("DFS", _reconstruir(pais, proximo), grade, expandidos, max_fronteira, inicio_tempo)
            fronteira.append(proximo)
        max_fronteira = max(max_fronteira, len(fronteira))
    raise ValueError("Não existe caminho até o objetivo.")


def busca_prioridade(
    grade: Grade,
    inicio: Estado = (0, 0),
    objetivo: Estado | None = None,
    heuristica: Heuristica | None = None,
    nome: str = "UCS",
) -> ResultadoBusca:
    """UCS quando h=0; A* para outras heurísticas. Reabre estados com g menor."""
    objetivo = objetivo or (len(grade) - 1, len(grade[0]) - 1)
    _validar(grade, inicio, objetivo)
    h = heuristica or (lambda _atual, _objetivo: 0)
    inicio_tempo = perf_counter()
    ordem = count()
    fronteira: list[tuple[float, int, int, Estado]] = []
    heappush(fronteira, (h(inicio, objetivo), next(ordem), 0, inicio))
    pais: dict[Estado, Estado | None] = {inicio: None}
    melhor_g = {inicio: 0}
    max_fronteira = 1
    expandidos = 0
    while fronteira:
        _, _, custo_atual, atual = heappop(fronteira)
        if custo_atual != melhor_g.get(atual):  # entrada antiga após uma reabertura
            continue
        if atual == objetivo:
            return _resultado(nome, _reconstruir(pais, atual), grade, expandidos, max_fronteira, inicio_tempo)
        expandidos += 1
        for proximo in _vizinhos(grade, atual):
            novo_g = custo_atual + CUSTO[grade[proximo[0]][proximo[1]]]
            if novo_g >= melhor_g.get(proximo, float("inf")):
                continue
            melhor_g[proximo] = novo_g
            pais[proximo] = atual
            heappush(fronteira, (novo_g + h(proximo, objetivo), next(ordem), novo_g, proximo))
        max_fronteira = max(max_fronteira, len(fronteira))
    raise ValueError("Não existe caminho até o objetivo.")


def ucs(grade: Grade, inicio: Estado = (0, 0), objetivo: Estado | None = None) -> ResultadoBusca:
    return busca_prioridade(grade, inicio, objetivo, nome="UCS")


def astar(
    grade: Grade,
    heuristica: Heuristica,
    inicio: Estado = (0, 0),
    objetivo: Estado | None = None,
    nome: str = "A*",
) -> ResultadoBusca:
    return busca_prioridade(grade, inicio, objetivo, heuristica, nome)
