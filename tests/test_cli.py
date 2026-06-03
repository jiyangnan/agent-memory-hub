import subprocess
import sys
import unittest


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


if __name__ == "__main__":
    unittest.main()
