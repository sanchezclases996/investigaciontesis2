"""Orquesta: catálogo → descarga → extracción → inventario → banco → perfiles."""

from __future__ import annotations

import logging

from thesis_routing.data.build_inventory import build_inventory
from thesis_routing.data.build_question_bank import build_pilot_bank
from thesis_routing.data.build_synthetic_profiles import build as build_profiles
from thesis_routing.data.download_sources import download_priority
from thesis_routing.data.extract_documents import extract_all

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Run the data preparation pipeline (before EDA)."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    LOGGER.info("1/5 download public sources")
    download_priority()
    LOGGER.info("2/5 extract text")
    extract_all()
    LOGGER.info("3/5 build inventory CSV")
    build_inventory()
    LOGGER.info("4/5 build pilot question bank")
    build_pilot_bank()
    LOGGER.info("5/5 synthetic profiles + demo malla graph")
    build_profiles()
    LOGGER.info("done — next step is EDA on organized data, not before")


if __name__ == "__main__":
    main()
