#!/usr/bin/env python3
"""Local ACP smoke test for the team progress bridge."""

from __future__ import annotations

import json
from pathlib import Path
import select
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]


def send(process: subprocess.Popen[str], message: dict) -> None:
    assert process.stdin is not None
    process.stdin.write(json.dumps(message) + "\n")
    process.stdin.flush()


def read_until(process: subprocess.Popen[str], predicate, timeout: float) -> list[dict]:
    assert process.stdout is not None
    messages: list[dict] = []
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ready, _, _ = select.select([process.stdout], [], [], 0.5)
        if not ready:
            continue
        line = process.stdout.readline()
        if not line:
            break
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        messages.append(message)
        if predicate(message):
            break
    return messages


def main() -> int:
    process = subprocess.Popen(
        [str(ROOT / "opencode-isolated"), "acp"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        send(process, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": 1,
                "clientCapabilities": {},
                "clientInfo": {"name": "s05-smoke", "version": "1"},
            },
        })
        read_until(process, lambda message: message.get("id") == 1, 30)
        send(process, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "session/new",
            "params": {"cwd": str(ROOT), "mcpServers": []},
        })
        created = read_until(process, lambda message: message.get("id") == 2, 30)
        session_id = created[-1].get("result", {}).get("sessionId") if created else None
        if not isinstance(session_id, str):
            print("session/new failed")
            return 2

        send(process, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "session/set_config_option",
            "params": {
                "sessionId": session_id,
                "configId": "model",
                "value": "opencode/muse-spark-1.3-contributor-free",
            },
        })
        configured = read_until(process, lambda message: message.get("id") == 3, 30)
        if not configured or "error" in configured[-1]:
            print("model selection failed")
            return 3

        send(process, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "session/prompt",
            "params": {
                "sessionId": session_id,
                "messageId": "msg-s05-smoke",
                "prompt": [{
                    "type": "text",
                    "text": (
                        "Use exclusively team_spawn. Start one child named smoke-worker "
                        "using the configured agent explorer. Give it this prompt: respond "
                        "with the single word done. Do not choose a model directly or use "
                        "other tools. "
                        "After team_spawn returns, state the queued child id."
                    ),
                }],
            },
        })
        messages = read_until(process, lambda message: message.get("id") == 4, 240)
        updates = [message for message in messages if message.get("method") == "session/update"]
        progress = [
            message.get("params", {}).get("update", {}).get("content", {}).get("text", "")
            for message in updates
            if "Subagents working:" in json.dumps(message)
        ]
        progress_kinds = [
            message.get("params", {}).get("update", {}).get("sessionUpdate")
            for message in updates
            if "Subagents working:" in json.dumps(message)
        ]
        print(json.dumps({
            "sessionID": session_id,
            "messages": len(messages),
            "updates": len(updates),
            "progressSeen": bool(progress),
            "progress": progress[:3],
            "progressKinds": progress_kinds[:3],
            "promptStop": messages[-1].get("result", {}).get("stopReason") if messages else None,
        }, ensure_ascii=True))
        return 0 if progress and "agent_message_chunk" in progress_kinds else 4
    finally:
        if process.stdin is not None:
            process.stdin.close()
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
