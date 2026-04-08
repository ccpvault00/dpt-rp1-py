"""Shared pytest fixtures for dpt-rp1-py tests."""
import sys
import types
import pytest
from unittest.mock import MagicMock

# httpsig uses pkg_resources only to read its own version number.
# Stub it out if setuptools isn't installed (common on CI).
if "pkg_resources" not in sys.modules:
    try:
        import pkg_resources  # noqa: F401
    except ImportError:
        _stub = types.ModuleType("pkg_resources")
        _stub.get_distribution = MagicMock(return_value=MagicMock(version="unknown"))
        _stub.DistributionNotFound = Exception
        sys.modules["pkg_resources"] = _stub

from dptrp1.dptrp1 import DigitalPaper


@pytest.fixture
def dp(tmp_path):
    """DigitalPaper instance with all network state bypassed.

    Uses object.__new__ to skip __init__ so no network calls are made.
    """
    obj = object.__new__(DigitalPaper)
    obj.session = MagicMock()
    obj.addr = "192.168.1.1"
    obj.assume_yes = False
    obj.folder_list = []
    return obj
