import unittest

from chat import LogLine, parse_log_line


class TestChatParsing(unittest.TestCase):

    def _internal(self, line, expected):
        log_line = parse_log_line(line)
        self.assertEqual(log_line, expected)

    def test_parse_system_message(self):
        msg = "2021-09-21 09:42:35 [System] [] Critical hit - Additional damage! You inflicted 519.1 points of damage"
        expected = LogLine(
            "2021-09-21 09:42:35",
            "System",
            "",
            "Critical hit - Additional damage! You inflicted 519.1 points of damage"
        )
        self._internal(msg, expected)

    def test_parse_global_message(self):
        msg = "2021-09-21 09:46:31 [Globals] [] Nanashana Nana Itsanai killed a creature " \
              "(Desert Crawler Provider) with a value of 416 PED!"
        expected = LogLine(
            "2021-09-21 09:46:31",
            "Globals",
            "",
            "Nanashana Nana Itsanai killed a creature (Desert Crawler Provider) with a value of 416 PED!"
        )
        self._internal(msg, expected)

    def test_parse_global_message_with_apostrophe_name(self):
        msg = "2021-09-21 09:46:31 [Globals] [] Na'na'sha'na Na'na It'san'ai killed a creature " \
              "(Desert Crawler Provider) with a value of 416 PED!"
        expected = LogLine(
            "2021-09-21 09:46:31",
            "Globals",
            "",
            "Na'na'sha'na Na'na It'san'ai killed a creature (Desert Crawler Provider) with a value of 416 PED!"
        )
        self._internal(msg, expected)

if __name__ == '__main__':
    unittest.main()
