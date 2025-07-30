"""Batch FDBScan Runner
======================

This module mirrors the legacy ``scripts/fdbscan_caching_250521.sh`` Bash
script. It loops over a small list of instruments and timeframes, invoking
``FDBScanAgent`` for each combination while respecting the ``JGT_CACHE``
environment variable.

The real FDBScan logic is optional. If ``jgtml`` is unavailable the agent
will print the actions it *would* take. Results are written to a simple
markdown log file so they can be consumed by other tools.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, List, Optional

from fdbscan_agent import FDBScanAgent


def run_batch(
    instruments: Iterable[str] | None = None,
    timeframes: Iterable[str] | None = None,
    cache_dir: str = "cache",
    log_dir: str = "logs",
    log_file: Optional[str] = None,
) -> str:
    """Run FDBScan across the given instruments and timeframes.

    Parameters
    ----------
    instruments:
        Iterable of instruments (e.g. ``["EUR/USD", "AUD/USD"]``).
    timeframes:
        Iterable of timeframes (e.g. ``["H4", "H1", "m15"]``).
    cache_dir:
        Directory used for JGT_CACHE.
    log_dir:
        Directory to store the resulting markdown log.
    log_file:
        Optional explicit log file path. When ``None`` a timestamped
        file inside ``log_dir`` is created.

    Returns
    -------
    str
        The path to the generated log file.
    """

    instruments = list(instruments or ["EUR/USD", "AUD/USD", "SPX500"])
    timeframes = list(timeframes or ["H4", "H1", "m15"])

    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"fdbscan_{timestamp}.log.md")

    agent = FDBScanAgent()

    with open(log_file, "w") as log:
        for inst in instruments:
            log.write(f"## Scanning : {inst}\n")
            for tf in timeframes:
                log.write(f"### Scanning timeframe: {tf}\n")
                os.environ["JGT_CACHE"] = cache_dir
                agent.scan_timeframe(tf, inst)
                log.write("----\n")
            log.write("----\n")
        log.write("## Finished scanning\n")
        log.write(f"## Log file: {log_file}\n")
        log.write(f"## Cache directory: {cache_dir}\n")

    return log_file


if __name__ == "__main__":
    run_batch()
