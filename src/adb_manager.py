"""
Backwards-compatibility shim.
ADBManager is now AndroidManager — import from here or from android_manager directly.
"""
from src.android_manager import AndroidManager as ADBManager   # noqa: F401

__all__ = ["ADBManager"]
