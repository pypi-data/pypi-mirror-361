"""Set package version."""

from __future__ import annotations

import logging

from ._logging import LogLevels, RunwayLogger  # noqa: F401

logging.setLoggerClass(RunwayLogger)

__version__: str = "2.8.4"
"""Version of the Python package presented as a :class:`string`.

Dynamically set upon release by `poetry-dynamic-versioning <https://github.com/mtkennerly/poetry-dynamic-versioning>`__.

"""

__version_tuple__: tuple[int, int, int] | tuple[int, int, int, str] = (2, 8, 4)
"""Version of the Python package presented as a :class:`tuple`.

Dynamically set upon release by `poetry-dynamic-versioning <https://github.com/mtkennerly/poetry-dynamic-versioning>`__.

"""
