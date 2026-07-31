import unittest

from software.python.jz_pwm2 import (
    build_duty_command,
    build_frequency_command,
    parse_reply,
)


class CommandBuilderTests(unittest.TestCase):
    def test_frequency_hz(self):
        self.assertEqual(build_frequency_command(1, 1), "S1F001T")
        self.assertEqual(build_frequency_command(2, 999), "S2F999T")

    def test_frequency_khz(self):
        self.assertEqual(build_frequency_command(1, 54_100), "S1F54.1T")

    def test_duty(self):
        self.assertEqual(build_duty_command(1, 25), "S1D025T")
        self.assertEqual(build_duty_command(2, 100), "S2D100T")

    def test_replies(self):
        self.assertTrue(parse_reply("DOWN\r\n").success)
        self.assertTrue(parse_reply("DONE").success)
        self.assertFalse(parse_reply("FALL").success)
        self.assertFalse(parse_reply("unknown").known)


if __name__ == "__main__":
    unittest.main()
