"""Consultas sobre el grafo de malla curricular."""

from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


def unlocks(course_id: str, graph: dict[str, Any]) -> list[str]:
    """Return courses unlocked by ``course_id``."""
    LOGGER.debug("unlocks(%s)", course_id)
    return list(graph.get(course_id, {}).get("unlocks", []))
