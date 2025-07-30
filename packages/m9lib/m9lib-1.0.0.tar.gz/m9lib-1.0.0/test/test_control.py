import _test_case
import os

from m9lib import uControl
from m9lib import uCommand,uCommandRegistry, uCommandResult
from m9lib import uType
from m9lib.u_failures import uFailures

class coTestResult(uCommandResult):

    def __init__(self):
        super().__init__()
        self.details = []
        self.fancy = None
        
    def AddDetailedResult(self, in_string):
        self.details.append(in_string)

    def FirstResult(self):
        return self.details[0]

    def GetFancy(self):
        return self.fancy
        
    def SetFancy(self, in_fancy):
        self.fancy = in_fancy
        
class coTest(uCommand):
    
    def imp_execute(self, in_preview):
        result = self.GetResult()
        self.LogParam("myparam")
        self.LogParam("force_errors")
        self.LogMessage("Section name: " + uType.SafeString(self.GetName()))
        self.LogMessage("Section id: " + uType.SafeString(self.GetId()))
        self.LogMessage("Section class: " + uType.SafeString(self.GetClass()))
        # result.AddDetailedResult("result: " )
        self.LogMessage("This is a log message")
        self.LogWarning("This is a log warning")
        if self.GetControl().__class__.__name__ == "controlTest":
            self.LogMessage("Fancy value is " + uType.SafeString(self.GetControl().Fancy()))
            result.SetFancy(self.GetControl().Fancy())
        else:
            result.SetFancy("Not Fancy")

        cnt_force_errors = self.GetIntParam("force_errors")
        if cnt_force_errors is not None:
            for errno in range(cnt_force_errors):
                self.LogError("Failure number {s}".format(s=errno+1))

        force_result = self.GetParam("force_result")
        if force_result is not None:
            return force_result
        
        return "Success"
    
uCommandRegistry.RegisterCommand(coTest, coTestResult)

class controlTest(uControl):

    def __init__(self, filepath):
        super().__init__("MyControl", filepath)

    def Fancy(self):
        return "999"
    
    def imp_ini_command (self, in_command):
        skip = in_command.GetBoolParam("skip_me")
        if skip is None:
            return None
        if skip is True:
            return False
        return True
    
    def imp_prepare (self):
        self.GetLogger().WriteLine("@prepare step")
        self.GetLogger().WriteLine(self.GetConfig ().GetSectionValue ("Prepare", "message"))

    def imp_finalize (self):
        self.GetLogger().WriteLine("@finalize step")
        self.GetLogger().WriteLine(str(len(self.GetResults())) + " results")
        for result in self.GetResults():
            self.GetLogger().WriteLine("Result for {cls}:{id} is {fr}".format(cls=result.GetCommandClass(), id=result.GetCommandId(), fr=str(result.GetResult())))

        self.GetLogger().WriteLine("There were a total of {e} errors.".format(e=self.CountTotalErrors()))

        return "SuperGood"

