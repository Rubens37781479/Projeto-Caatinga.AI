"""Ponto de entrada: python src/main.py <matricula>."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

# Ao executar `python src/main.py`, o diretório inicial do Python é `src/`.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.bayes import carga_falsos_alertas, valor_preditivo_dois_positivos, valor_preditivo_positivo
from src.busca_local import resumo_execucoes
from src.buscas import astar, bfs, dfs, manhattan, ucs
from src.especialista import decidir_manejo, encadeamento_para_tras
from src.gerador_pomar import gerar_pomar, parametros_sensor

PASTA_RESULTADOS = RAIZ / "resultados"


def _formatar_rota(caminho):
    return " -> ".join(f"({i},{j})" for i, j in caminho)


def executar(matricula: int) -> dict:
    grade = gerar_pomar(matricula)
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    (PASTA_RESULTADOS / "pomar.txt").write_text(
        f"matricula-semente: {matricula}\n" + "\n".join(" ".join(linha) for linha in grade) + "\n",
        encoding="utf-8",
    )

    # Sem estimativa, o A* se comporta como a busca de custo uniforme.
    heuristica_zero = lambda _atual, _objetivo: 0
    estrategias = [
        bfs(grade),
        dfs(grade),
        ucs(grade),
        astar(grade, heuristica_zero, nome="A*"),
        astar(grade, manhattan, nome="A*"),
        astar(grade, lambda a, b: 4 * manhattan(a, b), nome="A*"),
    ]
    linhas = []
    for resultado, heuristica in zip(estrategias, ("n/a", "n/a", "n/a", "h1=0", "h2=Manhattan", "h3=4xManhattan")):
        linhas.append({
            "estrategia": resultado.estrategia,
            "heuristica": heuristica,
            "custo": resultado.custo,
            "passos": resultado.passos,
            "nos_expandidos": resultado.nos_expandidos,
            "fronteira_max": resultado.fronteira_max,
            "tempo_ms": round(resultado.tempo_ms, 3),
        })
    with (PASTA_RESULTADOS / "resultados.csv").open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=linhas[0].keys())
        writer.writeheader()
        writer.writerows(linhas)

    # Import tardio deixa os algoritmos de busca independentes do Matplotlib.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([f"{r['estrategia']}\n{r['heuristica']}" for r in linhas], [r["nos_expandidos"] for r in linhas])
    ax.set_ylabel("Nós expandidos (nós)")
    ax.set_xlabel("Estratégia e heurística")
    ax.set_title("Nós expandidos por estratégia de busca")
    ax.tick_params(axis="x", labelrotation=20)
    fig.tight_layout()
    fig.savefig(PASTA_RESULTADOS / "grafico.png", dpi=160)
    plt.close(fig)

    resumo_local = resumo_execucoes(grade, repeticoes=30, k=15, semente_base=matricula % 1_000_000)
    with (PASTA_RESULTADOS / "busca_local.csv").open("w", newline="", encoding="utf-8") as arquivo:
        campos = ("algoritmo", "repeticao", "semente", "valor", "iteracoes", "pioras_aceitas", "talhoes")
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        writer.writeheader()
        for algoritmo, resumo in resumo_local.items():
            for indice, resultado in enumerate(resumo["resultados"], start=1):
                writer.writerow({
                    "algoritmo": algoritmo,
                    "repeticao": indice,
                    "semente": resultado.semente,
                    "valor": round(resultado.valor, 6),
                    "iteracoes": resultado.iteracoes,
                    "pioras_aceitas": resultado.pioras_aceitas,
                    "talhoes": _formatar_rota(sorted(resultado.estado)),
                })

    sensor = parametros_sensor(matricula)
    bayes = carga_falsos_alertas(
        sensor["prevalencia"], sensor["sensibilidade"],
        sensor["taxa_falso_positivo"], sensor["talhoes_por_semana"],
    )
    vpp_sensibilidade_999 = valor_preditivo_positivo(
        sensor["prevalencia"], 0.999, sensor["taxa_falso_positivo"],
    )
    especialista = encadeamento_para_tras(
        "inspecionar_prioridade_alta",
        {"sensor_positivo", "umidade_alta", "pulverizacao_antiga"},
    )
    dados = {
        "matricula_semente": matricula,
        "ordem_vizinhos": ["Norte", "Sul", "Oeste", "Leste"],
        "astar_reabre_nos": True,
        "espaco_estados": len(grade) * len(grade[0]),
        "talhoes_livres": sum(c != "#" for linha in grade for c in linha),
        "sensor": sensor,
        "bayes": {
            **bayes,
            "vpp_sensibilidade_999": vpp_sensibilidade_999,
            "vpp_dois_positivos_independentes": valor_preditivo_dois_positivos(
                sensor["prevalencia"], sensor["sensibilidade"], sensor["taxa_falso_positivo"],
            ),
        },
        "busca_local": {
            nome: {"media": resumo["media"], "desvio_populacional": resumo["desvio_populacional"], "melhor": resumo["melhor"]}
            for nome, resumo in resumo_local.items()
        },
        "cadeia_especialista_exemplo": especialista,
        "caso_regra_excecao": {
            "regra_base_sem_prioridade": encadeamento_para_tras(
                "inspecionar_prioridade_media", {"sensor_positivo", "umidade_alta", "pulverizacao_recente"},
            ),
            "decisao_com_excecao": decidir_manejo(
                {"sensor_positivo", "umidade_alta", "pulverizacao_recente"},
            ),
        },
        "rotas": {f"{r.estrategia}_{i}": {"custo": r.custo, "passos": r.passos, "caminho": r.caminho}
                  for i, r in enumerate(estrategias)},
        "resultados": linhas,
    }
    (PASTA_RESULTADOS / "resumo.json").write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Resultados gerados em {PASTA_RESULTADOS}")
    print(f"Matrícula-semente: {matricula}")
    for linha in linhas:
        print("{estrategia:4} {heuristica:15} custo={custo:3} passos={passos:3} expandidos={nos_expandidos:4} fronteira={fronteira_max:4}".format(**linha))
    print("Ordem de vizinhos: Norte, Sul, Oeste, Leste")
    print(f"Cadeia especialista: {' -> '.join(especialista['regras'])} -> {especialista['meta']}")
    return dados


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit("Uso: python src/main.py <matricula>")
    try:
        matricula = int(argv[0].replace(".", ""))
    except ValueError as exc:
        raise SystemExit("A matrícula deve conter apenas algarismos e pontos opcionais.") from exc
    executar(matricula)


if __name__ == "__main__":
    main()
