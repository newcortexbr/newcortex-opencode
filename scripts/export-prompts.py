#!/usr/bin/env python3
"""Exporta os prompts vigentes da V2 para docs/PROMPTS.md.

Fonte da verdade é a configuracao resolvida pelo launcher (`debug agent`), nao o
texto dos arquivos: assim o export reflete overrides de modelo/effort e a
composicao real, e nao o que alguem supos estar valendo.

Nao exporta prompt interno da plataforma nem segredo: apenas o que este projeto
define em `v2/kernel.md`, `v2/agent/*.md` e `.opencode/command/`.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = ROOT / "opencode-isolated"
OUT = ROOT / "docs" / "PROMPTS.md"
TIMEOUT = 120

ORDER = ["tasker", "coder", "designer", "leader",
         "coder-basic", "coder-plus", "coder-pro",
         "explorer", "summarizer", "reviewer"]


def debug_agent(name):
    try:
        raw = subprocess.run([str(LAUNCHER), "debug", "agent", name],
                             capture_output=True, timeout=TIMEOUT, cwd=ROOT)
    except subprocess.SubprocessError:
        return None
    if raw.returncode != 0:
        return None
    try:
        return json.loads(raw.stdout.decode("utf-8", "replace"))
    except ValueError:
        return None


def model_label(agent):
    """Primario sem modelo fixo herda o que estiver selecionado na sessao."""
    model = agent.get("model") or {}
    pid, mid = model.get("providerID"), model.get("modelID")
    if not pid or not mid:
        return "(herda da sessao)"
    return "`%s/%s`" % (pid, mid)


def enabled_tools(agent):
    tools = agent.get("tools") or {}
    return sorted(k for k, v in tools.items() if v is True)


def main():
    if not LAUNCHER.is_file():
        print("launcher nao encontrado", file=sys.stderr)
        return 1

    agents = []
    for name in ORDER:
        data = debug_agent(name)
        if data is None:
            print(f"aviso: {name} nao resolvido; omitido", file=sys.stderr)
            continue
        agents.append(data)
    if not agents:
        print("nenhum agente resolvido", file=sys.stderr)
        return 1

    lines = [
        "# Prompts vigentes da V2",
        "",
        "Gerado por `scripts/export-prompts.py` a partir da configuracao resolvida",
        "pelo launcher isolado. Nao editar a mao: altere `v2/kernel.md` ou",
        "`v2/agent/<nome>.md` e rode o script de novo.",
        "",
        "Modelo e effort refletem overrides de `subconfig` no momento da geracao.",
        "Este documento cobre apenas o que este projeto define; nao reproduz o",
        "prompt interno da plataforma.",
        "",
        "## Kernel",
        "",
        "Carregado como `instructions` para toda sessao desta instalacao.",
        "",
        "```markdown",
        (ROOT / "v2" / "kernel.md").read_text().rstrip(),
        "```",
        "",
        "## Agentes",
        "",
        "| agente | modo | modelo | effort | ferramentas habilitadas |",
        "| --- | --- | --- | --- | --- |",
    ]

    for a in agents:
        lines.append("| `%s` | %s | %s | %s | %d |" % (
            a.get("name", "?"), a.get("mode", "?"), model_label(a),
            a.get("variant") or "-", len(enabled_tools(a))))

    for a in agents:
        lines += [
            "",
            "### `%s`" % a.get("name", "?"),
            "",
            "- modo: %s" % a.get("mode", "?"),
            "- modelo: %s, effort `%s`" % (model_label(a), a.get("variant") or "-"),
            "- descricao: %s" % (a.get("description") or "-"),
            "- ferramentas habilitadas: %s" % (
                ", ".join("`%s`" % t for t in enabled_tools(a)) or "nenhuma"),
            "",
            "```markdown",
            (a.get("prompt") or "").rstrip(),
            "```",
        ]

    commands = sorted((ROOT / ".opencode" / "command").glob("*.md"))
    if commands:
        lines += ["", "## Commands de projeto", ""]
        for c in commands:
            lines += ["### `/%s`" % c.stem, "", "```markdown",
                      c.read_text().rstrip(), "```", ""]

    OUT.write_text("\n".join(lines).rstrip() + "\n")
    print(f"{OUT.relative_to(ROOT)}: {len(agents)} agentes, {OUT.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
