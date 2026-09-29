"""Chat-client selection contracts; never inspect real windows or applications."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import chat_apps


class ChatAppSelection(unittest.TestCase):
    """Ensure user configuration cannot accidentally select an unsupported client."""

    def test_feishu_alias_and_local_lark_bundle_are_supported(self):
        """The installed Lark client maps to the Feishu profile used by the rest of the app."""
        self.assertEqual(chat_apps.app_for_key("lark").key, "feishu")
        self.assertIn("com.electron.lark", chat_apps.app_for_key("feishu").bundle_ids)

    def test_config_pins_one_client_and_unknown_value_stays_safe(self):
        """Known values constrain capture; a typo keeps auto detection instead of failing closed."""
        with patch.object(chat_apps.userconfig, "get", return_value="feishu"):
            self.assertEqual([app.key for app in chat_apps.configured_apps()], ["feishu"])
        with patch.object(chat_apps.userconfig, "get", return_value="unsupported-client"):
            self.assertEqual([app.key for app in chat_apps.configured_apps()], ["wechat", "feishu"])

    def test_owner_lookup_respects_the_configured_allow_list(self):
        """A WeChat window cannot be selected while the user explicitly chose Feishu."""
        feishu_only = (chat_apps.app_for_key("feishu"),)
        self.assertIsNone(chat_apps.app_for_owner("WeChat", feishu_only))
        self.assertEqual(chat_apps.app_for_owner("Lark", feishu_only).key, "feishu")


if __name__ == "__main__":
    unittest.main()
