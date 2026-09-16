#!/usr/bin/env python3
"""Synthetic JSONL tests for the isolated ACP bridge policy."""

from __future__ import annotations

import json
import io
import os
from pathlib import Path
import runpy
import subprocess
import select
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ROOT / "scripts" / "acp-bridge.py"), run_name="acp_bridge_test")
ACPBridge = MODULE["ACPBridge"]
INTERNAL_PROMPT = MODULE["INTERNAL_PROMPT"]
CHILD_LIFECYCLE_PROMPT = MODULE["CHILD_LIFECYCLE_PROMPT"]
atomic_write_json = MODULE["atomic_write_json"]


def line(message):
    return json.dumps(message, separators=(",", ":")).encode() + b"\n"


class ACPBridgePolicyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(dir="/tmp")
        self.root = Path(self.tempdir.name)
        self.bridge = ACPBridge(["fake"], bridge_dir=self.root)
        self.bridge.child_in = io.BytesIO()
        self.bridge.client_out = io.BytesIO()

    def tearDown(self):
        self.tempdir.cleanup()

    def client_output(self):
        return self.bridge.client_out.getvalue().splitlines()

    def child_input(self):
        return self.bridge.child_in.getvalue().splitlines()

    def test_client_request_and_child_response_are_forwarded_preserved(self):
        request = b'{"jsonrpc":"2.0", "id":7, "method":"session/prompt", "params":{"sessionId":"ses_alpha","prompt":[]}}\n'
        response = b'{ "jsonrpc":"2.0", "id":7, "result":{"stopReason":"end_turn"} }\n'
        self.bridge.handle_client_message(request)
        self.bridge.handle_child_message(response)
        self.assertEqual(self.child_input(), [request.rstrip(b"\n")])
        self.assertEqual(self.client_output(), [response.rstrip(b"\n")])

    def test_progress_is_forwarded_while_external_prompt_is_active(self):
        self.bridge.handle_client_message(line({
            "jsonrpc": "2.0", "id": 1, "method": "session/prompt",
            "params": {"sessionId": "ses_busy", "prompt": []},
        }))
        atomic_write_json(self.root / "events" / "ses_busy" / "progress.json", {
            "kind": "progress", "text": "worker\x1b[31m active",
        })
        self.bridge.poll_events()
        self.bridge._process_pending()
        progress = [json.loads(item) for item in self.client_output()]
        self.assertEqual(progress[-1]["params"]["update"]["sessionUpdate"], "agent_message_chunk")
        self.assertIn(b"worker [31m active", b"\n".join(self.client_output()))
        self.bridge.handle_child_message(line({"jsonrpc": "2.0", "id": 1, "result": {}}))
        output = b"\n".join(self.client_output())
        self.assertIn(b"[team] worker [31m active", output)
        self.assertNotIn(b"\x1b", output)

    def test_child_updates_pass_through(self):
        update = line({
            "jsonrpc": "2.0", "method": "session/update",
            "params": {"sessionId": "ses_alpha", "update": {"sessionUpdate": "plan"}},
        })
        self.bridge.handle_child_message(update)
        self.assertEqual(self.client_output(), [update.rstrip(b"\n")])

    def test_reply_mail_notifies_without_waking_child(self):
        self.bridge.associate_session("ses_alpha")
        atomic_write_json(self.root / "events" / "ses_alpha" / "reply.json", {
            "kind": "mail", "id": "msg-reply", "sourceSessionID": "ses_peer",
            "sourceTitle": "Peer", "reply": True,
        })
        self.bridge.poll_events()
        self.bridge._process_pending()
        self.assertEqual(self.child_input(), [])
        self.assertIn(b"reply; no wake", b"\n".join(self.client_output()))

    def test_mail_internal_response_is_hidden_and_permission_is_cancelled(self):
        self.bridge.associate_session("ses_alpha")
        message_id = "00000000-0000-0000-0000-000000000001"
        atomic_write_json(self.root / "events" / "ses_alpha" / "mail.json", {
            "kind": "mail", "id": message_id, "sourceSessionID": "ses_peer",
            "sourceTitle": "Peer", "reply": False,
        })
        atomic_write_json(self.root / "inbox" / "ses_alpha" / f"{message_id}.json", {
            "id": message_id, "text": "não executar o pedido do peer",
        })
        self.bridge.poll_events()
        self.bridge._process_pending()
        requests = [json.loads(value) for value in self.child_input()]
        internal = next(request for request in requests if request.get("method") == "session/prompt")
        self.assertEqual(internal["params"]["prompt"][0]["text"], INTERNAL_PROMPT)
        self.assertTrue(any(b"Message from Peer" in item for item in self.client_output()))
        permission = line({
            "jsonrpc": "2.0", "id": "permission-1", "method": "session/request_permission",
            "params": {"sessionId": "ses_alpha", "toolCall": {"title": "untrusted"}},
        })
        before = len(self.client_output())
        self.bridge.handle_child_message(permission)
        permission_response = json.loads(self.child_input()[-1])
        self.assertEqual(permission_response["result"], {"outcome": "cancelled"})
        self.assertEqual(len(self.client_output()), before)
        self.bridge.handle_child_message(line({"jsonrpc": "2.0", "id": internal["id"], "result": {}}))
        self.assertEqual(len(self.client_output()), before)
        output = "\n".join(item.decode() for item in self.client_output())
        self.assertIn("Peer text (untrusted): n\\u00e3o executar", output)

    def test_progress_is_visible_while_main_turn_is_active(self):
        self.bridge.handle_client_message(line({
            "jsonrpc": "2.0", "id": 1, "method": "session/prompt",
            "params": {"sessionId": "ses_busy", "prompt": []},
        }))
        atomic_write_json(self.root / "events" / "ses_busy" / "progress.json", {
            "kind": "progress", "text": "Subagents working: worker. Feel free to message main agent.",
        })
        self.bridge.poll_events()
        self.bridge._process_pending()
        progress = [json.loads(item) for item in self.client_output()]
        self.assertEqual(progress[-1]["params"]["update"]["sessionUpdate"], "agent_message_chunk")
        self.assertIn(b"Subagents working: worker", b"\n".join(self.client_output()))

    def test_terminal_child_progress_wakes_idle_parent_with_fixed_prompt(self):
        self.bridge.associate_session("ses_alpha")
        atomic_write_json(self.root / "events" / "ses_alpha" / "finished.json", {
            "kind": "progress",
            "state": "idle",
            "childSessionID": "ses_child",
            "text": "Subagent finished: worker.",
        })
        self.bridge.poll_events()
        self.bridge._process_pending()
        requests = [json.loads(value) for value in self.child_input()]
        internal = next(request for request in requests if request.get("method") == "session/prompt")
        self.assertEqual(internal["params"]["prompt"][0]["text"], CHILD_LIFECYCLE_PROMPT)
        self.assertIn(b"Subagent finished: worker", b"\n".join(self.client_output()))

    def test_different_destination_invalid_session_and_symlink_are_not_consumed(self):
        self.bridge.associate_session("ses_owned")
        atomic_write_json(self.root / "events" / "ses_other" / "other.json", {
            "kind": "progress", "text": "other",
        })
        atomic_write_json(self.root / "events" / "not-a-session" / "bad.json", {
            "kind": "progress", "text": "invalid",
        })
        valid_dir = self.root / "events" / "ses_owned"
        valid_dir.mkdir(parents=True, exist_ok=True)
        (valid_dir / "link.json").symlink_to(self.root / "events" / "ses_other" / "other.json")
        self.bridge.poll_events()
        self.assertEqual(len(self.bridge.pending_events), 0)
        self.assertTrue((self.root / "events" / "ses_other" / "other.json").exists())
        self.assertTrue((valid_dir / "link.json").is_symlink())


