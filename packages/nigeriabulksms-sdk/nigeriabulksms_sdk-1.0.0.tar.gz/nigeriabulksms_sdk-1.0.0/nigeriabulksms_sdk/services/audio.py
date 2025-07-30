
import requests
from ..exceptions import NigeriaBulkSMSException

class Audio:
    def __init__(self, session, base_url, username, password):
        self._session = session
        self._base_url = base_url
        self._auth_params = {
            "username": username,
            "password": password,
        }

    def upload(self, url):
        params = {
            "action": "upload",
            "url": url,
        }
        params.update(self._auth_params)

        try:
            response = self._session.get(self._base_url, params=params)
            response.raise_for_status()
            body = response.json()

            if body.get("status") == "success":
                return body
            elif body.get("error") is not None:
                raise NigeriaBulkSMSException(body["error"], code=body.get("errno"))
            else:
                raise NigeriaBulkSMSException("Unknown API error or unexpected response format.")
        except requests.exceptions.RequestException as e:
            raise NigeriaBulkSMSException(f"HTTP Request failed: {e}")


