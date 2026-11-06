"""Detecta documentos duplicados o casi duplicados."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def content_hash(text: str) -> str:
    """SHA-256 of normalized content for duplicate detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def find_exact_duplicates(paths: list[Path]) -> dict[str, list[Path]]:
    """Group paths that share the same content hash.

    Parameters
    ----------
    paths :
        Text files to compare.
    """
    groups: dict[str, list[Path]] = {}
    for path in paths:
        digest = content_hash(path.read_text(encoding="utf-8"))
        groups.setdefault(digest, []).append(path)
    return {k: v for k, v in groups.items() if len(v) > 1}