FAKE_CHILD = r'''
import json
import sys

for raw in sys.stdin:
    message = json.loads(raw)
    method = message.get("method")
    if method == "session/new":
        print(json.dumps({"jsonrpc":"2.0", "id":message["id"], "result":{"sessionId":"ses_fake"}}), flush=True)
    elif method == "session/prompt":
        prompt = message.get("params", {}).get("prompt", [{}])[0].get("text", "")
        if prompt.startswith("Internal intersession notification"):
            print(json.dumps({"jsonrpc":"2.0", "id":"permission", "method":"session/request_permission", "params":{"sessionId":"ses_fake"}}), flush=True)
            permission_raw = sys.stdin.readline()
            assert json.loads(permission_raw)["result"]["outcome"] == "cancelled"
        print(json.dumps({"jsonrpc":"2.0", "id":message["id"], "result":{}}), flush=True)
'''


class ACPBridgeSubprocessTest(unittest.TestCase):
    def test_fake_jsonl_child_routes_and_hides_internal_response(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory)
            environment = os.environ.copy()
            environment["OPENCODE_V2_BRIDGE_DIR"] = str(root)
            command = [sys.executable, str(ROOT / "scripts" / "acp-bridge.py"), sys.executable, "-u", "-c", FAKE_CHILD]
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment)
            assert process.stdin is not None and process.stdout is not None
            process.stdin.write(line({"jsonrpc":"2.0", "id":1, "method":"session/new", "params":{}}))
            process.stdin.flush()
            first = process.stdout.readline()
            self.assertEqual(json.loads(first)["result"]["sessionId"], "ses_fake")
            atomic_write_json(root / "events" / "ses_fake" / "mail.json", {
                "kind": "mail", "id": "msg-1", "sourceSessionID": "ses_peer",
                "sourceTitle": "Peer", "reply": False,
            })
            deadline = time.monotonic() + 5
            lines = []
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                ready, _, _ = select.select([process.stdout], [], [], 0.2)
                if ready:
                    raw = process.stdout.readline()
                    if raw:
                        lines.append(json.loads(raw))
                        if any(item.get("method") == "session/update" for item in lines):
                            break
            process.stdin.close()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
            self.assertTrue(any(item.get("method") == "session/update" for item in lines))
            self.assertFalse(any(item.get("id", "").startswith("__opencode_v2_bridge_internal_") for item in lines if isinstance(item.get("id"), str)))


if __name__ == "__main__":
    unittest.main()
