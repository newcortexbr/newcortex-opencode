#!/usr/bin/env python3
"""Check resolved agent rules without reading protected files or calling models.

Pattern simulation covers only simple configured globs, not all runtime semantics,
absolute-path normalization, search tools, or shell behavior. CLI diagnostics can
initialize local plugin/cache state; raw diagnostic output is not logged.
"""
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = {"coder", "tasker", "designer", "leader"}
READ_ONLY_SUBAGENTS = {"reviewer", "explorer", "summarizer"}
VAULT_WRITERS = PRIMARY | {"coder-basic", "coder-plus", "coder-pro"}
VAULT_ROOT = "/home/dasher/projects/opencode-prefs-v2/vault"
failures = []


def check(condition, label):
    if not condition:
        failures.append(label)
        print("FAIL", label)


def action(agent, tool, target):
    result = "ask"
    for rule in agent["permission"]:
        if fnmatch.fnmatchcase(tool, rule["permission"]) and fnmatch.fnmatchcase(target, rule["pattern"]):
            result = rule["action"]
    return result


def get_agent(name):
    try:
        proc = subprocess.run([str(ROOT / "opencode-isolated"), "debug", "agent", name],
                              cwd=ROOT, capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired:
        raise ValueError(f"debug agent {name} timed out") from None
    except OSError:
        raise ValueError(f"debug agent {name} could not run") from None
    if proc.returncode:
        raise ValueError(f"debug agent {name} returned non-zero")
    try:
        agent = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise ValueError(f"debug agent {name} returned invalid JSON") from None
    if not isinstance(agent, dict) or not isinstance(agent.get("permission"), list):
        raise ValueError(f"debug agent {name} returned unexpected JSON shape")
    if any(
        not isinstance(rule, dict)
        or not all(isinstance(rule.get(field), str) for field in ("permission", "pattern", "action"))
        for rule in agent["permission"]
    ):
        raise ValueError(f"debug agent {name} returned invalid permission rules")
    return agent


def test_basic_agent(name, agent):
    check(agent["name"] == name, f"{name}: identity")
    protected = ("pessoal/probe.txt", "conversa-probe.json", "demo/.env", "demo/.env.local", "demo/auth.json")
    for path in protected:
        check(action(agent, "read", path) == "deny", f"{name}: deny read {path}")
    if name in PRIMARY:
        check(agent["mode"] == "primary" and not agent.get("model"), f"{name}: primary/model")
        check(action(agent, "question", "*") == "allow", f"{name}: question")
        if name in {"coder", "tasker", "designer"}:
            check(action(agent, "bash", "gh pr merge 123") == "ask", f"{name}: gh pr merge asks")
    else:
        check(agent["mode"] == "subagent" and bool(agent.get("model")), f"{name}: fixed model")
        check(action(agent, "task", "coder") == "deny", f"{name}: delegation denied")
    if name in READ_ONLY_SUBAGENTS:
        for tool in ("bash", "edit", "write", "task"):
            check(action(agent, tool, "probe") == "deny", f"{name}: {tool} denied")


def test_shell_bypass(agent, name):
    """Risco conhecido: denies de read não bloqueiam bash 'cat /pessoal/secret'."""
    protected_files = [
        "/pessoal/probe.txt",
        "/conversa-probe.json",
        "/demo/.env",
    ]
    for f in protected_files:
        bash_action = action(agent, "bash", f"cat {f}")
        if bash_action == "allow":
            print(f"RISK {name}: bash can read {f} (read rules don't block shell)")


def test_vault_boundary(agent, name):
    """Check explicit vault edit/write rules; this remains a permission-map probe."""
    human_paths = (
        "vault/human/probe.md",
        f"{VAULT_ROOT}/human/probe.md",
    )
    agent_paths = (
        "vault/agents/00-index.md",
        f"{VAULT_ROOT}/agents/00-index.md",
    )
    legacy_paths = (
        "vault/conceitos/probe.md",
        f"{VAULT_ROOT}/conceitos/probe.md",
    )

    for path in human_paths:
        check(action(agent, "read", path) == "allow", f"{name}: read human data {path}")
    for path in human_paths + legacy_paths:
        for tool in ("edit", "write"):
            check(action(agent, tool, path) == "deny", f"{name}: deny {tool} {path}")
    expected = "allow" if name in VAULT_WRITERS else "deny"
    for path in agent_paths:
        for tool in ("edit", "write"):
            check(action(agent, tool, path) == expected, f"{name}: {expected} {tool} {path}")


def test_project_config_precedence():
    """Fail closed when the project-config diagnostic cannot prove the fixture."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "opencode.json").write_text(json.dumps({
            "$schema": "https://opencode.ai/config.json",
            "agent": {"build": {"disable": False}, "custom-agent": {"mode": "primary"}}
        }))
        (tmp / "AGENTS.md").write_text("# Projeto Teste\nContrato local.")
        
        env = os.environ.copy()
        env["OPENCODE_CONFIG_DIR"] = str(ROOT / "v2")
        try:
            proc = subprocess.run(
                [str(ROOT / "opencode-isolated"), "debug", "config"],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env
            )
        except subprocess.TimeoutExpired:
            check(False, "project config precedence: diagnostic timed out")
            return
        except OSError:
            check(False, "project config precedence: diagnostic could not run")
            return

        if proc.returncode:
            check(False, f"project config precedence: diagnostic failed (return code {proc.returncode})")
            return

        try:
            cfg = json.loads(proc.stdout)
        except json.JSONDecodeError:
            check(False, "project config precedence: diagnostic returned invalid JSON")
            return

        if not isinstance(cfg, dict) or not isinstance(cfg.get("agent"), dict):
            check(False, "project config precedence: diagnostic returned unexpected JSON shape")
            return

        agents = cfg["agent"]
        if not isinstance(agents.get("custom-agent"), dict):
            check(False, "project config precedence: fixture custom-agent missing")
            return

        build_cfg = agents.get("build")
        if not isinstance(build_cfg, dict):
            check(False, "project config precedence: build configuration missing")
            return

        if build_cfg.get("disable") is not True:
            check(False, "project config precedence: build was enabled by local opencode.json (V2 lost)")
            print("RISK project config mescla e pode sobrepor V2")
        print("CHECKED project config precedence test")


def main():
    failures.clear()
    config = json.loads((ROOT / "v2/opencode.json").read_text())
    check(config["default_agent"] == "coder", "default agent")
    check(config["mcp"]["exa"]["enabled"] is False, "Exa disabled")
    for name in ("build", "plan", "general", "explore"):
        check(config["agent"][name]["disable"] is True, f"disabled {name}")
    
    files = sorted((ROOT / "v2/agent").glob("*.md"))
    names = {file.stem for file in files}
    check(len(files) == 10, "10 custom agents")
    check(names == PRIMARY | VAULT_WRITERS | READ_ONLY_SUBAGENTS, "expected agent roster")
    check(not any("-gpt" in name or "-claude" in name for name in names), "no provider-suffixed agents")
    
    for file in files:
        name = file.stem
        try:
            agent = get_agent(name)
            test_basic_agent(name, agent)
            test_shell_bypass(agent, name)
            test_vault_boundary(agent, name)
            print("CHECKED", name)
        except (ValueError, KeyError):
            check(False, f"{name}: unable to decode diagnostic")
    
    test_project_config_precedence()
    
    print(f"{len(files)} agents; {len(failures)} failures. No model calls; not a sandbox test.")
    print("RISK: read denies don't block shell commands (cat/tee/cp on protected paths).")
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
