
import requests
from .services.sms import SMS
from .services.call import Call
from .services.audio import Audio
from .services.data import Data

class NigeriaBulkSMSClient:
    def __init__(self, username, password, base_url="https://portal.nigeriabulksms.com/api/"):
        self.username = username
        self.password = password
        self.base_url = base_url
        self._session = requests.Session()

        self.sms = SMS(self._session, self.base_url, self.username, self.password)
        self.call = Call(self._session, self.base_url, self.username, self.password)
        self.audio = Audio(self._session, self.base_url, self.username, self.password)
        self.data = Data(self._session, self.base_url, self.username, self.password)

    def _get_auth_params(self):
        return {
            "username": self.username,
            "password": self.password,
        }


