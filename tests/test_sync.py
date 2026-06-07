import unittest
from pathlib import Path

from agent_memory.registry import register_agent
from agent_memory.setup import setup_workspace
from agent_memory.sync import install_marker, sync_apply, sync_dry_run


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


if __name__ == "__main__":
    unittest.main()
