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


if __name__ == "__main__":
    unittest.main()
