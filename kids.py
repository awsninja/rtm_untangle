from unifi import Unifi
from rtm import RTM
from dotenv import load_dotenv
from datetime import datetime
from ssh import execute_remote_command
from state import manual_lock
from sys import stdout

import logging
import pytz
import os
import random
import time
import json

load_dotenv()

NTH_CHAOS_MONKEY = int(os.environ.get('NTH_CHAOS_MONKEY'))
SLEEP_BEFORE_LOCKOUT = int(os.environ.get('SLEEP_BEFORE_LOCKOUT', 60))
rtm = RTM()
# Define logger
logger = logging.getLogger('kids_routine')
logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


class KidsRoutine:
    accounts = []

    def __init__(self):
        f = open("accounts.json")
        json_obj = json.load(f)
        self.accounts = json_obj['accounts']
        macs = [entry['mac'] for account in self.accounts for entry in account.get('macs', [])]
        self.unifi = Unifi(macs)


    def kids_routine(self):
        status_obj = self.unifi.firewall_get_status()
        status = status_obj['result']
        logger.info(f"Firewall Status is {status}")

        if manual_lock.is_active():
            logger.info(f"Manual lock active until {manual_lock.expires_at()}")
            if status != 'RUNNING':
                self.start_firewall()
            return

        chaos_monkey = random.randint(1, NTH_CHAOS_MONKEY) == 1
        if chaos_monkey:
            logger.info("Chaos Monkey flag set to True")
        now = datetime.now(pytz.timezone('America/New_York'))
        four_am = now.replace(hour=4, minute=0, second=0, microsecond=0)
        ten_pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
        if chaos_monkey:
            if status != 'RUNNING':
                logger.info('🙈🙈🙈 Chaos Monkey Sending START FIREWALL call')
                self.start_firewall()
            else:
                logger.info('Chaos Monkey called for again. Overriding and turning off firewall.')
                self.stop_firewall()
        elif now < four_am or now > ten_pm:
            if status != 'RUNNING':
                logger.info('Nighttime Sending START FIREWALL call')
                self.start_firewall()
            else:
                logger.info('Nighttime mode continuing')
        else:
            tasks_overdue = rtm.poll()
            if tasks_overdue:
                if status != 'RUNNING':
                    logger.info('Overdue Tasks Sending START FIREWALL call')
                    self.start_firewall()
                else:
                    logger.info('Overdue mode continuing')

            else:
                if status != 'INITIALIZED':
                    logger.info('Sending Stop Firewall call')
                    self.stop_firewall()

    def start_firewall(self):
        self.unifi.firewall_start()

    def stop_firewall(self):
        self.unifi.firewall_stop()
    
