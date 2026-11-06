"""Pipeline step: build_index."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Entry point for `python -m thesis_routing.pipeline.build_index`."""
    LOGGER.info("build_index: stub (implementar según docs/experimental_protocol.md)")
    raise SystemExit("NotImplemented: build_index")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
