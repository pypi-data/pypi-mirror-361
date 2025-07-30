# Copyright (C) 2025 Embedl AB

"""
Public Embedl Hub library API.
```pycon
>>> import embedl_hub
>>> embedl_hub.__version__
'2025.6.0'
```
"""

from embedl_hub.core.context import tuning_context
from embedl_hub.tracking import log_metric, log_param

__all__ = ['tuning_context', 'log_metric', 'log_param']

try:
    from importlib.metadata import version as _v

    __version__ = _v(__name__)
except Exception:
    __version__ = "2025.6.0.dev1"
