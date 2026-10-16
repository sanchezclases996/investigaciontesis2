"""Resúmenes para leer la tabla de características.

No estiman si el enrutamiento mejora. Solo describen el banco.
"""

from __future__ import annotations

import pandas as pd


def binary_rates(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Porcentaje de consultas con cada marca binaria en 1.

    Parameters
    ----------
    frame :
        Tabla de características.
    columns :
        Columnas 0/1.

    Returns
    -------
    pd.DataFrame
        Columnas ``n``, ``pct`` y ``n_consultas``, ordenadas por ``pct``.
    """
    present = [column for column in columns if column in frame.columns]
    rates = []
    total = len(frame)
    for column in present:
        count = int(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum())
        rates.append(
            {
                "caracteristica": column,
                "n": count,
                "pct": round(100.0 * count / total, 1) if total else 0.0,
            }
        )
    out = pd.DataFrame(rates)
    if out.empty:
        return out
    return out.sort_values("pct", ascending=False).reset_index(drop=True)


def numeric_by_group(
    frame: pd.DataFrame,
    value_column: str,
    group_column: str,
) -> pd.DataFrame:
    """Mediana y media de una columna numérica por grupo.

    Parameters
    ----------
    frame :
        Tabla de características.
    value_column :
        Columna numérica, por ejemplo la longitud en palabras.
    group_column :
        Columna de agrupación, por ejemplo la complejidad etiquetada.

    Returns
    -------
    pd.DataFrame
        Conteo, mediana y media por grupo.
    """
    grouped = frame.groupby(group_column, dropna=False)[value_column]
    summary = grouped.agg(n="size", mediana="median", media="mean").reset_index()
    summary["media"] = summary["media"].round(1)
    summary["mediana"] = summary["mediana"].round(1)
    return summary
