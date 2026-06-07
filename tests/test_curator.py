import json
import unittest
from pathlib import Path

from agent_memory.curator import curate_apply, scan_status
from agent_memory.inbox import add_inbox_note
from agent_memory.setup import setup_workspace


class CuratorTests(unittest.TestCase):
    from contextlib import contextmanager
    import tempfile

    @contextmanager
    def tmpdir(self):
        with self.tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    def test_scan_status_counts_pending_notes(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            add_inbox_note(
                root,
                machine="laptop",
                agent="codex",
                note_type="lesson",
                scope="global",
                fact="Curator should be single-writer.",
                why="Canonical memory must avoid concurrent edits.",
                evidence="unit test",
                suggested_destination="memory/lessons.md",
            )

            status = scan_status(root)

            self.assertEqual(status["pending_notes"], 1)
            self.assertEqual(status["invalid_notes"], 0)

    def test_curate_apply_merges_clean_lesson_and_archives_note(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            note = add_inbox_note(
                root,
                machine="laptop",
                agent="codex",
                note_type="lesson",
                scope="global",
                fact="Curator should be single-writer.",
                why="Canonical memory must avoid concurrent edits.",
                evidence="unit test",
                suggested_destination="memory/lessons.md",
            )

            result = curate_apply(root, machine="laptop", agent="codex")

            self.assertEqual(result["accepted"], 1)
            self.assertFalse(note["path"].exists())
            self.assertIn("Curator should be single-writer.", (root / "memory" / "lessons.md").read_text(encoding="utf-8"))
            canonical = (root / "memory" / "lessons.md").read_text(encoding="utf-8")
            self.assertIn("- Source: `laptop/codex`", canonical)
            self.assertIn("- Applicability: `all_agents`", canonical)
            self.assertIn("- Source Perspective: Observed by `laptop/codex`", canonical)
            self.assertTrue(list((root / "archive" / "accepted").glob("**/*.md")))
            self.assertIn("Curator should be single-writer", (root / ".curator" / "processed.jsonl").read_text(encoding="utf-8"))
            manifest = json.loads((root / ".curator" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], 1)

    def test_curate_apply_moves_secret_note_to_review_without_canonical_write(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            bad_dir = root / "inbox" / "laptop" / "codex"
            bad_dir.mkdir(parents=True, exist_ok=True)
            bad_note = bad_dir / "bad.md"
            bad_note.write_text(
                "---\n"
                "id: bad-secret\n"
                "source_agent: codex\n"
                "machine: laptop\n"
                "date: 2026-06-03\n"
                "type: infra\n"
                "scope: global\n"
                "priority: normal\n"
                "status: pending\n"
                "---\n\n"
                "## Fact\n\n"
                "Bearer abc.def\n",
                encoding="utf-8",
            )

            result = curate_apply(root, machine="laptop", agent="codex")

            self.assertEqual(result["needs_review"], 1)
            self.assertFalse(bad_note.exists())
            self.assertFalse((root / "memory" / "infra.md").read_text(encoding="utf-8").strip().endswith("Bearer abc.def"))
            self.assertTrue(list((root / "archive" / "needs_user_review").glob("**/*.md")))

    def test_curate_apply_moves_missing_applicability_note_to_review(self):
        with self.tmpdir() as root:
            setup_workspace(root, workspace="demo", machines=["laptop"], adapters=["codex"])
            bad_dir = root / "inbox" / "laptop" / "codex"
            bad_dir.mkdir(parents=True, exist_ok=True)
            bad_note = bad_dir / "bad.md"
            bad_note.write_text(
                "---\n"
                "id: missing-applicability\n"
                "source_agent: codex\n"
                "machine: laptop\n"
                "date: 2026-06-03\n"
                "type: lesson\n"
                "scope: global\n"
                "priority: normal\n"
                "status: pending\n"
                "---\n\n"
                "## Fact\n\n"
                "This note is missing applicability.\n",
                encoding="utf-8",
            )

            result = curate_apply(root, machine="laptop", agent="codex")

            self.assertEqual(result["needs_review"], 1)
            self.assertFalse(bad_note.exists())
            self.assertTrue(list((root / "archive" / "needs_user_review").glob("**/*.md")))


if __name__ == "__main__":
    unittest.main()
