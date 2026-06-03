from pathlib import Path
import unittest

from agent_memory.config import load_config
from agent_memory.setup import setup_workspace


class ConfigSetupTests(unittest.TestCase):
    def test_load_config_reads_agentmemory_yaml(self):
        with self.tmpdir() as root:
            config_file = root / "agentmemory.yaml"
            config_file.write_text(
                "version: 1\n"
                "workspace:\n"
                "  name: demo\n"
                "machines:\n"
                "  - id: laptop\n"
                "adapters:\n"
                "  codex:\n"
                "    adapter: adapters/codex.yaml\n",
                encoding="utf-8",
            )

            config = load_config(root)

            self.assertEqual(config["workspace"]["name"], "demo")
            self.assertEqual(config["machines"][0]["id"], "laptop")
            self.assertEqual(config["adapters"]["codex"]["adapter"], "adapters/codex.yaml")

    def test_setup_workspace_creates_generic_private_instance_state(self):
        with self.tmpdir() as root:
            result = setup_workspace(
                root,
                workspace="demo-memory",
                machines=["laptop", "desktop"],
                adapters=["codex", "claude"],
            )

            self.assertEqual(result["status"], "created")
            self.assertTrue((root / "agentmemory.yaml").exists())
            self.assertTrue((root / "memory" / "lessons.md").exists())
            self.assertTrue((root / "registry" / "agents.json").exists())
            self.assertTrue((root / "inbox" / "laptop" / "codex").exists())
            self.assertTrue((root / ".curator" / "manifest.json").exists())
            self.assertNotIn("Ferdinand", (root / "agentmemory.yaml").read_text(encoding="utf-8"))

    def test_setup_workspace_refuses_to_overwrite_existing_config(self):
        with self.tmpdir() as root:
            (root / "agentmemory.yaml").write_text("version: 1\n", encoding="utf-8")

            result = setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])

            self.assertEqual(result["status"], "exists")

    from contextlib import contextmanager
    import tempfile

    @contextmanager
    def tmpdir(self):
        with self.tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)


if __name__ == "__main__":
    unittest.main()
