"""Pipeline step: generate_report."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Entry point for `python -m thesis_routing.pipeline.generate_report`."""
    LOGGER.info("generate_report: stub (implementar según docs/experimental_protocol.md)")
    raise SystemExit("NotImplemented: generate_report")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
