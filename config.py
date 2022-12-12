import os
import json
from typing import List

from helpers import format_filename
import utils.config_utils as CU
from modules.combat import Loadout, CustomWeapon


CONFIG_FILENAME = format_filename("config.json")

STREAMER_LAYOUT_DEFAULT = {'layout': [
    [
        ['{}%', 'PERCENTAGE_RETURN', 'font-size: 20pt;']
    ],
    [
        ['Total Loots: {}', 'TOTAL_LOOTS'],
        ['Total Spend: {} PED', 'TOTAL_SPEND'],
        ['Total Return: {} PED', 'TOTAL_RETURN']
    ]], 'style': 'font-size: 12pt;'}


class Config(object):

    # Version
    version = CU.ConfigValue(2)

    # Core Configuration
    location = CU.ConfigSecret("")
    name = CU.ConfigValue("")
    theme = CU.ConfigValue("dark")

    # Screenshot Configuration
    screenshot_directory = CU.ConfigValue("~/Documents/Globals/")
    screenshot_delay = CU.ConfigValue(500)
    screenshot_threshold = CU.ConfigValue(0)
    screenshot_enabled = CU.ConfigValue(True)

    # Combat Configuration
    loadouts: List[Loadout] = CU.ConfigValue(None)
    selected_loadout: Loadout = CU.ConfigValue(None)
    custom_weapons: List[CustomWeapon] = CU.ConfigValue(None)

    # Streaming and Twitch
    streamer_layout = CU.JsonConfigValue(STREAMER_LAYOUT_DEFAULT)

    twitch_prefix = CU.ConfigValue("!")
    twitch_token = CU.ConfigValue("oauth:")
    twitch_username = CU.ConfigValue("NannyBot")
    twitch_channel = CU.ConfigValue("")
    twitch_commands_enabled = CU.ConfigValue(None)

    def __init__(self):
        # Initialize mutable options
        self.initialized = False
        self.loadouts = []
        self.custom_weapons = []
        self.twitch_commands_enabled = ["commands", "allreturns", "toploots", "info"]

        self.load_config()
        self.print()
        self.initialized = True

    def load_config(self):
        if not os.path.exists(CONFIG_FILENAME):
            return

        try:
            with open(CONFIG_FILENAME, 'r') as f:
                CONFIG = json.loads(f.read())
        except:
            config_contents = ""
            print("Emtpy Config")
            return

        if CONFIG.get("version", 1) < self.version.value:
            fn_name = "version_{}_to_{}".format(CONFIG.get("version", 1), self.version.value)
            CONFIG = getattr(CU, fn_name)(CONFIG)

        for item, value in CONFIG.items():
            setattr(self, item, value)

    def dump(self) -> dict:
        p = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, CU.ConfigValue):
                p[attr_name] = attr.value
        return p

    def print(self):
        print(json.dumps(self.dump(), sort_keys=True, indent=4))

    def save(self):
        if not self.initialized:
            return
        try:
            to_save = json.dumps(self.dump(), indent=2, sort_keys=True)
            with open(CONFIG_FILENAME, 'w') as f:
                f.write(to_save)
        except:
            print("Error saving config!")


    def __setattr__(self, item, value):
        if not isinstance(getattr(self, item, None), CU.ConfigValue):
            return super().__setattr__(item, value)
        config_item: CU.ConfigValue = getattr(self, item)
        config_item._value = value
        self.save()
