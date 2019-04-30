
import os
import sys
import inspect
import  Configuration as Config
import subprocess

current_module = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

os.environ["atpMode"] = "2"
os.environ["execMode"] = "0"
os.environ["CONFIG_FILE"] = Config.APP_NAME
os.environ["MENU_OPTION_LIST"] = '["Host", "DWM ATPs (for non-Unified Framework programs)", "Quit"]'
os.environ["DAILY_RUN"]="ON"
os.environ["postSetupScript"] = current_module+"\\"+"RunTestsLocallyVista_Call.py"
p = subprocess.Popen(["start", Config.VISTA_START_BAT, Config.APP_NAME, Config.DIRECTORY, "0", "0", "0", Config.VISTA_VERSION, "AUTO_RUN", "0", Config.VISTA_PATH, Config.VISTA_ENVIRON, os.environ["execMode"], os.environ["atpMode"]])
p.wait()