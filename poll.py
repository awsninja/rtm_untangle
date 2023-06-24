from rtm import RTM
from untangle import Untangle
from dotenv import load_dotenv

import logging


import time

load_dotenv()

untangle = Untangle()
rtm = RTM()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
class Poll:
    def run(self):
        while True:
            tasks_overdue = rtm.poll()
            status = untangle.firewall_get_status()
            if tasks_overdue:
                if status != 'RUNNING':
                    logging.info('Sending START FIREWALL call')
                    untangle.firewall_start()
            else:
                if status != 'INITIALIZED':
                    logging.info('Sending Stop Firewall call')
                    untangle.firewall_stop()
            time.sleep(30*60)

poll = Poll()
poll.run()

