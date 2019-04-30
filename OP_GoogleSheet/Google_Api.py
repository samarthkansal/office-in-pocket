
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import re
import gspread
import sys
sys.path.append(r'C:\Users\skansal\Desktop\Agile_Tool\Agile_Send_Email')
from AgileData_email import AgileData_email
agile = AgileData_email()

import Configuration as Config
import os 
import requests
from requests.auth import HTTPBasicAuth
import datetime
import json
import time
import subprocess
import inspect
from threading import Thread

sys.path.append(os.path.dirname(os.path.abspath((inspect.getfile(inspect.currentframe())))))
from RunTestsLocallyVista import RunTestsLocallyVista



class Google_Api(RunTestsLocallyVista):
    def __init__(self):
      self.google_sheet = None
      self.worksheet = None
      self.list_of_cells = {}
      self.stories = []
      self.old_request = {}
      self.new_request = {}
      self.google_sheet_data = None
      self.count = 14
      self.sprintName = '' 
      self.userName = ''
      self.password = ''
      self.story_subtask_dictionary = None
      self.sprintID = ''
      self.labelName = []
      self.projectID = ''
      self.review_changeset_dict = {}
      self.issue_review_dict = {}
      self.starwarsMarkForRerunON = True
      self.test_ids =[95,103,104]
     
    def intializeVariables(self,story_subtask_dictionary,userName,password,*args): 
      
      self.story_subtask_dictionary = story_subtask_dictionary
      self.userName = userName
      self.password = password
      self.sprintName = args[0]
      self.sprintID = args[1]
      self.labelName = args[2]
      self.projectID = args[3]

    def create_object_of_gSheet(self):
      worksheet_needed = None
      google_sheet_open = None
      self.count = self.count+1
      if self.worksheet in [None,'',' '] or self.count % 15 == 0:
        scope = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\skansal\Desktop\Agile_Tool\Agile_Google_Sheets\Rest API-db110e7f03df.json',scope)
        self.google_sheet = gspread.authorize(credentials)
        google_sheet_open = self.google_sheet.open("project_Agile_Board")
        google_work_sheets = google_sheet_open.worksheets()
        work_sheet_to_work = google_work_sheets[-1]
        self.worksheet = google_sheet_open.get_worksheet(len(google_work_sheets)-1)
      
      worksheet_needed = self.checkIf_newSheetisNeeded()
      
      if worksheet_needed and google_sheet_open != None:
          self.worksheet = google_sheet_open.add_worksheet(title="_{}_".format(self.sprintName),rows="1000",cols="20")
          self.read_allData_ofGsheet()
          print("New Sheet Added:")
          
      else:  
        old_stories_deleted,stories_to_delete = self.checkIf_oldStoriesDeleted()   
        if old_stories_deleted: 
            self.delteoldStories(stories_to_delete)
            print("Old Stories have been deleted")
            time.sleep(100)
            
        if self.checkIf_newStoriesAdded():
            self.intialize_cells()
            self.fillOut_cellData_AndUpdateExistingCells()
            print("New Stories have been added")        
        

          
          
    def delteoldStories(self, old_stories_deleted):
      cell_list_deleted = [] 
      for story_to_delete in old_stories_deleted:
        cell = self.worksheet.find(story_to_delete)
        cell_list_deleted += self.worksheet.range('A{}:I{}'.format(cell.row,cell.row))
        
        for cells in cell_list_deleted:
          cells.value = ""
      self.worksheet.update_cells(cell_list_deleted)
      time.sleep(100)
      
      
    def checkIf_newSheetisNeeded(self):
      count = 0
      status = False
      if self.read_allData_ofGsheet():
        for story in self.read_allStories_ofGsheet():
          if story not in self.story_subtask_dictionary:
            count = count+1
      if count>=15:
        status = True
      return status  
      
    def checkIf_newStoriesAdded(self):
      if self.google_sheet_data in [None,[],[[]]]:
        google_sheet_data = self.read_allStories_ofGsheet()
      else:
        google_sheet_data = self.google_sheet_data
      google_sheet_data = self.read_allStories_ofGsheet()
      count = 0
      status = False
      stories_inGsheet =[]
          
      if self.story_subtask_dictionary:
        for story in self.story_subtask_dictionary.keys():
          if story not in google_sheet_data:
            print("story_Added",stories_inGsheet)
            count = count+1
      if count < 15 and count > 0 :
        status = True
      return status
      
    def checkIf_oldStoriesDeleted(self):
      if self.google_sheet_data in [None,[],[[]]]:
        google_sheet_data = self.read_allStories_ofGsheet()
      else:
        google_sheet_data = self.google_sheet_data
      count = 0
      status = False
      stories = []
      if google_sheet_data:
        for story in self.read_allStories_ofGsheet():
          if story not in [None,[],'Story Number'] and story not in self.story_subtask_dictionary:
            stories.append(story)
            print("story_mismatch, This story seems to have been push out of the current sprint:",story)
            count = count+1
      if count < 15 and count > 0 :
        status = True
      return status,stories
      
    def read_allData_ofGsheet(self):
      self.google_sheet_data = self.worksheet.get_all_values()
      return self.google_sheet_data
      
    def read_allStories_ofGsheet(self):
      story_list = []
      if self.google_sheet_data in [None,[],[[]]]:
        google_sheet_data = self.read_allStories_ofGsheet()
      else:
        google_sheet_data = self.google_sheet_data
      for story in google_sheet_data:
        exp = re.findall('GSFDSA-\d+',story[0].strip())
        for str in exp:
          story_list.append(str)
      return story_list
      
    def check_data_in_google_sheet(self):
      if self.google_sheet_data in [None,[],[[]]]:
        self.read_allData_ofGsheet()
      self.intialize_cells()
      if self.google_sheet_data in [None,[],[[]]]:
        self.add_header_to_google_sheet()
        self.fillOut_cellData_AndUpdateExistingCells()
      else:
        self.compareDataWithNewRequest(self.google_sheet_data)
      self.get_review_id_for_issue()
      self.getStarwarsRerunInput()
      self.runLocally()
      self.read_allData_ofGsheet()
      
    def add_header_to_google_sheet(self):
      #if (not self.worksheet.row_values(1)) or (self.worksheet.row_values(1) == None):
        cell_header = {'11':'Story Number','12':'Summary','13':'Status','14':'Assignee',
                       '15':'Sub Tasks','16':'Review Raised ?','17':'Mark for Rerun Starwars ?',
                       '18':'Run Locally ?','19':'Comments'}
        cells = self.worksheet.range("A1:I1")
        for cell in cells:
          cell_position = str(cell.row)+str(cell.col)
          cell.value = cell_header[cell_position]
        self.worksheet.update_cells(cells)
    
    def intialize_cells(self):
      rows_in_sheet = len(self.story_subtask_dictionary.keys())
      rows_in_sheet= rows_in_sheet+1
      cells_story = self.worksheet.range("A2:A{}".format(rows_in_sheet))
      cells_summary = self.worksheet.range("B2:B{}".format(rows_in_sheet))
      cells_status = self.worksheet.range("C2:C{}".format(rows_in_sheet))
      cells_assignee = self.worksheet.range("D2:D{}".format(rows_in_sheet))
      cells_subtasks = self.worksheet.range("E2:E{}".format(rows_in_sheet))
      cells_review = self.worksheet.range("F2:F{}".format(rows_in_sheet))
      cells_starwars_rerun = self.worksheet.range("G2:G{}".format(rows_in_sheet))
      cells_run_locally = self.worksheet.range("H2:H{}".format(rows_in_sheet))
      cells_comment = self.worksheet.range("I2:I{}".format(rows_in_sheet))
      
      self.list_of_cells = {
                       "Stories":cells_story,"Summary":cells_summary,
                       "Status":cells_status,"Assignee":cells_assignee,
                       "Review":cells_review,"Starwars":cells_starwars_rerun,
                       "RunLocally":cells_run_locally,"Comments":cells_comment,
                       "SubTask":cells_subtasks
                      }
      return self.list_of_cells
    
    def fillOut_cellData_AndUpdateExistingCells(self,story_comment = None, story_review = None,review_comment = None):
      subtask_id = []
      story_cells = []
      story_keys = list(self.story_subtask_dictionary.keys())
      for cells in self.list_of_cells:
        for i,cell in enumerate(self.list_of_cells[cells]):
          subtask_id = [x for x in self.story_subtask_dictionary[story_keys[i]].keys() if x not in ['Status','Assignee','Summary']]
          if cells in ['Stories']:
            cell.value = story_keys[i]
          elif cells in ['Summary','Status','Assignee']:
            cell.value = self.story_subtask_dictionary[story_keys[i]][cells]
          elif cells in ['RunLocally','Starwars']:
            cell.value = "No"
          elif cells == "Review" and story_review:
            cell.value = "- ReviewID - {}\n- Review Creator - {}\n- Review State - {}".format(story_review[story_keys[i]][1],story_review[story_keys[i]][0],story_review[story_keys[i]][2]) if story_keys[i] in story_review else ""
            
            
          elif cells == "SubTask":
            # this is to take the subtask out of the dict
            
            def appp(id):
              if self.story_subtask_dictionary[story_keys[i]][id][1] in ['',' ']:
                Assignee = "Unassigned"
              else: 
                Assignee = self.story_subtask_dictionary[story_keys[i]][id][1]
              value = "Subtask ID -"+id+"\nSummary - "+self.story_subtask_dictionary[story_keys[i]][id][2]\
                      +"\nAssignee -"+Assignee\
                      +"\nStatus - "+self.story_subtask_dictionary[story_keys[i]][id][0]
              return value
            cell.value = "\n\n".join(list(map(appp,subtask_id))) if subtask_id else "No Subtask for this Story"
            
          elif (cells == "Comments") and (story_comment not in ['',{},' ',None] or review_comment not in ['',{},' ',None]):
            time_s = datetime.datetime.now()
            time_stamp = time_s.strftime("%Y-%m-%d  %I:%M %p")
           
            if story_comment not in ['',[],None,{}]:
                cell.value += "\n"+story_comment[story_keys[i]]+"\t("+str(time_stamp)+")"+"\n" if story_keys[i] in story_comment else ""
            else:  
                cell.value += "\n".join(review_comment[story_keys[i]])+"\t("+str(time_stamp)+")"+"\n" if story_keys[i] in review_comment else ""
        self.worksheet.update_cells(self.list_of_cells[cells])
        
    def compareDataWithNewRequest(self, google_sheet_data):
      comment = '' 
      storyStatus_in_new_request = ''
      storyAssignee_in_new_request = ''
      story_comment = {}
      self.stories = list(self.story_subtask_dictionary.keys())
      google_data = self.google_sheet_data
      for story in google_data:
        if story and story[0] not in["Story Number",'',' ',None,[]]:
          storyStatus_in_new_request = self.story_subtask_dictionary[story[0]]['Status'] if self.story_subtask_dictionary[story[0]] not in ['',' '] and story[0] in self.story_subtask_dictionary else ''
          storyAssignee_in_new_request = self.story_subtask_dictionary[story[0]]['Assignee'] if self.story_subtask_dictionary[story[0]] not in ['',' '] and story[0] in self.story_subtask_dictionary else ''
          storyStatus_in_old_request = story[2]
          storyAssignee_in_old_request = story[3]
          if ((storyStatus_in_new_request != storyStatus_in_old_request) or (storyAssignee_in_new_request != storyAssignee_in_old_request)):
            if (storyStatus_in_new_request != storyStatus_in_old_request):
              comment += "-Status of this story has been changed from "+storyStatus_in_old_request+" to "+storyStatus_in_new_request+"\n"
            if (storyAssignee_in_new_request != storyAssignee_in_old_request):
              comment += "-Story Assignee has been changed to " + storyAssignee_in_new_request+" This story was assigned to "+storyAssignee_in_old_request+"\n"
            if story[0] not in story_comment and comment not in['',' ']:
              story_comment.setdefault(story[0],comment)
            elif story[0] in story_comment and comment not in['',' ']: 
              story_comment[story[0]]+=comment
          comment = '' 
            
          # To update the cells for subtask Assignee and subtask status 
          if story[4]:
            
            subtasks = story[4].strip().split("Subtask ID -")
            if subtasks[0]not in ['No Subtask for this Story',[]]:
              for subtask in subtasks:
                if subtask not in ['',' ',None]:
                  subtask_id = subtask.split("\n")[0]
                  subtask_status_Gsheet= subtask.strip().replace("Status - ","").split("\n")[-1]
                  subtask_assignee_Gsheet = subtask.strip().replace("Assignee -","").split("\n")[-2]
                  subtask_status_newrequest= self.story_subtask_dictionary[story[0]][subtask_id][0]
                  subtask_assignee_newrequest = self.story_subtask_dictionary[story[0]][subtask_id][1]
                  if subtask_assignee_newrequest in ['',' ',None]:
                    subtask_assignee_newrequest = "Unassigned"
                  
                  if subtask_status_Gsheet != subtask_status_newrequest and subtask_status_newrequest:
                    comment += "-Status of the subtask -({}) has been changed from {} to {}".format(subtask_id,subtask_status_Gsheet,subtask_status_newrequest)+"\n"
                  if subtask_assignee_Gsheet != subtask_assignee_newrequest and subtask_assignee_newrequest:
                    comment += "-Assignee of the subtask -({}) has been changed from {} to {}".format(subtask_id,subtask_assignee_Gsheet, subtask_assignee_newrequest)+"\n"
                  if story[0] not in story_comment and comment not in['',' ']:
                    story_comment.setdefault(story[0],comment)
                  elif story[0] in story_comment and comment not in['',' ']: 
                    story_comment[story[0]]+=comment
                  comment = "" 
        comment = "" 
        
      if story_comment not in ['',' ',{},None]:
        self.fillOut_cellData_AndUpdateExistingCells(story_comment=story_comment)
        print("Updated sheet for:")
        print(story_comment)
          
    def compareReviewData(self,story_review_dict,review_changeset_dict):
    
      review_data_in_Gsheet = self.google_sheet_data
      stories = self.stories
      story_review_dict_inGsheet = {}
      story_review_comment = {}
      comment =''
      comment_status = False
      review_info_list=[]
      review_number_inPdfs = []
      
      for data_in_sheet in review_data_in_Gsheet:
        review_info = data_in_sheet[5]
        review_info_list = review_info.replace("- ReviewID - ","").replace("- Review State - ","").replace("- Review Creator - ","").split("\n")
        if data_in_sheet[0] not in ['',' ',None,[],"Story Number"] and review_info not in ['',' ',None,[],'Review Raised']:
          if data_in_sheet[0] not in story_review_dict:
            story_review_dict_inGsheet.setdefault(data_in_sheet[0],[])
            story_review_dict_inGsheet[data_in_sheet[0]]+="".join(review_info_list)
          if review_info_list not in ['',' ' , None,[]] and data_in_sheet[0] in story_review_dict and story_review_dict[data_in_sheet[0]][2] != review_info_list[2]:
            comment += "-Review state has been changed from {} to {}\n".format(review_info_list[2],story_review_dict[data_in_sheet[0]][2])
            
            if comment not in ['',' ',None] and data_in_sheet[0] not in story_review_comment:
              story_review_comment.setdefault(data_in_sheet[0],[])
            story_review_comment[data_in_sheet[0]]+= [comment]
            comment_status = True
            comment=''
            
          # Logic to create an action item  
          if story_review_dict[data_in_sheet[0]][2] == "Closed"  and review_info_list[2]!= story_review_dict[data_in_sheet[0]][2] and review_info_list[2] == 'Open' and data_in_sheet[0] in review_changeset_dict:
            for file in review_changeset_dict[data_in_sheet[0]]:
              if file.endswith(".pdf"):
                review_number_inPdfs += [file]
            review_number_inPdfs = list(set(review_number_inPdfs))
           
            if review_number_inPdfs not in [[],'',' ',None]:
              review_number_inPdfs = list(set(review_number_inPdfs))
              #self.readPDFDocument(review_number_inPdfs)
              action_item_number = self.create_action_item(review_number_inPdfs,story_review_dict[data_in_sheet[0]][1])
              if action_item_number not in [None,[],'',' ']:
                comment += "-An Action item {} has been created for the review {} as this review has just been closed out".format(action_item_number,story_review_dict[data_in_sheet[0]][1])+"\n"
                comment_status = True
              else: 
                print("Logic to create the Action item implemented but it returned an empty Action_tem_number:Pay Heed")
                         
              if comment not in ['',' ',None] and data_in_sheet[0] not in story_review_comment:
                story_review_comment.setdefault(data_in_sheet[0],[])
              story_review_comment[data_in_sheet[0]]+= [comment]
              comment=''
              
            del review_number_inPdfs[:]
              

      if story_review_dict_inGsheet not in ['',' ',{},[]]:
        for review in story_review_dict:
          if story_review_dict_inGsheet not in ['',' ',[],None,{}] and review not in story_review_dict_inGsheet:
            comment += "-{} has raised the review for this story.\n".format(story_review_dict[review][0])
            comment_status = True
          if review not in story_review_comment:
            story_review_comment.setdefault(review,[])
          story_review_comment[review] += [comment]
          comment = ''
        
      if story_review_dict:
        self.fillOut_cellData_AndUpdateExistingCells(review_comment=story_review_comment)
      
    def readPDFDocument(self,PDFDictionary):
      import pdb
      pdb.set_trace()
      for pdf in PDFDictionary:
        directory_name = re.findall('GSFDSA-\d+',pdf)[0]
        if os.path.isdir(Config.PDF_DOCUMENTPATH+"\\"+directory_name):
          pdf_object = parser.from_file(Config.PDF_DOCUMENTPATH+"\\"+directory_name+"\\"+pdf)
          print(pdf_object['content'])
          return True  
        else:
          print("Directory not found {} for the pdf".format(directory_name,pdf))
          return False
      
    def get_review_id_for_issue(self):
      issue_review_dict = {}
      cruc_list = []
      
     
      with requests.Session() as se:
        se.headers.update({'Accept':'application/json'})
        se.auth=(self.userName,self.password)
        for story_id in self.stories:
          url = 'url to Crucible I am not supposed to share the url of the companies server.'.format(str(story_id))
          se.get('url to Crucible I am not supposed to share the url of the companies server.')
          response = se.get(url)
          python_crucible_info = json.loads(response.text)
          if python_crucible_info['reviewData'] not in ['',' ', None,[]]:
            for info in python_crucible_info['reviewData']:
              author_review = info['creator']['displayName'] if info['creator']['displayName'] else "No author found for the review for this story"
              jira_issue = info['jiraIssueKey']
              review_number = info['permaIdHistory'][0] if info['permaIdHistory'][0] else "No review number found for this story"
              cruc_list.append(review_number)
            if jira_issue not in issue_review_dict:
              issue_review_dict.setdefault(jira_issue,[])
            issue_review_dict[jira_issue] += [author_review,review_number]
      self.getReviewState(issue_review_dict)
            
    def getReviewState(self, issue_review_dict):
      with requests.Session() as se:
        se.headers.update({'Accept':'application/json'})
        se.auth=(self.userName,self.password)
        for jira_issue_number in issue_review_dict:
          url2 = 'url to Crucible I am not supposed to share the url of the companies server.'.format(issue_review_dict[jira_issue_number][1])
          se.get('url to Crucible I am not supposed to share the url of the companies server.')
          review_state_response = json.loads(se.get(url2).text)
          if review_state_response['reviewData'] not in ['',' ', None,[]]:
            review_state = review_state_response['reviewData'][0]['state']
            if review_state == "Review":
              review_state = "Open"
            issue_review_dict[jira_issue_number] += [review_state]
      self.issue_review_dict = issue_review_dict.copy()
      self.getChangeSetFromReview(issue_review_dict)
      
    '''
    issue_review_dict[jira_issue_number] = [author_review,review_number,review_state]
    '''
        
    def getChangeSetFromReview(self, issue_review_dict):
      with requests.Session() as se:
        se.headers.update({'Accept':'application/json'})
        se.auth=(self.userName,self.password)
        # Logic to get the changeset from the review          
        for story in issue_review_dict:
            review_number = issue_review_dict[story][1]
            
            url3 = 'url to Crucible I am not supposed to share the url of the companies server.'.format(review_number)
            review_state_response = json.loads(se.get(url3).text)
            
            if story not in review_state_response:
              self.review_changeset_dict.setdefault(story,[])
            for file_in_review in review_state_response['reviewItem']:
              self.review_changeset_dict[story]+=[file_in_review['toContentUrl'].split("/")[-1]]
            
      self.fillOut_cellData_AndUpdateExistingCells(story_review = issue_review_dict)
      if issue_review_dict not in [None,{},'',' ']:
        self.compareReviewData(issue_review_dict,self.review_changeset_dict)
 

    def create_action_item(self,story_number, review_number):
      url= 'url to Crucible I am not supposed to share the url of the companies server.'
      action_item = '' 
      payload = {
                "fields":{
                           "project":{
                                   
                                      "id":str(self.projectID)
                                   },
                                   
                            "labels":self.labelName,
                           
                           "summary":"To move the proposed changes in DOORS for the review {}".format(review_number),
                           "description": "Review {}  has been closed for the story number(s) ".format(review_number,review_number) +",".join(story_number) + ". Move all the changes in DOORS(at path ******) for the same review.",
                           
                           "issuetype":{
                                   
                                      "name":"Action Item"
                                   },
                           "customfield_27803":{
                                       "value":"avc"
                           },  
                           
                           "assignee":{"name":"abc"}
                           
                        
                        }
              
              }
      
      #print ("Action Item Created",payload)
      '''
      if self.sprintID not in ['',' ',None,[],{},[[]]] and \
        self.projectID not in ['',' ',None,[],{},[[]]] and \
        self.labelName not in ['',' ',None,[],{},[[]]]:
        proxy = {"https":"#########################"}
        r = requests.post(url, json=payload,auth=(self.userName,self.password),proxies=proxy)
        print("Created an Action item for you:",r.text)
        
        action_item = self.moveActionItemTotheCurrentSprint(r.text)
        print("Moved the Created action item to the current_sprint: ", action_item )
        
        
      else:
        print("Tried to create an action item but could not find the required fields.")
      '''
      return action_item  
 
    def moveActionItemTotheCurrentSprint(self,response_action):
      action_item_number = ''
      # No logic found to add the action item to the current sprint, So following this approach:
      returned_data = re.findall("GSFDSA-\d+",str(response_action))
      if returned_data not in [None,[],'',' ']:
        action_item_number = returned_data
        
        payload2 = {
                      "issues":action_item_number
        
                   }
        url2 = 'url to Crucible I am not supposed to share the url of the companies server.'.format(self.sprintID)
        requests.post(url2, json = payload2, auth=(self.userName,self.password))
        
      return action_item_number
      
    def getStarwarsRerunInput(self):
      
      '''
      issue_review_dict[jira_issue_number] = [author_review,review_number,review_state]
      review_changeset_dict [jira_issue_number] = [no_of_files]
      '''
    
      if self.starwarsMarkForRerunON == True:
        from Starwars_MarkForRerun import Starwars_MarkForRerun
        intializers = [self.test_ids,self.review_changeset_dict, self.issue_review_dict]
        starwars_rerun = Starwars_MarkForRerun(*intializers)
        filesFoundinEvents = []
        ifFilesFoundDictIsEmpty = True
        storyStarwarsComment = {}
        comment = ''
        
        story_starwars_rerun = {}
        ids_testNameDict = {}
        
        for stories in self.google_sheet_data: 
          story_number = stories[0]
          StarwarsMarkForRerun = stories[6]
          storySummary = stories[1]
          
          if StarwarsMarkForRerun in ['Yes', 'yes','y','Y','YES']:
            storyStarwarsComment.setdefault(story_number,'')
            if ids_testNameDict in [{},None]:
              ids_testNameDict = starwars_rerun.GetAllTheTestFromTestIDs()

            if story_number in self.issue_review_dict:
              filesFoundinEvents = starwars_rerun.GetTestsToMarkBasedOnFilesInReview(story_number, ids_testNameDict)
              ifFilesFoundDictIsEmpty = starwars_rerun.ifFilesFoundDictIsEmpty(filesFoundinEvents)
              
              if ifFilesFoundDictIsEmpty in[None,[],'']:
                comment = '-Review is raised but no following test files found in starwars events.'+"\n-".join(self.review_changeset_dict[story_number])
                if not comment == '':
                  storyStarwarsComment[story_number] += comment
                
              else:
                starwars_rerun.markForReRunFiles(filesFoundinEvents)
                comment = "-Marked the Following files for rerun in starwars\n-"+"\n-".join(list(set(filesFoundinEvents)))+"\n"
                if not comment == '':
                  storyStarwarsComment[story_number] += comment
              
            else:
              fileToMarkInStarwarsDict = starwars_rerun.GettheFileNameFromStorySummary(storySummary)
              if fileToMarkInStarwarsDict not in ['',[],None]:
                starwars_rerun.markForReRunFiles(fileToMarkInStarwarsDict)
                comment = '-Marked the following files for rerrun in starwars.{}'.format("\n-".join(fileToMarkInStarwarsDict))+"\n"
                storyStarwarsComment[story_number] += comment
              else: 
                comment = 'Found no file in Review to mark for rerun or Review not raised yet and no file name written in the story summary could not be found in starwars'+"\n"
                if not comment == '':
                  storyStarwarsComment[story_number] += comment

                

            comment = '' 
        self.fillOut_cellData_AndUpdateExistingCells(story_comment = storyStarwarsComment)
    
    def runLocally(self):
      runTestOnVista = False
      runLocalDict = {}
      testNameFromSummaryDict = {}
      for stories in self.google_sheet_data: 
        story_number = stories[0]
        runLocally = stories[7]
        storySummary = stories[1]
        if runLocally in ['Yes', 'yes','y','Y','YES']:
          runTestOnVista = True
          if story_number not in testNameFromSummaryDict:
            testNameFromSummaryDict.setdefault(story_number,'')
          fileinStorySummary = storySummary.split()[-1]       
          if fileinStorySummary not in ['',None] and (fileinStorySummary.endswith('.xml') or \
            fileinStorySummary.endswith('.py') or fileinStorySummary.endswith('.c')):
            testNameFromSummaryDict[story_number] = fileinStorySummary
          intializers = [self.review_changeset_dict, self.issue_review_dict,testNameFromSummaryDict,story_number]
          RunTestsLocallyVista.__init__(self,*intializers)
          self.computeFilesToRunFromReview()
  
          
      if runTestOnVista:
        subprocess.Popen([Config.AFD_VISTAEXE_KILL, "-timeout=10"])
        time.sleep(10)
        subprocess.Popen(['python',Config.RUN_LOCALLY])
        #from RunTestsLocallyVista_Call import RunTestsLocallyVista_Call
        
      