
import requests
from ..exceptions import NigeriaBulkSMSException

class SMS:
    def __init__(self, session, base_url, username, password):
        self._session = session
        self._base_url = base_url
        self._auth_params = {
            "username": username,
            "password": password,
        }

    def send(self, message, sender, mobiles):
        params = {
            "message": message,
            "sender": sender,
            "mobiles": ",".join(mobiles) if isinstance(mobiles, list) else mobiles,
        }
        params.update(self._auth_params)

        try:
            response = self._session.get(self._base_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            body = response.json()

            if body.get("status") == "OK":
                return body
            elif body.get("error") is not None:
                raise NigeriaBulkSMSException(body["error"], code=body.get("errno"))
            else:
                raise NigeriaBulkSMSException("Unknown API error or unexpected response format.")
        except requests.exceptions.RequestException as e:
            raise NigeriaBulkSMSException(f"HTTP Request failed: {e}")


