"""Pipeline step: evaluate_results."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Entry point for `python -m thesis_routing.pipeline.evaluate_results`."""
    LOGGER.info("evaluate_results: stub (implementar según docs/experimental_protocol.md)")
    raise SystemExit("NotImplemented: evaluate_results")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
