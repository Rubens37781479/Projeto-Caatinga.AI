"""Busca local sobre conjuntos de talhões candidatos à inspeção."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from src.gerador_pomar import BLOQUEADO

EstadoLocal = frozenset[tuple[int, int]]


@dataclass(frozen=True)
class ResultadoLocal:
    algoritmo: str
    semente: int
    valor: float
    estado: EstadoLocal
    iteracoes: int
    pioras_aceitas: int = 0


def _candidatos(grade):
    return [(i, j) for i, linha in enumerate(grade) for j, terreno in enumerate(linha) if terreno != BLOQUEADO]


def _distancia(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _rota_aproximada(estado: EstadoLocal):
    """Rota gulosa de inspeção, incluindo o trajeto até o ponto de coleta."""
    restantes = set(estado)
    atual = (0, 0)
    passos = 0
    while restantes:
        proximo = min(restantes, key=lambda p: (_distancia(atual, p), p))
        passos += _distancia(atual, proximo)
        atual = proximo
        restantes.remove(proximo)
    objetivo = (11, 11)
    passos += _distancia(atual, objetivo)
    return passos


def _valor(estado: EstadoLocal, riscos: dict[tuple[int, int], float], limite_minutos: float) -> float:
    # 12 min por inspeção de campo e 3 min por passo de deslocamento.
    duracao = len(estado) * 12 + _rota_aproximada(estado) * 3
    if duracao > limite_minutos:
        return -math.inf
    return sum(riscos[p] for p in estado)


def _inicializar(candidatos, riscos, k, limite, rng):
    escolhidos = set()
    for posicao in sorted(candidatos, key=lambda p: (-(riscos[p] + rng.random() * 0.1), p)):
        proposta = escolhidos | {posicao}
        if _valor(frozenset(proposta), riscos, limite) != -math.inf:
            escolhidos = proposta
        if len(escolhidos) == k:
            return frozenset(escolhidos)
    raise ValueError("Não foi possível inicializar K talhões dentro do limite de bateria.")


def _vizinho(estado, candidatos, rng):
    escolhidos = set(estado)
    removido = rng.choice(tuple(escolhidos))
    disponiveis = [p for p in candidatos if p not in escolhidos]
    escolhido = rng.choice(disponiveis)
    escolhidos.remove(removido)
    escolhidos.add(escolhido)
    return frozenset(escolhidos)


def subida_encosta(grade, k=15, semente=0, limite_minutos=360, max_iteracoes=500):
    rng = random.Random(semente)
    candidatos = _candidatos(grade)
    if k > len(candidatos):
        raise ValueError("K não pode exceder o número de talhões livres.")
    riscos = {p: rng.random() for p in candidatos}
    estado = _inicializar(candidatos, riscos, k, limite_minutos, rng)
    valor = _valor(estado, riscos, limite_minutos)
    iteracoes = 0
    for iteracoes in range(1, max_iteracoes + 1):
        alternativas = [_vizinho(estado, candidatos, rng) for _ in range(40)]
        melhor = max(alternativas, key=lambda e: _valor(e, riscos, limite_minutos))
        melhor_valor = _valor(melhor, riscos, limite_minutos)
        if melhor_valor <= valor:
            break
        estado, valor = melhor, melhor_valor
    return ResultadoLocal("subida_encosta", semente, valor, estado, iteracoes)


def tempera_simulada(
    grade,
    k=15,
    semente=0,
    limite_minutos=360,
    max_iteracoes=5000,
    temperatura_inicial=0.2,
    resfriamento=0.995,
):
    rng = random.Random(semente)
    candidatos = _candidatos(grade)
    if k > len(candidatos):
        raise ValueError("K não pode exceder o número de talhões livres.")
    riscos = {p: rng.random() for p in candidatos}
    estado = _inicializar(candidatos, riscos, k, limite_minutos, rng)
    valor = _valor(estado, riscos, limite_minutos)
    melhor, melhor_valor = estado, valor
    temperatura = temperatura_inicial
    iteracoes = 0
    pioras_aceitas = 0
    for iteracoes in range(1, max_iteracoes + 1):
        candidato = _vizinho(estado, candidatos, rng)
        valor_candidato = _valor(candidato, riscos, limite_minutos)
        diferenca = valor_candidato - valor
        if diferenca >= 0 or (valor_candidato != -math.inf and rng.random() < math.exp(diferenca / temperatura)):
            if diferenca < 0:
                pioras_aceitas += 1
            estado, valor = candidato, valor_candidato
        if valor > melhor_valor:
            melhor, melhor_valor = estado, valor
        temperatura *= resfriamento
        if temperatura < 1e-5:
            break
    return ResultadoLocal("tempera_simulada", semente, melhor_valor, melhor, iteracoes, pioras_aceitas)


def resumo_execucoes(grade, repeticoes=30, k=15, semente_base=0):
    """Retorna resultados individuais e resumo populacional para ambos algoritmos."""
    saida = {}
    for nome, algoritmo in (("subida_encosta", subida_encosta), ("tempera_simulada", tempera_simulada)):
        resultados = [algoritmo(grade, k, semente_base + i) for i in range(repeticoes)]
        valores = [r.valor for r in resultados]
        media = sum(valores) / len(valores)
        desvio = math.sqrt(sum((v - media) ** 2 for v in valores) / len(valores))
        saida[nome] = {"resultados": resultados, "media": media, "desvio_populacional": desvio, "melhor": max(valores)}
    return saida