class TestControl(_test_case.uTestCase):

    def setUp(self):
        uFailures.PrintFailures()
        pass

    def test_control(self):
        logfile = os.path.join(self.GetOutputFolder(r"control"), "test_control.log")

        # ------------------------------------------------------------
        # controlTest: Execute list from configuration
        # ------------------------------------------------------------
        # [coTest:com1] -> Success
        # [coTest:com2] -> "This is a forced result from configuration"
        # [Quad:com4] -> Success

        control = controlTest(self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute ()
        self.assertTrue(uFailures.TestFailures(["C04", "C07", "C09"]))
        self.assertFileExists(logfile)
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result="SuperGood", cnt_results=3, cnt_success=2, cnt_failure=1, cnt_skipped=1))
        self.assertTrue(self.command_result(control, find_id="com1", co_name="coTest", co_class="coTest", co_success=True))

        # basic run info
        self.assertEqual(control.CountTotalErrors (), 13)
        # count sub commands
        self.assertEqual(len(control.GetResults (Name="coTest")), 2)
        self.assertEqual(len(control.GetResults (Name="Quad")), 1)
        # command info
        self.assertEqual(control.GetResults (Name="Quad")[0].GetSectionName(), "Quad")
        self.assertEqual(control.GetResults (Name="Quad")[0].GetCommandClass(), "coTest")
        self.assertEqual(control.GetResults (Name="Quad")[0].GetCommandId(), "com4")
        # result info
        self.assertEqual(control.GetResults (IsSuccess=False)[0].GetCommandId(), "com2")
        self.assertEqual(control.GetResults (Name="Quad")[0].GetFancy(), "999")
        # getresult calls
        self.assertEqual(control.GetResult("Quad").GetCommandId(), "com4")
        self.assertEqual(control.GetResult("com2").GetCommandId(), "com2")
        self.assertEqual(control.GetResult("com9"), None)

        # ------------------------------------------------------------
        # uControl: Execute list from configuration
        # ------------------------------------------------------------
        # [coTest:com1] -> Success
        # [coTest:com2] -> "This is a forced result from configuration"
        # [coTest:com7] -> Success
        # [Quad:com4] -> Success

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute ()
        self.assertTrue(uFailures.TestFailures(["C04", "C07"]))
        self.assertFileExists(logfile)
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result=False, cnt_results=4, cnt_success=3, cnt_failure=1, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="com1", co_name="coTest", co_class="coTest", co_success=True))
        self.assertTrue(control.GetDuration()>0)

        # basic run info
        self.assertEqual(control.CountTotalErrors (), 13)
        self.assertEqual(control.GetSkipped (), [])         # none skipped
        # count sub commands
        self.assertEqual(len(control.GetResults (Name="coTest")), 3)
        self.assertEqual(len(control.GetResults (Name="Quad")), 1)
        # command info
        self.assertEqual(control.GetResults (Name="Quad")[0].GetSectionName(), "Quad")
        self.assertEqual(control.GetResults (Name="Quad")[0].GetCommandClass(), "coTest")
        self.assertEqual(control.GetResults (Name="Quad")[0].GetCommandId(), "com4")
        # result info
        self.assertEqual(control.GetResults (IsSuccess=False)[0].GetCommandId(), "com2")

        # ------------------------------------------------------------
        # uControl: Execute by id (Success)
        # ------------------------------------------------------------
        # [coTest:com1] -> True

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute ("com1")
        summary = control.GetSummary()
        self.assertTrue(uFailures.TestFailures([]))
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result=True, cnt_results=1, cnt_success=1, cnt_failure=0, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="com1", co_name="coTest", co_class="coTest", co_success=True))

        # ------------------------------------------------------------
        # uControl: Execute by id (Failure)
        # ------------------------------------------------------------
        # [coTest:com2] -> "This is a forced result from configuration"

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute (["com2"])
        self.assertTrue(uFailures.TestFailures([]))
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result=False, cnt_results=1, cnt_success=0, cnt_failure=1, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="com2", co_name="coTest", co_class="coTest", co_success=False))

        # ------------------------------------------------------------
        # uControl: Execute by Name that is a Class
        # ------------------------------------------------------------
        # [coTest:com2] -> "This is a forced result from configuration"

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute ("coTest")
        self.assertTrue(uFailures.TestFailures([]))
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result=False, cnt_results=4, cnt_success=3, cnt_failure=1, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="com1", co_name="coTest", co_class="coTest", co_success=True))

        # ------------------------------------------------------------
        # uControl: Execute by Name that is NOT a Class
        # ------------------------------------------------------------
        # [coTest:com2] -> "This is a forced result from configuration"

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute ("Quad")
        self.assertTrue(uFailures.TestFailures([]))
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result=True, cnt_results=1, cnt_success=1, cnt_failure=0, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="com4", co_name="Quad", co_class="coTest", co_success=True))

        # ------------------------------------------------------------
        # uControl: Execute by id list
        # ------------------------------------------------------------
        # [coTest:com2] -> "This is a forced result from configuration"

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute ("com1, com2")
        self.assertTrue(uFailures.TestFailures([]))
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result=False, cnt_results=2, cnt_success=1, cnt_failure=1, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="com1", co_name="coTest", co_class="coTest", co_success=True))
        self.assertTrue(self.command_result(control, find_id="com2", co_name="coTest", co_class="coTest", co_success=False))

        # ------------------------------------------------------------
        # uControl: Execute by group
        # ------------------------------------------------------------
        # [coTest:com2] -> "This is a forced result from configuration"

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.Execute ("gr1")
        self.assertTrue(uFailures.TestFailures(["C04"]))
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertTrue(self.count_results(control, final_result=False, cnt_results=3, cnt_success=2, cnt_failure=1, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="com1", co_name="coTest", co_class="coTest", co_success=True))
        self.assertTrue(self.command_result(control, find_id="com2", co_name="coTest", co_class="coTest", co_success=False))
        self.assertTrue(self.command_result(control, find_id="com7", co_name="coTest", co_class="coTest", co_success=True))

        # ------------------------------------------------------------
        # uControl: Execute target command
        # ------------------------------------------------------------
        # [coTest:com2] -> "This is a forced result from configuration"

        control = uControl("MyControl", self.GetFilepath("test_control.ini"))
        uFailures.ClearFailures()
        control.ExecuteCommand("coTest", {"*id": "my_id", "*name": "my_name", "force_errors": 3})
        self.assertTrue(uFailures.TestFailures([]))
        summary = control.GetSummary()
        self.assertTrue(self.count_validation(control))
        self.assertEqual(control.CountTotalErrors (), 3)
        self.assertTrue(self.count_results(control, final_result=True, cnt_results=1, cnt_success=1, cnt_failure=0, cnt_skipped=0))
        self.assertTrue(self.command_result(control, find_id="my_id", co_name="my_name", co_class="coTest", co_success=True))

    def command_result(self, control, find_id, co_name, co_class, co_success):
        results = control.GetResults(Id=find_id)
        if len(results)!=1:
            return False
        
        if results[0].GetSectionName() != co_name:
            return False
        
        if results[0].GetCommandClass() != co_class:
            return False
        
        if results[0].IsSuccess() != co_success:
            return False
        
        return True

    def count_results(self, control, final_result, cnt_results, cnt_success, cnt_failure, cnt_skipped):
        if control.GetFinalResult() != final_result:
            return False
        
        if len(control.GetResults ()) != cnt_results:
               return False
        
        if control.CountSuccess () != cnt_success:
               return False

        if control.CountSuccess (IsSuccess=False) != cnt_failure:
               return False

        if control.CountSuccess (IsSuccess=None) != cnt_skipped:
               return False

        return True

    def count_validation(self, control):
        summary = control.GetSummary()
        if summary['total_commands'] != len(summary['results']):
            return False

        if summary['total_commands'] != summary['count_skipped']+summary['count_success']+summary['count_failure']:
            return False
        
        if summary['count_success']+summary['count_failure'] != len(control.GetResults ()):
            return False
        
        if summary['count_success'] != control.CountSuccess():
            return False

        if summary['count_failure'] != control.CountSuccess(False):
            return False

        if summary['count_skipped'] != control.CountSuccess(None):
            return False

        return True
    