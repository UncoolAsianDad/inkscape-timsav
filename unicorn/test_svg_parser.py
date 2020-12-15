from unittest import TestCase
from svg_parser import parse_length_with_units


class Test(TestCase):
    def test_parse_length_with_units(self):
        v, u = parse_length_with_units("hi")
        self.assertIsNone(u)
        self.assertIsNone(v)

        v, u = parse_length_with_units("30in")
        self.assertEqual(v, 30)
        self.assertEqual("in", u)

        v, u = parse_length_with_units("30px")
        self.assertEqual(v, 30)
        self.assertEqual("px", u)

        v, u = parse_length_with_units("30mm")
        self.assertEqual(v, 30)
        self.assertEqual("mm", u)

        v, u = parse_length_with_units("30%")
        self.assertEqual(v, 30)
        self.assertEqual("%", u)
