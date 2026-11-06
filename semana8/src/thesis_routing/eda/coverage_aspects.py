"""Cobertura por aspectos normativos con métricas numéricas y TF-IDF.

Separa aspectos (p. ej. matrícula vs anulación) y reporta hits, densidad y
similitud TF-IDF; la etiqueta final es binaria (cubierto / no_cubierto).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Umbrales explícitos (documentados en el notebook / informe).
MIN_HITS: int = 3
MIN_DENSIDAD_POR_1K: float = 0.40
MIN_TFIDF_COSINE: float = 0.04
MIN_WORDS_DOC: int = 300  # docs con extracción débil no marcan cubierto

# Aspectos = procesos/subtemas, no solo la palabra genérica del tema.
ASPECT_SPECS: dict[str, dict[str, str]] = {
    "matricula_inscripcion": {
        "patron": r"matr[ií]cula regular|proceso de matr[ií]cula|matr[ií]cula (de|en)|inscripci[oó]n",
        "query": "matricula inscripción proceso matrícula regular",
    },
    "anulacion_retiro": {
        "patron": r"anulaci[oó]n de (la )?matr[ií]cula|retiro de (asignatura|curso|matr[ií]cula)|retirarse",
        "query": "anulación matrícula retiro asignatura",
    },
    "asistencia_inasistencia": {
        "patron": r"inasistenc|asistenc",
        "query": "asistencia inasistencias porcentaje sesiones",
    },
    "evaluacion_examenes": {
        "patron": r"examen (parcial|final|sustitutor)|evaluaci[oó]n (parcial|final)|sustitutorio|aplazado",
        "query": "examen parcial final sustitutorio evaluación aplazados",
    },
    "creditos_academicos": {
        "patron": r"cr[eé]dito(s)?\b",
        "query": "créditos académicos crédito",
    },
    "prerrequisitos": {
        "patron": r"prerrequis|pre-?requis",
        "query": "prerrequisito prerrequisitos",
    },
    "convalidacion": {
        "patron": r"convalid",
        "query": "convalidación convalidar estudios",
    },
    "aprobacion_desaprobacion": {
        "patron": r"aprobaci[oó]n|desaprob|nota m[ií]nima",
        "query": "aprobación desaprobación nota mínima",
    },
    "tramites_grados_titulos": {
        "patron": r"bachiller|t[ií]tulo profesional|grados? y t[ií]tulos?",
        "query": "bachiller título profesional grados títulos",
    },
    "becas": {
        "patron": r"\bbeca(s)?\b",
        "query": "beca becas beneficio económico",
    },
    "admision": {
        "patron": r"admisi[oó]n",
        "query": "admisión postulante examen admisión",
    },
    "tarifas_pensiones": {
        "patron": r"tarif|pensi[oó]n|pago(s)?\b|tesorer",
        "query": "tarifario pensión pagos tesorería",
    },
    "malla_plan_estudios": {
        "patron": r"plan de estudi|malla curricular|curr[ií]cul",
        "query": "plan de estudios malla curricular",
    },
    "calendario_periodo": {
        "patron": r"calendario acad[eé]mico|periodo acad[eé]mico|ciclo acad[eé]mico",
        "query": "calendario académico periodo ciclo",
    },
}


def _compile_patterns() -> dict[str, re.Pattern[str]]:
    return {k: re.compile(v["patron"], re.I) for k, v in ASPECT_SPECS.items()}


def load_doc_texts(text_dir: Path, doc_ids: list[str]) -> dict[str, str]:
    """Load extracted texts keyed by doc_id."""
    out: dict[str, str] = {}
    for doc_id in doc_ids:
        path = text_dir / f"{doc_id}.txt"
        if path.exists():
            out[doc_id] = path.read_text(encoding="utf-8", errors="replace")
        else:
            out[doc_id] = ""
    return out


def count_hits(texts: dict[str, str]) -> pd.DataFrame:
    """Aspect × document raw hit counts."""
    pats = _compile_patterns()
    rows: list[dict[str, Any]] = []
    for aspect, pat in pats.items():
        row: dict[str, Any] = {"aspecto": aspect}
        for doc_id, text in texts.items():
            row[doc_id] = int(len(pat.findall(text)))
        rows.append(row)
    return pd.DataFrame(rows).set_index("aspecto")


def density_per_1k(hits: pd.DataFrame, words_by_doc: dict[str, int]) -> pd.DataFrame:
    """Hits normalized per 1000 words (avoids long-doc bias)."""
    dens = hits.copy().astype(float)
    for doc_id in dens.columns:
        w = max(int(words_by_doc.get(doc_id, 0)), 1)
        dens[doc_id] = dens[doc_id] * 1000.0 / w
    return dens.round(3)


def tfidf_cosine_matrix(texts: dict[str, str]) -> pd.DataFrame:
    """Cosine TF-IDF between each aspect query and each document."""
    doc_ids = list(texts.keys())
    corpus = [texts[d] for d in doc_ids]
    queries = [ASPECT_SPECS[a]["query"] for a in ASPECT_SPECS]
    aspects = list(ASPECT_SPECS.keys())

    vectorizer = TfidfVectorizer(
        lowercase=True,
        min_df=1,
        max_df=1.0,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    # Fit on documents only; transform queries in the same space.
    doc_mat = vectorizer.fit_transform(corpus)
    query_mat = vectorizer.transform(queries)
    sim = cosine_similarity(query_mat, doc_mat)
    return pd.DataFrame(sim, index=aspects, columns=doc_ids).round(4)


def label_cubierto(
    hits: pd.DataFrame,
    dens: pd.DataFrame,
    tfidf: pd.DataFrame,
    words_by_doc: dict[str, int],
    *,
    min_hits: int = MIN_HITS,
    min_dens: float = MIN_DENSIDAD_POR_1K,
    min_tfidf: float = MIN_TFIDF_COSINE,
    min_words: int = MIN_WORDS_DOC,
) -> pd.DataFrame:
    """Binary label: cubierto / no_cubierto.

    Regla (OR de evidencia cuantitativa), solo si el doc tiene texto suficiente:
    (hits >= min_hits AND dens_1k >= min_dens) OR (tfidf_cosine >= min_tfidf)
    """
    labels = pd.DataFrame(index=hits.index, columns=hits.columns, dtype=object)
    for aspect in hits.index:
        for doc_id in hits.columns:
            if int(words_by_doc.get(str(doc_id), 0)) < min_words:
                labels.loc[aspect, doc_id] = "no_cubierto"
                continue
            h = int(hits.loc[aspect, doc_id])
            d = float(dens.loc[aspect, doc_id])
            t = float(tfidf.loc[aspect, doc_id])
            ok = (h >= min_hits and d >= min_dens) or (t >= min_tfidf)
            labels.loc[aspect, doc_id] = "cubierto" if ok else "no_cubierto"
    return labels


def summarize_coverage(labels: pd.DataFrame) -> pd.DataFrame:
    """Per-aspect counts of documents marked cubierto."""
    rows: list[dict[str, Any]] = []
    n_docs = labels.shape[1]
    for aspect in labels.index:
        n_ok = int((labels.loc[aspect] == "cubierto").sum())
        rows.append(
            {
                "aspecto": aspect,
                "docs_cubiertos": n_ok,
                "docs_total": n_docs,
                "pct_docs": round(100.0 * n_ok / n_docs, 1),
            }
        )
    return pd.DataFrame(rows)


def plot_matrix_heatmap(
    matrix: pd.DataFrame,
    out: Path,
    *,
    title: str,
    cbar_label: str,
    cmap: str = "YlGn",
) -> None:
    """Save aspecto × documento heatmap for a numeric matrix."""
    fig, ax = plt.subplots(figsize=(11, 6.2))
    im = ax.imshow(matrix.to_numpy(dtype=float), aspect="auto", cmap=cmap)
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.03, label=cbar_label)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)


def plot_tfidf_heatmap(tfidf: pd.DataFrame, out: Path) -> None:
    """Save continuous TF-IDF cosine heatmap."""
    plot_matrix_heatmap(
        tfidf,
        out,
        title="Similitud TF-IDF (cosine) aspecto × documento",
        cbar_label="cosine TF-IDF",
        cmap="YlGn",
    )


def plot_summary_bars(summary: pd.DataFrame, out: Path) -> None:
    """Bar chart: % of documents marked cubierto per aspect."""
    ordered = summary.sort_values("pct_docs", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.barh(
        ordered["aspecto"],
        ordered["pct_docs"],
        color="#4C72B0",
        edgecolor="black",
        linewidth=0.4,
    )
    ax.set_xlabel("% de documentos cubiertos")
    ax.set_ylabel("aspecto")
    ax.set_xlim(0, 100)
    ax.set_title("Cobertura por aspecto (% docs con etiqueta cubierto)")
    for y, pct, n_ok, n_tot in zip(
        ordered["aspecto"],
        ordered["pct_docs"],
        ordered["docs_cubiertos"],
        ordered["docs_total"],
        strict=True,
    ):
        ax.text(min(float(pct) + 1.5, 92), y, f"{n_ok}/{n_tot}", va="center", fontsize=8)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)


def plot_top_aspect_bars(tfidf: pd.DataFrame, out: Path, *, top_n: int = 6) -> None:
    """Grouped bars: mean TF-IDF of top aspects across documents."""
    means = tfidf.mean(axis=1).sort_values(ascending=False).head(top_n)
    subset = tfidf.loc[means.index]
    fig, ax = plt.subplots(figsize=(11, 5.2))
    x = np.arange(len(subset.columns))
    width = 0.12
    for i, aspect in enumerate(subset.index):
        ax.bar(
            x + (i - len(subset.index) / 2) * width + width / 2,
            subset.loc[aspect].to_numpy(dtype=float),
            width=width,
            label=aspect,
            edgecolor="black",
            linewidth=0.2,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(subset.columns, rotation=45, ha="right")
    ax.set_ylabel("TF-IDF cosine")
    ax.set_title(f"TF-IDF por documento (top {top_n} aspectos por media)")
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)


def build_coverage_bundle(
    text_dir: Path,
    inventory: pd.DataFrame,
    fig_dir: Path,
) -> dict[str, Any]:
    """Compute all coverage tables and write CSV/PNG artifacts."""
    doc_ids = inventory["doc_id"].astype(str).tolist()
    words_by_doc = {
        str(r["doc_id"]): int(r["words"]) for _, r in inventory.iterrows()
    }
    texts = load_doc_texts(text_dir, doc_ids)
    hits = count_hits(texts)
    dens = density_per_1k(hits, words_by_doc)
    tfidf = tfidf_cosine_matrix(texts)
    labels = label_cubierto(hits, dens, tfidf, words_by_doc)
    summary = summarize_coverage(labels)

    fig_dir.mkdir(parents=True, exist_ok=True)
    hits.to_csv(fig_dir / "eda_cobertura_hits.csv")
    dens.to_csv(fig_dir / "eda_cobertura_densidad_1k.csv")
    tfidf.to_csv(fig_dir / "eda_cobertura_tfidf.csv")
    labels.to_csv(fig_dir / "eda_cobertura_etiqueta.csv")
    summary.to_csv(fig_dir / "eda_cobertura_resumen.csv", index=False)
    # Compat: matriz antigua reemplazada por etiquetas binarias
    labels.reset_index().rename(columns={"aspecto": "tema"}).to_csv(
        fig_dir / "eda_matriz_cobertura.csv", index=False
    )
    plot_matrix_heatmap(
        hits.astype(float),
        fig_dir / "eda_cobertura_hits.png",
        title="Hits por aspecto × documento",
        cbar_label="conteo de coincidencias",
        cmap="Blues",
    )
    plot_matrix_heatmap(
        dens,
        fig_dir / "eda_cobertura_densidad.png",
        title="Densidad (hits / 1000 palabras) aspecto × documento",
        cbar_label="densidad por 1k palabras",
        cmap="Oranges",
    )
    plot_tfidf_heatmap(tfidf, fig_dir / "eda_matriz_cobertura.png")
    plot_tfidf_heatmap(tfidf, fig_dir / "eda_cobertura_tfidf.png")
    plot_top_aspect_bars(tfidf, fig_dir / "eda_cobertura_tfidf_barras.png")
    plot_summary_bars(summary, fig_dir / "eda_cobertura_resumen_barras.png")

    return {
        "hits": hits,
        "densidad": dens,
        "tfidf": tfidf,
        "etiquetas": labels,
        "resumen": summary,
        "umbrales": {
            "min_hits": MIN_HITS,
            "min_densidad_por_1k": MIN_DENSIDAD_POR_1K,
            "min_tfidf_cosine": MIN_TFIDF_COSINE,
            "min_words_doc": MIN_WORDS_DOC,
        },
        "docs_cubiertos_por_aspecto": {
            str(r["aspecto"]): int(r["docs_cubiertos"]) for _, r in summary.iterrows()
        },
    }
