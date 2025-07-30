# https://docs.python.org/3/library/unittest.html

import unittest

from test_args import *
from test_color import *
from test_command import *
from test_control import *
from test_csv import *
from test_dictionary import *
from test_folder import *
from test_format import *
from test_logger import *
from test_scan import *
from test_timer import *
from test_web import *

unittest.main(verbosity=0, exit=False)
unittest.main(verbosity=0, exit=False, module="test_csv")

from  _test_case import uTestCase
uTestCase.WriteSummary()
