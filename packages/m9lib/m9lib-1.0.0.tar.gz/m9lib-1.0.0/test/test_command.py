import _test_case
import os

from m9lib import uCommand, uCommandRegistry, uCommandResult
from m9lib import uConfig, uConfigSection
from m9lib import uFileLogger, uLoggerLevel
from m9lib import uDictionary

from m9lib.u_failures import uFailures

def test_init():
    return "test"

class commandTestResult(uCommandResult):

    def __init__(self):
        super().__init__()
        self.details = []
        
    def AddDetailedResult(self, in_string):
        self.details.append(in_string)
        
class commandTest(uCommand):
    
    def __init__(self):
        super().__init__()
        self.SetDefaults([('default_int', 12), ('default_bool', True), ('default_float', "3.33")])
        
    def imp_execute(self, in_preview):
        result = self.GetResult()
        result.AddDetailedResult("This is an interesting line...")
        result.AddDetailedResult("More detailed results...")
        self.LogParam("p1")
        self.LogParam("p2", IfNone=False)
        self.LogMessage("Testing LogParams()")
        self.LogParams(["p1", "p2", ("p9", "Test p9!")], IfNone=False)
        self.LogParamString("Testing LogParamString()")
        self.LogParamString("Three Values: [=p1] [=p2] [=p3]", "Some missing value")
        self.LogParamString("Testing LogParamStrings()")
        self.LogParamStrings(["[=p1]", ("[=p2]", "p2 is empty"), ("[=p3]", "p3 is empty")])

        self.LogMessage("This is a log message")
        self.LogWarning("This is a log warning")
        self.LogError("This is a log error")
        self.LogMessage("Errors: " + str(self.GetResult().CountErrors()))
        return "Success"

uCommandRegistry.RegisterCommand(commandTest, commandTestResult)

