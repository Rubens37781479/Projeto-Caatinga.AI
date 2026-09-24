"""Experimentos complementares da Parte 2, executados isoladamente."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def _worker(matricula: int, n: int, nome: str) -> None:
    from src.buscas import bfs, dfs, ucs
    from src.gerador_pomar import gerar_pomar

    funcoes = {"BFS": bfs, "DFS": dfs, "UCS": ucs}
    inicio = perf_counter()
    grade = gerar_pomar(matricula, n)
    resultado = funcoes[nome](grade, objetivo=(n - 1, n - 1))
    print(json.dumps({
        "n": n,
        "estrategia": nome,
        "segundos": perf_counter() - inicio,
        "nos_expandidos": resultado.nos_expandidos,
        "fronteira_max": resultado.fronteira_max,
        "custo": resultado.custo,
        "passos": resultado.passos,
    }))


def medir_limites(matricula: int, timeout_s: int = 60) -> list[dict]:
    """Aumenta n e encerra o subprocesso quando excede o limite de tempo."""
    observacoes = []
    for n in (12, 40, 100, 200, 400, 800, 1200, 1600, 3200, 6400):
        for estrategia in ("BFS", "DFS", "UCS"):
            comando = [sys.executable, str(Path(__file__).resolve()), "--worker", str(matricula), str(n), estrategia]
            inicio = perf_counter()
            try:
                processo = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True, timeout=timeout_s)
            except subprocess.TimeoutExpired:
                observacoes.append({"n": n, "estrategia": estrategia, "situacao": f"tempo > {timeout_s}s", "segundos": timeout_s})
                return observacoes
            if processo.returncode:
                saida = processo.stdout + processo.stderr
                if "MemoryError" in saida:
                    situacao = "estouro de memória"
                elif "RecursionError" in saida:
                    situacao = "estouro de pilha"
                else:
                    situacao = f"falha do processo (código {processo.returncode})"
                observacoes.append({"n": n, "estrategia": estrategia, "situacao": situacao, "segundos": perf_counter() - inicio})
                return observacoes
            registro = json.loads(processo.stdout.strip().splitlines()[-1])
            registro["situacao"] = "concluiu"
            observacoes.append(registro)
    return observacoes


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--worker":
        _worker(int(argv[1]), int(argv[2]), argv[3])
        return
    if argv and argv[0] == "--single":
        n, estrategia, matricula = int(argv[1]), argv[2], int(argv[3])
        comando = [sys.executable, str(Path(__file__).resolve()), "--worker", str(matricula), str(n), estrategia]
        try:
            processo = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True, timeout=60)
            print(f"returncode={processo.returncode}")
            print(processo.stdout)
            print(processo.stderr)
        except subprocess.TimeoutExpired:
            print(f"{estrategia} n={n}: tempo >60s")
        return
    if len(argv) != 1:
        raise SystemExit("Uso: python src/experimentos.py <matricula>")
    matricula = int(argv[0].replace(".", ""))
    observacoes = medir_limites(matricula)
    destino = RAIZ / "resultados" / "limites.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    colunas = sorted({chave for linha in observacoes for chave in linha})
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(observacoes)
    for linha in observacoes:
        print(linha)
    print(f"Experimento salvo em {destino}")


if __name__ == "__main__":
    main()
