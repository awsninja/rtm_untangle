import os
import sys
import webbrowser
import logging
from sys import stdout
from datetime import datetime, timezone
from rtmapi import Rtm

from dotenv import load_dotenv
load_dotenv()

RTM_API_KEY = os.environ.get('RTM_API_KEY')
RTM_SHARED_SECRET = os.environ.get('RTM_SHARED_SECRET')
RTM_TOKEN = os.environ.get('RTM_TOKEN')
OVERDUE_TASK_FILTER = os.environ.get('OVERDUE_TASK_FILTER')
OVERDUE_FOCUS_FILTER = os.environ.get('OVERDUE_FOCUS_FILTER')

logger = logging.getLogger('rtm_logger')
logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


class RTM:

    api = Rtm(RTM_API_KEY, RTM_SHARED_SECRET, "delete", RTM_TOKEN)

    def poll(self):
        overdue = False
        result = self.api.rtm.tasks.getList(filter=OVERDUE_TASK_FILTER)
        for tasklist in result.tasks:
            for taskseries in tasklist:
                if taskseries.task.completed == '':
                    logger.info(f"Overdue Task: {taskseries.name} in list")
                    overdue = True
        return overdue


    def poll_focus(self):
        overdue = False
        result = self.api.rtm.tasks.getList(filter=OVERDUE_FOCUS_FILTER)
        for tasklist in result.tasks:
            for taskseries in tasklist:
                if taskseries.task.completed == '':
                    logger.info(f"Overdue Task: {taskseries.name} in list")
                    overdue = True
        return overdue
        
