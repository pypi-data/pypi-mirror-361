import _test_case

from m9lib import uDictionary

class TestDictionary(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_udict(self):
        u = uDictionary({"x":3, "y":6})
        ud = uDictionary(u)
        ud.SetValue("z", 9)
        ud.ClearValue("x")
        self.assertEqual(ud.GetDictionary(), {"y":6, "z":9})

        ud2 = ud.Copy()
        ud2.MergeValues(uDictionary({"a":5, "z":5}))
        self.assertEqual(ud2.GetDictionary(), {"a":5, "y":6, "z":9})

        ud2 = ud.Copy()
        ud2.MergeValues(uDictionary({"a":5, "z":5}), True)
        self.assertEqual(ud2.GetDictionary(), {"a":5, "y":6, "z":5})
