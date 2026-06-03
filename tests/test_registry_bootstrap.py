import json
import unittest
from pathlib import Path

from agent_memory.bootstrap import render_bootstrap
from agent_memory.registry import register_agent, render_members
from agent_memory.setup import setup_workspace


class RegistryBootstrapTests(unittest.TestCase):
    from contextlib import contextmanager
    import tempfile

    @contextmanager
    def tmpdir(self):
        with self.tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    def test_register_agent_adds_record_and_inbox_path(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])

            record = register_agent(
                root,
                machine="laptop",
                agent="codex",
                primary_memory="~/.codex/memory/shared.md",
                adapter="codex",
            )

            self.assertEqual(record["agent"], "codex")
            payload = json.loads((root / "registry" / "agents.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["agents"][0]["machine"], "laptop")
            self.assertTrue((root / "inbox" / "laptop" / "codex").exists())

    def test_render_members_lists_registered_agents(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            register_agent(
                root,
                machine="laptop",
                agent="codex",
                primary_memory="~/.codex/memory/shared.md",
                adapter="codex",
            )

            text = render_members(root)

            self.assertIn("laptop/codex", text)
            self.assertIn("~/.codex/memory/shared.md", text)

    def test_render_bootstrap_contains_cold_start_contract(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            register_agent(
                root,
                machine="laptop",
                agent="codex",
                primary_memory="~/.codex/memory/shared.md",
                adapter="codex",
            )

            text = render_bootstrap(root, machine="laptop", agent="codex")

            self.assertIn("agent memory hub Cold Start Contract", text)
            self.assertIn("Agent: `codex`", text)
            self.assertIn("保存到共享记忆", text)
            self.assertIn("拉取一下云端的记忆", text)
            self.assertIn("记住这个", text)
            self.assertIn("inbox/laptop/codex/", text)


if __name__ == "__main__":
    unittest.main()

