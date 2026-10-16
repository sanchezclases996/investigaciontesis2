"""Construye inventario_documental.csv a partir de catálogo + manifests."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

import yaml

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "data" / "sources" / "catalog_sources.yaml"
DOWNLOAD = ROOT / "data" / "interim" / "document_metadata" / "download_manifest.json"
EXTRACT = ROOT / "data" / "interim" / "document_metadata" / "extraction_manifest.json"
OUT_CSV = ROOT / "data" / "processed" / "corpus" / "inventario_documental.csv"

FIELDS = [
    "doc_id",
    "tipo_documento",
    "titulo",
    "dominio",
    "prioridad",
    "url_origen",
    "fecha_consulta",
    "formato",
    "local_path",
    "bytes",
    "sha256",
    "n_pages",
    "chars",
    "words",
    "texto_extraible",
    "estado_descarga",
    "estado_extraccion",
    "notas",
]


def build_inventory() -> Path:
    """Merge catalog, download and extraction manifests into one CSV."""
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    downloads = {
        r["doc_id"]: r
        for r in json.loads(DOWNLOAD.read_text(encoding="utf-8"))
        if DOWNLOAD.exists()
    } if DOWNLOAD.exists() else {}
    extracts = {
        r["doc_id"]: r
        for r in json.loads(EXTRACT.read_text(encoding="utf-8"))
        if EXTRACT.exists()
    } if EXTRACT.exists() else {}

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for item in catalog.get("priority_documents", []):
        doc_id = item["doc_id"]
        d = downloads.get(doc_id, {})
        e = extracts.get(doc_id, {})
        rows.append(
            {
                "doc_id": doc_id,
                "tipo_documento": item.get("tipo_documento"),
                "titulo": item.get("titulo"),
                "dominio": item.get("dominio"),
                "prioridad": item.get("prioridad"),
                "url_origen": item.get("url"),
                "fecha_consulta": d.get("fecha_consulta", ""),
                "formato": item.get("formato", d.get("formato", "pdf")),
                "local_path": d.get("local_path", ""),
                "bytes": d.get("bytes", ""),
                "sha256": d.get("sha256", ""),
                "n_pages": e.get("n_pages", ""),
                "chars": e.get("chars", ""),
                "words": e.get("words", ""),
                "texto_extraible": e.get("texto_extraible", ""),
                "estado_descarga": d.get("estado_descarga", "missing"),
                "estado_extraccion": e.get("estado_extraccion", "missing"),
                "notas": d.get("notas") or item.get("notas", ""),
            }
        )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    LOGGER.info("inventory -> %s (%d docs)", OUT_CSV, len(rows))
    return OUT_CSV


def main() -> None:
    """CLI entry."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    build_inventory()


if __name__ == "__main__":
    main()
