import json
from typing import Type, Any


class ConfigValue(object):

    def __init__(self, value: Any, default: Any = None, type: Type = object) -> None:
        self._value = value
        self.default = default
        self.type = type

    @property
    def value(self):
        return self._value

    @property
    def ui_value(self):
        return str(self.value)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)


class JsonConfigValue(ConfigValue):

    @property
    def ui_value(self):
        return json.dumps(self.value, indent=2, sort_keys=True)


class ConfigSecret(ConfigValue):

    @property
    def ui_value(self):
        return "".join(["*" if ch != "/" else "/" for ch in self.value])


def version_1_to_2(old_version: dict) -> dict:
    """
    Upgrades a version 1 config object to version 2
    :param old_version:
    :return:
    """
    # Late import to avoid circular references
    from modules.combat import Loadout

    old_version["version"] = 2

    # Transform Loadouts
    loadout = Loadout(old_version.pop("weapon", "Sollomate Opalo"),
                      old_version.pop("amp", "Unamped"),
                      old_version.pop("sight_1", "None"),
                      old_version.pop("sight_2", "None"),
                      old_version.pop("scope", "None"),
                      old_version.pop("damage_enhancers", 0),
                      old_version.pop("accuracy_enhancers", 0))
    old_version["loadouts"] = [loadout]

    twitch_config = old_version.pop("twitch", {})
    old_version["twitch_channel"] = twitch_config.pop("channel", "")
    old_version["twitch_username"] = twitch_config.pop("username", "LootNanny")
    old_version["twitch_token"] = twitch_config.pop("token", "oauth:")
    old_version["twitch_prefix"] = twitch_config.pop("prefix", "!")

    return old_version
