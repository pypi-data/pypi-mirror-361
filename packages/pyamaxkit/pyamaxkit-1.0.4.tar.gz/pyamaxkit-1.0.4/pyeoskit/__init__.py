"""Compatibility wrapper for the :mod:`pyamaxkit` package.

This module re-exports all public symbols from :mod:`pyamaxkit` so that
existing code depending on the historical ``pyeoskit`` name continues to
function.  The native extension ``_pyeoskit`` is not imported when using
``from pyamaxkit import *`` because its name starts with an underscore.  In
several places within this repository ``from pyeoskit import _pyeoskit`` is
used directly, so we explicitly expose the extension here as well.
"""

from pyamaxkit import *  # re-export public API
from pyamaxkit import _pyeoskit  # expose native extension

__all__ = [name for name in globals().keys() if not name.startswith("_")]
__all__.append("_pyeoskit")
