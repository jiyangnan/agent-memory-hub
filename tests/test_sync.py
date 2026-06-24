import unittest
from pathlib import Path

from agent_memory.registry import register_agent
from agent_memory.setup import setup_workspace
from agent_memory.sync import (
    _condense_canonical,
    install_marker,
    render_shared_memory,
    sync_apply,
    sync_dry_run,
)


class SyncTests(unittest.TestCase):
    from contextlib import contextmanager
    import tempfile

    @contextmanager
    def tmpdir(self):
        with self.tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    def test_sync_dry_run_preserves_target_and_previews_managed_section(self):
        with self.tmpdir() as tmp:
            root = tmp / "repo"
            home = tmp / "home"
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            register_agent(root, machine="laptop", agent="codex", adapter="codex", primary_memory="~/.codex/memory/shared.md")
            (root / "memory" / "lessons.md").write_text("# Lessons\n\nShared rule.\n", encoding="utf-8")
            target = home / ".codex" / "memory" / "shared.md"
            target.parent.mkdir(parents=True)
            original = (
                "Before\n"
                "<!-- agent-memory-hub:BEGIN shared -->\n"
                "old\n"
                "<!-- agent-memory-hub:END shared -->\n"
                "After\n"
            )
            target.write_text(original, encoding="utf-8")

            result = sync_dry_run(root, home=home, machine="laptop", agent="codex")

            self.assertEqual(result["status"], "would_update")
            self.assertIn("Current receiver: `laptop/codex`", result["preview"])
            self.assertIn("Shared rule.", result["preview"])
            self.assertEqual(target.read_text(encoding="utf-8"), original)

    def test_install_marker_adds_managed_section_and_backup(self):
        with self.tmpdir() as tmp:
            root = tmp / "repo"
            home = tmp / "home"
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            register_agent(root, machine="laptop", agent="codex", adapter="codex", primary_memory="~/.codex/memory/shared.md")
            target = home / ".codex" / "memory" / "shared.md"
            target.parent.mkdir(parents=True)
            target.write_text("Local memory.\n", encoding="utf-8")

            result = install_marker(root, home=home, machine="laptop", agent="codex")

            text = target.read_text(encoding="utf-8")
            self.assertEqual(result["status"], "installed")
            self.assertIn("Local memory.", text)
            self.assertIn("agent-memory-hub:BEGIN shared", text)
            self.assertTrue(Path(result["backup_path"]).exists())

    def test_sync_apply_replaces_only_managed_section(self):
        with self.tmpdir() as tmp:
            root = tmp / "repo"
            home = tmp / "home"
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["hermes"])
            register_agent(root, machine="laptop", agent="hermes", adapter="hermes", primary_memory="~/.hermes/memories/MEMORY.md")
            (root / "memory" / "lessons.md").write_text("# Lessons\n\nNew shared lesson.\n", encoding="utf-8")
            target = home / ".hermes" / "memories" / "MEMORY.md"
            target.parent.mkdir(parents=True)
            target.write_text(
                "Before\n"
                "<!-- agent-memory-hub:BEGIN shared -->\n"
                "old\n"
                "<!-- agent-memory-hub:END shared -->\n"
                "After\n",
                encoding="utf-8",
            )

            result = sync_apply(root, home=home, machine="laptop", agent="hermes")

            text = target.read_text(encoding="utf-8")
            self.assertEqual(result["status"], "applied")
            self.assertIn("Before", text)
            self.assertIn("After", text)
            self.assertIn("Current receiver: `laptop/hermes`", text)
            self.assertIn("New shared lesson.", text)
            self.assertNotIn("\nold\n", text)


    def test_condense_canonical_compresses_structured_entries(self):
        content = (
            "# Lessons\n\n"
            "## 2026-06-22T16:44:58+08:00 - 2026-06-22-macbook-claude-test-entry\n\n"
            "- Source: `macbook/claude`\n"
            "- Scope: `global`\n"
            "- Applicability: `all_agents`\n"
            "- Type: `lesson`\n"
            "- Fact: This is the actual fact text we want to keep.\n"
            "- Source Perspective: Observed by `macbook/claude`.\n"
            "- Why: This explains motivation that downstream agents do not need.\n"
            "- Evidence: This is supporting evidence agents do not need either.\n"
        )

        condensed = _condense_canonical(content)

        self.assertIn("This is the actual fact text we want to keep.", condensed)
        self.assertIn("(src:macbook/claude)", condensed)
        # metadata fields are stripped
        self.assertNotIn("explains motivation", condensed)
        self.assertNotIn("supporting evidence", condensed)
        self.assertNotIn("Source Perspective", condensed)
        # bullet form replaces full ## header
        self.assertTrue(condensed.lstrip().startswith("# Lessons") or "- **" in condensed)
        # significant size reduction
        self.assertLess(len(condensed), len(content) // 2)

    def test_condense_canonical_passes_through_unstructured(self):
        content = (
            "# Bootstrap\n\n"
            "This file contains the cold-start contract.\n"
            "Multiple lines of plain markdown should pass through unchanged.\n"
        )

        condensed = _condense_canonical(content)

        # no `- Fact:` field → returns content as-is
        self.assertEqual(condensed, content)

    def test_render_shared_memory_uses_condensed_form(self):
        with self.tmpdir() as tmp:
            root = tmp / "repo"
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            (root / "memory" / "lessons.md").write_text(
                "# Lessons\n\n"
                "## 2026-06-22T16:44:58+08:00 - sample-entry\n\n"
                "- Source: `laptop/codex`\n"
                "- Type: `lesson`\n"
                "- Fact: Compression should happen here.\n"
                "- Why: This Why line should be stripped.\n"
                "- Evidence: This Evidence line too.\n",
                encoding="utf-8",
            )

            rendered = render_shared_memory(root, machine="laptop", agent="codex")

            self.assertIn("Compression should happen here.", rendered)
            self.assertIn("(src:laptop/codex)", rendered)
            self.assertNotIn("This Why line should be stripped.", rendered)
            self.assertNotIn("This Evidence line too.", rendered)


if __name__ == "__main__":
    unittest.main()
