import sys
sys.path.append(r'C:\Users\skansal\Desktop\Agile_Tool\Agile_Send_Email')
from AgileData_email import AgileData_email
import time
from Google_Api import Google_Api
import time

agile = AgileData_email()
google = Google_Api()
while True:
  json_string = agile.call_to_rest()
  userName_jira = json_string[1]
  password_jira = json_string[2]

  try:
    json_python_object = agile.load_json(json_string[0])
  except:
      number_of_tries = 5
      count = 0
      print ("Exception Occured, While making the Call to the Rest API")
      while count < number_of_tries:
        count = count+1
        try:
          print("Trying one more time to call the rest API After 5 minutes:")
          time.sleep(300)
          json_string = agile.call_to_rest()
          json_python_object = agile.load_json(json_string[0])
          break
        except Exception:
          print("Trying making call to JIRA one More time")
          
      if count == number_of_tries:
        raise ("Oh oh tried making call to JIRA Rest API 5 times but it did not respond,Make Sure yor provided correct JIRA username and password:")
            
  try:      
    story_subtask_dictionary,list_of_variables = agile.story_subtask_breakup(json_python_object)
    google.intializeVariables(story_subtask_dictionary,userName_jira,password_jira,*list_of_variables)
    google.create_object_of_gSheet()
    google.check_data_in_google_sheet()
  except Exception:
    print("Exception occurred during the google Oauth token refresh, Trying one more time to create the token,After 200 seconds of pause")
    time.sleep(200)
    google.intializeVariables(story_subtask_dictionary,userName_jira,password_jira,*list_of_variables)
    google.create_object_of_gSheet()
    google.check_data_in_google_sheet()
  print("Waiting for 100 seconds to update the google sheet")
  time.sleep(100)