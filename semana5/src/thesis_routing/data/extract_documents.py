"""Extrae texto de PDF y HTML con trazabilidad a la fuente."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
RAW_PUBLIC = ROOT / "data" / "raw" / "public_documents"
TEXT_DIR = ROOT / "data" / "interim" / "extracted_text"
META_DIR = ROOT / "data" / "interim" / "document_metadata"


def extract_pdf(path: Path) -> tuple[str, dict[str, Any]]:
    """Extract text from a PDF using pypdf.

    Returns
    -------
    text, meta
        Full text and extraction diagnostics (pages, empty pages, selectable).
    """
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[str] = []
    empty = 0
    for page in reader.pages:
        chunk = page.extract_text() or ""
        if not chunk.strip():
            empty += 1
        pages.append(chunk)
    text = "\n\n".join(pages)
    n_chars = len(text.strip())
    # Guías escaneadas o casi vacías: marcar weak aunque haya algo de OCR/ruido
    if n_chars < 40:
        status = "empty_or_scanned"
    elif n_chars < 1500 and len(reader.pages) <= 2:
        status = "weak_or_scanned"
    else:
        status = "ok"
    meta = {
        "n_pages": len(reader.pages),
        "n_empty_pages": empty,
        "chars": len(text),
        "words": len(re.findall(r"\w+", text, flags=re.UNICODE)),
        "texto_extraible": n_chars > 40,
        "estado_extraccion": status,
    }
    return text, meta


def extract_html(path: Path) -> tuple[str, dict[str, Any]]:
    """Extract visible text from a saved HTML snapshot."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    # Lightweight strip (no BeautifulSoup dependency required)
    no_script = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", no_script)
    text = re.sub(r"\s+", " ", text).strip()
    meta = {
        "n_pages": 1,
        "n_empty_pages": 0,
        "chars": len(text),
        "words": len(re.findall(r"\w+", text, flags=re.UNICODE)),
        "texto_extraible": len(text) > 40,
        "estado_extraccion": "ok",
    }
    return text, meta


def extract_all() -> list[dict[str, Any]]:
    """Extract every file under ``raw/public_documents`` into interim text."""
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    for path in sorted(RAW_PUBLIC.iterdir()):
        if path.name.startswith(".") or not path.is_file():
            continue
        doc_id = path.name.split("__", 1)[0]
        try:
            if path.suffix.lower() == ".pdf":
                text, meta = extract_pdf(path)
            elif path.suffix.lower() in {".html", ".htm"}:
                text, meta = extract_html(path)
            else:
                LOGGER.warning("skip unsupported %s", path.name)
                continue
            out_txt = TEXT_DIR / f"{doc_id}.txt"
            out_txt.write_text(text, encoding="utf-8")
            row = {
                "doc_id": doc_id,
                "source_file": str(path.relative_to(ROOT)),
                "extracted_text": str(out_txt.relative_to(ROOT)),
                **meta,
            }
            rows.append(row)
            LOGGER.info(
                "extracted %s pages=%s chars=%s status=%s",
                doc_id,
                meta.get("n_pages"),
                meta.get("chars"),
                meta.get("estado_extraccion"),
            )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {
                    "doc_id": doc_id,
                    "source_file": str(path.relative_to(ROOT)),
                    "estado_extraccion": "error",
                    "error": str(exc),
                }
            )
            LOGGER.error("extract failed %s: %s", doc_id, exc)

    out = META_DIR / "extraction_manifest.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


def main() -> None:
    """CLI entry for text extraction."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    extract_all()


if __name__ == "__main__":
    main()
