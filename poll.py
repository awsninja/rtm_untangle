from rtm import RTM
from untangle import Untangle
from dotenv import load_dotenv
import os
import logging
import pytz
from sys import stdout
from datetime import datetime
import time
import random

load_dotenv()

untangle = Untangle()
rtm = RTM()

POLL_INTERVAL_MIN = os.environ.get('POLL_INTERVAL_MIN')
POLL_INTERVAL_MAX = os.environ.get('POLL_INTERVAL_MAX')

# Define logger
logger = logging.getLogger('poll_logger')

logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

class Poll:
    def run(self):
        while True:
            status_obj = untangle.firewall_get_status()
            status = status_obj['result']
            logger.info(f"Firewall Status is {status}")
            now = datetime.now(pytz.timezone('America/New_York'))
            four_am = now.replace(hour=4, minute=0, second=0, microsecond=0)
            ten_pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
            if now < four_am or now > ten_pm:
                if status != 'RUNNING':
                    logger.info('Nighttime Sending START FIREWALL call')
                    untangle.firewall_start()
            else:
                tasks_overdue = rtm.poll()
                if tasks_overdue:
                    if status != 'RUNNING':
                        logger.info('Overdue Tasks Sending START FIREWALL call')
                        untangle.firewall_start()
                else:
                    if status != 'INITIALIZED':
                        logger.info('Sending Stop Firewall call')
                        untangle.firewall_stop()
            sleep_for = random.randint(int(POLL_INTERVAL_MIN), int(POLL_INTERVAL_MAX))
            logger.info(f"Sleeping for {sleep_for} seconds")
            time.sleep(int(sleep_for))

poll = Poll()
poll.run()

