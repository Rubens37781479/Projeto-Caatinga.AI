"""Cálculos de valor preditivo positivo e carga de falsos alertas."""


def valor_preditivo_positivo(prevalencia: float, sensibilidade: float, falso_positivo: float) -> float:
    for nome, valor in (("prevalencia", prevalencia), ("sensibilidade", sensibilidade), ("taxa_falso_positivo", falso_positivo)):
        if not 0 <= valor <= 1:
            raise ValueError(f"{nome} deve estar entre 0 e 1.")
    denominador = prevalencia * sensibilidade + (1 - prevalencia) * falso_positivo
    return 0.0 if denominador == 0 else prevalencia * sensibilidade / denominador


def carga_falsos_alertas(prevalencia: float, sensibilidade: float, falso_positivo: float, talhoes_por_semana: int):
    vpp = valor_preditivo_positivo(prevalencia, sensibilidade, falso_positivo)
    alertas = talhoes_por_semana * (prevalencia * sensibilidade + (1 - prevalencia) * falso_positivo)
    falsos = alertas * (1 - vpp)
    return {"vpp": vpp, "falsos_por_semana": falsos, "horas_gastas": falsos * 12 / 60}


def valor_preditivo_dois_positivos(prevalencia: float, sensibilidade: float, falso_positivo: float) -> float:
    """VPP após dois positivos, assumindo independência condicional dos testes."""
    for nome, valor in (("prevalencia", prevalencia), ("sensibilidade", sensibilidade), ("taxa_falso_positivo", falso_positivo)):
        if not 0 <= valor <= 1:
            raise ValueError(f"{nome} deve estar entre 0 e 1.")
    tp = prevalencia * sensibilidade**2
    fp = (1 - prevalencia) * falso_positivo**2
    return 0.0 if tp + fp == 0 else tp / (tp + fp)
