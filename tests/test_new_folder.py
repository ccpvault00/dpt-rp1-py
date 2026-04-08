"""Unit tests for new_folder() recursion guards."""
import pytest
from unittest.mock import MagicMock, patch, call
from dptrp1.dptrp1 import DigitalPaper


@pytest.fixture
def dp_with_api(tmp_path):
    """DigitalPaper instance with API methods mocked."""
    obj = object.__new__(DigitalPaper)
    obj.session = MagicMock()
    obj.addr = "192.168.1.1"
    obj.assume_yes = False
    obj.folder_list = []
    return obj


class TestNewFolderGuards:
    def test_root_slash_returns_immediately(self, dp_with_api):
        with patch.object(dp_with_api, '_post_endpoint') as mock_post:
            dp_with_api.new_folder("/")
            mock_post.assert_not_called()

    def test_empty_string_returns_immediately(self, dp_with_api):
        with patch.object(dp_with_api, '_post_endpoint') as mock_post:
            dp_with_api.new_folder("")
            mock_post.assert_not_called()

    def test_trailing_slash_normalized(self, dp_with_api):
        with patch.object(dp_with_api, 'path_exists', return_value=True), \
             patch.object(dp_with_api, '_get_object_id', return_value="parent-id"), \
             patch.object(dp_with_api, '_post_endpoint'):
            # Should not raise; trailing slash stripped cleanly
            dp_with_api.new_folder("Document/Papers/")

    def test_parent_exists_no_extra_recursion(self, dp_with_api):
        with patch.object(dp_with_api, 'path_exists', return_value=True) as mock_exists, \
             patch.object(dp_with_api, '_get_object_id', return_value="parent-id"), \
             patch.object(dp_with_api, '_post_endpoint') as mock_post:
            dp_with_api.new_folder("Document/Papers")
            mock_exists.assert_called_once_with("Document")
            mock_post.assert_called_once()
