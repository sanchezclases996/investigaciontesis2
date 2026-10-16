"""Pipeline step: run_experiment."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Entry point for `python -m thesis_routing.pipeline.run_experiment`."""
    LOGGER.info("run_experiment: stub (implementar según docs/experimental_protocol.md)")
    raise SystemExit("NotImplemented: run_experiment")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
