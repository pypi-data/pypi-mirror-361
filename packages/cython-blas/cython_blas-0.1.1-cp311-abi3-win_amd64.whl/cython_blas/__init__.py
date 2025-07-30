"""Cython BLAS."""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'cython_blas.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

import contextlib
import importlib.metadata

with contextlib.suppress(ImportError):
    from cython_blas import _init_local  # noqa: F401


__version__ = importlib.metadata.version(__package__)