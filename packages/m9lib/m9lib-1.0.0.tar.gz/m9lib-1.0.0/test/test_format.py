import _test_case

import datetime
import time

from m9lib import uStringFormat

class TestStringFormat(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_formatting(self):
        self.assertEqual(uStringFormat.Bytes (4321), '4.2 kb')
        self.assertEqual(uStringFormat.Bytes (4321, "b"), '4321 bytes')

        s = uStringFormat.Duration (12345)
        self.assertEqual(uStringFormat.Duration (12345), '3.4 hrs')
        self.assertEqual(uStringFormat.Duration (12345, "m"), '205.8 min')

        self.assertEqual(uStringFormat.String ("{B} {D}", Bytes=12345, Seconds=12345), "12.1 kb 3.4 hrs")
        now = datetime.datetime.now()
        time.sleep(1)
        self.assertNotEqual(uStringFormat.String ("{TSM}", Now=now), uStringFormat.String ("{TSM}"))

        self.assertEqual(uStringFormat.Strip(" roses are red \t "), "roses are red")
        self.assertEqual(uStringFormat.Strip(" roses are red       "), "roses are red")
        self.assertEqual(uStringFormat.Strip([" roses are red       "]), ["roses are red"])
        self.assertEqual(uStringFormat.Strip(123), 123)
        self.assertEqual(uStringFormat.Strip([123, " roses   ", " are red "]), [123,"roses", "are red"])

        self.assertEqual(uStringFormat.ParseBytes("8888888"), 8888888)
        self.assertEqual(uStringFormat.ParseBytes("1              kB"), 1024)
        self.assertEqual(uStringFormat.ParseBytes("2.5MB"), int(1024*1024*2.5))
        self.assertEqual(uStringFormat.ParseBytes("1tb"), 1099511627776)

        self.assertEqual(uStringFormat.ParseDuration("1s"), 1)
        self.assertEqual(uStringFormat.ParseDuration("1.5m"), 90)
        self.assertEqual(uStringFormat.ParseDuration("3 hours"), 10800)
        self.assertEqual(uStringFormat.ParseDuration("0.5 days"), 43200)
