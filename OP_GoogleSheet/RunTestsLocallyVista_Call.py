import sys
import os
import inspect
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
from RunTestsLocallyVista import RunTestsLocallyVista as vista_run
listofitems = [None,None,None,'']
vrun = vista_run(*listofitems)

tests = vrun.GetTestsToRun()
for test in tests:
  resultdict = vrun.RunTests(test)
  resultdict = vrun.ParseResults(resultdict)

