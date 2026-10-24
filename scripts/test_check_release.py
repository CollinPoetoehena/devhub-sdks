"""Regression tests for release isolation, metadata consistency, and invalid tags."""

import tempfile
import unittest
from pathlib import Path

from check_release import MODULE, validate_release


class ReleaseTests(unittest.TestCase):
    """Exercise release validation without accessing GitHub or a registry."""

    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "python").mkdir()
        (self.root / "go").mkdir()
        (self.root / "python/pyproject.toml").write_text(
            '[project]\nversion = "0.1.0"\n', encoding="utf-8"
        )
        (self.root / "go/go.mod").write_text(f"module {MODULE}\n\ngo 1.25.0\n", encoding="utf-8")

    def test_independent_versions(self) -> None:
        self.assertEqual(validate_release(self.root, "python/v0.1.0"), "python")
        self.assertEqual(validate_release(self.root, "go/v1.2.3"), "go")

    def test_python_metadata_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "differs from Python version"):
            validate_release(self.root, "python/v0.2.0")

    def test_invalid_tags(self) -> None:
        for tag in (
            "v0.1.0",
            "python/v01.0.0",
            "python/v0.1",
            "go/v1.2.3-extra",
            "python/v0.1.0\n",
            "rust/v0.1.0",
            "python/v0.1.0/extra",
        ):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "Expected"):
                validate_release(self.root, tag)

    def test_go_major_migration_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "module-path"):
            validate_release(self.root, "go/v2.0.0")

    def test_wrong_go_module(self) -> None:
        (self.root / "go/go.mod").write_text("module example.com/wrong\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Expected Go module"):
            validate_release(self.root, "go/v0.1.0")


if __name__ == "__main__":
    unittest.main()
