import subprocess
import unittest
from pathlib import Path

from agent_memory.cloud import cloud_pull, cloud_push, cloud_save, cloud_status
from agent_memory.setup import setup_workspace


class CloudTests(unittest.TestCase):
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

    def init_git_repo(self, root: Path) -> None:
        self.git(root, "init")
        self.git(root, "config", "user.email", "agentmemory.test@example.com")
        self.git(root, "config", "user.name", "Agent Memory Hub Test")
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "initial")

    def test_cloud_status_reports_missing_remote(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            self.init_git_repo(root)

            result = cloud_status(root)

            self.assertEqual(result["status"], "missing_remote")

    def test_cloud_save_commits_only_shared_state_paths(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            self.init_git_repo(root)
            (root / "memory" / "lessons.md").write_text("# Lessons\n\nNew shared rule.\n", encoding="utf-8")
            (root / "README.md").write_text("product edit\n", encoding="utf-8")

            result = cloud_save(root, message="Update shared memory")

            self.assertEqual(result["status"], "committed")
            self.assertIn("memory/lessons.md", result["paths"])
            self.assertNotIn("README.md", result["paths"])
            status = self.git(root, "status", "--short").stdout
            self.assertIn("?? README.md", status)
            self.assertNotIn("memory/lessons.md", status)

    def test_cloud_pull_and_push_work_against_bare_remote(self):
        with self.tmpdir() as tmp:
            remote = tmp / "remote.git"
            root = tmp / "repo"
            remote.mkdir()
            subprocess.run(["git", "init", "--bare"], cwd=remote, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            root.mkdir()
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            self.init_git_repo(root)
            self.git(root, "branch", "-M", "main")
            self.git(root, "remote", "add", "origin", str(remote))

            pull = cloud_pull(root)
            push = cloud_push(root)

            self.assertEqual(pull["status"], "up_to_date")
            self.assertEqual(push["status"], "pushed")


if __name__ == "__main__":
    unittest.main()

