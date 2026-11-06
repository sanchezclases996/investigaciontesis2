"""Reglas académicas explícitas (no sustituyen actos administrativos)."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


def should_escalate_to_human(query_type: str) -> bool:
    """Return True for trámite queries that must go to a person (type A)."""
    return query_type.upper() == "A"
