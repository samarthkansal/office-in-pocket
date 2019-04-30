import json
import requests
from requests.auth import HTTPBasicAuth
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from email.utils import COMMASPACE
import getpass
import traceback
import csv
import os



class AgileData_email():

  def __init__(self):
    self.password = ''
    self.user_name= ''
    self.old_data = {}
    self.counter = 0 
    self.sprintName = ''
    self.labelNames = []
    self.projectID = ''
    self.sprintID = ''
    
  def call_to_rest(self):
    url='url to JIRA with the JQL parameters passed in the url, I am not supposed to share the url of the companies server.'
    proxy = {'https':'Behind a proxy server, Not a good practice to show the proxy details of the server'}
    Agile_Board = '' 
    try:
      if self.password=='' and self.user_name == '':
        self.user_name = input("Enter Jira User Name: ")
        self.password = getpass.getpass("Enter Jira Login Password: ")
        scrum_data = requests.get(url,proxies = proxy,auth = HTTPBasicAuth(self.user_name,self.password))
      else :
        scrum_data = requests.get(url,proxies = proxy,auth = HTTPBasicAuth(self.user_name,self.password))
      Agile_Board = scrum_data.json()
    except:
      errorString = traceback.format_exc()
    return [Agile_Board, self.user_name, self.password]

  
  def load_json(self,scrum_board_data):
    json_dump = json.dumps(scrum_board_data, indent=2 , sort_keys = True)
    with open(r'C:\Users\skansal\Desktop\json_data.json','w') as f:
        python_json_data = json.loads(json_dump)
        f.write(str(python_json_data))
    return python_json_data
  
  def story_subtask_breakup(self,story_subtask):
      issue_number = ''
      issue_type = ''
      issue_dict = {}
      for issues in story_subtask.get('issues',None):
          if issues: 
              if issues['key'] and not issues['key']=='':
                  
                  if issues['fields'].get('parent',None):
                    issue_number = issues['key']
                    story_number = issues['fields']['parent']['key']
                    asignee = issues['fields']['assignee']['displayName'] if issues['fields']['assignee'] else 'Unassigned'
                    status = issues['fields']['status']['name']
                    summary = issues['fields']['summary']
                    issue_dict.setdefault(story_number,{}) if story_number not in issue_dict else 'Do nothing'
                    if not issue_number in issue_dict[story_number] :
                        issue_dict[story_number].setdefault(issue_number,[])
                        issue_dict[story_number][issue_number] += [status,asignee,summary] 
                    else:
                        issue_dict[story_number][issue_number] += [status,asignee,summary] 
 
                  else:
                    issue_number = issues['key']
                    issue_dict.setdefault(issue_number,{}) if issue_number not in issue_dict else 'Do nothing'
                    issue_dict[issue_number].setdefault("Status",'') if issue_number in issue_dict else 'Do-nothing'
                    issue_dict[issue_number].setdefault("Assignee",'') if issue_number in issue_dict else 'Do-nothing'
                    issue_dict[issue_number].setdefault("Summary",'') if issue_number in issue_dict else 'Do-nothing'
                    issue_dict[issue_number]['Assignee'] = issues['fields']['assignee']['displayName'] if not issues['fields']['assignee'] in ['',None] else 'Unassigned'
                    issue_dict[issue_number]['Status'] = issues['fields']['status']['name'] if not issues['fields']['status'] in ['',None] else 'Do Nothing'
                    issue_dict[issue_number]['Summary'] = issues['fields']['summary'] if not issues['fields']['summary']=='' else 'Do Nothing'
                    
                    self.sprintName = issues['fields']['sprint']['name'] if not issues['fields']['sprint'] in ['',None] else 'No Sprint Name Found'
                    self.labelNames = issues['fields']['labels'] if not issues['fields']['labels'] in ['',None,[]] else 'No Label Found'
                    self.projectID = issues['fields']['project']['id'] if not issues['fields']['project'] in ['',None,[]] else 'No Project ID Found'
                    self.sprintID = issues['fields']['sprint']['id'] if not issues['fields']['sprint'] in ['',None,[]] else 'No Sprint ID Found'
                    
                    if issues['fields'].get('subtasks',None):
                     assignee = '' 
                     
                     path_subtask_ids = issues['fields']['subtasks']
                     for path_subtask_id in path_subtask_ids:
                       subtask_id = path_subtask_id['key']
                       #if (subtask_id == "GSFDSA-29945"):
                         #import pdb
                         #pdb.set_trace()
                       subtask_summary = path_subtask_id['fields']['summary']
                       subtask_status = path_subtask_id['fields']['status']['name']
                       if subtask_id not in [' ','']  :
                         if subtask_id not in issue_dict[issue_number]:
                           issue_dict[issue_number].setdefault(subtask_id,[])
                           issue_dict[issue_number][subtask_id] += [subtask_status,assignee,subtask_summary]
                         else:
                           issue_dict[issue_number][subtask_id] += [subtask_status,assignee,subtask_summary]
              else:
                        print("No key found")
          else:
              print('No issue Found')
      return issue_dict,[self.sprintName, self.sprintID ,self.labelNames, self.projectID]
      
  def compareDataWithPreviousRequest(self,issue_dict):
      self.counter = self.counter + 1

      sub_task_id = []
      new_subtask_status = []
      old_subtask_status = []
      send_email_subtask = False

      if not self.old_data:
        self.old_data = issue_dict
        return
      
      else:
         for story_number in issue_dict:
             old_request_story_number = self.old_data[story_number]
             new_request_story_number = issue_dict[story_number]
             if (new_request_story_number['Status'] in old_request_story_number) and (new_request_story_number['Status'] != old_request_story_number['Status']):
                 status ='Status of Story number '+ story_number +' :  /n('+ new_request_story_number +') assigned on '+new_request_story_number['Assignee']+' from '+ old_request_story_number['Status'] \
                              + ' to '+new_request_story_number['Status']
                 self.send_email(status)
                 print("Sent Email")
             sub_task_id = [x for x in { x : issue_dict[story_number][x] for x in issue_dict[story_number] if x not in ['Status','Assignee','Summary']}]
             for index in range(0,len(sub_task_id)):
                 new_subtask_status.insert(index,new_request_story_number[sub_task_id[index]][0])
                 old_subtask_status.insert(index,old_request_story_number[sub_task_id[index]][0])

             send_email_subtask = self.computesubtaskData(old_subtask_status,new_subtask_status) 
             #if (sub_task_id == list(self.old_data[story_number].keys())) else print ('One of the subtasks for the story number '+story_number+' is not found in previous request')
             del new_subtask_status[:]
             del old_subtask_status[:]
             if send_email_subtask:               
                 status_subtask = 'For story number '+story_number+ ' all the subtasks ( '+" , ".join(sub_task_id)+') have been closed and story can be closed.' 
                 self.send_email(status_subtask)
                 print("Sent Email")

         self.old_data=issue_dict
              
 
        
  def computesubtaskData(self,old_request_subtask_status, new_request_subtask_status):
      change = False 
      send_email = False
      
      for index in range (0,len(new_request_subtask_status)):
          if old_request_subtask_status[index] in ['Closed','Resolved']:
              pass
          
          elif not (old_request_subtask_status[index] == new_request_subtask_status[index]) and (new_request_subtask_status[index] in ['Closed','Resolved']) :
              change = True
      closed = int(new_request_subtask_status.count('Closed'))
      resolved = int(new_request_subtask_status.count('Resolved'))
      if (change == True) and (len(new_request_subtask_status) == closed+resolved):
          send_email = True
      return send_email
          
        
  def send_email(self,Msg_String):
      try:
        recipients = 'samarth.kansal@gmail.com'
        msg = MIMEText(str(Msg_String))
        email_from = 'JIRA_AW609_BOARD@gmail.com'
        email_subject = "Status of Agile Board" 
        msg['From'] = email_from
        msg['To'] = 'samarth.kansal@gmail.com'
        msg['Subject'] = email_subject
        mail = smtplib.SMTP(host='smtpimr.*****.com')
        mail.sendmail(email_from,recipients,msg.as_string())
        mail.quit()
      except:
         raise Exception("Error,While sending an email. Please Retry: "+traceback.format_exc())