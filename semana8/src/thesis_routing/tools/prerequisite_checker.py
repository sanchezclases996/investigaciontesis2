"""Comprueba prerrequisitos sobre un perfil demo."""

from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


def prereq(course_id: str, graph: dict[str, Any]) -> list[str]:
    """Return prerequisite course ids."""
    return list(graph.get(course_id, {}).get("prereq", []))


def can_take(profile: dict[str, Any], course_id: str, graph: dict[str, Any]) -> bool:
    """Whether ``profile`` satisfies prerequisites for ``course_id``."""
    needed = set(prereq(course_id, graph))
    taken = set(profile.get("passed_courses", []))
    return needed.issubset(taken)
