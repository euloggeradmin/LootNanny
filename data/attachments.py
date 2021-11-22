import json
import sys
import os
from decimal import Decimal
from helpers import resource_path


ALL_ATTACHMENTS = {}
data_filename = resource_path("attachments.json")

if os.path.exists(data_filename):
    with open(data_filename, 'r') as f:
        data = json.loads(f.read())
        for name, attachment_data in data.items():
            attachment_data["decay"] = Decimal(attachment_data["decay"])
            ALL_ATTACHMENTS[name] = attachment_data

FIELDS = ("name", "type", "decay", "ammo")

if __name__ == "__main__":

    all_amps = {}

    for fn in sys.argv[1:]:
        with open(fn, 'r') as f:
            header = True
            for line in f.readlines():
                if header:
                    header = False
                    continue
                try:
                    data = dict(zip(FIELDS, line.split(";")))
                    data["decay"] = Decimal(data["decay"] if data["decay"].strip() else "0.0") / Decimal(100.0)
                    data["ammo"] = int(data["ammo"] if data["ammo"].strip() else 0)

                    all_amps[data["name"]] = {
                        "type": data["type"],
                        "decay": str(data["decay"]),
                        "ammo": data["ammo"]
                    }

                except:
                    raise
                    print(line)
                    break

    if all_amps:
        output = open(data_filename, 'w')
        output.write(json.dumps(all_amps, indent=2, sort_keys=True))
