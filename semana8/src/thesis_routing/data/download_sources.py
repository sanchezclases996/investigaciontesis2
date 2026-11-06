"""Registra y descarga fuentes documentales permitidas desde el catálogo YAML."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

import yaml

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "data" / "sources" / "catalog_sources.yaml"
RAW_PUBLIC = ROOT / "data" / "raw" / "public_documents"
META_DIR = ROOT / "data" / "interim" / "document_metadata"


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    """Load the YAML source catalog."""
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _safe_filename(doc_id: str, url: str, formato: str = "pdf") -> str:
    """Build a stable local filename from doc_id and URL."""
    parsed = urllib.parse.urlparse(url)
    name = Path(urllib.parse.unquote(parsed.path)).name
    if not name or name.endswith("/"):
        name = f"{doc_id}.{formato}"
    # Keep extension
    if "." not in name:
        name = f"{name}.{formato}"
    return f"{doc_id}__{re.sub(r'[^A-Za-z0-9._-]+', '_', name)}"


def sha256_file(path: Path) -> str:
    """Return SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_document(
    item: dict[str, Any],
    out_dir: Path = RAW_PUBLIC,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Download one catalog item into ``out_dir`` and return metadata.

    Parameters
    ----------
    item :
        Catalog row with at least ``doc_id`` and ``url``.
    out_dir :
        Destination directory for public files.
    force :
        Re-download even if the file already exists.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    formato = str(item.get("formato", "pdf")).lower()
    url = str(item["url"])
    doc_id = str(item["doc_id"])
    target = out_dir / _safe_filename(doc_id, url, formato=formato)

    record: dict[str, Any] = {
        "doc_id": doc_id,
        "titulo": item.get("titulo"),
        "tipo_documento": item.get("tipo_documento"),
        "dominio": item.get("dominio"),
        "prioridad": item.get("prioridad"),
        "url_origen": url,
        "fecha_consulta": date.today().isoformat(),
        "formato": formato,
        "local_path": str(target.relative_to(ROOT)),
        "estado_descarga": "pending",
        "bytes": None,
        "sha256": None,
        "notas": item.get("notas", ""),
    }

    if formato == "html":
        # Save HTML snapshot for FAQ/portals
        target = out_dir / f"{doc_id}__faq.html"
        record["local_path"] = str(target.relative_to(ROOT))

    if target.exists() and not force:
        record["estado_descarga"] = "cached"
        record["bytes"] = target.stat().st_size
        record["sha256"] = sha256_file(target)
        LOGGER.info("cached %s", target.name)
        return record

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "tesis-routing-universitario/0.1"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
        target.write_bytes(data)
        record["estado_descarga"] = "ok"
        record["bytes"] = len(data)
        record["sha256"] = sha256_file(target)
        LOGGER.info("downloaded %s (%s bytes)", target.name, len(data))
    except Exception as exc:  # noqa: BLE001 - record error for inventory
        record["estado_descarga"] = "error"
        record["notas"] = f"{record.get('notas','')} | error={exc}".strip(" |")
        LOGGER.error("failed %s: %s", doc_id, exc)

    return record


def download_priority(*, force: bool = False) -> list[dict[str, Any]]:
    """Download all ``priority_documents`` from the catalog."""
    catalog = load_catalog()
    META_DIR.mkdir(parents=True, exist_ok=True)
    records = [
        download_document(item, force=force)
        for item in catalog.get("priority_documents", [])
    ]
    out = META_DIR / "download_manifest.json"
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("wrote %s (%d rows)", out, len(records))
    return records


def main() -> None:
    """CLI entry: download priority UMA public documents."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    download_priority()


if __name__ == "__main__":
    main()
