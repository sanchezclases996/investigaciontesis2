"""Características lingüísticas básicas de una consulta.

Son señales, no reglas de dificultad. Una pregunta larga no es, por eso,
más difícil que una corta.
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

_WORD = re.compile(r"[a-z0-9]+")

NEGATION_WORDS: frozenset[str] = frozenset({"no", "nunca", "tampoco", "sin", "ni"})

CONDITION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsi\b"),
    re.compile(r"\bsiempre que\b"),
    re.compile(r"\ben caso de\b"),
    re.compile(r"\baunque\b"),
    re.compile(r"\bmientras\b"),
)

COMPARISON_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdiferencia entre\b"),
    re.compile(r"\bcompara"),
    re.compile(r"\bcual es mejor\b"),
    re.compile(r"\ben que se diferencia\b"),
)

PERSONAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(estoy|soy|tengo|puedo|perdi|desaprobe|reprobe)\b"),
    re.compile(r"\b(mi|mis|me)\b"),
)

TEXT_FEATURE_COLUMNS: tuple[str, ...] = (
    "query_length_chars",
    "query_length_words",
    "question_mark_count",
    "has_multiple_questions",
    "contains_negation",
    "contains_condition",
    "contains_comparison",
    "contains_personal_case",
)


def fold_text(text: str) -> str:
    """Pasa a minúsculas y quita tildes para comparar palabras.

    Parameters
    ----------
    text :
        Consulta original.

    Returns
    -------
    str
        Texto plegado. La longitud en caracteres se mide sobre el original.
    """
    decomposed = unicodedata.normalize("NFD", str(text).lower())
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return unicodedata.normalize("NFC", without_marks)


def tokenize(text: str) -> list[str]:
    """Parte el texto plegado en palabras.

    Parameters
    ----------
    text :
        Consulta u otro texto.

    Returns
    -------
    list[str]
        Tokens alfanuméricos, sin tildes.
    """
    return _WORD.findall(fold_text(text))


def _any_pattern(patterns: tuple[re.Pattern[str], ...], folded: str) -> int:
    return int(any(pattern.search(folded) for pattern in patterns))


def extract_text_features(query: str) -> dict[str, int]:
    """Extrae características lingüísticas básicas de una consulta.

    Parameters
    ----------
    query :
        Texto de la pregunta tal como entra al sistema.

    Returns
    -------
    dict[str, int]
        Longitud, interrogaciones y marcas binarias de negación, condición,
        comparación y caso personal.
    """
    original = str(query).strip()
    folded = fold_text(original)
    words = tokenize(original)
    question_marks = original.count("?")
    return {
        "query_length_chars": len(original),
        "query_length_words": len(words),
        "question_mark_count": question_marks,
        "has_multiple_questions": int(question_marks > 1),
        "contains_negation": int(any(word in NEGATION_WORDS for word in words)),
        "contains_condition": _any_pattern(CONDITION_PATTERNS, folded),
        "contains_comparison": _any_pattern(COMPARISON_PATTERNS, folded),
        "contains_personal_case": _any_pattern(PERSONAL_PATTERNS, folded),
    }


def build_text_feature_table(queries: pd.Series) -> pd.DataFrame:
    """Construye la tabla de características textuales.

    Parameters
    ----------
    queries :
        Serie con el texto de cada consulta. El índice se conserva.

    Returns
    -------
    pd.DataFrame
        Una fila por consulta y las columnas de ``TEXT_FEATURE_COLUMNS``.
    """
    rows = [extract_text_features(query) for query in queries.astype(str)]
    return pd.DataFrame(rows, index=queries.index, columns=list(TEXT_FEATURE_COLUMNS))
