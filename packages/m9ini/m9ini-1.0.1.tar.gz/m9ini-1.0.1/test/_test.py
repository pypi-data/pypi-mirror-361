# https://docs.python.org/3/library/unittest.html

import unittest

from test_config import *
from test_expansion import *
from test_merge import *
from test_substitution import *

uConfig.PrintFailures(True, True)

unittest.main(verbosity=0, exit=False)
# unittest.main(verbosity=0, exit=False, module="test_config")
# unittest.main(verbosity=0, exit=False, module="test_merge")

from  _test_case import uTestCase
uTestCase.WriteSummary()
