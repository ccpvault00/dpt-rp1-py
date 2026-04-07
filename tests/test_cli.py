"""Unit tests for CLI command wrappers."""
import pytest
from unittest.mock import MagicMock
from dptrp1.cli.dptrp1 import (
    do_add_ignore, do_remove_ignore, do_list_ignore, do_list_ignored_files,
    build_parser,
)


class TestDoAddIgnore:
    def test_prints_added_when_pattern_is_new(self, capsys):
        d = MagicMock()
        d.add_ignore_pattern.return_value = True
        do_add_ignore(d, "/some/path", "*.tmp")
        assert "Added ignore pattern: *.tmp" in capsys.readouterr().out

    def test_prints_already_exists_when_duplicate(self, capsys):
        d = MagicMock()
        d.add_ignore_pattern.return_value = False
        do_add_ignore(d, "/some/path", "*.tmp")
        assert "Pattern already exists" in capsys.readouterr().out


class TestDoRemoveIgnore:
    def test_prints_removed_when_found(self, capsys):
        d = MagicMock()
        d.remove_ignore_pattern.return_value = True
        do_remove_ignore(d, "/some/path", "*.tmp")
        assert "Removed ignore pattern: *.tmp" in capsys.readouterr().out

    def test_prints_not_found(self, capsys):
        d = MagicMock()
        d.remove_ignore_pattern.return_value = False
        do_remove_ignore(d, "/some/path", "*.tmp")
        assert "Pattern not found" in capsys.readouterr().out


class TestDoListIgnore:
    def test_prints_each_pattern(self, capsys):
        d = MagicMock()
        d.load_ignore_patterns.return_value = ["*.tmp", "draft*.pdf"]
        do_list_ignore(d, "/some/path")
        out = capsys.readouterr().out
        assert "*.tmp" in out
        assert "draft*.pdf" in out

    def test_prints_none_configured_when_empty(self, capsys):
        d = MagicMock()
        d.load_ignore_patterns.return_value = []
        do_list_ignore(d, "/some/path")
        assert "No ignore patterns configured" in capsys.readouterr().out


class TestDoListIgnoredFiles:
    def test_prints_each_file(self, capsys):
        d = MagicMock()
        d.list_ignored_files.return_value = ["sub/file.pdf"]
        do_list_ignored_files(d, "/some/path")
        assert "sub/file.pdf" in capsys.readouterr().out

    def test_prints_none_when_empty(self, capsys):
        d = MagicMock()
        d.list_ignored_files.return_value = []
        do_list_ignored_files(d, "/some/path")
        assert "No files are currently ignored" in capsys.readouterr().out


class TestBuildParser:
    def test_workers_default_is_4(self):
        p = build_parser()
        args = p.parse_args(["sync", "local/", "remote/"])
        assert args.workers == 4

    def test_workers_accepts_valid_value(self):
        p = build_parser()
        args = p.parse_args(["--workers", "8", "sync", "local/", "remote/"])
        assert args.workers == 8

    def test_workers_clamps_to_1_minimum(self):
        p = build_parser()
        args = p.parse_args(["--workers", "0", "sync", "local/"])
        assert args.workers >= 1

    def test_workers_clamps_to_32_maximum(self):
        p = build_parser()
        args = p.parse_args(["--workers", "100", "sync", "local/"])
        assert args.workers <= 32
