import os
import logging
from pyunifi.controller import Controller
from dotenv import load_dotenv
from sys import stdout

load_dotenv()

UNIFI_SERVER_ADDRESS = os.environ.get('UNIFI_SERVER_ADDRESS')
UNIFI_PORT = int(os.environ.get('UNIFI_PORT', 8443))
UNIFI_USERNAME = os.environ.get('UNIFI_USERNAME')
UNIFI_PASSWORD = os.environ.get('UNIFI_PASSWORD')
UNIFI_SITE = os.environ.get('UNIFI_SITE', 'default')

logger = logging.getLogger('unifi')
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter(
    "%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s"
)
consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


class Unifi:

    status = "INITIALIZED"

    def __init__(self, macs):
        self.macs = macs
        self.controller = Controller(
            UNIFI_SERVER_ADDRESS,
            UNIFI_USERNAME,
            UNIFI_PASSWORD,
            port=UNIFI_PORT,
            version='UDMP-unifiOS',
            site_id=UNIFI_SITE,
            ssl_verify=False,
        )

    def firewall_start(self):
        for mac in self.macs:
            logger.info(f"Blocking MAC {mac}")
            self.controller.block_client(mac)
        self.status = "RUNNING"

    def firewall_stop(self):
        for mac in self.macs:
            logger.info(f"Unblocking MAC {mac}")
            self.controller.unblock_client(mac)
        self.status = "INITIALIZED"

    def firewall_get_status(self):
        return {
            "result": self.status,
        }
