import _test_case

import os

from m9lib import uLogger, uLoggerLevel, uFileLogger

class TestLogger(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_logger(self):

        # uLogger

        l = uLogger()
        print ("+++ Default logger")
        l.WriteDetails("Sample Details")
        l.WriteLine("Sample Line")
        l.WriteWarning("Sample Warning")
        l.WriteError("Sample Error")

        print ("+++ Color logger")
        l = uLogger(PrintLevel=uLoggerLevel.DETAILS, PrintColor=True)
        l.SetWriteLevel(uLoggerLevel.DETAILS)
        l.WriteDetails("Sample Details")
        l.WriteLine("Sample Line")
        l.WriteWarning("Sample Warning")
        l.WriteError("Sample Error")
        l.WriteLine("[+BLUE]Colored [+VIOLET]Line[+]")
        l.WriteError("[+BLUE]Colored [+BG_RED]Error[+]")

        # file logger
      
        filepath = os.path.join(self.GetOutputFolder("logger"), "logger.log")
        l = uFileLogger(filepath)
        l.WriteHeader("Sample Header")
        l.WriteSubHeader("Sub Header")

        l.ConfigFormat(SubheaderChar='*')
        l.WriteSubHeader("Star Header")
        l.WriteLine("Sample line")
        l.WriteSubDivider('~')
        l.WriteWarning("Sample warning")
        l.WriteError("Sample error")
        l.WriteError("Sample error")

        l.WriteSubDivider(Padding=True)
        l.WriteLine ("Warning count: " + str(l.GetWarningCount()))
        l.WriteLine ("Error count: " + str(l.GetErrorCount()))

        self.assertFileExists(filepath)
        self.assertEqual(l.GetWarningCount(), 1)
        self.assertEqual(l.GetErrorCount(), 2)
