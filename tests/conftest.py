"""Shared pytest fixtures for dpt-rp1-py tests."""
import pytest
from unittest.mock import MagicMock
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
