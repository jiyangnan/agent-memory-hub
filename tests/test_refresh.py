import subprocess
import unittest
from pathlib import Path

from agent_memory.refresh import refresh_shared_memory
from agent_memory.registry import register_agent
from agent_memory.setup import setup_workspace


class RefreshTests(unittest.TestCase):
    from contextlib import contextmanager
    import tempfile

    @contextmanager
    def tmpdir(self):
        with self.tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    def git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def prepare_workspace(self, tmp: Path) -> tuple[Path, Path]:
        root = tmp / "repo"
        home = tmp / "home"
        remote = tmp / "remote.git"
        remote.mkdir()
        subprocess.run(["git", "init", "--bare"], cwd=remote, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
        register_agent(
            root,
            machine="laptop",
            agent="codex",
            adapter="codex",
            primary_memory="~/.codex/memory/shared.md",
        )
        (root / "memory" / "lessons.md").write_text("# Lessons\n\nRefresh shared rule.\n", encoding="utf-8")
        self.git(root, "init")
        self.git(root, "config", "user.email", "agentmemory.test@example.com")
        self.git(root, "config", "user.name", "Agent Memory Hub Test")
        self.git(root, "branch", "-M", "main")
        self.git(root, "remote", "add", "origin", str(remote))
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "initial")
        target = home / ".codex" / "memory" / "shared.md"
        target.parent.mkdir(parents=True)
        target.write_text(
            "Local memory.\n"
            "<!-- agent-memory-hub:BEGIN shared -->\n"
            "old\n"
            "<!-- agent-memory-hub:END shared -->\n",
            encoding="utf-8",
        )
        return root, home

    def test_refresh_dry_run_pulls_then_previews_sync_without_modifying_target(self):
        with self.tmpdir() as tmp:
            root, home = self.prepare_workspace(tmp)
            target = home / ".codex" / "memory" / "shared.md"
            original = target.read_text(encoding="utf-8")

            result = refresh_shared_memory(root, home=home, machine="laptop", agent="codex", apply=False)

            self.assertEqual(result["status"], "sync_ready")
            self.assertEqual(result["pull"]["status"], "up_to_date")
            self.assertEqual(result["sync"]["status"], "would_update")
            self.assertIn("Current receiver: `laptop/codex`", result["sync"]["preview"])
            self.assertIn("Refresh shared rule.", result["sync"]["preview"])
            self.assertEqual(target.read_text(encoding="utf-8"), original)

    def test_refresh_apply_pulls_then_updates_agent_memory(self):
        with self.tmpdir() as tmp:
            root, home = self.prepare_workspace(tmp)
            target = home / ".codex" / "memory" / "shared.md"

            result = refresh_shared_memory(root, home=home, machine="laptop", agent="codex", apply=True)

            self.assertEqual(result["status"], "sync_applied")
            self.assertEqual(result["pull"]["status"], "up_to_date")
            self.assertEqual(result["sync"]["status"], "applied")
            self.assertIn("Current receiver: `laptop/codex`", target.read_text(encoding="utf-8"))
            self.assertIn("Refresh shared rule.", target.read_text(encoding="utf-8"))

    def test_refresh_does_not_sync_when_pull_is_blocked(self):
        with self.tmpdir() as tmp:
            root = tmp / "repo"
            home = tmp / "home"
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            register_agent(
                root,
                machine="laptop",
                agent="codex",
                adapter="codex",
                primary_memory="~/.codex/memory/shared.md",
            )
            target = home / ".codex" / "memory" / "shared.md"
            target.parent.mkdir(parents=True)
            target.write_text(
                "<!-- agent-memory-hub:BEGIN shared -->\nold\n<!-- agent-memory-hub:END shared -->\n",
                encoding="utf-8",
            )

            result = refresh_shared_memory(root, home=home, machine="laptop", agent="codex", apply=True)

            self.assertEqual(result["status"], "pull_blocked")
            self.assertEqual(result["pull"]["status"], "not_git")
            self.assertEqual(result["sync"]["status"], "not_started")
            self.assertIn("old", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
