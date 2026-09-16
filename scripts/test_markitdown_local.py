#!/usr/bin/env python3
"""Synthetic tests for the MarkItDown local-entrypoint policy."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest


SCRIPT = Path(__file__).with_name("markitdown-local.py")
WRAPPER = Path(__file__).with_name("markitdown-local.sh")


class MarkItDownLocalTests(unittest.TestCase):
    def load_script(self, telemetry_value: str | None) -> tuple[types.ModuleType, list[str]]:
        previous = os.environ.get("ORT_DISABLE_TELEMETRY")
        if telemetry_value is None:
            os.environ.pop("ORT_DISABLE_TELEMETRY", None)
        else:
            os.environ["ORT_DISABLE_TELEMETRY"] = telemetry_value

        seen: list[str] = []
        fake_markitdown = types.ModuleType("markitdown")

        class FakeMarkItDown:
            initializations: list[bool] = []
            converted: list[Path] = []

            def __init__(self, *, enable_plugins: bool) -> None:
                self.enable_plugins = enable_plugins
                self.initializations.append(enable_plugins)

            def convert_local(self, path: Path) -> object:
                self.converted.append(path)
                return types.SimpleNamespace(markdown="synthetic markdown")

        def record_import() -> type[FakeMarkItDown]:
            seen.append(os.environ.get("ORT_DISABLE_TELEMETRY", ""))
            return FakeMarkItDown

        fake_markitdown.__getattr__ = lambda name: record_import() if name == "MarkItDown" else None
        original = sys.modules.get("markitdown")
        sys.modules["markitdown"] = fake_markitdown
        try:
            spec = importlib.util.spec_from_file_location("markitdown_local_test", SCRIPT)
            self.assertIsNotNone(spec)
            module = importlib.util.module_from_spec(spec)
            self.assertIsNotNone(spec.loader)
            spec.loader.exec_module(module)
        finally:
            if original is None:
                del sys.modules["markitdown"]
            else:
                sys.modules["markitdown"] = original
            if previous is None:
                os.environ.pop("ORT_DISABLE_TELEMETRY", None)
            else:
                os.environ["ORT_DISABLE_TELEMETRY"] = previous
        return module, seen

    def run_main(self, module: types.ModuleType, *arguments: str) -> tuple[int, str, str]:
        original_argv = sys.argv
        stdout = io.StringIO()
        stderr = io.StringIO()
        sys.argv = [str(SCRIPT), *arguments]
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    status = module.main()
                except SystemExit as exc:
                    status = exc.code
        finally:
            sys.argv = original_argv
        return status, stdout.getvalue(), stderr.getvalue()

    def test_telemetry_is_forced_before_import_when_absent(self) -> None:
        _, seen = self.load_script(None)
        self.assertTrue(seen)
        self.assertTrue(all(value == "1" for value in seen))

    def test_telemetry_is_forced_before_import_when_inherited_as_zero(self) -> None:
        _, seen = self.load_script("0")
        self.assertTrue(seen)
        self.assertTrue(all(value == "1" for value in seen))

    def test_rejections_do_not_use_the_real_package(self) -> None:
        module, seen = self.load_script(None)
        self.assertTrue(seen)
        self.assertTrue(all(value == "1" for value in seen))
        for argument in ("https://example.invalid/file.txt", "-", "--use-plugins"):
            with self.subTest(argument=argument):
                status, stdout, stderr = self.run_main(module, argument)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertIn("error:", stderr)
        self.assertEqual(module.MarkItDown.converted, [])

    def test_local_file_uses_plugins_disabled(self) -> None:
        module, _ = self.load_script(None)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.txt"
            path.write_text("fixture", encoding="utf-8")
            status, stdout, stderr = self.run_main(module, str(path))
        self.assertEqual(status, 0)
        self.assertEqual(stdout, "synthetic markdown\n")
        self.assertEqual(stderr, "")
        self.assertEqual(module.MarkItDown.initializations, [False])

    def test_wrapper_forces_telemetry(self) -> None:
        wrapper = WRAPPER.read_text(encoding="utf-8")
        self.assertIn("ORT_DISABLE_TELEMETRY=1", wrapper)


if __name__ == "__main__":
    unittest.main()
