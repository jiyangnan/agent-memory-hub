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


if __name__ == "__main__":
    unittest.main()
