
import logging
import pytz
from rtm import RTM
from untangle import Untangle
from kids_monitor import KidsMonitor
from dotenv import load_dotenv
import os
import json
from sys import stdout
from datetime import datetime, timedelta
import time
import random

load_dotenv()

untangle = Untangle()
rtm = RTM()
kids_monitor = KidsMonitor()

POLL_INTERVAL_MIN = os.environ.get('POLL_INTERVAL_MIN')
POLL_INTERVAL_MAX = os.environ.get('POLL_INTERVAL_MAX')
NTH_CHAOS_MONKEY = int(os.environ.get('NTH_CHAOS_MONKEY'))
logger = logging.getLogger('poll_logger')
logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

class Poll:

    accounts = []
    
    def run(self):
        f = open("accounts.json")
        json_obj = self.accounts = json.load(f)
        self.accounts = json_obj['accounts']

        while True:
            kids_monitor.kids_monitor()
            self.sleep()

            
    def sleep(self):
        now = datetime.now(pytz.timezone('America/New_York'))
        sleep_for = random.randint(int(POLL_INTERVAL_MIN), int(POLL_INTERVAL_MAX))
        end_time = now + timedelta(0, sleep_for)
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S,%f')
        logger.info(f"Sleeping for {sleep_for} seconds ending {end_time_str}")
        time.sleep(int(sleep_for)) 

        

   
poll = Poll()
poll.run()

