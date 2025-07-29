import os
import sys
from .http_client import HttpClient
from .rpc_interface import RPCInterface, WalletClient
from .chainapi_sync import ChainApi

import types
import warnings

try:
    from . import _pyeoskit as _native
    _HAS_NATIVE = True
except ImportError as e:
    warnings.warn(
        "Failed to import native module '_pyeoskit'. "
        "Most functionality will be unavailable: %s" % e,
        RuntimeWarning,
    )
    _HAS_NATIVE = False

    class _MissingModule(types.ModuleType):
        """Placeholder that raises an informative error on attribute access."""

        def __getattr__(self, attr):
            raise ImportError(
                "pyamaxkit requires the compiled '_pyeoskit' extension for "
                f"function '{attr}'. Please build the project with its native "
                "dependencies."
            )

    _native = _MissingModule('_pyeoskit')

_pyeoskit = _native

__version__ = '1.0.4'

if _HAS_NATIVE:
    _pyeoskit.init()

amaxapi = ChainApi()
eosapi = amaxapi  # backwards compatibility
