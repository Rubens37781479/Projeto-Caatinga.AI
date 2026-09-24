"""Regras de manejo explicáveis, avaliadas por encadeamento para trás."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Regra:
    nome: str
    premissas: tuple[str, ...]
    conclusao: str


REGRAS = (
    Regra("R1", ("sensor_positivo", "risco_alto"), "inspecionar_prioridade_alta"),
    Regra("R2", ("sensor_positivo", "umidade_alta", "pulverizacao_antiga"), "risco_alto"),
    Regra("R3", ("armadilha_positiva", "fruto_danificado"), "risco_alto"),
    Regra("R4", ("sensor_positivo", "umidade_alta"), "inspecionar_prioridade_media"),
    Regra("R5", ("sensor_negativo", "fruto_saudavel"), "monitorar_rotina"),
    Regra("R6", ("pulverizacao_recente", "sensor_positivo"), "revisar_alerta"),
    Regra("R7", ("infestacao_confirmada",), "manejo_conforme_protocolo"),
)


def encadeamento_para_tras(meta: str, fatos: set[str] | frozenset[str]):
    """Retorna (meta provada, regras usadas, fatos consultados) sem ciclos."""
    fatos = set(fatos)
    provados = set()
    regras_usadas = []
    consultados = []
    em_avaliacao = set()

    def provar(objetivo):
        if objetivo in fatos or objetivo in provados:
            consultados.append(objetivo)
            return True
        if objetivo in em_avaliacao:
            return False
        em_avaliacao.add(objetivo)
        for regra in REGRAS:
            if regra.conclusao != objetivo:
                continue
            if all(provar(premissa) for premissa in regra.premissas):
                provados.add(objetivo)
                regras_usadas.append(regra.nome)
                em_avaliacao.remove(objetivo)
                return True
        em_avaliacao.remove(objetivo)
        consultados.append(objetivo)
        return False

    sucesso = provar(meta)
    return {"meta": meta, "provada": sucesso, "regras": regras_usadas, "consultas": consultados}


def decidir_manejo(fatos: set[str] | frozenset[str]):
    """Aplica prioridade explícita para não tratar leitura pós-pulverização como alerta novo."""
    fatos = set(fatos)
    if "sensor_positivo" in fatos and "pulverizacao_recente" in fatos:
        meta = "revisar_alerta"
    elif "infestacao_confirmada" in fatos:
        meta = "manejo_conforme_protocolo"
    elif {"sensor_positivo", "umidade_alta", "pulverizacao_antiga"} <= fatos:
        meta = "inspecionar_prioridade_alta"
    elif {"sensor_positivo", "umidade_alta"} <= fatos:
        meta = "inspecionar_prioridade_media"
    elif {"sensor_negativo", "fruto_saudavel"} <= fatos:
        meta = "monitorar_rotina"
    else:
        meta = "revisar_alerta"
    return encadeamento_para_tras(meta, fatos)
