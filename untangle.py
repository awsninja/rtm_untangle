import os
import http.client
import json

from dotenv import load_dotenv

load_dotenv()

UNTANGLE_FIREWALL_ID = os.environ.get('UNTANGLE_FIREWALL_ID')
UNTANGLE_SERVER_ADDRESS = os.environ.get('UNTANGLE_SERVER_ADDRESS')

class Untangle:

    nonce = ''
    cooke = ''
    
    request_id = 1

    def firewall_start(self):
        payload = {
            'method': f".obj#{UNTANGLE_FIREWALL_ID}.start",
        }
        return self.__request(payload)

    def firewall_stop(self):
        payload = {
            'method': f".obj#{UNTANGLE_FIREWALL_ID}.stop",
        }
        return self.__request(payload)

        
    def firewall_get_status(self):
        payload = {
            'method': f".obj#{UNTANGLE_FIREWALL_ID}.getRunState",
        }
        res = self.__request(payload)
        return res

    
    def __authenticate(self):
        conn = http.client.HTTPConnection(
            UNTANGLE_SERVER_ADDRESS,
        )
        payload = 'username=admin&password=HuFOI.ku7m4w'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = "/auth/login?url=/setup/welcome.do&realm=Administrator"
        conn.request("POST", url, payload, headers)
        res = conn.getresponse()
        headers = res.getheaders()

        for header in headers:
            if header[0] == 'Set-Cookie':
                self.cookie = header[1].split(';')[0]

        payload = {
            "method": "system.getNonce",
        }

        obj = self.__request(payload, True)
        self.nonce = obj['result']

    def __request(self, payload, skip_auth=False):
        if not skip_auth:
            self.__authenticate()

        headers = {
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
        }
        payload['id'] = self.request_id
        self.request_id += 1
        payload['nonce'] = self.nonce

        if 'params' not in payload:
            payload['params'] = []
        json_str = json.dumps(payload)
        conn = http.client.HTTPConnection(UNTANGLE_SERVER_ADDRESS)
        conn.request("POST", "/admin/JSON-RPC", json_str, headers)
        res = conn.getresponse()
        data = res.read()
        data_str = data.decode('utf-8')
        obj = json.loads(data_str)
        return obj


