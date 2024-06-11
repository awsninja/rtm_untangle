import json
from rtm import RTM
from ssh import execute_remote_command
import logging
from sys import stdout

rtm = RTM()

logger = logging.getLogger('ssh_logger')
logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)



class SelfRoutine:
    accounts = []

    def __init__(self):
        f = open("accounts.json")
        json_obj = self.accounts = json.load(f)
        self.accounts = json_obj['productivity_accounts']


    def self_routine(self):
        logger.info("self_routine called")
        tasks_overdue = rtm.poll_focus()
        logger.info(tasks_overdue)
        if tasks_overdue:
            self.start_productivity_mode()
        else:
            self.stop_productivity_mode()

    def start_productivity_mode(self):
        logger.info("Starting producivity mode")
        for account in self.accounts:
            execute_remote_command(
                account['hostname'],
                "root",
                "./productivity_on"
            )
        
    def stop_productivity_mode(self):
        logger.info("Stopping producivity mode")
        for account in self.accounts:
            execute_remote_command(
                account['hostname'],
                "root",
                "./productivity_off"
            )

        
