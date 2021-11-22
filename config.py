import os
import json
from helpers import format_filename


CONFIG_FILENAME = format_filename("config.json")
CONFIG = {}

if os.path.exists(CONFIG_FILENAME):
    with open(CONFIG_FILENAME, 'r') as f:
        CONFIG = json.loads(f.read())


def save_config(config: dict):
    with open(CONFIG_FILENAME, 'w') as f:
        f.write(json.dumps(config, indent=2, sort_keys=True))
