import json
import sys
import os
from decimal import Decimal

from helpers import resource_path
from modules.crafting import Slot, Blueprint

ALL_RESOURCES = {}
ALL_BLUEPRINTS = {}
bp_filename = "crafting.json"  # resource_path("crafting.json")
res_filename = "resources.json"  # resource_path("resources.json")

if os.path.exists(bp_filename):
    with open(bp_filename, 'r') as f:
        data = json.loads(f.read())
        for name, slots in data.items():
            bp = Blueprint(name, [Slot(*s) for s in slots])
            ALL_BLUEPRINTS[name] = bp

if os.path.exists(res_filename):
    with open(res_filename, 'r') as f:
        data = json.loads(f.read())
        for name, value in data.items():
            ALL_RESOURCES[name] = Decimal(value)


FIELDS = ("name", "material", "amount", "cost", "_", "__", "___")

if __name__ == "__main__":

    all_bps = {}
    all_resources = {}

    from pathlib import Path

    p = Path(os.path.dirname(sys.argv[1]))
    matches = list(p.glob(os.path.split(sys.argv[1])[-1]))
    for p in matches:
        with p.open('r') as f:
            header = True
            for line in f.readlines():
                if header:
                    header = False
                    continue
                try:
                    data = dict(zip(FIELDS, line.split(";")))
                    print(data)
                    cost = data["cost"].strip()
                    if not cost:
                        cost = "0.0"
                    amount = data["amount"].strip()
                    if not amount:
                        amount = "1"
                    if int(amount):
                        all_resources[data["material"]] = str(Decimal(cost) / int(amount))
                    else:
                        all_resources[data["material"]] = "1.0"
                    if data["name"] not in all_bps:
                        all_bps[data["name"]] = []
                    all_bps[data["name"]].append([data["material"], int(amount)])

                except:
                    raise
                    print(line)
                    break

    if all_bps:
        output = open(bp_filename, 'w')
        output.write(json.dumps(all_bps, indent=2, sort_keys=True))
    if all_resources:
        output = open(res_filename, 'w')
        output.write(json.dumps(all_resources, indent=2, sort_keys=True))
