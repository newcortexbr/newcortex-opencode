#!/usr/bin/env python3
"""Local A/B smoke test for sessions_send and ACP notification delivery."""

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


def read_messages(process: subprocess.Popen[str], count: int, timeout: float) -> list[dict]:
    assert process.stdout is not None
    messages: list[dict] = []
    deadline = time.monotonic() + timeout
    while len(messages) < count and time.monotonic() < deadline:
        ready, _, _ = select.select([process.stdout], [], [], 0.5)
        if not ready:
            continue
        line = process.stdout.readline()
        if not line:
            break
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return messages


def notification_text(message: dict) -> str:
    content = message.get("params", {}).get("update", {}).get("content", {})
    if isinstance(content, dict):
        return content.get("text", "") if isinstance(content.get("text"), str) else ""
    if isinstance(content, list):
        return " ".join(item.get("text", "") for item in content if isinstance(item, dict))
    return ""


def main() -> int:
    target = subprocess.Popen(
        [str(ROOT / "opencode-isolated"), "acp"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        send(target, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": 1, "clientCapabilities": {}, "clientInfo": {"name": "s04-target", "version": "1"}},
        })
        read_messages(target, 1, 30)
        send(target, {
            "jsonrpc": "2.0", "id": 2, "method": "session/new",
            "params": {"cwd": str(ROOT), "mcpServers": []},
        })
        created = read_messages(target, 1, 30)
        target_id = created[0].get("result", {}).get("sessionId") if created else None
        if not isinstance(target_id, str):
            print("target session creation failed")
            return 2
        time.sleep(1)
        registration_seen = False
        registration_dir = ROOT / ".opencode-local" / "state" / "session-bridge" / "registrations"
        for path in registration_dir.glob("*.json"):
            try:
                record = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if any(item.get("id") == target_id for item in record.get("sessions", [])):
                registration_seen = True
                break

        prompt = (
            "Use exclusively sessions_send, sem bash/read/edit/outras ferramentas. "
            f"Envie para a sessão {target_id} exatamente o texto TESTE_INTERSESSAO_A_B_2. "
            "Informe apenas o id queued retornado."
        )
        source = subprocess.run(
            [str(ROOT / "opencode-isolated"), "run", "--model", "opencode/muse-spark-1.3-contributor-free", "--agent", "coder", "--print-logs", prompt],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=180,
        )
        updates: list[dict] = []
        deadline = time.monotonic() + 10
        assert target.stdout is not None
        while time.monotonic() < deadline:
            ready, _, _ = select.select([target.stdout], [], [], 0.4)
            if not ready:
                continue
            line = target.stdout.readline()
            if not line:
                break
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("method") == "session/update":
                updates.append(message)
        texts = [notification_text(message) for message in updates]
        result = {
            "targetSessionID": target_id,
            "targetRegistered": registration_seen,
            "sourceStatus": source.returncode,
            "sourceToolUsed": "sessions_send" in (source.stdout + source.stderr),
            "sourceQueuedWord": "queued" in source.stdout,
            "sourceTail": source.stdout[-800:].replace("\x1b", ""),
            "targetUpdateCount": len(updates),
            "targetNoticeSeen": any("Message from" in text for text in texts),
            "targetNotice": next((text for text in texts if "Message from" in text), ""),
            "targetReceiveSeen": any("sessions_receive" in text for text in texts),
            "targetMarkerSeen": any("TESTE_INTERSESSAO_A_B_2" in text for text in texts),
        }
        print(json.dumps(result, ensure_ascii=True))
        return 0 if result["sourceStatus"] == 0 and result["sourceToolUsed"] and result["targetNoticeSeen"] else 3
    finally:
        if target.stdin is not None:
            target.stdin.close()
        target.terminate()
        try:
            target.wait(timeout=10)
        except subprocess.TimeoutExpired:
            target.kill()
            target.wait()


if __name__ == "__main__":
    raise SystemExit(main())
