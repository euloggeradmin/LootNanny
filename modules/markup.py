from collections import namedtuple
import json
import os
from decimal import Decimal

from helpers import format_filename


MARKUP_FILENAME = format_filename("markup.json")


Markup = namedtuple("MarkupItem", ["value", "is_absolute"])
DEFAULT_NULL_MARKUP = Markup(Decimal("1.0"), False)

DEFAULT_MARKUP = {
    "Shrapnel": Markup(Decimal("1.01"), False),
}


class MarkupStore(object):

    def __init__(self):
        self._data = DEFAULT_MARKUP
        self.load_markup()

    def load_markup(self):
        if not os.path.exists(MARKUP_FILENAME):
            return
        with open(MARKUP_FILENAME, 'r') as f:
            try:
                d = json.loads(f.read())
            except:
                d = DEFAULT_MARKUP
            for k, v in d.items():
                self._data[k] = Markup(Decimal(v[0]), v[1])

    def save_markup(self):
        with open(MARKUP_FILENAME, 'w') as f:
            f.write(json.dumps({k: [str(v[0]), v[1]] for k, v in self._data.items()}))

    def get_markup_for_item(self, name):
        if name not in self._data:
            # Asynchronously fetch markup data from Wiki Bot
            #response = requests.get("https://api.markupbot.com/markup/{}".format(name))
            # Will hopefully look something like:
            # {
            #    "day": {"rate": "101.00%", "volume": "100.0"},
            #    "week": {"rate": "101.00%", "volume": "100.0"},
            #    "month": {"rate": "101.00%", "volume": "100.0"},
            #    "year": {"rate": "101.00%", "volume": "100.0"},
            #    "decade": {"rate": "101.00%", "volume": "100.0"},
            #}
            #return Markup(response["month"]["rate"], False)
            return DEFAULT_NULL_MARKUP
        else:
            return self._data[name]

    def add_markup_for_item(self, name, value):
        if value.startswith("+"):
            markup = Markup(Decimal(value[1:]), True)
        else:
            if value.endswith("%"):
                markup = Markup(Decimal(value[:-1]) / 100, False)
            else:
                markup = Markup(Decimal(value), False)
        self._data[name] = markup
        self.save_markup()

    def get_formatted_markup(self, name):
        mu = self.get_markup_for_item(name)
        if mu.is_absolute:
            return "+{:.3f}".format(mu.value)
        else:
            return "{:.3f}%".format(mu.value * 100)

    def apply_markup_to_item(self, name, count: int, value: Decimal):
        mu = self.get_markup_for_item(name)
        if mu.is_absolute:
            return value + (count * mu.value)
        else:
            return value * mu.value
