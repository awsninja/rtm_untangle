from rtm import RTM
from untangle import Untangle
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
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
            status_obj = untangle.firewall_get_status()
            status = status_obj['result']
            logging.info(f"Firewall Status is {status}")
            now  = datetime.now()
            four_am = now.replace(hour=4, minute=0, second=0, microsecond=0)
            ten_pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
            if now < four_am or now > ten_pm:
                if status != 'RUNNING':
                    logging.info('Nighttime Sending START FIREWALL call')
                    untangle.firewall_start()
            else:
                tasks_overdue = rtm.poll()
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

