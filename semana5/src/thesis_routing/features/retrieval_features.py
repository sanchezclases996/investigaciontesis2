"""Características de una búsqueda léxica previa.

BM25 sobre el texto extraído del corpus. La puntuación no es una probabilidad
de respuesta correcta. Estas columnas solo existen después de buscar: no sirven
como entrada de un enrutador que decide antes de recuperar.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from rank_bm25 import BM25Okapi

from thesis_routing.features.text_features import tokenize

LOGGER = logging.getLogger(__name__)

TOP_K: int = 3
MIN_TOKENS_DOC: int = 40

STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "al", "de", "del", "el", "la", "los", "las", "un", "una", "unos",
        "y", "o", "u", "que", "en", "por", "para", "con", "se", "su", "sus",
        "es", "son", "lo", "le", "les", "me", "mi", "mis", "te", "tu", "como",
        "cual", "cuales", "donde", "cuando", "si", "no", "mas", "este", "esta",
        "estos", "estas", "hay", "the",
    }
)

RETRIEVAL_FEATURE_COLUMNS: tuple[str, ...] = (
    "top1_retrieval_score",
    "topk_mean_score",
    "retrieval_score_margin",
    "retrieved_document_count",
    "retrieved_source_count",
    "top1_doc_id",
)


def _content_tokens(text: str) -> list[str]:
    return [token for token in tokenize(text) if token not in STOPWORDS and len(token) > 2]


def load_corpus_documents(
    text_dir: Path,
    inventory: pd.DataFrame,
) -> pd.DataFrame:
    """Carga documentos con extracción usable.

    Parameters
    ----------
    text_dir :
        Carpeta con ``{doc_id}.txt``.
    inventory :
        Inventario documental. Se excluye ``estado_extraccion != ok``.

    Returns
    -------
    pd.DataFrame
        Columnas ``doc_id`` y ``tokens``.
    """
    usable = inventory.loc[inventory["estado_extraccion"].astype(str) == "ok", "doc_id"]
    rows: list[dict[str, object]] = []
    for doc_id in usable.astype(str):
        path = text_dir / f"{doc_id}.txt"
        if not path.exists():
            LOGGER.info("Sin texto extraído para %s", doc_id)
            continue
        tokens = _content_tokens(path.read_text(encoding="utf-8"))
        if len(tokens) < MIN_TOKENS_DOC:
            LOGGER.info("Texto corto, se omite %s (%s tokens)", doc_id, len(tokens))
            continue
        rows.append({"doc_id": doc_id, "tokens": tokens})
    return pd.DataFrame(rows)


def extract_retrieval_features(
    query: str,
    bm25: BM25Okapi,
    doc_ids: list[str],
) -> dict[str, float | int | str]:
    """Puntúa una consulta contra el corpus ya indexado.

    Parameters
    ----------
    query :
        Texto de la consulta.
    bm25 :
        Índice BM25 del corpus usable.
    doc_ids :
        Identificadores en el mismo orden del índice.

    Returns
    -------
    dict[str, float | int | str]
        Puntuación del mejor documento, media del top-k, margen, conteos y
        el ``doc_id`` del primer puesto.
    """
    scores = bm25.get_scores(_content_tokens(query))
    order = sorted(range(len(scores)), key=lambda i: float(scores[i]), reverse=True)
    top = order[:TOP_K]
    top_scores = [float(scores[i]) for i in top]
    top1 = top_scores[0] if top_scores else 0.0
    top2 = top_scores[1] if len(top_scores) > 1 else 0.0
    positive = [doc_ids[i] for i, score in enumerate(scores) if float(score) > 0.0]
    return {
        "top1_retrieval_score": top1,
        "topk_mean_score": float(sum(top_scores) / len(top_scores)) if top_scores else 0.0,
        "retrieval_score_margin": top1 - top2,
        "retrieved_document_count": len(positive),
        "retrieved_source_count": len(set(positive)),
        "top1_doc_id": doc_ids[order[0]] if order else "",
    }


def build_retrieval_feature_table(
    queries: pd.Series,
    text_dir: Path,
    inventory: pd.DataFrame,
) -> pd.DataFrame:
    """Calcula características BM25 para cada consulta.

    Parameters
    ----------
    queries :
        Textos de consulta.
    text_dir :
        Carpeta de textos extraídos.
    inventory :
        Inventario para filtrar documentos usables.

    Returns
    -------
    pd.DataFrame
        Una fila por consulta. Si no hay corpus usable, las puntuaciones quedan
        en cero y ``top1_doc_id`` vacío.
    """
    corpus = load_corpus_documents(text_dir, inventory)
    if corpus.empty:
        empty = {column: 0 for column in RETRIEVAL_FEATURE_COLUMNS}
        empty["top1_doc_id"] = ""
        return pd.DataFrame([empty] * len(queries), index=queries.index)

    doc_ids = corpus["doc_id"].astype(str).tolist()
    bm25 = BM25Okapi(corpus["tokens"].tolist())
    rows = [extract_retrieval_features(query, bm25, doc_ids) for query in queries.astype(str)]
    return pd.DataFrame(rows, index=queries.index, columns=list(RETRIEVAL_FEATURE_COLUMNS))
