import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_cli_help_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "agent_memory.cli", "--help"],
            cwd=".",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("agent memory hub", result.stdout)

    def test_cli_setup_and_inbox_add(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "setup",
                    "--workspace",
                    "demo",
                    "--machine",
                    "laptop",
                    "--adapter",
                    "codex",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(setup.returncode, 0)

            inbox = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "inbox-add",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--type",
                    "lesson",
                    "--scope",
                    "global",
                    "--fact",
                    "Shared memory should be curated.",
                    "--why",
                    "Direct canonical edits can conflict.",
                    "--evidence",
                    "cli test",
                    "--destination",
                    "memory/lessons.md",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(inbox.returncode, 0)
            self.assertIn("inbox note created", inbox.stdout)
            self.assertTrue(list((root / "inbox" / "laptop" / "codex").glob("*.md")))

    def test_cli_register_members_and_bootstrap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "setup",
                    "--workspace",
                    "demo",
                    "--machine",
                    "laptop",
                    "--adapter",
                    "codex",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            register = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "register-agent",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--adapter",
                    "codex",
                    "--primary-memory",
                    "~/.codex/memory/shared.md",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(register.returncode, 0)

            members = subprocess.run(
                [sys.executable, "-m", "agent_memory.cli", "--root", str(root), "members"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn("laptop/codex", members.stdout)

            bootstrap = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "bootstrap",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn("agent memory hub Cold Start Contract", bootstrap.stdout)

    def test_cli_status_and_curate_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "setup",
                    "--workspace",
                    "demo",
                    "--machine",
                    "laptop",
                    "--adapter",
                    "codex",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "inbox-add",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--type",
                    "lesson",
                    "--scope",
                    "global",
                    "--fact",
                    "Curator should merge clean notes.",
                    "--why",
                    "Canonical memory needs a single writer.",
                    "--evidence",
                    "cli test",
                    "--destination",
                    "memory/lessons.md",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            status = subprocess.run(
                [sys.executable, "-m", "agent_memory.cli", "--root", str(root), "status"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn('"pending_notes": 1', status.stdout)

            apply = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "curate-apply",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(apply.returncode, 0)
            self.assertIn('"accepted": 1', apply.stdout)

    def test_cli_cloud_status_reports_missing_remote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(
                [sys.executable, "-m", "agent_memory.cli", "--root", str(root), "setup", "--workspace", "demo"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            status = subprocess.run(
                [sys.executable, "-m", "agent_memory.cli", "--root", str(root), "cloud-status"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(status.returncode, 2)
            self.assertIn('"status": "missing_remote"', status.stdout)

    def test_cli_sync_dry_run_previews_without_modifying_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            home = Path(tmp) / "home"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "setup",
                    "--workspace",
                    "demo",
                    "--machine",
                    "laptop",
                    "--adapter",
                    "codex",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "register-agent",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--adapter",
                    "codex",
                    "--primary-memory",
                    "~/.codex/memory/shared.md",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            (root / "memory" / "lessons.md").write_text("# Lessons\n\nShared CLI rule.\n", encoding="utf-8")
            target = home / ".codex" / "memory" / "shared.md"
            target.parent.mkdir(parents=True)
            original = (
                "Local only.\n"
                "<!-- agent-memory-hub:BEGIN shared -->\n"
                "old shared\n"
                "<!-- agent-memory-hub:END shared -->\n"
            )
            target.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "sync",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--home",
                    str(home),
                    "--dry-run",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn('"status": "would_update"', result.stdout)
            self.assertIn("Shared CLI rule.", result.stdout)
            self.assertEqual(target.read_text(encoding="utf-8"), original)

    def test_cli_sync_install_marker_adds_managed_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            home = Path(tmp) / "home"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "setup",
                    "--workspace",
                    "demo",
                    "--machine",
                    "laptop",
                    "--adapter",
                    "codex",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "register-agent",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--adapter",
                    "codex",
                    "--primary-memory",
                    "~/.codex/memory/shared.md",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            target = home / ".codex" / "memory" / "shared.md"
            target.parent.mkdir(parents=True)
            target.write_text("Existing local memory.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "sync",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--home",
                    str(home),
                    "--install-marker",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn('"status": "installed"', result.stdout)
            self.assertIn("agent-memory-hub:BEGIN shared", target.read_text(encoding="utf-8"))

    def test_cli_refresh_reports_pull_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            home = Path(tmp) / "home"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "setup",
                    "--workspace",
                    "demo",
                    "--machine",
                    "laptop",
                    "--adapter",
                    "codex",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "register-agent",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--adapter",
                    "codex",
                    "--primary-memory",
                    "~/.codex/memory/shared.md",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_memory.cli",
                    "--root",
                    str(root),
                    "refresh",
                    "--machine",
                    "laptop",
                    "--agent",
                    "codex",
                    "--home",
                    str(home),
                    "--apply",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn('"status": "pull_blocked"', result.stdout)
            self.assertIn('"status": "not_git"', result.stdout)


if __name__ == "__main__":
    unittest.main()
