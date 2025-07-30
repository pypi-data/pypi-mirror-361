import _test_case

from m9lib import uTimer

class TestTimer(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_timer(self):
        import time
        x = uTimer()
        time.sleep (0.1)
        d1 = x.GetElapsedSeconds()
        time.sleep (0.1)
        x.Stop()
        d2 = x.GetElapsedSeconds()
        time.sleep (0.1)
        d3 = x.GetElapsedSeconds()

        self.assertTrue(d1>0)
        self.assertTrue(d1<1)
        self.assertTrue(d2>d1)
        self.assertEqual(d2,d3)
