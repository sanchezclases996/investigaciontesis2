"""Une las características de texto, intención y recuperación léxica."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from thesis_routing.features.intent_features import build_intent_feature_table
from thesis_routing.features.retrieval_features import build_retrieval_feature_table
from thesis_routing.features.text_features import build_text_feature_table

ID_COLUMNS: tuple[str, ...] = (
    "query_id",
    "pregunta",
    "origen",
    "categoria",
    "complejidad",
    "doc_referencia",
    "requiere_herramienta",
    "requiere_multiples_fuentes",
    "candidate_strategy",
    "validacion_experta",
)


def build_feature_table(
    queries: pd.DataFrame,
    *,
    text_column: str = "pregunta",
    text_dir: Path | None = None,
    inventory: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Arma la tabla de características de un banco de consultas.

    Parameters
    ----------
    queries :
        Banco con al menos la columna de texto.
    text_column :
        Nombre de la columna con la pregunta.
    text_dir :
        Carpeta de textos extraídos. Si es ``None``, no se calcula BM25.
    inventory :
        Inventario documental, requerido si se pasa ``text_dir``.

    Returns
    -------
    pd.DataFrame
        Identificadores presentes en el banco más las características.
        Las columnas de etiqueta se conservan para contrastar. No son entrada
        del enrutador.
    """
    text = queries[text_column]
    parts = [
        build_text_feature_table(text),
        build_intent_feature_table(text),
    ]
    if text_dir is not None:
        if inventory is None:
            raise ValueError("inventory es obligatorio cuando se calcula BM25")
        parts.append(build_retrieval_feature_table(text, text_dir, inventory))

    features = pd.concat(parts, axis=1)
    kept = [column for column in ID_COLUMNS if column in queries.columns]
    return pd.concat([queries.loc[:, kept].reset_index(drop=True), features.reset_index(drop=True)], axis=1)
