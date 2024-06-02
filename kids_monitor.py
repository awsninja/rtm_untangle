import logging
import random
import os
import pytz
import time
import json

from rtm import RTM
from untangle import Untangle
from datetime import datetime
from remote_command import RemoteCommand

# Define logger
logger = logging.getLogger('poll_logger')

NTH_CHAOS_MONKEY = int(os.environ.get('NTH_CHAOS_MONKEY'))


class KidsMonitor:

    def __init__(self):
        f = open("accounts.json")
        json_obj = self.accounts = json.load(f)
        self.accounts = json_obj['accounts']
        
        self.first_run = True
        self.untangle = Untangle()
        self.rtm = RTM()
        self.remote_command = RemoteCommand()

    def kids_monitor(self):
        if self.first_run:
            logger.info("Forcing a Firewall Stop for the first iteration")
            self.stop_firewall()
            self.first_run = False
            return
        status_obj = self.untangle.firewall_get_status()
        status = status_obj['result']
        logger.info(f"Firewall Status is {status}")
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
            tasks_overdue = self.rtm.poll()
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
        self.untangle.firewall_start()
        time.sleep(60)
        for account in self.accounts:
            logger.info(f"Locking workstation account for {account['username']}")
            self.remote_command.execute_remote_command(
                account['hostname'],
                "root",
                f"passwd -l {account['username']}"
            )
            logger.info(f"Locking screen for {account['username']}")
            self.remote_command.execute_remote_command(
                account['hostname'],
                account['username'],
                "xdg-screensaver lock"
            )

        
    def stop_firewall(self):
        for account in self.accounts:
            logger.info(f"Unlocking workstation account for {account['username']}")
            self.remote_command.execute_remote_command(
                account['hostname'],
                "root",
                f"passwd -u {account['username']}"
            )
        self.untangle.firewall_stop()
                    
