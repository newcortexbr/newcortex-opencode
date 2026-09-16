#!/usr/bin/env python3
"""Validate Obsidian wikilinks and exact duplicate note bodies in the vault."""
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1] / "vault"
WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})(?:[^\r\n]*)$")
FENCE_CLOSE = re.compile(r"^\s*(`{3,}|~{3,})[ \t]*(?:\r?\n)?$")
INLINE_CODE = re.compile(r"(?P<tick>`+)[^\n]*?(?P=tick)")
FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n.*?^---[ \t]*(?:\r?\n|\Z)", re.DOTALL | re.MULTILINE)


def find_notes(vault=VAULT):
    """Return every note indexed by its vault-relative path without ``.md``."""
    vault = Path(vault).resolve()
    return {
        path.relative_to(vault).with_suffix(""): path
        for path in sorted(vault.rglob("*.md"))
    }


def without_code(content):
    """Remove fenced and inline code so examples do not become wikilinks."""
    kept = []
    fence = None
    for line in content.splitlines(keepends=True):
        if fence:
            marker = FENCE_CLOSE.match(line)
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1]:
                fence = None
            continue
        marker = FENCE_OPEN.match(line)
        if marker:
            fence = (marker.group(1)[0], len(marker.group(1)))
            continue
        kept.append(INLINE_CODE.sub("", line))
    return "".join(kept)


def resolve_target(target, notes, vault):
    """Resolve a path link exactly, or a stem link only when it is unique."""
    vault = Path(vault).resolve()
    target_path = Path(target)
    if target_path.is_absolute():
        return None, "broken"

    if "/" in target or "\\" in target:
        target_file = target_path if target_path.suffix == ".md" else Path(f"{target_path}.md")
        candidate = (vault / target_file).resolve()
        try:
            candidate.relative_to(vault)
        except ValueError:
            return None, "broken"
        return (candidate, None) if candidate in notes.values() else (None, "broken")

    stem = target[:-3] if target.endswith(".md") else target
    matches = [path for rel, path in notes.items() if rel.name == stem]
    if len(matches) == 1:
        return matches[0], None
    return None, "ambiguous" if matches else "broken"


def check_links(vault=VAULT):
    vault = Path(vault).resolve()
    notes = find_notes(vault)
    broken = []
    ambiguous = []
    links = 0
    for path in notes.values():
        for match in WIKILINK.finditer(without_code(path.read_text())):
            links += 1
            target = match.group(1).strip()
            _, issue = resolve_target(target, notes, vault)
            if issue == "broken":
                broken.append((path, target))
            elif issue == "ambiguous":
                ambiguous.append((path, target))
    return broken, ambiguous, notes, links


def normalized_body(content):
    """Strip only a complete frontmatter block, then normalize whitespace."""
    body = FRONTMATTER.sub("", content, count=1)
    return " ".join(body.split())


def check_duplicates(vault=VAULT):
    vault = Path(vault).resolve()
    duplicates = {}
    for rel, path in find_notes(vault).items():
        body = normalized_body(path.read_text())
        if body:
            duplicates.setdefault(body, []).append((rel, path))
    return {body: entries for body, entries in duplicates.items() if len(entries) > 1}


def safe_text(value):
    """Render diagnostics without emitting terminal control characters."""
    return ascii(str(value))[1:-1]


def main(vault=VAULT):
    vault = Path(vault).resolve()
    broken, ambiguous, notes, links = check_links(vault)
    duplicates = check_duplicates(vault)
    print(f"{len(notes)} notes; {links} links; {len(duplicates)} duplicate groups")

    if broken:
        print("BROKEN LINKS:")
        for path, target in broken:
            print(f"  {safe_text(path.relative_to(vault))} -> [[{safe_text(target)}]] (not found)")
    if ambiguous:
        print("AMBIGUOUS LINKS:")
        for path, target in ambiguous:
            print(f"  {safe_text(path.relative_to(vault))} -> [[{safe_text(target)}]] (multiple notes share this stem)")
    if duplicates:
        print("POTENTIAL DUPLICATES:")
        for entries in duplicates.values():
            paths = [safe_text(path.relative_to(vault)) for _, path in entries]
            print(f"  paths: {paths}")

    if not broken and not ambiguous and not duplicates:
        print("All links resolved; no duplicate bodies found")
    return 1 if broken or ambiguous or duplicates else 0


if __name__ == "__main__":
    sys.exit(main())
