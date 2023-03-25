import tailer
import enum
from datetime import datetime
from collections import namedtuple
import re
import time
import win_unicode_console
import threading

from decimal import Decimal
win_unicode_console.enable()


class ChatType(str, enum.Enum):
    HEAL = "heal"
    COMBAT = "combat"
    SKILL = "skill"
    DEATH = "death"
    EVADE = "evade"
    DAMAGE = "damage"
    DEFLECT = "deflect"
    DODGE = "dodge"
    ENHANCER = "enhancer"
    LOOT = "loot"
    GLOBAL = "global"


class BaseChatRow(object):

    def __init__(self, *args, **kwargs):
        self.time = None


class HealRow(BaseChatRow):

    def __init__(self, amount):
        super().__init__()
        self.amount = float(amount)


class CombatRow(BaseChatRow):

    def __init__(self, amount=0.0, critical=False, miss=False):
        super().__init__()
        self.amount = float(amount) if amount else 0.0
        self.critical = critical
        self.miss = miss


class SkillRow(BaseChatRow):

    def __init__(self, amount, skill):
        super().__init__()
        try:
            self.amount = float(amount)
            self.skill = skill
        except ValueError:
            # Attributes have their values swapped around in the chat message
            self.amount = float(skill)
            self.skill = amount


class EnhancerBreakages(BaseChatRow):

    def __init__(self, type):
        super().__init__()
        self.type = type


class LootInstance(BaseChatRow):
    CUSTOM_VALUES = {
        "Shrapnel": Decimal("0.0001")
    }

    def __init__(self, name, amount, value):
        super().__init__()
        self.name = name
        self.amount = int(amount)

        if name in self.CUSTOM_VALUES:
            self.value = Decimal(amount) * self.CUSTOM_VALUES[name]
        else:
            self.value = Decimal(value)


class GlobalInstance(BaseChatRow):

    def __init__(self, name, creature, value, location=None, hof=False):
        super().__init__()
        self.name = name
        self.creature = creature
        self.value = value
        self.hof = hof
        self.location = location

LOG_LINE_REGEX = re.compile(
    r"([\d\-]+ [\d:]+) \[(\w+)\] \[(.*)\] (.*)"
)

LogLine = namedtuple("LogLine", ["time", "channel", "speaker", "msg"])


def parse_log_line(line: str) -> LogLine:
    """
    Parses a raw string log line and returns an exploded LogLine for easier manipulation
    :param line: The line to process
    :return: LogLine
    """
    matched = LOG_LINE_REGEX.match(line)
    if not matched:
        return LogLine("", "", "", "")
    return LogLine(*matched.groups())


REGEXES = {
    re.compile("Critical hit - Additional damage! You inflicted (\d+\.\d+) points of damage"): (ChatType.DAMAGE, CombatRow, {"critical": True}),
    re.compile("You inflicted (\d+\.\d+) points of damage"): (ChatType.DAMAGE, CombatRow, {}),
    re.compile("You healed yourself (\d+\.\d+) points"): (ChatType.HEAL, HealRow, {}),
    re.compile("Damage deflected!"): (ChatType.DEFLECT, BaseChatRow, {}),
    re.compile("You Evaded the attack"): (ChatType.EVADE, BaseChatRow, {}),
    re.compile("You missed"): (ChatType.DODGE, CombatRow, {"miss": True}),
    re.compile("The target Dodged your attack"): (ChatType.DODGE, CombatRow, {"miss": True}),
    re.compile("The target Evaded your attack"): (ChatType.DODGE, CombatRow, {"miss": True}),
    re.compile("The target Jammed your attack"): (ChatType.DODGE, CombatRow, {"miss": True}),
    re.compile("You took (\d+\.\d+) points of damage"): (ChatType.DAMAGE, BaseChatRow, {}),
    re.compile("You have gained (\d+\.\d+) experience in your ([a-zA-Z ]+) skill"): (ChatType.SKILL, SkillRow, {}),
    re.compile("You have gained (\d+\.\d+) ([a-zA-Z ]+)"): (ChatType.SKILL, SkillRow, {}),
    re.compile("Your ([a-zA-Z ]+) has improved by (\d+\.\d+)"): (ChatType.SKILL, SkillRow, {}),
    re.compile("Your enhancer ([a-zA-Z0-9 ]+) on your .* broke."): (ChatType.ENHANCER, EnhancerBreakages, {}),
    re.compile(r"You received (.*) x \((\d+)\) Value: (\d+\.\d+) PED"): (ChatType.LOOT, LootInstance, {})
}

