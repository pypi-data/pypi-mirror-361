# Push notifications
import requests
import json
import logging
logging.basicConfig(level=logging.INFO)
from datetime import datetime, timedelta
from ultrachatapp.constants import NOTIFICATION_URL

class Notification:
    def __init__(self):
        self.base_url = NOTIFICATION_URL
    def send(self, headers: dict, payload: dict):
        response = requests.post(self.base_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            logging.info(f"Notification sent to {self.base_url} successfully.")
        else:
            logging.error(f"Failed to send notification: {response.text}")
        