import os
import time
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

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries

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
        self.controller = self._connect()

    def _connect(self):
        logger.info("Connecting to Unifi controller")
        return Controller(
            UNIFI_SERVER_ADDRESS,
            UNIFI_USERNAME,
            UNIFI_PASSWORD,
            port=UNIFI_PORT,
            version='UDMP-unifiOS',
            site_id=UNIFI_SITE,
            ssl_verify=False,
        )

    def _apply(self, action, mac):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if action == 'block':
                    self.controller.block_client(mac)
                else:
                    self.controller.unblock_client(mac)
                logger.info(f"{action} {mac} succeeded")
                return True
            except Exception as e:
                logger.warning(f"{action} {mac} attempt {attempt}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    self.controller = self._connect()
        logger.error(f"{action} {mac} FAILED after {MAX_RETRIES} attempts")
        return False

    def _get_blocked_macs(self):
        try:
            clients = self.controller.get_all_clients()
            return {c['mac'].lower() for c in clients if c.get('blocked')}
        except Exception as e:
            logger.warning(f"Could not query blocked client list: {e}")
            return None

    def firewall_start(self):
        failed = []
        for mac in self.macs:
            if not self._apply('block', mac):
                failed.append(mac)
        if failed:
            logger.error(f"firewall_start incomplete — failed MACs: {failed}")
        else:
            logger.info("firewall_start complete — all MACs blocked")
        self._verify('block')
        self.status = "RUNNING"

    def firewall_stop(self):
        failed = []
        for mac in self.macs:
            if not self._apply('unblock', mac):
                failed.append(mac)
        if failed:
            logger.error(f"firewall_stop incomplete — failed MACs: {failed}")
        else:
            logger.info("firewall_stop complete — all MACs unblocked")
        self._verify('unblock')
        self.status = "INITIALIZED"

    def _verify(self, action):
        blocked = self._get_blocked_macs()
        if blocked is None:
            logger.warning("_verify: could not confirm — blocked client query failed")
            return
        expected_blocked = action == 'block'
        mismatched = []
        for mac in self.macs:
            is_blocked = mac.lower() in blocked
            if is_blocked != expected_blocked:
                mismatched.append(mac)
        if mismatched:
            state = "unblocked" if expected_blocked else "still blocked"
            logger.error(f"_verify FAILED after {action}: {state} MACs: {mismatched}")
        else:
            logger.info(f"_verify OK after {action}: controller state matches intent")

    def firewall_get_status(self):
        return {
            "result": self.status,
        }
