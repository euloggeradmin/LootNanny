import json
import sys
import os
from decimal import Decimal
from helpers import resource_path


SIGHTS = {}
SCOPES = {}
sights_filename = resource_path("sights.json")
scopes_filename = resource_path("scopes.json")

if os.path.exists(sights_filename):
    with open(sights_filename, 'r') as f:
        data = json.loads(f.read())
        for name, attachment_data in data.items():
            attachment_data["decay"] = Decimal(attachment_data["decay"])
            SIGHTS[name] = attachment_data

if os.path.exists(scopes_filename):
    with open(scopes_filename, 'r') as f:
        data = json.loads(f.read())
        for name, attachment_data in data.items():
            attachment_data["decay"] = Decimal(attachment_data["decay"])
            SCOPES[name] = attachment_data


FIELDS = ("name", "type", "decay", "ammo")

if __name__ == "__main__":

    file_type = ("sights", "scopes")

    for i, fn in enumerate(sys.argv[1:]):

        file_data = {}
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

                    file_data[data["name"]] = {
                        "type": data["type"],
                        "decay": str(data["decay"]),
                        "ammo": data["ammo"]
                    }

                except:
                    raise
                    print(line)
                    break

        if file_data:
            output = open(f"{file_type[i]}.json", 'w')
            output.write(json.dumps(file_data, indent=2, sort_keys=True))
