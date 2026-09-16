#!/usr/bin/env python3
"""Deterministic unit tests for check-v2 diagnostic handling."""
import contextlib
import importlib.util
import io
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("check_v2", "scripts/check-v2.py")
check_v2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_v2)


class ProjectConfigPrecedenceTests(unittest.TestCase):
    def run_diagnostic(self, result=None, error=None):
        check_v2.failures.clear()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch.object(check_v2.subprocess, "run", side_effect=error or [result]):
                check_v2.test_project_config_precedence()
        return list(check_v2.failures), output.getvalue()

    def test_nonzero_return_is_a_sanitized_failure(self):
        failures, output = self.run_diagnostic(
            SimpleNamespace(returncode=7, stdout="untrusted stdout", stderr="untrusted stderr")
        )
        self.assertEqual(failures, ["project config precedence: diagnostic failed (return code 7)"])
        self.assertNotIn("untrusted", output)

    def test_timeout_is_a_sanitized_failure(self):
        failures, output = self.run_diagnostic(
            error=subprocess.TimeoutExpired(["opencode-isolated"], 60, output="untrusted stdout", stderr="untrusted stderr")
        )
        self.assertEqual(failures, ["project config precedence: diagnostic timed out"])
        self.assertNotIn("untrusted", output)

    def test_subprocess_error_is_a_sanitized_failure(self):
        failures, output = self.run_diagnostic(error=OSError("untrusted diagnostic error"))
        self.assertEqual(failures, ["project config precedence: diagnostic could not run"])
        self.assertNotIn("untrusted", output)

    def test_invalid_json_is_a_sanitized_failure(self):
        failures, output = self.run_diagnostic(SimpleNamespace(returncode=0, stdout="not json", stderr="untrusted stderr"))
        self.assertEqual(failures, ["project config precedence: diagnostic returned invalid JSON"])
        self.assertNotIn("untrusted", output)

    def test_unexpected_json_shape_is_a_failure(self):
        failures, _ = self.run_diagnostic(SimpleNamespace(returncode=0, stdout="[]", stderr=""))
        self.assertEqual(failures, ["project config precedence: diagnostic returned unexpected JSON shape"])

    def test_missing_fixture_agent_is_a_failure(self):
        failures, _ = self.run_diagnostic(
            SimpleNamespace(returncode=0, stdout='{"agent": {"build": {"disable": true}}}', stderr="")
        )
        self.assertEqual(failures, ["project config precedence: fixture custom-agent missing"])

    def test_baseline_build_disable_must_be_preserved(self):
        failures, output = self.run_diagnostic(
            SimpleNamespace(
                returncode=0,
                stdout='{"agent": {"build": {"disable": false}, "custom-agent": {}}}',
                stderr="",
            )
        )
        self.assertEqual(failures, ["project config precedence: build was enabled by local opencode.json (V2 lost)"])
        self.assertIn("RISK project config mescla e pode sobrepor V2", output)

    def test_success_proves_fixture_and_preserves_baseline(self):
        failures, output = self.run_diagnostic(
            SimpleNamespace(
                returncode=0,
                stdout='{"agent": {"build": {"disable": true}, "custom-agent": {"mode": "primary"}}}',
                stderr="",
            )
        )
        self.assertEqual(failures, [])
        self.assertIn("CHECKED project config precedence test", output)

    def test_multiple_calls_do_not_contaminate_failures(self):
        failed, _ = self.run_diagnostic(SimpleNamespace(returncode=0, stdout="not json", stderr=""))
        succeeded, _ = self.run_diagnostic(
            SimpleNamespace(
                returncode=0,
                stdout='{"agent": {"build": {"disable": true}, "custom-agent": {}}}',
                stderr="",
            )
        )
        self.assertEqual(failed, ["project config precedence: diagnostic returned invalid JSON"])
        self.assertEqual(succeeded, [])


class AgentDiagnosticTests(unittest.TestCase):
    def get_agent_error(self, result=None, error=None):
        with patch.object(check_v2.subprocess, "run", side_effect=error or [result]):
            with self.assertRaises(ValueError) as raised:
                check_v2.get_agent("synthetic-agent")
        return str(raised.exception)

    def test_agent_nonzero_does_not_expose_diagnostic_output(self):
        error = self.get_agent_error(
            SimpleNamespace(returncode=9, stdout="SYNTHETIC_STDOUT", stderr="SYNTHETIC_STDERR")
        )
        self.assertEqual(error, "debug agent synthetic-agent returned non-zero")
        self.assertNotIn("SYNTHETIC_STDOUT", error)
        self.assertNotIn("SYNTHETIC_STDERR", error)

    def test_agent_invalid_json_does_not_expose_diagnostic_output(self):
        error = self.get_agent_error(
            SimpleNamespace(returncode=0, stdout="SYNTHETIC_STDOUT", stderr="SYNTHETIC_STDERR")
        )
        self.assertEqual(error, "debug agent synthetic-agent returned invalid JSON")
        self.assertNotIn("SYNTHETIC_STDOUT", error)
        self.assertNotIn("SYNTHETIC_STDERR", error)

    def test_agent_invalid_permission_shape_fails(self):
        error = self.get_agent_error(
            SimpleNamespace(returncode=0, stdout='{"permission": [{"permission": "read"}]}', stderr="")
        )
        self.assertEqual(error, "debug agent synthetic-agent returned invalid permission rules")

    def test_main_clears_previous_failures_and_sanitizes_agent_error(self):
        check_v2.failures[:] = ["previous failure"]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch.object(check_v2, "get_agent", side_effect=ValueError("synthetic stderr")):
                with patch.object(check_v2, "test_project_config_precedence"):
                    check_v2.main()
        self.assertNotIn("previous failure", check_v2.failures)
        self.assertNotIn("synthetic stderr", output.getvalue())
        self.assertIn("coder: unable to decode diagnostic", check_v2.failures)
        check_v2.failures.clear()


class VaultBoundaryTests(unittest.TestCase):
    def mock_agent(self, writable):
        rules = [
            {"permission": "read", "pattern": "*", "action": "allow"},
            {"permission": "edit", "pattern": "*", "action": "deny"},
            {"permission": "write", "pattern": "*", "action": "deny"},
        ]
        if writable:
            for tool in ("edit", "write"):
                rules.extend([
                    {"permission": tool, "pattern": "vault/agents/**", "action": "allow"},
                    {"permission": tool, "pattern": "/home/dasher/projects/opencode-prefs-v2/vault/agents/**", "action": "allow"},
                ])
        return {"permission": rules}

    def assert_boundary(self, name, writable):
        check_v2.failures.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            check_v2.test_vault_boundary(self.mock_agent(writable), name)
        self.assertEqual(check_v2.failures, [])

    def test_writer_allows_agent_paths_and_denies_human_relative_and_absolute(self):
        self.assert_boundary("coder-basic", writable=True)

    def test_read_only_denies_agent_and_human_writes_relative_and_absolute(self):
        self.assert_boundary("reviewer", writable=False)


if __name__ == "__main__":
    unittest.main()
