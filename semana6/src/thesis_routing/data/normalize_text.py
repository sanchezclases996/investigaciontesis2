"""Normaliza caracteres y limpia texto extraído."""

from __future__ import annotations

import logging
import unicodedata

LOGGER = logging.getLogger(__name__)


def normalize_text(text: str, *, strip_controls: bool = True) -> str:
    """Return NFC-normalized text.

    Parameters
    ----------
    text :
        Raw extracted text.
    strip_controls :
        If True, drop ASCII control characters except newlines/tabs.
    """
    cleaned = unicodedata.normalize("NFC", text)
    if strip_controls:
        cleaned = "".join(
            ch for ch in cleaned if ch in "\n\t" or ord(ch) >= 32
        )
    return cleaned
