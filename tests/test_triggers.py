import unittest

from agent_memory.triggers import classify_trigger


class TriggerTests(unittest.TestCase):
    def test_default_shared_trigger(self):
        self.assertEqual(classify_trigger("请保存到共享记忆"), "shared")


    def test_default_refresh_trigger(self):
        self.assertEqual(classify_trigger("拉取一下云端的记忆"), "refresh")


    def test_default_local_trigger(self):
        self.assertEqual(classify_trigger("记住这个"), "local")


    def test_unrelated_text_returns_none(self):
        self.assertEqual(classify_trigger("帮我跑一下测试"), "none")


    def test_user_configured_aliases_override_defaults(self):
        config = {
            "trigger_aliases": {
                "shared": ["publish to team memory"],
                "refresh": ["reload team memory"],
                "local": ["private note"],
            }
        }

        self.assertEqual(classify_trigger("publish to team memory", config=config), "shared")
        self.assertEqual(classify_trigger("reload team memory", config=config), "refresh")
        self.assertEqual(classify_trigger("private note", config=config), "local")


if __name__ == "__main__":
    unittest.main()
