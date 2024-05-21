from rtm import RTM
from untangle import Untangle
from dotenv import load_dotenv
import os
import logging
import pytz
import paramiko
import json
import sys
from sys import stdout
from datetime import datetime, timedelta
import time
import random

load_dotenv()

untangle = Untangle()
rtm = RTM()

POLL_INTERVAL_MIN = os.environ.get('POLL_INTERVAL_MIN')
POLL_INTERVAL_MAX = os.environ.get('POLL_INTERVAL_MAX')

NTH_CHAOS_MONKEY = int(os.environ.get('NTH_CHAOS_MONKEY'))

# Define logger
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

        first_run = True
        while True:
            if first_run:
                logger.info("Forcing a Firewall Stop for the first iteration")
                self.stop_firewall()
                first_run = False
                self.sleep()
                continue
            status_obj = untangle.firewall_get_status()
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
            self.sleep()

    def start_firewall(self):
        untangle.firewall_start()
        time.sleep(60)
        for account in self.accounts:
            logger.info(f"Locking workstation account for {account['username']}")
            self.execute_remote_command(
                account['hostname'],
                "root",
                f"passwd -l {account['username']}"
            )
            logger.info(f"Locking screen for {account['username']}")
            self.execute_remote_command(
                account['hostname'],
                account['username'],
                "xdg-screensaver lock"
            )

        
    def stop_firewall(self):
        for account in self.accounts:
            logger.info(f"Unocking workstation account for {account['username']}")
            self.execute_remote_command(
                account['hostname'],
                "root",
                f"passwd -u {account['username']}"
            )
        untangle.firewall_stop()

            
    def sleep(self):
        now = datetime.now(pytz.timezone('America/New_York'))
        sleep_for = random.randint(int(POLL_INTERVAL_MIN), int(POLL_INTERVAL_MAX))
        end_time = now + timedelta(0, sleep_for)
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S,%f')
        logger.info(f"Sleeping for {sleep_for} seconds ending {end_time_str}")
        time.sleep(int(sleep_for)) 

        
    def execute_remote_command(self, host, username, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        k = paramiko.RSAKey.from_private_key_file("./ssh_private_key")
        try:
            ssh.connect(host, username=username, pkey=k)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
            ssh_stdin.close()
        except:
            logger.info(f"Cound not connect via ssh to host {host}.")
   
poll = Poll()
poll.run()

