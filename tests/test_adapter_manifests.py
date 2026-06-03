import unittest
from pathlib import Path

import yaml


class AdapterManifestTests(unittest.TestCase):
    def test_builtin_adapter_manifests_are_generic_and_parseable(self):
        root = Path(__file__).resolve().parents[1]
        for path in sorted((root / "adapters").glob("*.yaml")):
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))

            self.assertIn("id", payload)
            self.assertIn("primary_memory", payload)
            self.assertIn("allowlist", payload)
            self.assertNotIn("Ferdinand", path.read_text(encoding="utf-8"))
            self.assertNotIn("jiyangnan", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

