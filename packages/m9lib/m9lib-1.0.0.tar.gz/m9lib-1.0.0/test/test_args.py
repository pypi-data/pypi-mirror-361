import _test_case

from m9lib import uArgs

class TestArgs(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_args(self):
        args = uArgs()
        args.AddParam ("p1")
        args.AddParam ("p2")
        args.AddOption("option1")
        args.AddOption("option2", "o2")
        args.AddOption("option3", "o3", True)
        args.AddOption("option4", "o4", True)

        # No parse trial
        self.assertEqual(args.parsed_params, None)
        self.assertEqual(args.HasOption("p1"), False)
        self.assertEqual(args.parsed_params, {})

        # Zero condition
        args.Parse([])
        self.assertTrue(args.NoArguments())
        self.assertEqual(args.HasParam("p1"), False)
        self.assertEqual(args.GetParam("p1"), None)
        self.assertEqual(args.HasParam("x"), False)
        self.assertEqual(args.GetParam("x"), False)
        self.assertEqual(args.HasOption("option1"), False)
        self.assertEqual(args.GetOption("option1"), None)
        self.assertEqual(args.HasOption("option3"), False)
        self.assertEqual(args.GetOption("option3"), None)
        self.assertEqual(args.HasOption("x"), False)
        self.assertEqual(args.GetOption("x"), False)
        self.assertEqual(args.GetBadOptions(), None)
        self.assertEqual(args.GetBadParams(), None)
        
        # List test
        args.Parse(["-o2", "-o3", "myoption", "myparam"])
        self.assertFalse(args.NoArguments())
        self.assertEqual(args.HasParam("p1"), True)
        self.assertEqual(args.HasParam("p2"), False)
        self.assertEqual(args.GetParam("p1"), "myparam")
        self.assertEqual(args.HasOption("option1"), False)
        self.assertEqual(args.GetOption("option1"), None)
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)
        self.assertEqual(args.HasOption("option3"), True)
        self.assertEqual(args.GetOption("option3"), "myoption")
        self.assertEqual(args.HasOption("option4"), False)
        self.assertEqual(args.GetOption("option4"), None)
        self.assertEqual(args.GetBadOptions(), None)
        self.assertEqual(args.GetBadParams(), None)

        # String-based
        args.Parse("-o2 -o3 myoption myparam")
        self.assertFalse(args.NoArguments())
        self.assertEqual(args.HasParam("p1"), True)
        self.assertEqual(args.HasParam("p2"), False)
        self.assertEqual(args.GetParam("p1"), "myparam")
        self.assertEqual(args.HasOption("option1"), False)
        self.assertEqual(args.GetOption("option1"), None)
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)
        self.assertEqual(args.HasOption("option3"), True)
        self.assertEqual(args.GetOption("option3"), "myoption")
        self.assertEqual(args.HasOption("option4"), False)
        self.assertEqual(args.GetOption("option4"), None)
        self.assertEqual(args.HasOption("o1"), False)   # option1 does not have a short form
        self.assertEqual(args.GetOption("o1"), False)   # option1 does not have a short form
        self.assertEqual(args.HasOption("o2"), True)
        self.assertEqual(args.GetOption("o2"), True)
        self.assertEqual(args.HasOption("o3"), True)
        self.assertEqual(args.GetOption("o3"), "myoption")
        self.assertEqual(args.HasOption("o4"), False)
        self.assertEqual(args.GetOption("o4"), None)

        # Double quotes
        args.Parse('-o2 -o3 " myoption  myparam  "')
        self.assertEqual(args.HasOption("option3"), True)
        self.assertEqual(args.GetOption("option3"), "myoption  myparam")
        self.assertEqual(args.GetMissingOptions(), None)

        # Option without value (termination)
        args.Parse("-o2 -o3")
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)
        self.assertEqual(args.HasOption("option3"), False)
        self.assertEqual(args.GetOption("option3"), None)
        self.assertEqual(args.HasParam("p1"), False)
        self.assertEqual(args.GetParam("p1"), None)
        self.assertEqual(args.GetMissingOptions(), ["option3"])

        # Option without value (following)
        args.Parse("-o2 -o3 -o4")
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)
        self.assertEqual(args.HasOption("option3"), False)
        self.assertEqual(args.GetOption("option3"), None)
        self.assertEqual(args.HasOption("option4"), False)
        self.assertEqual(args.GetOption("option4"), None)
        self.assertEqual(args.HasParam("p1"), False)
        self.assertEqual(args.GetParam("p1"), None)
        self.assertTrue("option3" in args.GetMissingOptions())
        self.assertTrue("option4" in args.GetMissingOptions())

        # Option value specified by colon
        args.Parse("-o2 -o3:myoption myparam")
        self.assertEqual(args.HasParam("p1"), True)
        self.assertEqual(args.GetParam("p1"), "myparam")
        self.assertEqual(args.HasOption("option3"), True)
        self.assertEqual(args.GetOption("option3"), "myoption")

        # uArgs initialization
        args = uArgs([("option1"), ("option2", "o2"), ("option3", "o3", True), ("option4", "o4", True)], ["p1", "p2"])
        args.Parse("-o2 -o3 myoption myparam")
        self.assertFalse(args.NoArguments())
        self.assertEqual(args.HasParam("p1"), True)
        self.assertEqual(args.HasParam("p2"), False)
        self.assertEqual(args.GetParam("p1"), "myparam")
        self.assertEqual(args.HasOption("option1"), False)
        self.assertEqual(args.GetOption("option1"), None)
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)
        self.assertEqual(args.HasOption("option3"), True)
        self.assertEqual(args.GetOption("option3"), "myoption")
        self.assertEqual(args.HasOption("option4"), False)
        self.assertEqual(args.GetOption("option4"), None)

        # unexpected option values
        args.Parse("-o2:xxx")
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), False)
        args.Parse("-o2:FAlse")
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), False)
        args.Parse("-o2")
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)
        args.Parse("-o2:TrUe")
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)
        args.Parse("-o2:Three")
        self.assertEqual(args.HasOption("option2"), True)
        self.assertEqual(args.GetOption("option2"), True)

        # bad options and parameters
        args.Parse("-x param1 param2 param3")
        self.assertEqual(args.GetBadOptions(), ["x"])
        self.assertEqual(args.GetBadParams(), ["param3"])
