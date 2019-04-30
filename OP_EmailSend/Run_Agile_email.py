from AgileData_email import AgileData_email
import time

agile = AgileData_email()

#while True:
json_string = agile.call_to_rest()
if json_string == None:
    raise Exception("Call to rest is not made correctly, Please try again, Make sure you provided correct Agile Username and Password:")
else:
    try:
        json_python_object = agile.load_json(json_string)
    except:
        raise Exception("Unable to convert json_data to python objects, Please try again")
    story_subtask_dictionary = agile.story_subtask_breakup(json_python_object)
    agile.compareDataWithPreviousRequest(story_subtask_dictionary)
  #print("Waiting for 30 seconds for next JIRA request")
  #time.sleep(30)