class TestCommand(_test_case.uTestCase):

    def setUp(self):
        uFailures.PrintFailures()
        pass

    def init_logfile(self, id):
        logfile = os.path.join(self.GetOutputFolder(r"command"), f"command-{id}.log")
        return uFileLogger(logfile, PrintLevel=uLoggerLevel.INFO, PrintColor=True)

    def test_command(self):
        xParams = {"p1":3, "p2":6, "p3":"7", "p4":"1, 2, 3 "}

        com = uCommandRegistry.NewCommand("commandTest")
        xConfig = uConfig(self.GetFilepath("test_config.ini"))        
        com.SetConfig(xConfig)

        # dict target
        xLogger = self.init_logfile("1-dict")
        com.SetLogger(xLogger)
        com.Execute(xParams)
        self.assertTrue(isinstance(com.params, uDictionary))
        self.assertFileExists(xLogger.GetFilepath())
        self.assertEqual(com.GetParam("default_int"), "12")
        self.assertEqual(com.GetIntParam("default_int"), 12)
        self.assertEqual(com.GetParam("default_bool"), "True")
        self.assertEqual(com.GetBoolParam("default_bool"), True)
        self.assertEqual(com.GetParam("default_float"), "3.33")
        self.assertEqual(com.GetFloatParam("default_float"), 3.33)
        self.assertEqual(com.GetParam("p1"), 3)
        self.assertEqual(com.GetParam("p1", 5), 3)
        self.assertEqual(com.GetParam("p3"), "7")
        self.assertEqual(com.GetIntParam("p3"), 7)
        self.assertEqual(com.GetParam("p9"), None)
        self.assertEqual(com.GetParam("p9", 9), 9)
        self.assertEqual(com.GetListParam("p4"), ['1','2','3'])
        self.assertEqual(com.GetListParam("p9"), None)
        self.assertEqual(com.GetListParam("p9", [0]), [0])
        self.assertTrue(com.IsSuccess ())
        self.assertEqual(com.GetId(), None)
        self.assertEqual(com.GetName(), "commandTest")
        self.assertEqual(com.GetClass(), "commandTest")
        self.assertEqual(com.GetResult().GetCommandId(), None)
        self.assertTrue(com.GetResult().GetDuration()>0)

        # test result messages
        self.assertEqual(len(com.GetResult().GetMessages()), 20)
        self.assertEqual(len(com.GetResult().GetMessages(uLoggerLevel.INFO)), 20)
        self.assertEqual(len(com.GetResult().GetMessages(uLoggerLevel.WARNING)), 2)
        self.assertEqual(len(com.GetResult().GetMessages(uLoggerLevel.ERROR)), 1)

        # dict target with name and id overrides
        xParams['*name'] = "cool_name"
        xParams['*id'] = "cool_id"
        xLogger = self.init_logfile("1x-dict")
        com.SetLogger(xLogger)
        com.Execute(xParams)
        self.assertTrue(isinstance(com.params, uDictionary))
        self.assertEqual(com.GetId(), "cool_id")
        self.assertEqual(com.GetName(), "cool_name")
        self.assertEqual(com.GetClass(), "commandTest")

        # uDictionary target
        com.SetLogger(self.init_logfile("2-udict"))
        com.Execute(uDictionary(xParams))
        self.assertTrue(isinstance(com.params, uDictionary))
        self.assertEqual(com.GetParam("p1"), 3)
        self.assertEqual(com.GetParam("p1", 5), 3)
        self.assertEqual(com.GetParam("p3"), "7")
        self.assertEqual(com.GetIntParam("p3"), 7)
        self.assertEqual(com.GetParam("p9"), None)
        self.assertEqual(com.GetParam("p9", 9), 9)
        self.assertEqual(com.GetListParam("p4"), ['1','2','3'])
        self.assertEqual(com.GetListParam("p9"), None)
        self.assertEqual(com.GetListParam("p9", [0]), [0])
        self.assertTrue(com.IsMatch(Name="cool_name"))
        self.assertTrue(com.IsSuccess ())
        self.assertEqual(com.GetId(), "cool_id")
        self.assertEqual(com.GetResult().GetCommandId(), "cool_id")

        # id target
        com.SetLogger(self.init_logfile("3-idtarget"))
        com.Execute("my_test_id")
        self.assertTrue(isinstance(com.params, uConfigSection))
        self.assertTrue(com.IsSuccess ())
        self.assertEqual(com.GetParam("xxx"), "yyy")
        self.assertEqual(com.GetParam("def1"), "my_default_1")
        self.assertEqual(com.GetParam("def2"), "my_test")
        self.assertEqual(com.GetId(), "my_test_id")
        res = com.GetResult()
        self.assertEqual(com.GetResult().GetCommandId(), "my_test_id")

        # class target
        com.SetLogger(self.init_logfile("4-classtarget"))
        com.Execute()
        self.assertTrue(isinstance(com.params, uConfigSection))
        self.assertTrue(com.IsSuccess ())
        self.assertEqual(com.GetParam("xxx"), "yyy")
        self.assertEqual(com.GetId(), "my_test_id") # from config section, even though not targeted this way
        self.assertEqual(com.GetResult().GetCommandId(), "my_test_id")

        # section target
        com.SetLogger(self.init_logfile("5-sectiontarget"))
        xSection = xConfig.GetSection(Name="commandTest", Id="my_test_id")
        com.Execute(xSection)
        self.assertTrue(isinstance(com.params, uConfigSection))
        self.assertTrue(com.IsSuccess ())
        self.assertEqual(com.GetParam("xxx"), "yyy")
        self.assertEqual(com.GetId(), "my_test_id")
        self.assertEqual(com.GetResult().GetCommandId(), "my_test_id")

        # failure - no config
        xConfig = uConfig(self.GetFilepath("no_config.ini"))        
        com.SetConfig(xConfig)
        xLogger = self.init_logfile("6-noconfig")
        com.SetLogger(xLogger)
        # none found - no class matches found
        uFailures.ClearFailures()
        result = com.Execute()
        self.assertTrue(uFailures.TestFailures(["C21"]))
        self.assertFalse(result.IsSuccess())
        # none found - class name mismatch
        result = com.Execute("my_test_id")
        self.assertFalse(result.IsSuccess())

        xConfig = uConfig(self.GetFilepath("noid_config.ini"))        
        com.SetConfig(xConfig)
        xLogger = self.init_logfile("7-noid_config")
        # default case is success
        result = com.Execute()
        self.assertTrue(result.IsSuccess())
        # no id is failure
        result = com.Execute("no_id_found")
        self.assertFalse(result.IsSuccess())

        pass

