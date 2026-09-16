#!/usr/bin/env python3
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vault_links", ROOT / "scripts" / "vault-links.py")
vault_links = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vault_links)


class VaultLinksTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(dir=ROOT)
        self.vault = Path(self.tempdir.name) / "vault"
        self.vault.mkdir()

    def tearDown(self):
        self.tempdir.cleanup()

    def write(self, relative, content):
        path = self.vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def test_homonyms_are_preserved_and_stem_link_is_ambiguous(self):
        self.write("one/topic.md", "one")
        self.write("two/topic.md", "two")
        self.write("source.md", "[[topic]]")
        notes = vault_links.find_notes(self.vault)
        self.assertEqual(set(notes), {Path("one/topic"), Path("two/topic"), Path("source")})
        broken, ambiguous, _, links = vault_links.check_links(self.vault)
        self.assertEqual(broken, [])
        self.assertEqual(links, 1)
        self.assertEqual([(path.name, target) for path, target in ambiguous], [("source.md", "topic")])

    def test_explicit_path_and_alias_resolve(self):
        self.write("one/topic.md", "one")
        self.write("source.md", "[[one/topic]] [[one/topic|shown alias]]")
        broken, ambiguous, _, links = vault_links.check_links(self.vault)
        self.assertEqual((broken, ambiguous, links), ([], [], 2))

    def test_path_and_stem_with_dots_resolve_from_a_relative_root(self):
        self.write("conceitos/open-code-1.18.30-retry.md", "target")
        self.write("source.md", "[[conceitos/open-code-1.18.30-retry]] [[conceitos/open-code-1.18.30-retry.md]] [[open-code-1.18.30-retry]] [[open-code-1.18.30-retry.md]]")
        relative_vault = self.vault.relative_to(ROOT)
        notes = vault_links.find_notes(relative_vault)
        self.assertTrue(all(path.is_absolute() for path in notes.values()))
        broken, ambiguous, _, links = vault_links.check_links(relative_vault)
        self.assertEqual((broken, ambiguous, links), ([], [], 4))

    def test_path_link_cannot_escape_the_vault(self):
        self.write("source.md", "[[../outside]]")
        broken, ambiguous, _, links = vault_links.check_links(self.vault)
        self.assertEqual((ambiguous, links), ([], 1))
        self.assertEqual([(path.name, target) for path, target in broken], [("source.md", "../outside")])

    def test_code_examples_are_ignored(self):
        self.write("target.md", "target")
        self.write("source.md", "`[[missing-inline]]`\n```md\n[[missing-fenced]]\n```python\n[[still-fenced]]\n```\n~~~\n[[missing-tilde]]\n~~~\n[[target]]")
        broken, ambiguous, _, links = vault_links.check_links(self.vault)
        self.assertEqual((broken, ambiguous, links), ([], [], 1))

    def test_duplicate_comparison_uses_full_normalized_body(self):
        prefix = "x" * 500
        self.write("first.md", f"---\ntitle: first\n---\n{prefix} one")
        self.write("second.md", f"---\ntitle: second\n---\n{prefix} two")
        self.write("third.md", "alpha   beta\n")
        self.write("fourth.md", " alpha beta ")
        duplicates = vault_links.check_duplicates(self.vault)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual({path.name for _, path in next(iter(duplicates.values()))}, {"third.md", "fourth.md"})

    def test_only_complete_frontmatter_is_removed_and_empty_bodies_are_ignored(self):
        self.write("one.md", "---\ntitle: one\n---\nbody")
        self.write("two.md", "---\ntitle: two\n---\nbody")
        self.write("empty-one.md", "---\ntitle: one\n---\n")
        self.write("empty-two.md", "---\ntitle: two\n---\n")
        self.write("invalid.md", "---\ntitle: invalid\nbody")
        duplicates = vault_links.check_duplicates(self.vault)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual({path.name for _, path in next(iter(duplicates.values()))}, {"one.md", "two.md"})

    def test_main_exit_codes_cover_broken_ambiguous_and_duplicate(self):
        self.write("broken.md", "[[missing]]")
        self.assertEqual(vault_links.main(self.vault), 1)
        (self.vault / "broken.md").unlink()
        self.write("one/topic.md", "one")
        self.write("two/topic.md", "two")
        self.write("ambiguous.md", "[[topic]]")
        self.assertEqual(vault_links.main(self.vault), 1)
        (self.vault / "ambiguous.md").unlink()
        self.write("duplicate-one.md", "same")
        self.write("duplicate-two.md", "same")
        self.assertEqual(vault_links.main(self.vault), 1)
        (self.vault / "duplicate-two.md").unlink()
        self.assertEqual(vault_links.main(self.vault), 0)

    def test_diagnostic_escapes_control_characters(self):
        self.write("source.md", "[[bad\x1b[31m-target]]")
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(vault_links.main(self.vault), 1)
        self.assertNotIn("\x1b", output.getvalue())
        self.assertIn("\\x1b", output.getvalue())


if __name__ == "__main__":
    unittest.main()
