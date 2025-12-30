"""Contains the main namespace."""

from __future__ import annotations

try:
    from ._version import version as __version__  # ty: ignore[unresolved-import]
except ImportError:  # pragma: no cover
    # broken installation, we don't even try unknown only works because we do poor mans
    # version compare
    __version__ = "unknown"


__all__ = ["__version__"]
