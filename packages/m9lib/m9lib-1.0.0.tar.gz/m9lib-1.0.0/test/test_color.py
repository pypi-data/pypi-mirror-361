import _test_case

from m9lib import uConsoleColor

class TestColor(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_color(self):
        self.assertEqual(uConsoleColor.GetCode("VIOLET"), '\33[35m')
        self.assertEqual(uConsoleColor.GetCode("END"), '\33[0m')
        s = uConsoleColor.Wrap("Roses", 'RED')
        self.assertEqual(s, "\33[31mRoses\33[0m")
        print(s)
        self.assertEqual(uConsoleColor.Format("[+RED]Roses[+]"), "\33[31mRoses\33[0m")

        s = uConsoleColor.Format("Roses are [+RED]red[+], Violets are [+BLUE]blue[+].")
        self.assertEqual(s, "Roses are \33[31mred\33[0m, Violets are \33[34mblue\33[0m.")
        print(s)

        s = uConsoleColor.Format("Roses are [+RED]red[+], Violets are [+BLUE]blue[+].", StripColors=True)
        self.assertEqual(s, "Roses are red, Violets are blue.")
        print(s)

        s = uConsoleColor.Format("[+BAD]Bad[+] roses.")
        self.assertEqual(s, "Bad\33[0m roses.")

        cc = uConsoleColor()
        cc.Header("Test Header")
        cc.Message("Test Message")
        cc.Warning("Test Warning")

        cc = uConsoleColor("testColor")
        cc.Header("Test Header")
        cc.Message("Test Message")
        cc.Warning("Test Warning")

        uConsoleColor.PrintTest()

        # for x in range(90):
        #     val = x+10
        #     print(f"\33[{val}m{val}\33[0m")

