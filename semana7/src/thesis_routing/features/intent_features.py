"""Intención y entidades por reglas léxicas.

Las reglas son interpretables y fallan ante paráfrasis. No sustituyen
el etiquetado del banco.
"""

from __future__ import annotations

import re

import pandas as pd

from thesis_routing.features.text_features import fold_text

# Orden de desempate si una consulta cae en más de una familia.
INTENT_PRIORITY: tuple[str, ...] = (
    "prerrequisitos",
    "matricula",
    "pagos",
    "tramites",
    "horarios",
    "calendario",
)

INTENT_PATTERNS: dict[str, re.Pattern[str]] = {
    "prerrequisitos": re.compile(r"\bprerrequisito"),
    "matricula": re.compile(r"\bmatricul"),
    "pagos": re.compile(r"\b(pago|pagar|cuota|tesoreria|cuesta|precio|costo)\b"),
    "tramites": re.compile(r"\b(tramite|diploma|bachiller|titulo|carne|constancia|sunedu)\b"),
    "horarios": re.compile(r"\b(horario|aula|clase|zoom|wifi)\b"),
    "calendario": re.compile(r"\b(calendario|plazo|fecha|semana)\b"),
}

ACADEMIC_PATTERN = re.compile(
    r"\b(ciclo|curso|credito|prerrequisito|malla|asignatura|evaluacion|examen|nota)\b"
)
ADMIN_PATTERN = re.compile(
    r"\b(matricula|pago|tramite|carne|constancia|diploma|reserva|tesoreria|sigu)\b"
)
MULTI_SOURCE_PATTERN = re.compile(r"\b(ademas|y tambien|tanto .+ como)\b")
PERSONAL_CONTEXT_PATTERN = re.compile(
    r"\b(puedo|cumplo|estoy|desaprobe|perdi|mi avance|me pueden)\b"
)
CALCULATION_PATTERN = re.compile(
    r"\b(cuanto|cuantos|cuantas|suma|suman|porcentaje|cuesta|costo)\b"
)
RULE_PATTERN = re.compile(
    r"\b(puedo|cumplo|requisito|debo|permitid|inhabilit|desaprob)\b"
)
TEMPORAL_PATTERN = re.compile(
    r"\b(cuando|todavia|aun|plazo|fecha|vigencia|antes de|despues de)\b"
)

INTENT_FEATURE_COLUMNS: tuple[str, ...] = (
    "intent_category",
    "n_intent_families",
    "requires_multiple_sources_rule",
    "requires_personal_context",
    "requires_calculation",
    "requires_rule_validation",
    "requires_temporal_reasoning",
    "contains_academic_entity",
    "contains_administrative_entity",
)


def _intent_category(folded: str) -> tuple[str, int]:
    hits = [name for name, pattern in INTENT_PATTERNS.items() if pattern.search(folded)]
    if not hits:
        return "otro", 0
    chosen = min(hits, key=INTENT_PRIORITY.index)
    return chosen, len(hits)


def extract_intent_features(query: str) -> dict[str, str | int]:
    """Extrae intención y marcas de complejidad aparente.

    Parameters
    ----------
    query :
        Texto de la consulta.

    Returns
    -------
    dict[str, str | int]
        ``intent_category`` es una etiqueta de regla. El resto son marcas 0/1,
        salvo ``n_intent_families``.
    """
    folded = fold_text(query)
    intent, n_families = _intent_category(folded)
    multi = int(bool(MULTI_SOURCE_PATTERN.search(folded)) or n_families >= 2)
    return {
        "intent_category": intent,
        "n_intent_families": n_families,
        "requires_multiple_sources_rule": multi,
        "requires_personal_context": int(bool(PERSONAL_CONTEXT_PATTERN.search(folded))),
        "requires_calculation": int(bool(CALCULATION_PATTERN.search(folded))),
        "requires_rule_validation": int(bool(RULE_PATTERN.search(folded))),
        "requires_temporal_reasoning": int(bool(TEMPORAL_PATTERN.search(folded))),
        "contains_academic_entity": int(bool(ACADEMIC_PATTERN.search(folded))),
        "contains_administrative_entity": int(bool(ADMIN_PATTERN.search(folded))),
    }


def build_intent_feature_table(queries: pd.Series) -> pd.DataFrame:
    """Construye la tabla de características de intención.

    Parameters
    ----------
    queries :
        Serie con el texto de cada consulta.

    Returns
    -------
    pd.DataFrame
        Una fila por consulta.
    """
    rows = [extract_intent_features(query) for query in queries.astype(str)]
    return pd.DataFrame(rows, index=queries.index, columns=list(INTENT_FEATURE_COLUMNS))
