from django.test import TestCase

from plugin.manager import plugin_manager


class TestWhiteboxPluginMapIcons(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginMapIcons"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "Map Icons")

    def test_plugin_augments(self):
        self.assertEqual(self.plugin.augments_plugin, "Map")

    def test_bootstraped_assets(self):
        bootstrap_assets = self.plugin.get_bootstrap_assets()

        self.assertIn("js", bootstrap_assets)
        self.assertIn(
            "/static/whitebox_plugin_map_icons/whitebox_marker_override.mjs",
            bootstrap_assets["js"],
        )
