import os
import sys
import inspect
import fnmatch
import re
import time
sys.path.append(os.path.dirname(os.path.abspath((inspect.getfile(inspect.currentframe())))))
import Configuration as Config


class RunTestsLocallyVista():

  def __init__(self,review_changeset_dict, issue_review_dict, testNameFromSummaryDict,story_number):
    self.review_changeset_dict = review_changeset_dict
    self.issue_review_dict = issue_review_dict
    self.testNameFromSummaryDict = testNameFromSummaryDict
    self.story_number = story_number
    self.tests = {}
    self.test_status_dict = {}
    
  def computeFilesToRunFromReview(self):
    testsFoundinReview = []
    if os.path.isfile(Config.PATH_TO_FILES_TO_RUN):
      os.remove(Config.PATH_TO_FILES_TO_RUN)
    with open(Config.PATH_TO_FILES_TO_RUN,'w') as f:
      if self.story_number in self.review_changeset_dict:
        f.write(",".join(self.review_changeset_dict[self.story_number]))
        
      else:
        f.write(testNameFromSummaryDict[self.story_number])
        
  def GetTestsFromProgram(self):
    automated = {}
    for root,dirnames,filenames in os.walk(Config.VERIFICATION_ARC):
      for file in fnmatch.filter(filenames, '*.py'):
        with open(os.path.join(root, file)) as f:
          contents = f.read()
          if not re.findall("framework.confirm", contents) and not re.findall("raw_input", contents):
            if file not in automated:
              automated.setdefault(file,[])
            automated[file] += [root + "\\" + file]
    self.tests = automated.copy()

    return self.tests
    
  def GetTestsToRun(self):
    teststoRunDict = []
    with open(Config.PATH_TO_FILES_TO_RUN,'r') as f:
      content = f.read()
      content = content.strip()
      tempdict = content.split(',')
      for file in tempdict:
        if file.endswith('.c') or file.endswith('.py'):
          teststoRunDict.append(file)
    return teststoRunDict
    
  def RunTests(self,teststoRun):
    self.GetTestsFromProgram()
    logpathList = []
    if teststoRun in self.tests:
      import dwmRunTest
      dwmRunTest.rtp(teststoRun)
    return self.tests[teststoRun]
    
    
  def ParseResults(self,logpathList):
    traceback = ""
    testStatus = "CRASHED"
    coverage = ""
    passedTests = failedTests = totalTests = erroredTests = 0
    dispositioned = False
    
    if logpathList not in ['',[], None] :
      for logFilePath in logpathList :
        if os.path.isfile(logFilePath):
          traceback = ""
          logFile = [line.rstrip('\n') for line in open(logFilePath)]
          # Parse out a summary of the log file
          try:
            for lineContents in logFile:
               if (lineContents.find("Total Tests  :") != -1):
                  totalTests = int(lineContents.split(":")[1])
               if (lineContents.find("Tests Failed :") != -1): 
                  failedTests = int(lineContents.split(":")[1]) 
               if (lineContents.find("Tests Passed :") != -1): 
                  passedTests = int(lineContents.split(":")[1])
               if (lineContents.find("Errors       :") != -1): 
                  erroredTests = int(lineContents.split(":")[1])
            
            #If we've made it here, we've been able to parse the log file as well as coverage data (if applicable)
            if failedTests == 0 and passedTests == 0:
              #No steps must have been marked for integration, or the test crashed and no pass/fails were logged.
              testStatus = "CRASHED"
              traceback = "No test steps were executed. This likely indicates an issue with the test. See log for details."
            elif erroredTests > 0:
              testStatus = "CRASHED"
              traceback = "Errors occured during test run. See log for details."
            elif failedTests > 0:
              testStatus = "FAILED"
            else:
              testStatus = "PASSED"
            with open(logFilePath) as logFile:
              lines = logFile.read()  # We need to do a read here instead of readlines so we can parse the entire file at once
            scaErrRe = re.compile(r'Error using verify_TC.*\n((?:.|\n)+)(?=Log File Summary)')  # For SCA crashes
            errMatch = scaErrRe.search(lines)
            if errMatch:
              traceback = errMatch.group(1).strip()
          
          except Exception:
            testStatus = "CRASHED"
          
    self.test_status_dict = {"status":testStatus, "passed":passedTests, "failed":failedTests, "total":totalTests,"errored":erroredTests, "traceback":traceback, "dispositioned":False}
    return self.test_status_dict
    
        
    