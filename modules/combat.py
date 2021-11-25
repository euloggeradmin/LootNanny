from collections import defaultdict
from datetime import datetime
import time
from typing import List
from decimal import Decimal
import threading
import os
import json


from modules.base import BaseModule
from chat import BaseChatRow, CombatRow, LootInstance, SkillRow, EnhancerBreakages, HealRow, GlobalInstance
from helpers import dt_to_ts, ts_to_dt, format_filename
from ocr import screenshot_window


SAVE_FILENAME = format_filename("runs.json")


def take_screenshot(delay_ms, directory, glob: GlobalInstance):
    """
    :param glob:
    :return:
    """
    time.sleep(delay_ms / 1000.0)
    im, _, _ = screenshot_window()

    ts = time.mktime(glob.time.timetuple())
    screenshot_name = f"{glob.creature}_{glob.value}_{ts}.png"
    screenshot_fullpath = os.path.join(os.path.expanduser(directory), screenshot_name)
    print(screenshot_fullpath)
    im.save(screenshot_fullpath)


class HuntingTrip(object):

    def __init__(self, time_start: datetime, cost_per_shot: Decimal):
        self.time_start = time_start
        self.time_end = None

        self.cost_per_shot: Decimal = cost_per_shot

        self.tt_return = 0
        self.globals = 0
        self.hofs = 0
        self.total_cost = 0

        self.last_loot_instance = None
        self.loot_instances = 0

        # Tracking multipliers
        self.loot_instance_cost = Decimal(0)
        self.loot_instance_value = Decimal(0)
        self.multipliers = ([], [])
        self.return_over_time = []

        self.looted_items = defaultdict(lambda: {"c": 0, "v": Decimal()})

        self.adjusted_cost = Decimal(0)

        # Enhancers
        self.enhancer_breaks = defaultdict(int)

        # Skillgains
        self.skillgains = defaultdict(int)

        # Combat Stats
        self.total_attacks = 0
        self.total_damage = 0
        self.total_crits = 0
        self.total_misses = 0

    def serialize_run(self):
        return {
            "start": dt_to_ts(self.time_start),
            "end": dt_to_ts(self.time_end) if self.time_end else None,
            "config": {
                "cps": str(self.cost_per_shot)
            },
            "summary": {
                "tt_return": str(self.tt_return),
                "total_cost": str(self.total_cost),
                "globals": self.globals,
                "hofs": self.hofs,
                "loots": self.loot_instances,
                "adj_cost": str(self.adjusted_cost)
            },
            "loot": {k: {"c": v["c"], "v": str(v["v"])} for k, v in self.looted_items.items()},
            "skills": dict(self.skillgains),
            "enhancers": dict(self.enhancer_breaks),
            "combat": {
                "attacks": self.total_attacks,
                "dmg": self.total_damage,
                "crits": self.total_crits,
                "misses": self.total_misses
            },
            "graphs": {
                "returns": self.return_over_time,
                "multis": list(self.multipliers)
            }
        }

    @classmethod
    def from_seralized(cls, seralized):
        inst = cls(ts_to_dt(seralized["start"]), Decimal(seralized["config"]["cps"]))

        if seralized["end"]:
            inst.time_end = ts_to_dt(seralized["end"])

        # loot
        inst.tt_return = Decimal(seralized["summary"]["tt_return"])
        inst.globals = seralized["summary"]["globals"]
        inst.hofs = seralized["summary"]["hofs"]
        inst.loot_instances = seralized["summary"]["loots"]
        inst.adjusted_cost = Decimal(seralized["summary"]["adj_cost"])
        if "total_cost" not in seralized["summary"]:
            # Fix for case where total_cost wont be present in serialized runs
            total_cost = Decimal(seralized["config"]["cps"]) * int(seralized["combat"]["attacks"])
            inst.total_cost = total_cost
        else:
            inst.total_cost = Decimal(seralized["summary"].get("total_cost", "0.0"))

        # combat
        inst.total_attacks = seralized["combat"]["attacks"]
        inst.total_damage = seralized["combat"]["dmg"]
        inst.total_crits = seralized["combat"]["crits"]
        inst.total_misses = seralized["combat"]["misses"]

        # graphs
        inst.return_over_time = seralized["graphs"]["returns"]
        inst.multipliers = seralized["graphs"]["multis"]

        for k, v in seralized["enhancers"].items():
            inst.enhancer_breaks[k] = v

        for k, v in seralized["skills"].items():
            inst.skillgains[k] = v

        for k, v in seralized["loot"].items():
            inst.looted_items[k] = {"c": v["c"], "v": Decimal(v["v"])}

        return inst

    @property
    def duration(self):
        d = self.time_end - self.time_start if self.time_end else datetime.now() - self.time_start
        return "{}:{}:{}".format(d.hours, d.seconds // 60, d.seconds % 60)

    def add_skillgain_row(self, row: SkillRow):
        self.skillgains[row.skill] += row.amount

    def add_enhancer_break_row(self, row: EnhancerBreakages):
        self.enhancer_breaks[row.type] += 1

    @property
    def total_enhancer_breaks(self):
        return sum(self.enhancer_breaks.values())

    def add_global_row(self, row: GlobalInstance):
        if row.hof:
            self.hofs += 1
            return
        self.globals += 1

    def add_combat_chat_row(self, row: CombatRow):
        self.total_attacks += 1
        self.total_damage += row.amount
        if row.critical:
            self.total_crits += 1
        if row.miss:
            self.total_misses += 1
        self.loot_instance_cost += self.cost_per_shot
        self.total_cost += self.cost_per_shot

    def add_loot_instance_chat_row(self, row: LootInstance):
        ts = time.mktime(row.time.timetuple()) // 2

        # We dont want to consider sharp conversion as a loot event
        if row.name == "Universal Ammo":
            return

        if self.last_loot_instance != ts:
            # If looks like an enhancer break
            if row.name == "Shrapnel" and row.amount == 8000:
                pass  # But we still add the shrapnel back to the total items looted
            else:
                self.last_loot_instance = ts
                self.loot_instances += 1

                if self.loot_instance_value and self.loot_instance_cost:
                    self.multipliers[0].append(float(self.loot_instance_cost))
                    self.multipliers[1].append(float(self.loot_instance_value))

                    self.loot_instance_cost = Decimal(0)
                    self.loot_instance_value = Decimal(0)

                    self.return_over_time.append(float(self.tt_return / self.total_cost))

        self.tt_return += row.value

        self.looted_items[row.name]["v"] += row.value
        self.looted_items[row.name]["c"] += row.amount
        self.loot_instance_value += row.value

    @property
    def miss_chance(self):
        if self.total_attacks == 0:
            return "0.00%"
        return "%.2f" % (self.total_misses / float(self.total_attacks) * 100) + "%"

    @property
    def crit_chance(self):
        if self.total_attacks == 0:
            return "0.00%"
        return "%.2f" % (self.total_crits / float(self.total_attacks) * 100) + "%"

    @property
    def dpp(self):
        if self.total_cost > Decimal(0):
            return Decimal(self.total_damage) / Decimal(self.total_cost * 100)
        return Decimal(0.0)

    def get_skill_table_data(self):
        d = {"Skill": [], "Value": []}
        for k, v in sorted(self.skillgains.items(), key=lambda t: t[1], reverse=True):
            d["Skill"].append(k)
            d["Value"].append("%.4f" % v)
        return d

    def get_total_skill_gain(self):
        return sum(self.skillgains.values())

    def get_enhancer_table_data(self):
        d = {"Enhancer": [], "Breaks": []}
        for k, v in sorted(self.enhancer_breaks.items(), key=lambda t: t[1], reverse=True):
            d["Enhancer"].append(k)
            d["Breaks"].append(str(v))
        return d

    def get_item_loot_table_data(self):
        r = {"Item": [], "Value": [], "Count": []}
        for k, v in sorted(self.looted_items.items(), key=lambda t: t[1]["v"], reverse=True):
            r["Item"].append(k)
            r["Value"].append(str(v["v"]))
            r["Count"].append(str(v["c"]))
        return r


class CombatModule(BaseModule):

    def __init__(self, app):
        super().__init__()
        self.app = app

        # Core
        self.is_logging = False
        self.is_paused = False
        self.active_character = ""  # the name of the character

        # Both of these are set by the parent app
        self.loot_table = None
        self.runs_table = None
        self.skill_table = None
        self.enhancer_table = None
        self.combat_fields = {}
        self.loot_fields = {}

        # Configuration
        self.active_weapon: str = None
        self.active_amp: str = None
        self.damage_enhancers = 0
        self.accuracy_enhancers = 0

        # Calculated Configuration
        self.ammo_burn = 0
        self.decay = 0

        # Runs
        self.active_run: HuntingTrip = None
        self.runs: List[HuntingTrip] = []

        # Graphs
        self.multiplier_graph = None
        self.return_graph = None

        self.load_runs()

    def update_active_run_cost(self):
        if self.active_run:
            cost = Decimal(self.ammo_burn) / Decimal(10000) + self.decay
            self.active_run.cost_per_shot = cost

    def tick(self, lines: List[BaseChatRow]):
        if self.is_logging and not self.is_paused:

            if self.active_run is None:
                self.create_new_run()

            for chat_instance in lines:
                if isinstance(chat_instance, CombatRow):
                    self.active_run.add_combat_chat_row(chat_instance)
                elif isinstance(chat_instance, LootInstance):
                    self.active_run.add_loot_instance_chat_row(chat_instance)
                elif isinstance(chat_instance, EnhancerBreakages):
                    self.active_run.add_enhancer_break_row(chat_instance)
                elif isinstance(chat_instance, SkillRow):
                    self.active_run.add_skillgain_row(chat_instance)
                elif isinstance(chat_instance, GlobalInstance):
                    if chat_instance.name.strip() == self.active_character.strip():
                        if self.app.config_tab.screenshots_enabled:
                            t = threading.Thread(target=take_screenshot, args=(
                                self.app.config_tab.screenshot_delay_ms,
                                self.app.config_tab.screenshot_directory,
                                chat_instance, ))
                            t.start()
                        self.active_run.add_global_row(chat_instance)

            if self.app.streamer_window:
                self.app.streamer_window.set_text_from_module(self)

        if self.runs:
            self.update_tables()

    def update_tables(self):
        self.update_loot_table()
        self.update_combat_table()
        self.update_skill_table()
        self.update_enhancer_table()
        self.update_graphs()

    def update_combat_table(self):
        """
        {
            "attacks": shots_text,
            "damage": damage_text,
            "crits": critical_rate,
            "misses": miss_rate,
            "dpp": dpp,
            "enhancer_table": table
        }
        :return:
        """
        if not self.active_run:
            return
        self.combat_fields["attacks"].setText(str(self.active_run.total_attacks))
        self.combat_fields["damage"].setText("%.2f" % self.active_run.total_damage)
        self.combat_fields["crits"].setText(str(self.active_run.crit_chance))
        self.combat_fields["misses"].setText(str(self.active_run.miss_chance))
        self.combat_fields["dpp"].setText("%.4f" % self.active_run.dpp)

    def update_loot_table(self):
        """
        {
            "looted_text": looted_text,
            "total_cost_text": total_cost_text,
            "total_return_text": total_return_text,
            "return_perc_text": return_perc_text,
            "globals": globals,
            "hofs": hofs
        }
        :return:
        """
        if not self.active_run:
            return
        self.loot_table.clear()
        self.loot_fields["looted_text"].setText(str(self.active_run.loot_instances))
        self.loot_fields["total_cost_text"].setText("%.2f" % self.active_run.total_cost)
        self.loot_fields["total_return_text"].setText("%.2f" % self.active_run.tt_return)
        if self.active_run.total_cost:
            self.loot_fields["return_perc_text"].setText("%.2f" % (self.active_run.tt_return / self.active_run.total_cost * 100))
        self.loot_fields["globals"].setText(str(self.active_run.globals))
        self.loot_fields["hofs"].setText(str(self.active_run.hofs))

        self.loot_table.setData(self.active_run.get_item_loot_table_data())
        self.update_runs_table()

    def update_runs_table(self):
        self.runs_table.setData(self.get_runs_data())

    def update_skill_table(self):
        if not self.active_run:
            return
        self.skill_table.setData(self.active_run.get_skill_table_data())
        self.app.total_skills_text.setText(f"{self.active_run.get_total_skill_gain():.4f}")

    def update_enhancer_table(self):
        if not self.active_run:
            return
        self.enhancer_table.setData(self.active_run.get_enhancer_table_data())

    def update_graphs(self):
        if not self.active_run:
            return
        self.return_graph.clear()
        self.return_graph.plot(list(map(lambda x: float(x * 100), self.active_run.return_over_time)))
        self.multiplier_graph.clear()
        self.multiplier_graph.plot(*self.active_run.multipliers, pen=None, symbol="o")

    def get_runs_data(self):
        d = {"Start": [], "End": [], "Spend": [], "Enhancers": [], "Extra Spend": [], "Return": [], "%": []}
        for run in self.runs[::-1]:
            run: HuntingTrip
            d["Start"].append(run.time_start.strftime("%Y-%m-%d %H:%M:%S"))
            d["End"].append(run.time_end.strftime("%Y-%m-%d %H:%M:%S") if run.time_end else "")
            d["Spend"].append("%.2f" % run.total_cost)
            d["Enhancers"].append(str(run.total_enhancer_breaks))
            d["Extra Spend"].append("")
            d["Return"].append(run.tt_return)
            if run.total_cost:
                d["%"].append("%.2f" % (run.tt_return / run.total_cost * 100) + "%")
            else:
                d["%"].append("%")
        return d

    def create_new_run(self):
        self.active_run = HuntingTrip(datetime.now(), Decimal(self.ammo_burn) / Decimal(10000) + self.decay)
        self.runs.append(self.active_run)

    def save_runs(self):
        all_runs = []
        if not self.active_run:
            return
        for run in self.runs:
            serialized = run.serialize_run()
            all_runs.append(serialized)
        with open(SAVE_FILENAME, 'w') as f:
            f.write(json.dumps(all_runs))

    def load_runs(self):
        if not os.path.exists(SAVE_FILENAME):
            return

        with open(SAVE_FILENAME, 'r') as f:
            data = json.loads(f.read())

        for run_data in data:
            run = HuntingTrip.from_seralized(run_data)
            self.runs.append(run)

        if self.runs:
            self.active_run = self.runs[-1]
