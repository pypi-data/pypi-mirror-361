
import requests
from ..exceptions import NigeriaBulkSMSException

class Data:
    def __init__(self, session, base_url, username, password):
        self._session = session
        self._base_url = base_url
        self._auth_params = {
            "username": username,
            "password": password,
        }

    def _fetch_data(self, action):
        params = {
            "action": action,
        }
        params.update(self._auth_params)

        try:
            response = self._session.get(self._base_url, params=params)
            response.raise_for_status()
            body = response.json()

            if body.get("status") == "success" or body.get("status") == "OK" or "balance" in body:
                return body
            elif body.get("error") is not None:
                raise NigeriaBulkSMSException(body["error"], code=body.get("errno"))
            else:
                raise NigeriaBulkSMSException("Unknown API error or unexpected response format.")
        except requests.exceptions.RequestException as e:
            raise NigeriaBulkSMSException(f"HTTP Request failed: {e}")

    def get_balance(self):
        return self._fetch_data("balance")

    def get_profile(self):
        return self._fetch_data("profile")

    def get_contacts(self):
        return self._fetch_data("contacts")

    def get_numbers(self):
        return self._fetch_data("numbers")

    def get_groups(self):
        return self._fetch_data("groups")

    def get_audios(self):
        return self._fetch_data("audios")

    def get_history(self):
        return self._fetch_data("history")

    def get_scheduled(self):
        return self._fetch_data("scheduled")

    def get_reports(self):
        return self._fetch_data("reports")

    def get_payments(self):
        return self._fetch_data("payments")


