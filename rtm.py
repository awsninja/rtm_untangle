import os
import sys
import webbrowser
from datetime import datetime, timezone
from rtmapi import Rtm

from dotenv import load_dotenv
load_dotenv()

RTM_API_KEY = os.environ.get('RTM_API_KEY')
RTM_SHARED_SECRET = os.environ.get('RTM_SHARED_SECRET')
RTM_TOKEN = os.environ.get('RTM_TOKEN')
OVERDUE_TASK_FILTER = os.environ.get('OVERDUE_TASK_FILTER')

class RTM:

    api = Rtm(RTM_API_KEY, RTM_SHARED_SECRET, "delete", RTM_TOKEN)

    def poll(self):
        overdue = False
        result = self.api.rtm.tasks.getList(filter=OVERDUE_TASK_FILTER)
        for tasklist in result.tasks:
            overdue = True
        return overdue

