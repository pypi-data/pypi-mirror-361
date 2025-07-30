"""Cython BLAS."""

import contextlib
import importlib.metadata

with contextlib.suppress(ImportError):
    from cython_blas import _init_local  # noqa: F401


__version__ = importlib.metadata.version(__package__)
