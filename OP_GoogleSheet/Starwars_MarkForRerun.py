import re
import sys

sys.path.append(r'C:\project_files\#########################')
sys.path.append(r'C:\project_files\################################')
sys.path.append(r'C:\project_files\#############################')

import starwars_client as starwars
import Configuration as Config

class Starwars_MarkForRerun():
  
  def __init__(self,test_ids,story_changeset_dictionary,issue_review_dict):
    self.test_ids = test_ids
    self.story_changeset_dictionary = story_changeset_dictionary
    self.issue_review_dict = issue_review_dict
    self.id_testNameDict = {}
    
  def GetAllTheTestFromTestIDs(self):
    starwars.Login(Config.STARWARS_TOKEN_PATH)
    starwars.Select_Database(Config.STARWARS_DATABASE)
    for event_id in self.test_ids:
      starwars_testsForEvent = starwars.Get_Test_Cases_For_Test_Event(event_id)
      for file_names in starwars_testsForEvent:
        fileNameinStarwars = file_names['test']['function_name']
        FileIDinStarwars = file_names['test']['id']
        if fileNameinStarwars not in self.id_testNameDict:
          self.id_testNameDict.setdefault(fileNameinStarwars,[])
        self.id_testNameDict[file_names['test']['function_name']] += [FileIDinStarwars, event_id]
        
    return self.id_testNameDict
    
  def GetTestsToMarkBasedOnFilesInReview(self,story_number,id_testNameDict):
    totalFilesMarkedForRerun = []
    totalFilesFoundinEvents = []
    for file in self.story_changeset_dictionary[story_number]:
      if file in id_testNameDict and not file.endswith('.mht') and not file.endswith('.htm') and not file.endswith('.c'):
        totalFilesFoundinEvents.append(file)
         
    return totalFilesFoundinEvents
    
  def GettheFileNameFromStorySummary(self,storySummary):
    fileToMarkInStarwars = []
    filesInStorySummary = storySummary.split()
    for file in filesInStorySummary:
      if file.endswith(".py") or file.endswith(".xml") and file in self.id_testNameDict:
        fileToMarkInStarwars.append(file)
    return fileToMarkInStarwars
    
  def ifFilesFoundDictIsEmpty(self,FilesFoundDictempty):
    if FilesFoundDictempty in [[],None,{}]:
      return True
    else:
      return False
      
  def markForReRunFiles(self, filesMarkedForReRun):
    for file in filesMarkedForReRun:
      starwars.Update_Test_In_Event(int(self.id_testNameDict[file][1]), self.id_testNameDict[file][0], rerun = 1)
    
      
      
    