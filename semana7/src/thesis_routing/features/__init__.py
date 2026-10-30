"""Características de consultas para el enrutamiento predictivo.

Esta semana extrae señales del texto, de la intención por reglas y de una
búsqueda léxica BM25. No entrena el enrutador ni asigna la ruta.
"""

from thesis_routing.features.feature_pipeline import build_feature_table

__all__ = ["build_feature_table"]
