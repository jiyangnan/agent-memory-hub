import tomllib
import unittest
from pathlib import Path


class PackagingTests(unittest.TestCase):
    def test_builtin_adapters_are_declared_as_package_data(self):
        root = Path(__file__).resolve().parents[1]
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

        package_data = pyproject["tool"]["setuptools"]["package-data"]

        self.assertIn("agent_memory", package_data)
        self.assertIn("adapters/*.yaml", package_data["agent_memory"])

    def test_builtin_adapters_exist_inside_package(self):
        root = Path(__file__).resolve().parents[1]

        for adapter in ("codex", "claude", "openclaw", "hermes"):
            self.assertTrue((root / "agent_memory" / "adapters" / f"{adapter}.yaml").exists())


if __name__ == "__main__":
    unittest.main()