GLOBAL_REGEXES = {
    re.compile(r"([\w\s\'\(\)]+) killed a creature \(([\w\s\(\),]+)\) with a value of (\d+) PED! A record has been added to the Hall of Fame!"): (ChatType.GLOBAL, GlobalInstance, {"hof": True}),
    re.compile(r"([\w\s\'\(\)]+) killed a creature \(([\w\s\(\),]+)\) with a value of (\d+) PED!"): (ChatType.GLOBAL, GlobalInstance, {}),
    re.compile(r"([\w\s\'\(\)]+) constructed an item \(([\w\s\(\),]+)\) worth (\d+) PED! A record has been added to the Hall of Fame!"): (ChatType.GLOBAL, GlobalInstance, {"hof": True}),
    re.compile(r"([\w\s\'\(\)]+) constructed an item \(([\w\s\(\),]+)\) worth (\d+) PED!"): (ChatType.GLOBAL, GlobalInstance, {}),
    re.compile(r"([\w\s\'\(\)]+) found a deposit \(([\w\s\(\)]+)\) with a value of (\d+) PED! A record has been added to the Hall of Fame!"): (ChatType.GLOBAL, GlobalInstance, {"hof": True}),
    re.compile(r"([\w\s\'\(\)]+) found a deposit \(([\w\s\(\)]+)\) with a value of (\d+) PED!"): (ChatType.GLOBAL, GlobalInstance, {}),
    re.compile(r"([\w\s\'\(\)]+) killed a creature \(([\w\s\(\),]+)\) with a value of (\d+) PED at ([\s\w\W]+)!"): (ChatType.GLOBAL, GlobalInstance, {}),
}


class ChatReader(object):

    def __init__(self, app):
        self.app = app
        self.lines = []

        self.reader = None

    def delay_start_reader(self):
        if self.reader:
            return

        if not self.app.config.location.value:
            return

        self.fd = tailer.follow(open(self.app.config.location.value, "r", encoding="utf_8_sig"), delay=0.01)
        self.reader = threading.Thread(target=self.readlines, daemon=True)
        self.reader.start()

    def readlines(self):
        try:
            for line in self.fd:
                log_line = parse_log_line(line)
                if log_line.channel == "System":
                    matched = False
                    for rx in REGEXES:
                        match = rx.search(log_line.msg)
                        if match:
                            chat_type, chat_cls, kwargs = REGEXES[rx]
                            chat_instance: BaseChatRow = chat_cls(*match.groups(), **kwargs)
                            chat_instance.time = datetime.strptime(log_line.time, "%Y-%m-%d %H:%M:%S")
                            self.lines.append(chat_instance)
                            matched = True
                            break
                    if not matched:
                        print([log_line.msg])
                elif log_line.channel == "Globals":
                    matched = False
                    for rx in GLOBAL_REGEXES:
                        match = rx.search(log_line.msg)
                        if match:
                            chat_type, chat_cls, kwargs = GLOBAL_REGEXES[rx]
                            chat_instance: GlobalInstance = chat_cls(*match.groups(), **kwargs)
                            chat_instance.time = datetime.strptime(log_line.time, "%Y-%m-%d %H:%M:%S")
                            self.lines.append(chat_instance)
                            matched = True
                            break
        except UnicodeDecodeError:
            pass

    def getline(self):
        if len(self.lines):
            return self.lines.pop(0)
        return None
