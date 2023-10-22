from datetime import datetime, timedelta
import logging
import requests

logger = logging.getLogger("eps")


class EPS:

    ARMED_AWAY = "TOTAL"
    ARMED_NIGHT = "PARTIAL"
    DISARMED = "OFF"
    TRIGGERED = ""

    tokenHeaders = {
        'accept': '*/*',
        'Content-type': 'application/x-www-form-urlencoded',
        'Host': 'y41hsspp-mobile.eps-api.com',
    }

    connectHeaders = {
        'accept': '*/*',
        'Content-type': 'application/json',
        'Host': 'y41hsspp-mobile.eps-api.com',
        'Eps-Ctx-Source': 'MOB-ABO',
    }

    apiHeaders = {
        'accept': '*/*',
        'Content-type': 'application/json',
    }

    apiURL = 'https://y41hsspp-mobile.eps-api.com/'

    def __init__(self, token, login, password) -> None:
        self.token = token
        self.login = login
        self.password = password

        self.site = None

        self.session_id = None
        self.login_expires = None

        super().__init__()

    def _get_token(self):
        self.tokenHeaders['authorization'] = f'Basic {self.token}'
        response = requests.post(self.apiURL+'token',
            headers=self.tokenHeaders,
            data='grant_type=client_credentials&scope=PRODUCTION'
        )
        if response.status_code != 200:
            logger.warning(f"Response with status {response.status_code}: {response.text}")
            return False

        expires_in = response.json()['expires_in']
        login_expires_delay = expires_in * 1000
        self.login_expires = datetime.now() + timedelta(milliseconds=login_expires_delay - 30000)

        access_token = response.json()['access_token']
        self.apiHeaders['authorization'] = 'Bearer ' + access_token
        self.connectHeaders['authorization'] = 'Bearer ' + access_token

        logger.info(f"Token obtaineed {datetime.now():%Y-%m-%d %H:%M:%S}")
        logger.info(f"Token is {access_token}")
        logger.info(f"Token expires {self.login_expires:%Y-%m-%d %H:%M:%S}")
        return True


    def _get_session(self):
        json_body = {
          'application': 'SMARTPHONE',
          'typeDevice': 'SMARTPHONE',
          'pwd': self.password,
          'login': self.login,
          # 'originSession': self.originSession,
          'phoneType': '',
          'codeLanguage': 'FR',
          'version': '',
          'timestamp': '0',
          'system': '',
        }
        self.connectHeaders['Eps-Ctx-Username'] = self.login
        response = requests.post(
            self.apiURL + 'smartphone/production/1.0.0/connect',
            headers=self.connectHeaders,
            json=json_body
        )
        # print(json.dumps(response.json(), indent=4))
        if response.status_code != 200:
            logger.warning(f"Response with status {response.status_code}: {response.text}")
            return False
        self.session_id = response.json()['idSession']
        logger.info(f"Session ID is {self.session_id}")
        self.site = response.json()['sites'][0]['idSite']
        logger.info(f"Site is {response.json()['sites'][0]['title']} ({self.site})")
        return True

    def _auth(self) -> None:
        if self.login_expires is None:
            logger.info("Login exipiry is not defined, asking token and session")
            self._get_token()
            self._get_session()
            return
        if self.login_expires <= datetime.now():
            logger.info("Login expired, asking token and session")
            self._get_token()
            self._get_session()
            return
        if self.session_id is None:
            logger.info("No session, asking session")
            self._get_session()
            return
        return

    def get_site(self):
        self._auth()
        return self.site

    def get_status(self):
        self._auth()
        response = requests.get(
            f"{self.apiURL}smartphone/production/1.0.0/homepage/{self.session_id}",
            headers=self.apiHeaders,
        )
        if response.status_code == 403:
            self.session_id = None
            return False
        if response.status_code != 200:
            logger.warning(f"Response with status {response.status_code}: {response.text}")
            return False
        status = response.json()['systemLastState']['securityMode']
        logger.info(f"Alarm status is {status}")
        return status

    def arm_away(self, silent=False):
        self._auth()
        json_body = {
            'idSession': self.session_id,
            'silentMode': silent,
            'interventionService': True,
            # self.securitySystem.procedure == 'INTERVENTION' ? true : false,
            'systemMode': 'TOTAL',
        }
        response = requests.post(self.apiURL + 'system/askstart/',
            headers=self.apiHeaders,
            json=json_body
        )
        if response.status_code != 200:
            logger.warning(f"Response with status {response.status_code}: {response.text}")
            return False
        print(response.text)
        return True

    def arm_night(self, silent=False):
        self._auth()
        json_body = {
            'idSession': self.session_id,
            'silentMode': silent,
            'interventionService': True, 
            # self.securitySystem.procedure == 'INTERVENTION' ? true : false,
            'systemMode': 'PARTIAL',
        }
        response = requests.post(self.apiURL + 'system/askstart/',
            headers=self.apiHeaders,
            json=json_body
        )
        if response.status_code != 200:
            logger.warning(f"Response with status {response.status_code}: {response.text}")
            return False
        print(response.text)
        return True

    def disarm(self, silent=False):
        self._auth()
        json_body = {
            'silentMode': silent,
            'idSession': self.session_id
        }
        response = requests.post(self.apiURL + 'system/askstop',
            headers=self.apiHeaders,
            json=json_body
        )
        if response.status_code != 200:
            logger.warning(f"Response with status {response.status_code}: {response.text}")
            return False
        print(response.text)
        return True
