"""Genera perfiles demo sintéticos para tools de malla (sin PII real)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "synthetic" / "synthetic_profiles" / "perfiles_demo.json"
GRAPH_OUT = ROOT / "data" / "processed" / "corpus" / "malla_demo_grafo.json"


def demo_curriculum_graph() -> dict[str, Any]:
    """Minimal synthetic curriculum graph for tool demos (not official UMA malla)."""
    return {
        "meta": {
            "status": "synthetic_placeholder",
            "note": "Reemplazar con malla oficial de la facultad cuando se autorice/publique.",
        },
        "courses": {
            "MAT101": {"name": "Matemática I", "credits": 4, "prereq": [], "unlocks": ["MAT102"]},
            "MAT102": {"name": "Matemática II", "credits": 4, "prereq": ["MAT101"], "unlocks": ["EST201"]},
            "EST201": {"name": "Estadística", "credits": 3, "prereq": ["MAT102"], "unlocks": []},
            "PRG101": {"name": "Programación I", "credits": 4, "prereq": [], "unlocks": ["PRG102"]},
            "PRG102": {"name": "Programación II", "credits": 4, "prereq": ["PRG101"], "unlocks": []},
        },
    }


def demo_profiles() -> list[dict[str, Any]]:
    """Small set of edge-case synthetic student profiles."""
    return [
        {
            "profile_id": "P001",
            "label": "regular",
            "passed_courses": ["MAT101", "PRG101"],
            "credits_passed": 8,
            "condition": "regular",
        },
        {
            "profile_id": "P002",
            "label": "listo_estadistica",
            "passed_courses": ["MAT101", "MAT102", "PRG101"],
            "credits_passed": 12,
            "condition": "regular",
        },
        {
            "profile_id": "P003",
            "label": "sin_prereq",
            "passed_courses": [],
            "credits_passed": 0,
            "condition": "ingresante",
        },
        {
            "profile_id": "P004",
            "label": "tramite_grados",
            "passed_courses": ["MAT101", "MAT102", "EST201", "PRG101", "PRG102"],
            "credits_passed": 19,
            "condition": "egresado_en_tramite",
            "escalate_hint": True,
        },
    ]


def build() -> None:
    """Write synthetic graph and profiles."""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_OUT.parent.mkdir(parents=True, exist_ok=True)
    graph = demo_curriculum_graph()
    profiles = demo_profiles()
    GRAPH_OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT.write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("wrote %s and %s", GRAPH_OUT, OUT)


def main() -> None:
    """CLI entry."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    build()


if __name__ == "__main__":
    main()
