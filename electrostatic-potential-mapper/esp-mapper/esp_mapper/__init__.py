"""Top-level package for the electrostatic potential mapper.

The main public modules are imported lazily to keep import times small.
"""

from . import src

__all__ = ["coulomb", "grid", "pb_linear", "reader", "visualize"]


def __getattr__(name: str):  # pragma: no cover - thin wrapper
	if name in __all__:
		return getattr(src, name)
	raise AttributeError(name)
