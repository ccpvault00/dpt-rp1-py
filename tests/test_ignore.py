"""Unit tests for the .syncignore pattern system."""
import pytest
from pathlib import Path


class TestLoadIgnorePatterns:
    def test_missing_file_returns_empty_list(self, dp, tmp_path):
        assert dp.load_ignore_patterns(str(tmp_path)) == []

    def test_comments_and_blanks_are_skipped(self, dp, tmp_path):
        (tmp_path / ".syncignore").write_text("# comment\n\n*.tmp\n")
        assert dp.load_ignore_patterns(str(tmp_path)) == ["*.tmp"]

    def test_trailing_whitespace_stripped(self, dp, tmp_path):
        (tmp_path / ".syncignore").write_text("*.tmp   \n")
        assert dp.load_ignore_patterns(str(tmp_path)) == ["*.tmp"]

    def test_multiple_patterns_returned(self, dp, tmp_path):
        (tmp_path / ".syncignore").write_text("*.tmp\ndraft*.pdf\n")
        assert dp.load_ignore_patterns(str(tmp_path)) == ["*.tmp", "draft*.pdf"]


class TestAddRemoveIgnorePattern:
    def test_add_new_pattern_returns_true(self, dp, tmp_path):
        assert dp.add_ignore_pattern(str(tmp_path), "*.tmp") is True
        assert "*.tmp" in dp.load_ignore_patterns(str(tmp_path))

    def test_add_duplicate_returns_false_and_no_duplicate(self, dp, tmp_path):
        dp.add_ignore_pattern(str(tmp_path), "*.tmp")
        assert dp.add_ignore_pattern(str(tmp_path), "*.tmp") is False
        assert dp.load_ignore_patterns(str(tmp_path)).count("*.tmp") == 1

    def test_remove_existing_pattern_returns_true(self, dp, tmp_path):
        dp.add_ignore_pattern(str(tmp_path), "*.tmp")
        assert dp.remove_ignore_pattern(str(tmp_path), "*.tmp") is True
        assert dp.load_ignore_patterns(str(tmp_path)) == []

    def test_remove_absent_pattern_returns_false(self, dp, tmp_path):
        assert dp.remove_ignore_pattern(str(tmp_path), "ghost.pdf") is False


class TestSaveIgnorePatternPreservesComments:
    def test_comments_preserved_on_add(self, dp, tmp_path):
        (tmp_path / ".syncignore").write_text("# my comment\n*.tmp\n")
        dp.add_ignore_pattern(str(tmp_path), "draft*.pdf")
        content = (tmp_path / ".syncignore").read_text()
        assert "# my comment" in content
        assert "*.tmp" in content
        assert "draft*.pdf" in content

    def test_comments_preserved_on_remove(self, dp, tmp_path):
        (tmp_path / ".syncignore").write_text("# keep me\n*.tmp\ndraft*.pdf\n")
        dp.remove_ignore_pattern(str(tmp_path), "*.tmp")
        content = (tmp_path / ".syncignore").read_text()
        assert "# keep me" in content
        assert "*.tmp" not in content
        assert "draft*.pdf" in content


class TestIsIgnored:
    def test_wildcard_basename_match(self, dp):
        assert dp.is_ignored("subdir/draft.tmp", ["*.tmp"]) is True

    def test_no_patterns_never_ignored(self, dp):
        assert dp.is_ignored("anything.pdf", []) is False

    def test_full_path_pattern(self, dp):
        assert dp.is_ignored("archive/old.pdf", ["archive/*.pdf"]) is True

    def test_non_matching_pattern(self, dp):
        assert dp.is_ignored("final.pdf", ["*.tmp"]) is False

    def test_exact_filename_match(self, dp):
        assert dp.is_ignored("subdir/secret.pdf", ["secret.pdf"]) is True


class TestListIgnoredFiles:
    def test_returns_relative_paths(self, dp, tmp_path):
        (tmp_path / ".syncignore").write_text("draft*.pdf\n")
        (tmp_path / "draft1.pdf").touch()
        (tmp_path / "final.pdf").touch()
        result = dp.list_ignored_files(str(tmp_path))
        assert result == ["draft1.pdf"]

    def test_empty_when_no_syncignore(self, dp, tmp_path):
        (tmp_path / "something.pdf").touch()
        assert dp.list_ignored_files(str(tmp_path)) == []

    def test_symlink_cycle_does_not_hang(self, dp, tmp_path):
        loop = tmp_path / "loop"
        loop.symlink_to(tmp_path)
        (tmp_path / ".syncignore").write_text("*.tmp\n")
        # Must complete without RecursionError or infinite loop
        dp.list_ignored_files(str(tmp_path))

    def test_nested_directory_traversal(self, dp, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        (tmp_path / ".syncignore").write_text("draft*.pdf\n")
        (sub / "draft2.pdf").touch()
        (sub / "final.pdf").touch()
        result = dp.list_ignored_files(str(tmp_path))
        assert any("draft2.pdf" in r for r in result)
        assert not any("final.pdf" in r for r in result)
