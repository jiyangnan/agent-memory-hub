import unittest
from pathlib import Path

from agent_memory.inbox import add_inbox_note
from agent_memory.setup import setup_workspace


class InboxTests(unittest.TestCase):
    from contextlib import contextmanager
    import tempfile

    @contextmanager
    def tmpdir(self):
        with self.tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    def test_add_inbox_note_writes_generic_frontmatter_and_body(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])

            note = add_inbox_note(
                root,
                machine="laptop",
                agent="codex",
                note_type="lesson",
                scope="global",
                fact="Refresh must pull cloud state before downstream sync.",
                why="Otherwise an agent may think it is fresh while using stale memory.",
                evidence="unit test",
                suggested_destination="memory/lessons.md",
            )

            self.assertTrue(note["path"].exists())
            text = note["path"].read_text(encoding="utf-8")
            self.assertIn("source_agent: codex", text)
            self.assertIn("machine: laptop", text)
            self.assertIn("type: lesson", text)
            self.assertIn("content_hash: sha256:", text)
            self.assertIn("Refresh must pull cloud state", text)

    def test_add_inbox_note_rejects_secret_like_content(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])

            with self.assertRaises(ValueError):
                add_inbox_note(
                    root,
                    machine="laptop",
                    agent="codex",
                    note_type="infra",
                    scope="global",
                    fact="Bearer abc.def",
                    why="Should not be stored",
                    evidence="unit test",
                    suggested_destination="memory/infra.md",
                )


if __name__ == "__main__":
    unittest.main()

