from whitebox import Plugin


class WhiteboxPluginMapIcons(Plugin):
    """
    A plugin to display alternative icons on the map display.

    Attributes:
        name: The name of the plugin.
        augments_plugin: The name of the plugin that this plugin augments.
    """

    name = "Map Icons"
    augments_plugin = "Map"


plugin_class = WhiteboxPluginMapIcons
